from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from procrun.readiness_source import (
    PublishedRequirement,
    RequirementKind,
    SourceDocument,
    SourcePackage,
    SourcePackageState,
    SourceReuseMode,
    package_manifest,
    package_sha256,
)


def _document(
    *,
    reuse_mode: SourceReuseMode = SourceReuseMode.COMMERCIAL_REUSE_CONFIRMED,
) -> SourceDocument:
    observed = datetime(2026, 9, 1, 8, tzinfo=UTC)
    return SourceDocument(
        document_id="bando",
        document_type="BANDO",
        title="Official bando",
        public_url="https://example.invalid/bando",
        sha256="a" * 64,
        observed_at=observed,
        reuse_mode=reuse_mode,
        reuse_basis_url="https://example.invalid/public-reuse-policy",
        reuse_basis_note="Public test fixture basis for the declared reuse mode.",
    )


def _package(*, complete: bool = True) -> SourcePackage:
    observed = datetime(2026, 9, 1, 8, tzinfo=UTC)
    document = _document()
    requirement = PublishedRequirement(
        requirement_id="min-funding",
        kind=RequirementKind.MINIMUM_EUR,
        label="Published minimum investment",
        source_document_id="bando",
        source_citation="Art. 4",
        source_text="Minimum investment EUR 100,000",
        scope_note="Applies to the selected project class.",
        boundary_value=100_000,
    )
    return SourcePackage(
        source_package_id="pkg-1",
        bando_code="BANDO-X",
        benchmark_cohort_id="SAME_BANDO:BANDO-X",
        version=1,
        verified_at=observed,
        documents=(document,),
        requirements=(requirement,),
        completeness_attested=complete,
    )


def test_source_package_is_fresh_for_at_most_seven_days() -> None:
    package = _package()
    assert package.state_at(package.verified_at + timedelta(days=7)) is SourcePackageState.FRESH
    assert (
        package.state_at(package.verified_at + timedelta(days=7, seconds=1))
        is SourcePackageState.SOURCE_REFRESH_REQUIRED
    )


def test_invalidation_overrides_ttl_and_incomplete_fails_closed() -> None:
    package = _package()
    invalidated = package.verified_at + timedelta(hours=3)
    assert (
        package.state_at(invalidated + timedelta(seconds=1), invalidated_at=invalidated)
        is SourcePackageState.INVALIDATED
    )
    assert _package(complete=False).state_at(package.verified_at) is SourcePackageState.INCOMPLETE


def test_package_hash_is_deterministic_and_binds_cohort_and_reuse_basis() -> None:
    package = _package()
    assert package_sha256(package) == package_sha256(_package())
    assert package.benchmark_cohort_id == "SAME_BANDO:BANDO-X"
    document = package_manifest(package)["documents"][0]
    assert document["reuse_mode"] == "COMMERCIAL_REUSE_CONFIRMED"
    assert document["reuse_basis_url"] == "https://example.invalid/public-reuse-policy"


def test_source_document_requires_public_reuse_basis() -> None:
    with pytest.raises(ValueError, match="public basis URL and note"):
        replace(_document(), reuse_basis_url="")
    with pytest.raises(ValueError, match="public basis URL and note"):
        replace(_document(), reuse_basis_note="")


def test_blocked_document_cannot_enter_source_package() -> None:
    package = _package()
    blocked = replace(_document(), reuse_mode=SourceReuseMode.BLOCKED)
    with pytest.raises(ValueError, match="blocked source documents"):
        replace(package, documents=(blocked,))


def test_fact_extraction_only_cannot_republish_source_wording() -> None:
    package = _package()
    fact_only = replace(_document(), reuse_mode=SourceReuseMode.FACT_EXTRACTION_ONLY)
    with pytest.raises(ValueError, match="cannot carry source_text"):
        replace(package, documents=(fact_only,))

    fact_requirement = replace(package.requirements[0], source_text="")
    allowed = replace(package, documents=(fact_only,), requirements=(fact_requirement,))
    manifest = package_manifest(allowed)
    assert manifest["documents"][0]["reuse_mode"] == "FACT_EXTRACTION_ONLY"
    assert manifest["requirements"][0]["source_text"] == ""
