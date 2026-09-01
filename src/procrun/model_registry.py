"""Pinned local-model artifacts and offline integrity verification."""

from __future__ import annotations

import hashlib
from enum import StrEnum
from pathlib import Path

from pydantic import Field

from procrun.domain import StrictModel
from procrun.model_fallback import LocalModelIdentity


class ModelApprovalStatus(StrEnum):
    BENCHMARK_CANDIDATE = "BENCHMARK_CANDIDATE"
    APPROVED = "APPROVED"


class ModelArtifactError(RuntimeError):
    """Raised when a local model artifact does not match its pinned registry entry."""


class ModelArtifactSpec(StrictModel):
    repository: str = Field(min_length=1)
    revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    filename: str = Field(min_length=1)
    identity: LocalModelIdentity
    size_bytes: int = Field(gt=0)
    license_id: str = Field(min_length=1)
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
    status=ModelApprovalStatus.BENCHMARK_CANDIDATE,
)

SELECTED_COMPONENT_MODEL = QWEN3_4B_Q4_K_M


def verify_local_model_artifact(
    path: Path,
    spec: ModelArtifactSpec = SELECTED_COMPONENT_MODEL,
) -> LocalModelIdentity:
    """Verify exact local bytes before an inference adapter may load them."""

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
