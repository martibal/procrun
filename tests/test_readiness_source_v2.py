from datetime import UTC, datetime, timedelta

from procrun.readiness_source import (
    PublishedRequirement,
    RequirementKind,
    SourceDocument,
    SourcePackage,
    SourcePackageState,
    package_sha256,
)


def _package(*, complete: bool = True) -> SourcePackage:
    observed = datetime(2026, 9, 1, 8, tzinfo=UTC)
    document = SourceDocument(
        document_id="bando",
        document_type="BANDO",
        title="Official bando",
        public_url="https://example.invalid/bando",
        sha256="a" * 64,
        observed_at=observed,
    )
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


def test_package_hash_is_deterministic() -> None:
    assert package_sha256(_package()) == package_sha256(_package())
