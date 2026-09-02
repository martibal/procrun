"""Pinned local-model artifacts and offline integrity/compliance verification."""

from __future__ import annotations

import hashlib
from datetime import date
from enum import StrEnum
from pathlib import Path

from pydantic import Field

from procrun.domain import StrictModel
from procrun.model_fallback import LocalModelIdentity


class ModelApprovalStatus(StrEnum):
    BENCHMARK_CANDIDATE = "BENCHMARK_CANDIDATE"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ModelArtifactError(RuntimeError):
    """Raised when a local model artifact/compliance check fails."""


class ModelArtifactSpec(StrictModel):
    repository: str = Field(min_length=1)
    revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    filename: str = Field(min_length=1)
    identity: LocalModelIdentity
    size_bytes: int = Field(gt=0)
    license_id: str = Field(min_length=1)
    license_url: str = Field(min_length=1)
    commercial_use_allowed: bool
    license_reviewed_on: date
    license_review_due_on: date
    status: ModelApprovalStatus


QWEN3_4B_Q4_K_M = ModelArtifactSpec(
    repository="Qwen/Qwen3-4B-GGUF",
    revision="bc640142c66e1fdd12af0bd68f40445458f3869b",
    filename="Qwen3-4B-Q4_K_M.gguf",
    identity=LocalModelIdentity(
        model_id="Qwen/Qwen3-4B-GGUF:Q4_K_M",
        artifact_sha256="7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5",
    ),
    size_bytes=2_497_280_256,
    license_id="Apache-2.0",
    license_url="https://huggingface.co/Qwen/Qwen3-4B-GGUF",
    commercial_use_allowed=True,
    license_reviewed_on=date(2026, 9, 1),
    license_review_due_on=date(2026, 11, 30),
    status=ModelApprovalStatus.REJECTED,
)


MINISTRAL3_3B_Q4_K_M = ModelArtifactSpec(
    repository="mistralai/Ministral-3-3B-Instruct-2512-GGUF",
    revision="eb599d408350ea2bb60452cb86be7c7b2fc28227",
    filename="Ministral-3-3B-Instruct-2512-Q4_K_M.gguf",
    identity=LocalModelIdentity(
        model_id="mistralai/Ministral-3-3B-Instruct-2512-GGUF:Q4_K_M",
        artifact_sha256="9ed150d4367e68df0ac8e1540f6ddc65b42d0ee26378329d1ecbca60f93fc5f8",
    ),
    size_bytes=2_147_023_008,
    license_id="Apache-2.0",
    license_url="https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512-GGUF",
    commercial_use_allowed=True,
    license_reviewed_on=date(2026, 9, 2),
    license_review_due_on=date(2026, 11, 30),
    status=ModelApprovalStatus.BENCHMARK_CANDIDATE,
)


SELECTED_COMPONENT_MODEL = MINISTRAL3_3B_Q4_K_M


def verify_model_compliance(
    spec: ModelArtifactSpec,
    *,
    as_of: date | None = None,
) -> None:
    """Fail closed when model licensing/commercial-use evidence is missing or stale."""

    if not spec.commercial_use_allowed:
        raise ModelArtifactError("model is not approved for commercial use")
    if not spec.license_id.strip() or not spec.license_url.strip():
        raise ModelArtifactError("model licence metadata is incomplete")
    if spec.license_reviewed_on > spec.license_review_due_on:
        raise ModelArtifactError("model licence review dates are invalid")

    effective_date = as_of or date.today()
    if effective_date > spec.license_review_due_on:
        raise ModelArtifactError(
            "model licence review expired on "
            f"{spec.license_review_due_on.isoformat()}"
        )


def verify_local_model_artifact(
    path: Path,
    spec: ModelArtifactSpec = SELECTED_COMPONENT_MODEL,
    *,
    as_of: date | None = None,
) -> LocalModelIdentity:
    """Verify licensing and exact local bytes before an inference adapter may load them."""

    verify_model_compliance(spec, as_of=as_of)
    if not path.is_file():
        raise ModelArtifactError(f"local model artifact does not exist: {path}")
    actual_size = path.stat().st_size
    if actual_size != spec.size_bytes:
        raise ModelArtifactError(
            f"model size mismatch: expected {spec.size_bytes}, got {actual_size}"
        )

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    actual_sha256 = digest.hexdigest()
    if actual_sha256 != spec.identity.artifact_sha256:
        raise ModelArtifactError(
            "model SHA-256 mismatch: local bytes do not match the pinned registry artifact"
        )
    return spec.identity
