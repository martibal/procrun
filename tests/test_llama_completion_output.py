import hashlib
import json
from datetime import date
from pathlib import Path

import pytest

from procrun.component_engine import ComponentDomain
from procrun.llama_adapter import (
    LlamaAdapterError,
    LlamaBenchmarkConfig,
    ProcessResult,
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


def _runtime(tmp_path: Path):
    model_bytes = b"fixture-model"
    binary_bytes = b"fixture-llama-completion"
    model_path = tmp_path / "fixture.gguf"
    binary_path = tmp_path / "llama-completion"
    model_path.write_bytes(model_bytes)
    binary_path.write_bytes(binary_bytes)
    binary_path.chmod(0o755)
    spec = ModelArtifactSpec(
        repository="fixture/local-model",
        revision="a" * 40,
        filename="fixture.gguf",
        identity=LocalModelIdentity(
            model_id="fixture/local-model:Q4_K_M",
            artifact_sha256=hashlib.sha256(model_bytes).hexdigest(),
        ),
        size_bytes=len(model_bytes),
        license_id="Apache-2.0",
        license_url="https://example.invalid/model-license",
        commercial_use_allowed=True,
        license_reviewed_on=date(2026, 9, 1),
        license_review_due_on=date(2026, 11, 30),
        status=ModelApprovalStatus.BENCHMARK_CANDIDATE,
    )
    return prepare_llama_benchmark_runtime(
        llama_cli_path=binary_path,
        model_path=model_path,
        model_spec=spec,
        config=LlamaBenchmarkConfig(max_memory_mb=6144),
    )


def _request() -> LocalModelRequest:
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


def _valid_output() -> bytes:
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


def test_llama_completion_eog_marker_is_accepted(tmp_path: Path) -> None:
    prepared = _runtime(tmp_path)

    def fake_invoker(
        argv: tuple[str, ...],
        env: dict[str, str],
        timeout_seconds: float,
        max_memory_mb: int,
    ) -> ProcessResult:
        del argv, env, timeout_seconds, max_memory_mb
        return ProcessResult(
            returncode=0,
            stdout=_valid_output() + b" [end of text]\n",
            stderr=b"",
            elapsed_seconds=0.1,
        )

    result = run_llama_component_benchmark(
        _request(),
        prepared,
        invoker=fake_invoker,
    )

    assert result.batch.proposals[0].start == SPAN_START
    assert result.batch.proposals[0].end == SPAN_END
    assert result.batch.proposals[0].source_text == SPAN_TEXT


def test_unknown_trailing_runtime_output_is_rejected(tmp_path: Path) -> None:
    prepared = _runtime(tmp_path)

    def fake_invoker(
        argv: tuple[str, ...],
        env: dict[str, str],
        timeout_seconds: float,
        max_memory_mb: int,
    ) -> ProcessResult:
        del argv, env, timeout_seconds, max_memory_mb
        return ProcessResult(
            returncode=0,
            stdout=_valid_output() + b" unexpected trailer",
            stderr=b"",
            elapsed_seconds=0.1,
        )

    with pytest.raises(LlamaAdapterError, match="strict proposal JSON"):
        run_llama_component_benchmark(
            _request(),
            prepared,
            invoker=fake_invoker,
        )
