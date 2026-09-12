from dataclasses import replace
from datetime import UTC, date, datetime, timedelta

import pytest

from procrun.readiness_benchmark import BenchmarkObservation
from procrun.readiness_dossier import (
    DossierBlockedError,
    DossierBuildInput,
    build_dossier,
    verify_dossier,
)
from procrun.readiness_matrix import AdvisorConfirmation, AdvisorState
from procrun.readiness_source import (
    PublishedRequirement,
    RequirementKind,
    SourceDocument,
    SourcePackage,
    SourceReuseMode,
)


def _package() -> SourcePackage:
    verified = datetime(2026, 9, 10, 8, tzinfo=UTC)
    document = SourceDocument(
        document_id="bando",
        document_type="BANDO",
        title="Official bando",
        public_url="https://example.invalid/bando",
        sha256="c" * 64,
        observed_at=verified,
        reuse_mode=SourceReuseMode.COMMERCIAL_REUSE_CONFIRMED,
        reuse_basis_url="https://example.invalid/public-reuse-policy",
        reuse_basis_note="Public test fixture licence permits commercial reuse.",
    )
    return SourcePackage(
        source_package_id="pkg-1",
        bando_code="BANDO-X",
        benchmark_cohort_id="SAME_BANDO:BANDO-X",
        version=1,
        verified_at=verified,
        documents=(document,),
        requirements=(
            PublishedRequirement(
                requirement_id="review-dnsh",
                kind=RequirementKind.PROFESSIONAL_VERIFICATION,
                label="DNSH professional verification",
                source_document_id="bando",
                source_citation="Art. 8",
                source_text="DNSH requirements must be documented.",
                scope_note="ProcRun records the advisor status only.",
            ),
        ),
        completeness_attested=True,
    )


def _input(created_at: datetime) -> DossierBuildInput:
    observations = tuple(
        BenchmarkObservation(
            operation_code=f"OP-{i:03d}",
            approved_funding_eur=100_000 + i * 10_000,
            project_start=date(2025, 1, 1),
            project_end=date(2026, 1, 1),
        )
        for i in range(30)
    )
    return DossierBuildInput(
        dossier_id="11111111-1111-1111-1111-111111111111",
        tenant_key="org_0123456789abcdef0123456789abcdef",
        purchase_reference="purchase-1",
        source_package=_package(),
        invalidated_at=None,
        benchmark_snapshot_id="snapshot-1",
        benchmark_data_through="2026-09-10",
        benchmark_snapshot_sha256="d" * 64,
        benchmark_source_binding={
            "funding_source_id": "opencoesione-2021-2027",
            "funding_source_sha256": "a" * 64,
            "cohort_source_id": "lombardia-structured",
            "cohort_source_sha256": "b" * 64,
            "cohort_membership_semantics": "Exact structured membership only.",
        },
        observations=observations,
        proposed_funding_eur=250_000,
        proposed_duration_months=12,
        confirmations=(
            AdvisorConfirmation(
                requirement_id="review-dnsh",
                state=AdvisorState.PROFESSIONAL_REVIEW_REQUIRED,
            ),
        ),
        created_at=created_at,
    )


def test_dossier_binds_source_snapshot_and_is_byte_verifiable() -> None:
    created = _package().verified_at + timedelta(days=1)
    payload, canonical, digest = build_dossier(_input(created))
    assert payload["source_package"]["source_package_id"] == "pkg-1"
    assert (
        payload["source_package"]["manifest"]["benchmark_cohort_id"]
        == "SAME_BANDO:BANDO-X"
    )
    source_document = payload["source_package"]["manifest"]["documents"][0]
    assert source_document["reuse_mode"] == "COMMERCIAL_REUSE_CONFIRMED"
    historical = payload["historical_dimensioning"]
    assert historical["snapshot_id"] == "snapshot-1"
    assert historical["source_binding"]["cohort_source_id"] == "lombardia-structured"
    assert len(digest) == 64
    verify_dossier(payload, canonical, digest)


def test_stale_or_invalidated_source_package_blocks_paid_dossier() -> None:
    stale = _package().verified_at + timedelta(days=7, seconds=1)
    with pytest.raises(DossierBlockedError, match="SOURCE_REFRESH_REQUIRED"):
        build_dossier(_input(stale))

    current = _package().verified_at + timedelta(days=1)
    invalidated = replace(
        _input(current),
        invalidated_at=current - timedelta(minutes=1),
    )
    with pytest.raises(DossierBlockedError, match="INVALIDATED"):
        build_dossier(invalidated)


def test_paid_dossier_requires_trusted_purchase_reference() -> None:
    current = _package().verified_at + timedelta(days=1)
    unpaid = replace(_input(current), purchase_reference="")
    with pytest.raises(DossierBlockedError, match="purchase reference"):
        build_dossier(unpaid)


def test_missing_benchmark_source_binding_blocks_dossier() -> None:
    current = _package().verified_at + timedelta(days=1)
    missing = replace(_input(current), benchmark_source_binding={})
    with pytest.raises(DossierBlockedError, match="source binding is incomplete"):
        build_dossier(missing)
