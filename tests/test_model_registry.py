import hashlib
from datetime import date
from pathlib import Path

import pytest

from procrun.model_fallback import LocalModelIdentity
from procrun.model_registry import (
    MINISTRAL3_3B_Q4_K_M,
    QWEN3_4B_Q4_K_M,
    SELECTED_COMPONENT_MODEL,
    ModelApprovalStatus,
    ModelArtifactError,
    ModelArtifactSpec,
    verify_local_model_artifact,
    verify_model_compliance,
)


def fixture_spec(
    content: bytes,
    *,
    sha256: str | None = None,
    commercial_use_allowed: bool = True,
) -> ModelArtifactSpec:
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
        license_url="https://example.invalid/model-license",
        commercial_use_allowed=commercial_use_allowed,
        license_reviewed_on=date(2026, 9, 1),
        license_review_due_on=date(2026, 11, 30),
        status=ModelApprovalStatus.BENCHMARK_CANDIDATE,
    )


def test_qwen_candidate_is_pinned_but_exact_span_verdict_is_inconclusive() -> None:
    assert QWEN3_4B_Q4_K_M.repository == "Qwen/Qwen3-4B-GGUF"
    assert QWEN3_4B_Q4_K_M.filename == "Qwen3-4B-Q4_K_M.gguf"
    assert QWEN3_4B_Q4_K_M.size_bytes == 2_497_280_256
    assert QWEN3_4B_Q4_K_M.license_id == "Apache-2.0"
    assert QWEN3_4B_Q4_K_M.commercial_use_allowed is True
    assert QWEN3_4B_Q4_K_M.identity.artifact_sha256 == (
        "7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5"
    )
    assert QWEN3_4B_Q4_K_M.status is ModelApprovalStatus.INCONCLUSIVE


def test_ministral_candidate_is_exactly_pinned_and_selected() -> None:
    assert MINISTRAL3_3B_Q4_K_M.repository == (
        "mistralai/Ministral-3-3B-Instruct-2512-GGUF"
    )
    assert MINISTRAL3_3B_Q4_K_M.revision == (
        "eb599d408350ea2bb60452cb86be7c7b2fc28227"
    )
    assert MINISTRAL3_3B_Q4_K_M.filename == (
        "Ministral-3-3B-Instruct-2512-Q4_K_M.gguf"
    )
    assert MINISTRAL3_3B_Q4_K_M.size_bytes == 2_147_023_008
    assert MINISTRAL3_3B_Q4_K_M.license_id == "Apache-2.0"
    assert MINISTRAL3_3B_Q4_K_M.commercial_use_allowed is True
    assert MINISTRAL3_3B_Q4_K_M.identity.artifact_sha256 == (
        "9ed150d4367e68df0ac8e1540f6ddc65b42d0ee26378329d1ecbca60f93fc5f8"
    )
    assert MINISTRAL3_3B_Q4_K_M.status is ModelApprovalStatus.BENCHMARK_CANDIDATE
    assert SELECTED_COMPONENT_MODEL is MINISTRAL3_3B_Q4_K_M


def test_model_compliance_review_expires_fail_closed() -> None:
    with pytest.raises(ModelArtifactError, match="review expired"):
        verify_model_compliance(
            fixture_spec(b"fixture-model-bytes"),
            as_of=date(2026, 12, 1),
        )


def test_noncommercial_model_is_rejected() -> None:
    with pytest.raises(ModelArtifactError, match="not approved for commercial use"):
        verify_model_compliance(
            fixture_spec(b"fixture-model-bytes", commercial_use_allowed=False),
            as_of=date(2026, 9, 1),
        )


def test_exact_local_artifact_passes_offline_verification(tmp_path: Path) -> None:
    content = b"fixture-model-bytes"
    path = tmp_path / "fixture.gguf"
    path.write_bytes(content)

    identity = verify_local_model_artifact(
        path,
        fixture_spec(content),
        as_of=date(2026, 9, 1),
    )

    assert identity.artifact_sha256 == hashlib.sha256(content).hexdigest()


def test_wrong_file_size_is_rejected_before_hashing(tmp_path: Path) -> None:
    content = b"fixture-model-bytes"
    path = tmp_path / "fixture.gguf"
    path.write_bytes(content + b"x")

    with pytest.raises(ModelArtifactError, match="size mismatch"):
        verify_local_model_artifact(
            path,
            fixture_spec(content),
            as_of=date(2026, 9, 1),
        )


def test_wrong_sha256_is_rejected(tmp_path: Path) -> None:
    content = b"fixture-model-bytes"
    path = tmp_path / "fixture.gguf"
    path.write_bytes(content)
    spec = fixture_spec(content, sha256="b" * 64)

    with pytest.raises(ModelArtifactError, match="SHA-256 mismatch"):
        verify_local_model_artifact(path, spec, as_of=date(2026, 9, 1))


def test_missing_model_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ModelArtifactError, match="does not exist"):
        verify_local_model_artifact(
            tmp_path / "missing.gguf",
            fixture_spec(b"fixture-model-bytes"),
            as_of=date(2026, 9, 1),
        )
