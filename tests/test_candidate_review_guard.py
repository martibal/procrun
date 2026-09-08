from datetime import date

from procrun.candidates import build_match_candidate
from procrun.domain import FundingProject, ProcurementEvidence, PurchaseComponent
from procrun.matching import MatchTier, evaluate_candidate


def _project() -> FundingProject:
    return FundingProject(
        operation_code="OP-1",
        project_title="Advanced Port Monitoring",
        project_start=date(2025, 1, 1),
        project_end=date(2027, 12, 31),
        approved_funding_eur=10_000,
        project_scope_text="Advanced Port Monitoring",
        programme="PR FESR Lombardia 2021-2027",
        region="Lombardia",
        nuts_code="ITC4",
        source_url="https://example.invalid/project",
    )


def _component() -> PurchaseComponent:
    return PurchaseComponent(
        component_id="cmp-1",
        operation_code="OP-1",
        category="ports_coastal:monitoring",
        description="Monitoring",
        scope_evidence="Monitoring",
    )


def _evidence(*, title: str, nuts_code: str = "ITC4") -> ProcurementEvidence:
    return ProcurementEvidence(
        evidence_id="ev-1",
        component_id="cmp-1",
        notice_id="notice-1",
        publication_date=date(2026, 5, 1),
        title=title,
        scope_description="Monitoring services",
        cpv_codes=("38400000",),
        nuts_code=nuts_code,
        source_url="https://example.invalid/notice",
    )


def test_shared_geography_does_not_count_as_project_title_or_location_match() -> None:
    candidate = build_match_candidate(
        _project(),
        _component(),
        _evidence(title="Unrelated regional monitoring procurement"),
    )

    assert candidate.features.geography_match is True
    assert candidate.features.project_title_or_location_match is False
    assert evaluate_candidate(candidate, date(2026, 9, 8)).tier is MatchTier.NONE


def test_actual_project_title_match_can_still_form_tier_c_review_candidate() -> None:
    candidate = build_match_candidate(
        _project(),
        _component(),
        _evidence(title="Advanced Port Monitoring - monitoring services"),
    )

    assert candidate.features.geography_match is True
    assert candidate.features.project_title_or_location_match is True
    assert candidate.features.cpv_or_category_match is True
    assert evaluate_candidate(candidate, date(2026, 9, 8)).tier is MatchTier.C
