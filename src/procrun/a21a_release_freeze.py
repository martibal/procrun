"""Frozen A21a release-candidate identity and final-holdout readiness guard."""

from __future__ import annotations

from dataclasses import dataclass

from procrun.a21a_thresholds import PREREGISTRATION_VERSION
from procrun.evidence_retrieval import EVIDENCE_RETRIEVAL_VERSION

RELEASE_CANDIDATE_ID = "a21a-evidence-rc1"
RELEASE_CANDIDATE_BASELINE_COMMIT = "49e6345e514f85fe2e5b5f58076efe3f7dba85dc"
EVIDENCE_RETRIEVAL_BLOB_SHA = "d077a919d91f2049ced6546e585ff0e651c81dd7"
EXPECTED_EXTRACTOR_VERSION = "evidence-retrieval-v1"
EXPECTED_THRESHOLD_VERSION = "a21a-thresholds-v1"


@dataclass(frozen=True)
class FinalPopulationFreeze:
    source_pool_sha256: str | None = None
    population_sha256: str | None = None
    case_ids_sha256: str | None = None
    case_count: int | None = None
    development_overlap_count: int | None = None
    frozen: bool = False


CURRENT_FINAL_POPULATION = FinalPopulationFreeze()


def release_candidate_is_frozen() -> bool:
    return (
        EVIDENCE_RETRIEVAL_VERSION == EXPECTED_EXTRACTOR_VERSION
        and PREREGISTRATION_VERSION == EXPECTED_THRESHOLD_VERSION
    )


def require_final_holdout_ready(
    population: FinalPopulationFreeze = CURRENT_FINAL_POPULATION,
) -> None:
    """Fail closed until RC identity and an exact disjoint final population are frozen."""

    if not release_candidate_is_frozen():
        raise RuntimeError("A21a release-candidate identity no longer matches the frozen contract")
    if not population.frozen:
        raise RuntimeError("A21a final population is not frozen")
    if not population.source_pool_sha256 or not population.population_sha256 or not population.case_ids_sha256:
        raise RuntimeError("A21a final population freeze lacks required hash anchors")
    if population.case_count is None or population.case_count < 1:
        raise RuntimeError("A21a final population freeze lacks a positive case count")
    if population.development_overlap_count != 0:
        raise RuntimeError("A21a final population is not disjoint from development material")
