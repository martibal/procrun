"""A21a final-population manifest validation without opening holdout content."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable

FINAL_POPULATION_MANIFEST_VERSION = "a21a-final-population-v1"


def _sha256_lines(values: Iterable[str]) -> str:
    normalized = "\n".join(sorted(set(values))) + "\n"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class FinalPopulationManifest:
    source_pool_sha256: str
    population_sha256: str
    case_ids_sha256: str
    case_count: int
    development_overlap_count: int
    manifest_version: str = FINAL_POPULATION_MANIFEST_VERSION
    sealed: bool = True


def build_manifest_from_case_ids(
    *,
    source_pool_sha256: str,
    population_sha256: str,
    final_case_ids: Iterable[str],
    development_case_ids: Iterable[str],
) -> FinalPopulationManifest:
    """Build a content-blind manifest from stable identifiers only."""

    final_ids = frozenset(final_case_ids)
    development_ids = frozenset(development_case_ids)
    if not final_ids:
        raise ValueError("A21a final population must contain at least one case")

    return FinalPopulationManifest(
        source_pool_sha256=source_pool_sha256,
        population_sha256=population_sha256,
        case_ids_sha256=_sha256_lines(final_ids),
        case_count=len(final_ids),
        development_overlap_count=len(final_ids & development_ids),
    )


def validate_manifest(manifest: FinalPopulationManifest) -> None:
    """Fail closed unless the manifest is sealed, hash-anchored and disjoint."""

    if manifest.manifest_version != FINAL_POPULATION_MANIFEST_VERSION:
        raise RuntimeError("A21a final population manifest version mismatch")
    if not manifest.sealed:
        raise RuntimeError("A21a final population manifest is not sealed")
    for value in (
        manifest.source_pool_sha256,
        manifest.population_sha256,
        manifest.case_ids_sha256,
    ):
        if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
            raise RuntimeError("A21a final population manifest contains an invalid SHA-256 anchor")
    if manifest.case_count < 1:
        raise RuntimeError("A21a final population manifest has no cases")
    if manifest.development_overlap_count != 0:
        raise RuntimeError("A21a final population overlaps development material")
