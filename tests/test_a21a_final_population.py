import pytest

from procrun.a21a_final_population import (
    FINAL_POPULATION_MANIFEST_VERSION,
    FinalPopulationManifest,
    build_manifest_from_case_ids,
    validate_manifest,
)


def test_manifest_is_deterministic_for_case_id_order() -> None:
    first = build_manifest_from_case_ids(
        source_pool_sha256="a" * 64,
        population_sha256="b" * 64,
        final_case_ids=["case-2", "case-1", "case-2"],
        development_case_ids=["dev-1"],
    )
    second = build_manifest_from_case_ids(
        source_pool_sha256="a" * 64,
        population_sha256="b" * 64,
        final_case_ids=["case-1", "case-2"],
        development_case_ids=["dev-1"],
    )

    assert first == second
    assert first.case_count == 2
    assert first.manifest_version == FINAL_POPULATION_MANIFEST_VERSION


def test_manifest_detects_development_overlap() -> None:
    manifest = build_manifest_from_case_ids(
        source_pool_sha256="a" * 64,
        population_sha256="b" * 64,
        final_case_ids=["case-1", "case-2"],
        development_case_ids=["case-2", "dev-1"],
    )

    assert manifest.development_overlap_count == 1
    with pytest.raises(RuntimeError, match="overlaps development material"):
        validate_manifest(manifest)


def test_manifest_requires_valid_hash_anchors() -> None:
    manifest = FinalPopulationManifest(
        source_pool_sha256="not-a-hash",
        population_sha256="b" * 64,
        case_ids_sha256="c" * 64,
        case_count=1,
        development_overlap_count=0,
    )

    with pytest.raises(RuntimeError, match="invalid SHA-256 anchor"):
        validate_manifest(manifest)


def test_manifest_must_be_sealed() -> None:
    manifest = FinalPopulationManifest(
        source_pool_sha256="a" * 64,
        population_sha256="b" * 64,
        case_ids_sha256="c" * 64,
        case_count=1,
        development_overlap_count=0,
        sealed=False,
    )

    with pytest.raises(RuntimeError, match="not sealed"):
        validate_manifest(manifest)


def test_empty_final_population_fails_closed() -> None:
    with pytest.raises(ValueError, match="at least one case"):
        build_manifest_from_case_ids(
            source_pool_sha256="a" * 64,
            population_sha256="b" * 64,
            final_case_ids=[],
            development_case_ids=[],
        )
