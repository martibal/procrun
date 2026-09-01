import hashlib
import json
from pathlib import Path

import pytest

from procrun.component_engine import ComponentDomain
from procrun.llama_adapter import (
    LlamaAdapterError,
    LlamaBenchmarkConfig,
    ProcessResult,
    benchmark_cache_key,
    prepare_llama_benchmark_runtime,
    run_llama_component_benchmark,
)
from procrun.model_fallback import (
    AllowedComponentCategory,
    LocalModelIdentity,
    LocalModelRequest,
    ModelPromptSpan,
)
from procrun.model_registry import ModelApprovalStatus, ModelArtifactSpec


SPAN_TEXT = "nova subestação"
SPAN_START = 100
SPAN_END = SPAN_START + len(SPAN_TEXT)


def fixture_spec(content: bytes) -> ModelArtifactSpec:
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
        status=ModelApprovalStatus.BENCHMARK_CANDIDATE,
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


def runtime(tmp_path: Path):
    model_bytes = b"fixture-model"
    binary_bytes = b"fixture-llama-cli"
    model_path = tmp_path / "fixture.gguf"
    binary_path = tmp_path / "llama-cli"
    model_path.write_bytes(model_bytes)
    binary_path.write_bytes(binary_bytes)
    spec = fixture_spec(model_bytes)
    prepared = prepare_llama_benchmark_runtime(
        llama_cli_path=binary_path,
        model_path=model_path,
        model_spec=spec,
        config=LlamaBenchmarkConfig(
            threads=4,
            context_size=4096,
            max_output_tokens=256,
            timeout_seconds=30,
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
                    "start": SPAN_START,
                    "end": SPAN_END,
                    "source_text": SPAN_TEXT,
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


def test_adapter_uses_only_local_files_and_deterministic_cli_bounds(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepared = runtime(tmp_path)
    monkeypatch.setenv("LLAMA_ARG_N_PREDICT", "999999")
    captured: dict[str, object] = {}

    def fake_invoker(
        argv: tuple[str, ...],
        env: dict[str, str],
        timeout_seconds: float,
    ) -> ProcessResult:
        captured["argv"] = argv
        captured["env"] = env
        captured["timeout"] = timeout_seconds

        prompt_path = Path(argv[argv.index("--file") + 1])
        schema_path = Path(argv[argv.index("--json-schema-file") + 1])
        assert SPAN_TEXT in prompt_path.read_text(encoding="utf-8")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        assert schema["additionalProperties"] is False

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
    assert "--json-schema-file" in argv
    assert "--single-turn" in argv
    assert argv[argv.index("--temp") + 1] == "0"
    assert argv[argv.index("--seed") + 1] == "0"
    assert argv[argv.index("--ctx-size") + 1] == "4096"
    assert argv[argv.index("--n-predict") + 1] == "256"
    assert "-hf" not in argv
    assert "--hf-repo" not in argv

    env = captured["env"]
    assert isinstance(env, dict)
    assert "LLAMA_ARG_N_PREDICT" not in env
    assert captured["timeout"] == 30
    assert result.cache_hit is False
    assert result.elapsed_seconds == 1.25
    assert result.batch.proposals[0].source_text == SPAN_TEXT


def test_extra_or_non_json_model_output_is_rejected(tmp_path: Path) -> None:
    prepared = runtime(tmp_path)

    def fake_invoker(
        argv: tuple[str, ...],
        env: dict[str, str],
        timeout_seconds: float,
    ) -> ProcessResult:
        del argv, env, timeout_seconds
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


def test_proposal_outside_unmatched_scope_is_rejected(tmp_path: Path) -> None:
    prepared = runtime(tmp_path)
    bad = json.dumps(
        {
            "proposals": [
                {
                    "domain": "rail_transport",
                    "category": "electrification_catenary",
                    "start": 0,
                    "end": 4,
                    "source_text": "fake",
                }
            ]
        }
    ).encode()

    def fake_invoker(
        argv: tuple[str, ...],
        env: dict[str, str],
        timeout_seconds: float,
    ) -> ProcessResult:
        del argv, env, timeout_seconds
        return ProcessResult(
            returncode=0,
            stdout=bad,
            stderr=b"",
            elapsed_seconds=0.1,
        )

    with pytest.raises(LlamaAdapterError, match="outside the supplied unmatched"):
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
                    "start": SPAN_START,
                    "end": SPAN_END,
                    "source_text": SPAN_TEXT,
                }
            ]
        },
        ensure_ascii=False,
    ).encode()

    def fake_invoker(
        argv: tuple[str, ...],
        env: dict[str, str],
        timeout_seconds: float,
    ) -> ProcessResult:
        del argv, env, timeout_seconds
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
    ) -> ProcessResult:
        del argv, env, timeout_seconds
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
    ) -> ProcessResult:
        nonlocal calls
        del argv, env, timeout_seconds
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
    ) -> ProcessResult:
        del argv, env, timeout_seconds
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


def test_nonzero_llama_exit_is_fail_closed(tmp_path: Path) -> None:
    prepared = runtime(tmp_path)

    def fake_invoker(
        argv: tuple[str, ...],
        env: dict[str, str],
        timeout_seconds: float,
    ) -> ProcessResult:
        del argv, env, timeout_seconds
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
