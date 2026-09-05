"""Conservative deterministic procurement candidate matching.

The hierarchy is intentionally asymmetric: missing or ambiguous evidence may reduce output volume,
but it may never manufacture OPEN or CLOSED. Tier A/B can close only when the candidate also carries
an exact source span that has already passed the domain-model verbatim validation.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from procrun.coverage import ted_open_wording
from procrun.domain import (
    ComponentAssessment,
    ComponentState,
    ProcurementEvidence,
    PurchaseComponent,
)

MATCH_RULE_VERSION = "phase-b-conservative-v2-exact-evidence"


class MatchTier(StrEnum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    NONE = "NONE"


class CandidateDisposition(StrEnum):
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
    REVIEW = "REVIEW"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class CandidateFeatures:
    """Deterministic feature facts produced upstream; no probability is implied."""

    exact_project_identifier: bool = False
    contracting_authority_match: bool = False
    geography_match: bool = False
    high_scope_overlap: bool = False
    cpv_or_category_match: bool = False
    compatible_date_window: bool = False
    project_title_or_location_match: bool = False
    corroborating_amount_or_date: bool = False
    semantic_similarity: bool = False


@dataclass(frozen=True)
class MatchCandidate:
    evidence: ProcurementEvidence
    features: CandidateFeatures


@dataclass(frozen=True)
class CandidateEvaluation:
    evidence_id: str
    tier: MatchTier
    disposition: CandidateDisposition
    effective_date: date
    pre_cutoff: bool
    reason: str


@dataclass(frozen=True)
class ComponentMatchResult:
    assessment: ComponentAssessment
    evaluations: tuple[CandidateEvaluation, ...]
    rule_version: str = MATCH_RULE_VERSION


def _effective_procurement_date(evidence: ProcurementEvidence) -> date:
    dates = [evidence.publication_date]
    if evidence.award_date is not None:
        dates.append(evidence.award_date)
    if evidence.contract_date is not None:
        dates.append(evidence.contract_date)
    return min(dates)


def _tier(features: CandidateFeatures) -> MatchTier:
    if (
        features.exact_project_identifier
        and features.high_scope_overlap
        and features.compatible_date_window
    ):
        return MatchTier.A
    if (
        features.contracting_authority_match
        and features.geography_match
        and features.high_scope_overlap
        and features.cpv_or_category_match
        and features.compatible_date_window
    ):
        return MatchTier.B
    if (
        features.project_title_or_location_match
        and features.high_scope_overlap
        and features.cpv_or_category_match
        and features.compatible_date_window
        and features.corroborating_amount_or_date
    ):
        return MatchTier.C
    if features.semantic_similarity:
        return MatchTier.D
    return MatchTier.NONE


def _has_exact_evidence(evidence: ProcurementEvidence) -> bool:
    return all(
        value is not None
        for value in (
            evidence.evidence_field,
            evidence.evidence_text,
            evidence.evidence_start,
            evidence.evidence_end,
        )
    )


def evaluate_candidate(candidate: MatchCandidate, cutoff_date: date) -> CandidateEvaluation:
    """Evaluate one candidate without inventing an unfrozen numeric score."""

    tier = _tier(candidate.features)
    effective_date = _effective_procurement_date(candidate.evidence)
    pre_cutoff = effective_date <= cutoff_date

    if not pre_cutoff:
        disposition = CandidateDisposition.REJECTED
        reason = "procurement evidence is after the historical cutoff"
    elif tier in {MatchTier.A, MatchTier.B} and not _has_exact_evidence(candidate.evidence):
        disposition = CandidateDisposition.REVIEW
        reason = "Tier A/B structural facts lack the required exact source span"
    elif tier in {MatchTier.A, MatchTier.B}:
        disposition = CandidateDisposition.HIGH_CONFIDENCE
        reason = f"complete deterministic Tier {tier.value} evidence covers the component"
    elif tier is MatchTier.C:
        disposition = CandidateDisposition.REVIEW
        reason = (
            "Tier C evidence is corroborated but remains in review until a CLOSED threshold is "
            "explicitly frozen"
        )
    elif tier is MatchTier.D:
        disposition = CandidateDisposition.REJECTED
        reason = "semantic similarity alone is Tier D and cannot establish CLOSED"
    else:
        disposition = CandidateDisposition.REJECTED
        reason = "candidate does not satisfy a frozen Tier A-C structural rule"

    return CandidateEvaluation(
        evidence_id=candidate.evidence.evidence_id,
        tier=tier,
        disposition=disposition,
        effective_date=effective_date,
        pre_cutoff=pre_cutoff,
        reason=reason,
    )


def classify_component(
    component: PurchaseComponent,
    cutoff_date: date,
    candidates: Sequence[MatchCandidate],
    *,
    coverage_complete: bool,
    component_boundary_resolved: bool,
    coverage_note: str,
) -> ComponentMatchResult:
    """Assign CLOSED/OPEN/UNRESOLVED with false-OPEN protection."""

    for candidate in candidates:
        if candidate.evidence.component_id != component.component_id:
            raise ValueError(
                "procurement evidence component_id does not match the assessed component"
            )

    evaluations = tuple(evaluate_candidate(candidate, cutoff_date) for candidate in candidates)
    high_confidence = tuple(
        evaluation
        for evaluation in evaluations
        if evaluation.disposition is CandidateDisposition.HIGH_CONFIDENCE
    )
    review = tuple(
        evaluation
        for evaluation in evaluations
        if evaluation.disposition is CandidateDisposition.REVIEW
    )

    if not component_boundary_resolved:
        state = ComponentState.UNRESOLVED
        rationale = "Component boundary is ambiguous; false-OPEN protection requires withholding."
        evidence_ids = tuple(evaluation.evidence_id for evaluation in high_confidence + review)
    elif high_confidence:
        state = ComponentState.CLOSED
        rationale = (
            "At least one high-confidence pre-cutoff procurement record covers the component."
        )
        evidence_ids = tuple(evaluation.evidence_id for evaluation in high_confidence)
    elif review:
        state = ComponentState.UNRESOLVED
        rationale = "A pre-cutoff procurement candidate is in the review band; OPEN is prohibited."
        evidence_ids = tuple(evaluation.evidence_id for evaluation in review)
    elif not coverage_complete:
        state = ComponentState.UNRESOLVED
        rationale = "Required procurement-source coverage is incomplete; OPEN is prohibited."
        evidence_ids = ()
    else:
        state = ComponentState.OPEN
        rationale = ted_open_wording(cutoff_date)
        evidence_ids = ()

    return ComponentMatchResult(
        assessment=ComponentAssessment(
            component_id=component.component_id,
            state=state,
            cutoff_date=cutoff_date,
            rationale=rationale,
            evidence_ids=evidence_ids,
            coverage_note=coverage_note,
        ),
        evaluations=evaluations,
    )