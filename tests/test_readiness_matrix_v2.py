from datetime import UTC, datetime

from procrun.readiness_matrix import AdvisorConfirmation, AdvisorState, build_readiness_matrix
from procrun.readiness_source import PublishedRequirement, RequirementKind, SourceDocument, SourcePackage


def _package() -> SourcePackage:
    document = SourceDocument(
        document_id="bando",
        document_type="BANDO",
        title="Bando",
        public_url="https://example.invalid/bando",
        sha256="b" * 64,
        observed_at=datetime(2026, 9, 1, tzinfo=UTC),
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
        project_inputs={"proposed_funding_eur": 80_000, "proposed_duration_months": 24},
        confirmations=(
            AdvisorConfirmation(
                requirement_id="dnsh",
                state=AdvisorState.PROFESSIONAL_REVIEW_REQUIRED,
            ),
        ),
    )
    row = matrix["rows"][0]
    assert row["mechanical_comparison"]["result_code"] == "BELOW_PUBLISHED_MINIMUM"
    assert "80,000" not in row["mechanical_comparison"]["statement"]
    assert matrix["points_requiring_professional_verification"][0]["requirement_id"] == "dnsh"
    assert "verdict" in matrix["completion"]["language"]


def test_unknown_confirmation_fails_closed() -> None:
    try:
        build_readiness_matrix(
            _package(),
            project_inputs={"proposed_funding_eur": 100_000},
            confirmations=(AdvisorConfirmation("unknown", AdvisorState.CONFIRMED_BY_ADVISOR),),
        )
    except ValueError as exc:
        assert "unknown requirement" in str(exc)
    else:
        raise AssertionError("unknown confirmation must fail")
