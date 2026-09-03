"""Deterministic procurement-candidate feature construction.

This module is the only production bridge between normalized procurement evidence and the matching
hierarchy. It never assigns a customer state and never treats semantic similarity as evidence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from procrun.component_engine import RULES, ComponentRule, cpv_matches_prefixes
from procrun.domain import EvidenceField, FundingProject, ProcurementEvidence, PurchaseComponent
from procrun.matching import CandidateFeatures, MatchCandidate

_SENTENCE_BOUNDARIES = ".;!?\n"


class CandidateConstructionError(ValueError):
    """Raised when component/evidence provenance is inconsistent or unsupported."""


@dataclass(frozen=True)
class BoundEvidence:
    evidence: ProcurementEvidence
    matched_phrase: str


def _rule_for_component(component: PurchaseComponent) -> ComponentRule:
    try:
        domain_name, category = component.category.split(":", 1)
    except ValueError as exc:
        raise CandidateConstructionError("component category must be domain:category") from exc
    matches = tuple(
        rule
        for rule in RULES
        if rule.domain.value == domain_name and rule.category == category
    )
    if len(matches) != 1:
        raise CandidateConstructionError(
            f"component category is not uniquely represented in frozen taxonomy: {component.category}"
        )
    return matches[0]


def _phrase_pattern(phrase: str) -> re.Pattern[str]:
    return re.compile(rf"(?<!\w){re.escape(phrase)}(?!\w)", flags=re.IGNORECASE)


def _supporting_span(text: str, start: int, end: int) -> tuple[int, int, str]:
    left = max(text.rfind(boundary, 0, start) for boundary in _SENTENCE_BOUNDARIES)
    right_positions = [
        position
        for boundary in _SENTENCE_BOUNDARIES
        if (position := text.find(boundary, end)) >= 0
    ]
    span_start = left + 1
    span_end = min(right_positions) + 1 if right_positions else len(text)
    while span_start < span_end and text[span_start].isspace():
        span_start += 1
    while span_end > span_start and text[span_end - 1].isspace():
        span_end -= 1
    return span_start, span_end, text[span_start:span_end]


def bind_exact_component_evidence(
    component: PurchaseComponent,
    evidence: ProcurementEvidence,
) -> BoundEvidence | None:
    """Bind a notice to a component only when frozen taxonomy text occurs verbatim in source text."""

    if evidence.component_id != component.component_id:
        raise CandidateConstructionError("evidence component_id does not match component")
    rule = _rule_for_component(component)
    fields = (
        (EvidenceField.SCOPE_DESCRIPTION, evidence.scope_description),
        (EvidenceField.TITLE, evidence.title),
    )
    for field, text in fields:
        if not text:
            continue
        for phrase in rule.phrases:
            match = _phrase_pattern(phrase).search(text)
            if match is None:
                continue
            start, end, span = _supporting_span(text, match.start(), match.end())
            return BoundEvidence(
                evidence=evidence.model_copy(
                    update={
                        "evidence_field": field,
                        "evidence_text": span,
                        "evidence_start": start,
                        "evidence_end": end,
                    }
                ),
                matched_phrase=phrase,
            )
    return None


def _reference_matches(project: FundingProject, evidence: ProcurementEvidence) -> bool:
    if not evidence.project_reference:
        return False
    return evidence.project_reference.strip().casefold() == project.operation_code.strip().casefold()


def _date_compatible(project: FundingProject, publication_date: date) -> bool:
    # Missing project timing never becomes positive evidence.
    if project.project_start is None and project.project_end is None:
        return False
    if project.project_start is not None and publication_date < project.project_start:
        return False
    if project.project_end is not None and publication_date > project.project_end:
        return False
    return True


def _geography_matches(project: FundingProject, evidence: ProcurementEvidence) -> bool:
    if not project.nuts_code or not evidence.nuts_code:
        return False
    project_code = project.nuts_code.strip().casefold()
    evidence_codes = [part.strip().casefold() for part in evidence.nuts_code.split("|")]
    return any(
        code == project_code or code.startswith(project_code) or project_code.startswith(code)
        for code in evidence_codes
        if code
    )


def _title_or_location_matches(project: FundingProject, evidence: ProcurementEvidence) -> bool:
    if _geography_matches(project, evidence):
        return True
    if not project.project_title:
        return False
    needle = project.project_title.strip().casefold()
    if not needle:
        return False
    haystacks = (evidence.title, evidence.scope_description or "")
    return any(needle in value.casefold() for value in haystacks)


def build_match_candidate(
    project: FundingProject,
    component: PurchaseComponent,
    evidence: ProcurementEvidence,
) -> MatchCandidate:
    """Build conservative matching facts from explicit project and procurement evidence."""

    if component.operation_code != project.operation_code:
        raise CandidateConstructionError("component does not belong to project")
    bound = bind_exact_component_evidence(component, evidence)
    rule = _rule_for_component(component)
    high_scope_overlap = bound is not None
    bound_evidence = evidence if bound is None else bound.evidence
    cpv_match = any(
        cpv_matches_prefixes(code, rule.cpv_prefixes) for code in evidence.cpv_codes
    ) if rule.cpv_prefixes else False
    compatible_date = _date_compatible(project, evidence.publication_date)

    return MatchCandidate(
        evidence=bound_evidence,
        features=CandidateFeatures(
            exact_project_identifier=_reference_matches(project, evidence),
            contracting_authority_match=False,
            geography_match=_geography_matches(project, evidence),
            high_scope_overlap=high_scope_overlap,
            cpv_or_category_match=cpv_match,
            compatible_date_window=compatible_date,
            project_title_or_location_match=_title_or_location_matches(project, evidence),
            corroborating_amount_or_date=compatible_date,
            semantic_similarity=False,
        ),
    )


def build_match_candidates(
    project: FundingProject,
    component: PurchaseComponent,
    evidence: tuple[ProcurementEvidence, ...],
) -> tuple[MatchCandidate, ...]:
    """Build candidates deterministically, preserving input order for reproducibility."""

    return tuple(build_match_candidate(project, component, item) for item in evidence)
