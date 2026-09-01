import hashlib
from pathlib import Path

import pytest

from procrun.model_fallback import LocalModelIdentity
from procrun.model_registry import (
    QWEN3_4B_Q4_K_M,
    ModelApprovalStatus,
    ModelArtifactError,
    ModelArtifactSpec,
    verify_local_model_artifact,
)


def fixture_spec(content: bytes, *, sha256: str | None = None) -> ModelArtifactSpec:
    digest = sha256 or hashlib.sha256(content).hexdigest()
    return ModelArtifactSpec(
        repository="fixture/local-model",
        revision="a" * 40,
        filename="fixture.gguf",
        identity=LocalModelIdentity(
            model_id="fixture/local-model:Q4_K_M",
            artifact_sha256=digest,
        ),
        size_bytes=len(content),
        license_id="Apache-2.0",
        status=ModelApprovalStatus.BENCHMARK_CANDIDATE,
    )


def test_qwen_candidate_is_exactly_pinned_but_not_production_approved() -> None:
    assert QWEN3_4B_Q4_K_M.repository == "Qwen/Qwen3-4B-GGUF"
    assert QWEN3_4B_Q4_K_M.filename == "Qwen3-4B-Q4_K_M.gguf"
    assert QWEN3_4B_Q4_K_M.size_bytes == 2_497_280_256
    assert QWEN3_4B_Q4_K_M.license_id == "Apache-2.0"
    assert QWEN3_4B_Q4_K_M.identity.artifact_sha256 == (
        "7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5"
    )
    assert QWEN3_4B_Q4_K_M.status is ModelApprovalStatus.BENCHMARK_CANDIDATE


def test_exact_local_artifact_passes_offline_verification(tmp_path: Path) -> None:
    content = b"fixture-model-bytes"
    path = tmp_path / "fixture.gguf"
    path.write_bytes(content)

    identity = verify_local_model_artifact(path, fixture_spec(content))

    assert identity.artifact_sha256 == hashlib.sha256(content).hexdigest()


def test_wrong_file_size_is_rejected_before_hashing(tmp_path: Path) -> None:
    content = b"fixture-model-bytes"
    path = tmp_path / "fixture.gguf"
    path.write_bytes(content + b"x")

    with pytest.raises(ModelArtifactError, match="size mismatch"):
        verify_local_model_artifact(path, fixture_spec(content))


def test_wrong_sha256_is_rejected(tmp_path: Path) -> None:
    content = b"fixture-model-bytes"
    path = tmp_path / "fixture.gguf"
    path.write_bytes(content)
    spec = fixture_spec(content, sha256="b" * 64)

    with pytest.raises(ModelArtifactError, match="SHA-256 mismatch"):
        verify_local_model_artifact(path, spec)


def test_missing_model_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ModelArtifactError, match="does not exist"):
        verify_local_model_artifact(
            tmp_path / "missing.gguf",
            fixture_spec(b"fixture-model-bytes"),
        )
