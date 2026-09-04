from datetime import date

import pytest

from procrun.domain import (
    ComponentState,
    EvidenceField,
    ProcurementEvidence,
    PurchaseComponent,
)
from procrun.matching import (
    CandidateDisposition,
    CandidateFeatures,
    MatchCandidate,
    MatchTier,
    classify_component,
    evaluate_candidate,
)

CUTOFF = date(2026, 7, 31)
COMPONENT = PurchaseComponent(
    component_id="crossing-a",
    operation_code="PACS-FC-04022300",
    category="rail_transport:crossings",
    description="Level-crossing suppression civil works",
    scope_evidence="Suppression of one of the funded level crossings.",
)
TITLE = "Level-crossing suppression works"


def evidence(
    evidence_id: str = "ev-1",
    *,
    publication_date: date = date(2026, 3, 1),
    component_id: str = "crossing-a",
    exact_span: bool = True,
) -> ProcurementEvidence:
    kwargs: dict[str, object] = {}
    if exact_span:
        kwargs = {
            "evidence_field": EvidenceField.TITLE,
            "evidence_text": TITLE,
            "evidence_start": 0,
            "evidence_end": len(TITLE),
        }
    return ProcurementEvidence(
        evidence_id=evidence_id,
        component_id=component_id,
        notice_id=f"notice-{evidence_id}",
        publication_date=publication_date,
        title=TITLE,
        cpv_codes=("45200000",),
        source_url=f"https://example.invalid/{evidence_id}",
        **kwargs,
    )


def classify(
    candidates: tuple[MatchCandidate, ...],
    *,
    coverage_complete: bool = True,
    component_boundary_resolved: bool = True,
):
    return classify_component(
        COMPONENT,
        CUTOFF,
        candidates,
        coverage_complete=coverage_complete,
        component_boundary_resolved=component_boundary_resolved,
        coverage_note="TED iteration completed through cutoff.",
        open_rationale="No relevant procurement found in TED as of 2026-07-31.",
    )


def test_complete_tier_a_closes_component() -> None:
    candidate = MatchCandidate(
        evidence(),
        CandidateFeatures(
            exact_project_identifier=True,
            high_scope_overlap=True,
            compatible_date_window=True,
        ),
    )
    result = classify((candidate,))

    assert result.assessment.state is ComponentState.CLOSED
    assert result.assessment.evidence_ids == ("ev-1",)
    assert result.evaluations[0].tier is MatchTier.A
    assert result.evaluations[0].disposition is CandidateDisposition.HIGH_CONFIDENCE


def test_tier_a_without_exact_source_span_is_withheld() -> None:
    candidate = MatchCandidate(
        evidence(exact_span=False),
        CandidateFeatures(
            exact_project_identifier=True,
            high_scope_overlap=True,
            compatible_date_window=True,
        ),
    )
    result = classify((candidate,))

    assert result.assessment.state is ComponentState.UNRESOLVED
    assert result.evaluations[0].disposition is CandidateDisposition.REVIEW


def test_complete_tier_b_closes_component() -> None:
    candidate = MatchCandidate(
        evidence(),
        CandidateFeatures(
            contracting_authority_match=True,
            geography_match=True,
            high_scope_overlap=True,
            cpv_or_category_match=True,
            compatible_date_window=True,
        ),
    )
    result = classify((candidate,))

    assert result.assessment.state is ComponentState.CLOSED
    assert result.evaluations[0].tier is MatchTier.B


def test_tier_c_is_review_and_never_open() -> None:
    candidate = MatchCandidate(
        evidence(),
        CandidateFeatures(
            project_title_or_location_match=True,
            high_scope_overlap=True,
            cpv_or_category_match=True,
            compatible_date_window=True,
            corroborating_amount_or_date=True,
        ),
    )
    result = classify((candidate,))

    assert result.assessment.state is ComponentState.UNRESOLVED
    assert result.assessment.evidence_ids == ("ev-1",)
    assert result.evaluations[0].tier is MatchTier.C
    assert result.evaluations[0].disposition is CandidateDisposition.REVIEW


def test_semantic_similarity_alone_cannot_close_or_block_open() -> None:
    candidate = MatchCandidate(
        evidence(),
        CandidateFeatures(semantic_similarity=True),
    )
    result = classify((candidate,))

    assert result.assessment.state is ComponentState.OPEN
    assert result.assessment.rationale == "No relevant procurement found in TED as of 2026-07-31."
    assert result.evaluations[0].tier is MatchTier.D
    assert result.evaluations[0].disposition is CandidateDisposition.REJECTED


def test_incomplete_coverage_can_never_be_open() -> None:
    result = classify((), coverage_complete=False)
    assert result.assessment.state is ComponentState.UNRESOLVED


def test_high_confidence_match_closes_even_if_other_coverage_is_incomplete() -> None:
    candidate = MatchCandidate(
        evidence(),
        CandidateFeatures(
            exact_project_identifier=True,
            high_scope_overlap=True,
            compatible_date_window=True,
        ),
    )
    result = classify((candidate,), coverage_complete=False)
    assert result.assessment.state is ComponentState.CLOSED


def test_ambiguous_component_boundary_is_withheld() -> None:
    candidate = MatchCandidate(
        evidence(),
        CandidateFeatures(
            exact_project_identifier=True,
            high_scope_overlap=True,
            compatible_date_window=True,
        ),
    )
    result = classify((candidate,), component_boundary_resolved=False)
    assert result.assessment.state is ComponentState.UNRESOLVED


def test_post_cutoff_exact_match_does_not_change_historical_open_state() -> None:
    candidate = MatchCandidate(
        evidence(publication_date=date(2026, 8, 1)),
        CandidateFeatures(
            exact_project_identifier=True,
            high_scope_overlap=True,
            compatible_date_window=True,
        ),
    )
    result = classify((candidate,))

    assert result.assessment.state is ComponentState.OPEN
    assert result.assessment.rationale == "No relevant procurement found in TED as of 2026-07-31."
    assert result.evaluations[0].pre_cutoff is False
    assert result.evaluations[0].disposition is CandidateDisposition.REJECTED


def test_open_without_explicit_scope_rationale_fails_closed() -> None:
    with pytest.raises(ValueError, match="explicit source-scoped rationale"):
        classify_component(
            COMPONENT,
            CUTOFF,
            (),
            coverage_complete=True,
            component_boundary_resolved=True,
            coverage_note="complete",
        )


def test_earlier_contract_date_can_establish_pre_cutoff_procurement() -> None:
    item = evidence(publication_date=date(2026, 8, 2)).model_copy(
        update={"contract_date": date(2026, 7, 20)}
    )
    candidate = MatchCandidate(
        item,
        CandidateFeatures(
            exact_project_identifier=True,
            high_scope_overlap=True,
            compatible_date_window=True,
        ),
    )
    evaluation = evaluate_candidate(candidate, CUTOFF)

    assert evaluation.pre_cutoff is True
    assert evaluation.effective_date == date(2026, 7, 20)
    assert evaluation.disposition is CandidateDisposition.HIGH_CONFIDENCE


def test_evidence_cannot_leak_across_components() -> None:
    candidate = MatchCandidate(
        evidence(component_id="different-component"),
        CandidateFeatures(
            exact_project_identifier=True,
            high_scope_overlap=True,
            compatible_date_window=True,
        ),
    )
    with pytest.raises(ValueError):
        classify((candidate,))
