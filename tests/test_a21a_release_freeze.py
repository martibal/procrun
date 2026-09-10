from procrun.a21a_release_freeze import (
    CURRENT_FINAL_POPULATION,
    EVIDENCE_RETRIEVAL_BLOB_SHA,
    EXPECTED_EXTRACTOR_VERSION,
    RELEASE_CANDIDATE_BASELINE_COMMIT,
    RELEASE_CANDIDATE_ID,
    FinalPopulationFreeze,
    release_candidate_is_frozen,
    require_final_holdout_ready,
)


def test_release_candidate_identity_is_frozen() -> None:
    assert RELEASE_CANDIDATE_ID == "a21a-evidence-rc1"
    assert RELEASE_CANDIDATE_BASELINE_COMMIT == "49e6345e514f85fe2e5b5f58076efe3f7dba85dc"
    assert EVIDENCE_RETRIEVAL_BLOB_SHA == "d077a919d91f2049ced6546e585ff0e651c81dd7"
    assert EXPECTED_EXTRACTOR_VERSION == "evidence-retrieval-v1"
    assert release_candidate_is_frozen() is True


def test_final_holdout_is_fail_closed_while_population_is_missing() -> None:
    assert CURRENT_FINAL_POPULATION.frozen is False
    try:
        require_final_holdout_ready()
    except RuntimeError as exc:
        assert "final population is not frozen" in str(exc)
    else:
        raise AssertionError("missing final population must block holdout access")


def test_final_holdout_requires_hash_anchored_disjoint_population() -> None:
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
    try:
        require_final_holdout_ready(overlapping)
    except RuntimeError as exc:
        assert "not disjoint" in str(exc)
    else:
        raise AssertionError("development overlap must block holdout access")
