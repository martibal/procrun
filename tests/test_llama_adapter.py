import hashlib
import json
from datetime import date
from pathlib import Path

import pytest

from procrun import component_engine, llama_adapter, model_fallback, model_registry

ComponentDomain = component_engine.ComponentDomain
LlamaAdapterError = llama_adapter.LlamaAdapterError
LlamaBenchmarkConfig = llama_adapter.LlamaBenchmarkConfig
ProcessResult = llama_adapter.ProcessResult
benchmark_cache_key = llama_adapter.benchmark_cache_key
prepare_llama_benchmark_runtime = llama_adapter.prepare_llama_benchmark_runtime
run_llama_component_benchmark = llama_adapter.run_llama_component_benchmark
AllowedComponentCategory = model_fallback.AllowedComponentCategory
LocalModelIdentity = model_fallback.LocalModelIdentity
LocalModelRequest = model_fallback.LocalModelRequest
ModelPromptSpan = model_fallback.ModelPromptSpan
ModelApprovalStatus = model_registry.ModelApprovalStatus
ModelArtifactSpec = model_registry.ModelArtifactSpec


SPAN_TEXT = "nova subestação"
SPAN_START = 100
SPAN_END = SPAN_START + len(SPAN_TEXT)


def fixture_spec(
    content: bytes,
    *,
    status: ModelApprovalStatus = ModelApprovalStatus.BENCHMARK_CANDIDATE,
) -> ModelArtifactSpec:
    return ModelArtifactSpec(
        repository="fixture/local-model",
        revision="a" * 40,
        filename="fixture.gguf",
        identity=LocalModelIdentity(
            model_id="fixture/local-model:Q4_K_M",
            artifact_sha256=hashlib.sha256(content).hexdigest(),
        ),
        size_bytes=len(content),
        license_id="Apache-2.0",
        license_url="https://example.invalid/model-license",
        commercial_use_allowed=True,
        license_reviewed_on=date(2026, 9, 1),
        license_review_due_on=date(2026, 11, 30),
        status=status,
    )


def request() -> LocalModelRequest:
    return LocalModelRequest(
        operation_code="OP-1",
        source_sha256="a" * 64,
        domains=(ComponentDomain.RAIL_TRANSPORT,),
        unmatched_scope_spans=(
            ModelPromptSpan(
                start=SPAN_START,
                end=SPAN_END,
                text=SPAN_TEXT,
            ),
        ),
        allowed_categories=(
            AllowedComponentCategory(
                domain=ComponentDomain.RAIL_TRANSPORT,
                category="electrification_catenary",
                label="Electrification and catenary",
            ),
        ),
    )


def runtime(
    tmp_path: Path,
    *,
    status: ModelApprovalStatus = ModelApprovalStatus.BENCHMARK_CANDIDATE,
    max_cache_entries: int = 256,
):
    model_bytes = b"fixture-model"
    binary_bytes = b"fixture-llama-cli"
    model_path = tmp_path / "fixture.gguf"
    binary_path = tmp_path / "llama-cli"
    model_path.write_bytes(model_bytes)
    binary_path.write_bytes(binary_bytes)
    binary_path.chmod(0o755)
    spec = fixture_spec(model_bytes, status=status)
    prepared = prepare_llama_benchmark_runtime(
        llama_cli_path=binary_path,
        model_path=model_path,
        model_spec=spec,
        config=LlamaBenchmarkConfig(
            threads=4,
            context_size=4096,
            max_output_tokens=256,
            timeout_seconds=30,
            max_cache_entries=max_cache_entries,
            max_memory_mb=6144,
        ),
    )
    return prepared


def valid_output() -> bytes:
    return json.dumps(
        {
            "proposals": [
                {
                    "domain": "rail_transport",
                    "category": "electrification_catenary",
                    "span_index": 0,
                    "start_token": 0,
                    "end_token": 1,
                }
            ]
        },
        ensure_ascii=False,
    ).encode("utf-8")


