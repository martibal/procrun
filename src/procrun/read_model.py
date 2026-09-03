"""Customer-safe runway read model.

This module is the sole contract intended for a future browser/API layer. It contains no source
response envelopes, buyer/contact identity, beneficiary identity, model prompts or unvalidated
candidate text.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from procrun.domain import ComponentState, EvidenceField, ProjectState
from procrun.ledger import content_sha256
from procrun.matching import CandidateDisposition
from procrun.runway import RunwayComponentResult, RunwayResult

READ_MODEL_VERSION = "customer-runway-v1"


class ReadModelInvariantError(ValueError):
    """Raised when an internal result cannot be safely represented for a customer."""


class PublicModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SourceSpan(PublicModel):
    source_field: str
    text: str
    start: int = Field(ge=0)
    end: int = Field(gt=0)


class ProcurementMatch(PublicModel):
    evidence_id: str
    notice_id: str
    publication_date: date
    title: str
    source_url: str
    cpv_codes: tuple[str, ...]
    estimated_value_eur: int | None = Field(default=None, ge=0)
    nuts_code: str | None = None
    project_reference: str | None = None
    evidence: SourceSpan


class RunwayComponent(PublicModel):
    component_id: str
    category: str
    label: str
    state: ComponentState
    cutoff_date: date
    project_evidence: SourceSpan
    procurement_matches: tuple[ProcurementMatch, ...]
    coverage_note: str
    state_explanation: str


class RunwayProject(PublicModel):
    operation_code: str
    project_title: str | None
    project_start: date | None
    project_end: date | None
    approved_funding_eur: int | None = Field(default=None, ge=0)
    programme: str | None
    region: str | None
    nuts_code: str | None
    source_url: str
    state: ProjectState
    cutoff_date: date
    components: tuple[RunwayComponent, ...]
    orchestration_version: str
    component_rule_version: str
    match_rule_version: str
    project_classifier_version: str
    read_model_version: str = READ_MODEL_VERSION
    content_hash: str


def _project_span(item: RunwayComponentResult) -> SourceSpan:
    spans = item.extracted.evidence_spans
    if not spans:
        raise ReadModelInvariantError("customer component lacks exact project source evidence")
    primary = spans[0]
    if primary.end <= primary.start or primary.text != item.extracted.component.scope_evidence:
        raise ReadModelInvariantError("component primary evidence span is internally inconsistent")
    return SourceSpan(
        source_field="project_scope_text",
        text=primary.text,
        start=primary.start,
        end=primary.end,
    )


def _procurement_match(item: RunwayComponentResult, evidence_id: str) -> ProcurementMatch:
    matching = tuple(
        candidate for candidate in item.candidates if candidate.evidence.evidence_id == evidence_id
    )
    if len(matching) != 1:
        raise ReadModelInvariantError(
            f"accepted evidence id must map to exactly one candidate: {evidence_id}"
        )
    evidence = matching[0].evidence
    if (
        evidence.evidence_field is None
        or evidence.evidence_text is None
        or evidence.evidence_start is None
        or evidence.evidence_end is None
    ):
        raise ReadModelInvariantError("accepted procurement match lacks exact source evidence")
    source_text = (
        evidence.title
        if evidence.evidence_field is EvidenceField.TITLE
        else evidence.scope_description
    )
    span = (
        source_text[evidence.evidence_start : evidence.evidence_end]
        if source_text is not None
        else None
    )
    if span != evidence.evidence_text:
        raise ReadModelInvariantError(
            "accepted procurement source span failed verbatim validation"
        )
    return ProcurementMatch(
        evidence_id=evidence.evidence_id,
        notice_id=evidence.notice_id,
        publication_date=evidence.publication_date,
        title=evidence.title,
        source_url=evidence.source_url,
        cpv_codes=evidence.cpv_codes,
        estimated_value_eur=evidence.estimated_value_eur,
        nuts_code=evidence.nuts_code,
        project_reference=evidence.project_reference,
        evidence=SourceSpan(
            source_field=evidence.evidence_field.value,
            text=evidence.evidence_text,
            start=evidence.evidence_start,
            end=evidence.evidence_end,
        ),
    )


def _component(item: RunwayComponentResult) -> RunwayComponent:
    assessment = item.match.assessment
    accepted = tuple(
        evaluation
        for evaluation in item.match.evaluations
        if evaluation.disposition is CandidateDisposition.HIGH_CONFIDENCE
    )
    accepted_ids = tuple(evaluation.evidence_id for evaluation in accepted)
    if (
        tuple(assessment.evidence_ids) != accepted_ids
        and assessment.state is ComponentState.CLOSED
    ):
        raise ReadModelInvariantError("CLOSED assessment/evidence ids are inconsistent")
    if assessment.state is ComponentState.CLOSED and not accepted_ids:
        raise ReadModelInvariantError("CLOSED component has no accepted procurement evidence")
    if assessment.state is ComponentState.OPEN and assessment.evidence_ids:
        raise ReadModelInvariantError("OPEN component cannot expose accepted evidence")

    matches = tuple(_procurement_match(item, evidence_id) for evidence_id in accepted_ids)
    return RunwayComponent(
        component_id=item.extracted.component.component_id,
        category=item.extracted.component.category,
        label=item.extracted.component.description,
        state=assessment.state,
        cutoff_date=assessment.cutoff_date,
        project_evidence=_project_span(item),
        procurement_matches=matches,
        coverage_note=assessment.coverage_note,
        state_explanation=assessment.rationale,
    )


def build_runway_read_model(result: RunwayResult) -> RunwayProject:
    """Build the frozen browser/API contract and attach a deterministic content hash."""

    components = tuple(_component(item) for item in result.components)
    hash_payload = {
        "operation_code": result.project.operation_code,
        "project_title": result.project.project_title,
        "project_start": result.project.project_start,
        "project_end": result.project.project_end,
        "approved_funding_eur": result.project.approved_funding_eur,
        "programme": result.project.programme,
        "region": result.project.region,
        "nuts_code": result.project.nuts_code,
        "source_url": result.project.source_url,
        "state": result.assessment.state,
        "cutoff_date": result.cutoff_date,
        "components": components,
        "orchestration_version": result.orchestration_version,
        "component_rule_version": result.component_rule_version,
        "match_rule_version": result.match_rule_version,
        "project_classifier_version": result.project_classifier_version,
        "read_model_version": READ_MODEL_VERSION,
    }
    digest = content_sha256(hash_payload)
    return RunwayProject(
        operation_code=result.project.operation_code,
        project_title=result.project.project_title,
        project_start=result.project.project_start,
        project_end=result.project.project_end,
        approved_funding_eur=result.project.approved_funding_eur,
        programme=result.project.programme,
        region=result.project.region,
        nuts_code=result.project.nuts_code,
        source_url=result.project.source_url,
        state=result.assessment.state,
        cutoff_date=result.cutoff_date,
        components=components,
        orchestration_version=result.orchestration_version,
        component_rule_version=result.component_rule_version,
        match_rule_version=result.match_rule_version,
        project_classifier_version=result.project_classifier_version,
        read_model_version=READ_MODEL_VERSION,
        content_hash=digest,
    )
