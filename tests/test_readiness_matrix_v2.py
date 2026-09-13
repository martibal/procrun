from datetime import UTC, datetime

from procrun.readiness_matrix import AdvisorConfirmation, AdvisorState, build_readiness_matrix
from procrun.readiness_source import (
    ProjectInputField,
    PublishedRequirement,
    RequirementKind,
    SourceDocument,
    SourcePackage,
    SourceReuseMode,
)


def _package() -> SourcePackage:
    document = SourceDocument(
        document_id="bando",
        document_type="BANDO",
        title="Bando",
        public_url="https://example.invalid/bando",
        sha256="b" * 64,
        observed_at=datetime(2026, 9, 1, tzinfo=UTC),
        reuse_mode=SourceReuseMode.COMMERCIAL_REUSE_CONFIRMED,
        reuse_basis_url="https://example.invalid/public-reuse-policy",
        reuse_basis_note="Public test fixture licence permits commercial reuse.",
    )
    return SourcePackage(
        source_package_id="pkg",
        bando_code="BANDO-X",
        benchmark_cohort_id="SAME_BANDO:BANDO-X",
        version=1,
        verified_at=datetime(2026, 9, 1, tzinfo=UTC),
        documents=(document,),
        requirements=(
            PublishedRequirement(
                requirement_id="min",
                kind=RequirementKind.MINIMUM_EUR,
                label="Minimum project size",
                source_document_id="bando",
                source_citation="Art. 4",
                source_text="Minimum EUR 100,000",
                scope_note="Selected project class only.",
                boundary_value=100_000,
                input_field=ProjectInputField.PROPOSED_PROJECT_COST_EUR,
            ),
            PublishedRequirement(
                requirement_id="dnsh",
                kind=RequirementKind.PROFESSIONAL_VERIFICATION,
                label="DNSH verification",
                source_document_id="bando",
                source_citation="Art. 8",
                source_text="DNSH requirements must be addressed.",
                scope_note="Professional assessment required.",
            ),
        ),
        completeness_attested=True,
    )


def test_matrix_separates_source_fact_user_fact_and_professional_judgment() -> None:
    matrix = build_readiness_matrix(
        _package(),
        project_inputs={
            "proposed_project_cost_eur": 80_000,
            "proposed_funding_eur": 250_000,
            "proposed_duration_months": 24,
        },
        confirmations=(
            AdvisorConfirmation(
                requirement_id="dnsh",
                state=AdvisorState.PROFESSIONAL_REVIEW_REQUIRED,
            ),
        ),
    )
    row = matrix["rows"][0]
    mechanical = row["mechanical_comparison"]
    assert mechanical["field"] == "proposed_project_cost_eur"
    assert mechanical["user_value"] == 80_000
    assert mechanical["result_code"] == "BELOW_PUBLISHED_MINIMUM"
    assert matrix["points_requiring_professional_verification"][0]["requirement_id"] == "dnsh"
    assert "verdict" in matrix["completion"]["language"]


def test_project_cost_boundary_cannot_silently_use_requested_funding() -> None:
    matrix = build_readiness_matrix(
        _package(),
        project_inputs={
            "proposed_project_cost_eur": 99_999,
            "proposed_funding_eur": 500_000,
        },
        confirmations=(),
    )
    comparison = matrix["rows"][0]["mechanical_comparison"]
    assert comparison["field"] == "proposed_project_cost_eur"
    assert comparison["result_code"] == "BELOW_PUBLISHED_MINIMUM"


def test_unknown_confirmation_fails_closed() -> None:
    try:
        build_readiness_matrix(
            _package(),
            project_inputs={"proposed_project_cost_eur": 100_000},
            confirmations=(AdvisorConfirmation("unknown", AdvisorState.CONFIRMED_BY_ADVISOR),),
        )
    except ValueError as exc:
        assert "unknown requirement" in str(exc)
    else:
        raise AssertionError("unknown confirmation must fail")