def test_runtime_preparation_verifies_model_and_hashes_llama_binary(
    tmp_path: Path,
) -> None:
    prepared = runtime(tmp_path)

    assert prepared.model_spec.identity.model_id == "fixture/local-model:Q4_K_M"
    assert prepared.llama_cli_sha256 == hashlib.sha256(
        b"fixture-llama-cli"
    ).hexdigest()


def test_benchmark_adapter_rejects_non_candidate_artifact(tmp_path: Path) -> None:
    with pytest.raises(LlamaAdapterError, match="BENCHMARK_CANDIDATE"):
        runtime(tmp_path, status=ModelApprovalStatus.APPROVED)


def test_adapter_uses_offline_deterministic_resource_bounds(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepared = runtime(tmp_path)
    monkeypatch.setenv("LLAMA_ARG_N_PREDICT", "999999")
    monkeypatch.setenv("HTTPS_PROXY", "https://proxy.invalid")
    captured: dict[str, object] = {}

    def fake_invoker(
        argv: tuple[str, ...],
        env: dict[str, str],
        timeout_seconds: float,
        max_memory_mb: int,
    ) -> ProcessResult:
        captured["argv"] = argv
        captured["env"] = env
        captured["timeout"] = timeout_seconds
        captured["memory"] = max_memory_mb

        prompt_path = Path(argv[argv.index("--file") + 1])
        schema_path = Path(argv[argv.index("--json-schema-file") + 1])
        prompt = prompt_path.read_text(encoding="utf-8")
        assert SPAN_TEXT in prompt
        assert '"token_index":0' in prompt
        assert '"token_index":1' in prompt
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        assert schema["additionalProperties"] is False
        properties = schema["properties"]["proposals"]["items"]["properties"]
        assert set(properties) == {
            "domain",
            "category",
            "span_index",
            "start_token",
            "end_token",
        }

        return ProcessResult(
            returncode=0,
            stdout=valid_output(),
            stderr=b"",
            elapsed_seconds=1.25,
        )

    result = run_llama_component_benchmark(
        request(),
        prepared,
        invoker=fake_invoker,
    )

    argv = captured["argv"]
    assert isinstance(argv, tuple)
    joined = " ".join(argv)
    assert "Qwen" not in joined
    assert SPAN_TEXT not in joined
    assert "--offline" in argv
    assert "--json-schema-file" in argv
    assert "--single-turn" in argv
    assert argv[argv.index("--reasoning") + 1] == "off"
    assert argv[argv.index("--reasoning-budget") + 1] == "0"
    assert argv[argv.index("--temp") + 1] == "0"
    assert argv[argv.index("--seed") + 1] == "0"
    assert argv[argv.index("--ctx-size") + 1] == "4096"
    assert argv[argv.index("--n-predict") + 1] == "256"
    assert argv[argv.index("--log-verbosity") + 1] == "1"
    assert "-hf" not in argv
    assert "--hf-repo" not in argv

    env = captured["env"]
    assert isinstance(env, dict)
    assert "LLAMA_ARG_N_PREDICT" not in env
    assert "HTTPS_PROXY" not in env
    assert captured["timeout"] == 30
    assert captured["memory"] == 6144
    assert result.cache_hit is False
    assert result.elapsed_seconds == 1.25
    assert result.batch.proposals[0].start == SPAN_START
    assert result.batch.proposals[0].end == SPAN_END
    assert result.batch.proposals[0].source_text == SPAN_TEXT


def test_extra_or_non_json_model_output_is_rejected(tmp_path: Path) -> None:
    prepared = runtime(tmp_path)

    def fake_invoker(
        argv: tuple[str, ...],
        env: dict[str, str],
        timeout_seconds: float,
        max_memory_mb: int,
    ) -> ProcessResult:
        del argv, env, timeout_seconds, max_memory_mb
        return ProcessResult(
            returncode=0,
            stdout=b'{"proposals":[],"status":"OPEN"}',
            stderr=b"",
            elapsed_seconds=0.1,
        )

    with pytest.raises(LlamaAdapterError, match="strict proposal JSON"):
        run_llama_component_benchmark(
            request(),
            prepared,
            invoker=fake_invoker,
        )


def test_token_range_outside_unmatched_scope_is_rejected(tmp_path: Path) -> None:
    prepared = runtime(tmp_path)
    bad = json.dumps(
        {
            "proposals": [
                {
                    "domain": "rail_transport",
                    "category": "electrification_catenary",
                    "span_index": 0,
                    "start_token": 0,
                    "end_token": 99,
                }
            ]
        }
    ).encode()

    def fake_invoker(
        argv: tuple[str, ...],
        env: dict[str, str],
        timeout_seconds: float,
        max_memory_mb: int,
    ) -> ProcessResult:
        del argv, env, timeout_seconds, max_memory_mb
        return ProcessResult(
            returncode=0,
            stdout=bad,
            stderr=b"",
            elapsed_seconds=0.1,
        )

    with pytest.raises(LlamaAdapterError, match="token range is outside"):
        run_llama_component_benchmark(
            request(),
            prepared,
            invoker=fake_invoker,
        )


def test_disallowed_domain_category_pair_is_rejected(tmp_path: Path) -> None:
    prepared = runtime(tmp_path)
    bad = json.dumps(
        {
            "proposals": [
                {
                    "domain": "rail_transport",
                    "category": "track",
                    "span_index": 0,
                    "start_token": 0,
                    "end_token": 1,
                }
            ]
        },
        ensure_ascii=False,
    ).encode()

    def fake_invoker(
        argv: tuple[str, ...],
        env: dict[str, str],
        timeout_seconds: float,
        max_memory_mb: int,
    ) -> ProcessResult:
        del argv, env, timeout_seconds, max_memory_mb
        return ProcessResult(
            returncode=0,
            stdout=bad,
            stderr=b"",
            elapsed_seconds=0.1,
        )

    with pytest.raises(LlamaAdapterError, match="domain/category pair"):
        run_llama_component_benchmark(
            request(),
            prepared,
            invoker=fake_invoker,
        )


def test_empty_proposals_are_valid_and_do_not_invent_a_component(
    tmp_path: Path,
) -> None:
    prepared = runtime(tmp_path)

    def fake_invoker(
        argv: tuple[str, ...],
        env: dict[str, str],
        timeout_seconds: float,
        max_memory_mb: int,
    ) -> ProcessResult:
        del argv, env, timeout_seconds, max_memory_mb
        return ProcessResult(
            returncode=0,
            stdout=b'{"proposals":[]}',
            stderr=b"",
            elapsed_seconds=0.1,
        )

    result = run_llama_component_benchmark(
        request(),
        prepared,
        invoker=fake_invoker,
    )

    assert result.batch.proposals == ()


def test_cache_is_bound_to_exact_request_model_runtime_and_settings(
    tmp_path: Path,
) -> None:
    prepared = runtime(tmp_path)
    first_key = benchmark_cache_key(request(), prepared)
    changed_config = LlamaBenchmarkConfig(
        threads=2,
        context_size=4096,
        max_output_tokens=256,
        timeout_seconds=30,
        max_memory_mb=6144,
    )
    changed_runtime = prepare_llama_benchmark_runtime(
        llama_cli_path=prepared.llama_cli_path,
        model_path=prepared.model_path,
        model_spec=prepared.model_spec,
        config=changed_config,
    )

    assert benchmark_cache_key(request(), changed_runtime) != first_key


def test_valid_cache_hit_bypasses_second_inference(tmp_path: Path) -> None:
    prepared = runtime(tmp_path)
    cache_dir = tmp_path / "cache"
    calls = 0

    def first_invoker(
        argv: tuple[str, ...],
        env: dict[str, str],
        timeout_seconds: float,
        max_memory_mb: int,
    ) -> ProcessResult:
        nonlocal calls
        del argv, env, timeout_seconds, max_memory_mb
        calls += 1
        return ProcessResult(
            returncode=0,
            stdout=valid_output(),
            stderr=b"",
            elapsed_seconds=0.2,
        )

    first = run_llama_component_benchmark(
        request(),
        prepared,
        cache_dir=cache_dir,
        invoker=first_invoker,
    )

    def must_not_run(
        argv: tuple[str, ...],
        env: dict[str, str],
        timeout_seconds: float,
        max_memory_mb: int,
    ) -> ProcessResult:
        del argv, env, timeout_seconds, max_memory_mb
        raise AssertionError("cache hit must not launch llama-cli")

    second = run_llama_component_benchmark(
        request(),
        prepared,
        cache_dir=cache_dir,
        invoker=must_not_run,
    )

    assert calls == 1
    assert first.cache_hit is False
    assert second.cache_hit is True
    assert second.elapsed_seconds is None
    assert second.batch == first.batch


def test_tampered_cache_proposal_is_revalidated_and_rejected(tmp_path: Path) -> None:
    prepared = runtime(tmp_path)
    cache_dir = tmp_path / "cache"

    def first_invoker(
        argv: tuple[str, ...],
        env: dict[str, str],
        timeout_seconds: float,
        max_memory_mb: int,
    ) -> ProcessResult:
        del argv, env, timeout_seconds, max_memory_mb
        return ProcessResult(
            returncode=0,
            stdout=valid_output(),
            stderr=b"",
            elapsed_seconds=0.2,
        )

    first = run_llama_component_benchmark(
        request(),
        prepared,
        cache_dir=cache_dir,
        invoker=first_invoker,
    )
    cache_path = cache_dir / f"{first.cache_key}.json"
    record = json.loads(cache_path.read_text(encoding="utf-8"))
    record["batch"]["proposals"][0]["source_text"] = "tampered"
    cache_path.write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(LlamaAdapterError, match="does not match"):
        run_llama_component_benchmark(
            request(),
            prepared,
            cache_dir=cache_dir,
        )


def test_cache_entry_count_is_bounded(tmp_path: Path) -> None:
    prepared = runtime(tmp_path, max_cache_entries=1)
    cache_dir = tmp_path / "cache"

    def invoker(
        argv: tuple[str, ...],
        env: dict[str, str],
        timeout_seconds: float,
        max_memory_mb: int,
    ) -> ProcessResult:
        del argv, env, timeout_seconds, max_memory_mb
        return ProcessResult(
            returncode=0,
            stdout=valid_output(),
            stderr=b"",
            elapsed_seconds=0.1,
        )

    first_request = request()
    run_llama_component_benchmark(
        first_request,
        prepared,
        cache_dir=cache_dir,
        invoker=invoker,
    )
    second_request = first_request.model_copy(update={"source_sha256": "b" * 64})
    run_llama_component_benchmark(
        second_request,
        prepared,
        cache_dir=cache_dir,
        invoker=invoker,
    )

    assert len(list(cache_dir.glob("*.json"))) == 1


def test_nonzero_llama_exit_is_fail_closed(tmp_path: Path) -> None:
    prepared = runtime(tmp_path)

    def fake_invoker(
        argv: tuple[str, ...],
        env: dict[str, str],
        timeout_seconds: float,
        max_memory_mb: int,
    ) -> ProcessResult:
        del argv, env, timeout_seconds, max_memory_mb
        return ProcessResult(
            returncode=7,
            stdout=b"",
            stderr=b"runtime failed",
            elapsed_seconds=0.1,
        )

    with pytest.raises(LlamaAdapterError, match="exited with code 7"):
        run_llama_component_benchmark(
            request(),
            prepared,
            invoker=fake_invoker,
        )
