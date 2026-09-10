import pytest

import procrun.a21a_release_freeze as release_freeze
from procrun.a21a_release_freeze import (
    CURRENT_FINAL_POPULATION,
    EVIDENCE_RETRIEVAL_BLOB_SHA,
    EXPECTED_EXTRACTOR_VERSION,
    EXPECTED_THRESHOLD_VERSION,
    RELEASE_CANDIDATE_BASELINE_COMMIT,
    RELEASE_CANDIDATE_ID,
    FinalPopulationFreeze,
    release_candidate_is_frozen,
    require_final_holdout_ready,
)


def test_release_candidate_identity_is_fail_closed_after_lineage_invalidation() -> None:
    assert RELEASE_CANDIDATE_ID == "a21a-evidence-rc1"
    assert RELEASE_CANDIDATE_BASELINE_COMMIT == "49e6345e514f85fe2e5b5f58076efe3f7dba85dc"
    assert EVIDENCE_RETRIEVAL_BLOB_SHA == "d077a919d91f2049ced6546e585ff0e651c81dd7"
    assert EXPECTED_EXTRACTOR_VERSION == "evidence-retrieval-v1"
    assert EXPECTED_THRESHOLD_VERSION == "a21a-thresholds-v1"
    assert release_candidate_is_frozen() is False


def test_final_holdout_is_blocked_by_invalidated_release_candidate() -> None:
    assert CURRENT_FINAL_POPULATION.frozen is False
    with pytest.raises(RuntimeError, match="release-candidate identity no longer matches"):
        require_final_holdout_ready()


def test_population_guards_remain_enforced_once_clean_threshold_version_is_restored(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(release_freeze, "PREREGISTRATION_VERSION", EXPECTED_THRESHOLD_VERSION)
    assert release_candidate_is_frozen() is True

    with pytest.raises(RuntimeError, match="final population is not frozen"):
        require_final_holdout_ready()

    valid = FinalPopulationFreeze(
        source_pool_sha256="a" * 64,
        population_sha256="b" * 64,
        case_ids_sha256="c" * 64,
        case_count=200,
        development_overlap_count=0,
        frozen=True,
    )
    require_final_holdout_ready(valid)

    overlapping = FinalPopulationFreeze(
        source_pool_sha256="a" * 64,
        population_sha256="b" * 64,
        case_ids_sha256="c" * 64,
        case_count=200,
        development_overlap_count=1,
        frozen=True,
    )
    with pytest.raises(RuntimeError, match="not disjoint"):
        require_final_holdout_ready(overlapping)
