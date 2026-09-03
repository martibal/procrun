"""Core immutable domain objects for Procurement Runway."""

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ComponentState(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    UNRESOLVED = "UNRESOLVED"


class TemporalProvenance(StrEnum):
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"


class ProjectState(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PARTIAL = "PARTIAL"
    UNRESOLVED = "UNRESOLVED"


class EvidenceField(StrEnum):
    TITLE = "title"
    SCOPE_DESCRIPTION = "scope_description"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class FundingProject(StrictModel):
    operation_code: str
    first_seen_at: datetime | None = None
    temporal_provenance: TemporalProvenance = TemporalProvenance.UNRESOLVED
    project_title: str | None = None
    project_start: date | None = None
    project_end: date | None = None
    approved_funding_eur: int | None = Field(default=None, ge=0)
    executed_funding_eur: int | None = Field(default=None, ge=0)
    project_scope_text: str
    fund: str | None = None
    programme: str | None = None
    objective: str | None = None
    theme: str | None = None
    region: str | None = None
    municipality: str | None = None
    nuts_code: str | None = None
    source_url: str


class PurchaseComponent(StrictModel):
    component_id: str
    operation_code: str
    category: str
    description: str
    scope_evidence: str
    scope_evidence_start: int | None = Field(default=None, ge=0)
    scope_evidence_end: int | None = Field(default=None, ge=0)
    scope_source_field: str = "project_scope_text"

    @model_validator(mode="after")
    def validate_scope_span(self) -> "PurchaseComponent":
        start = self.scope_evidence_start
        end = self.scope_evidence_end
        if (start is None) != (end is None):
            raise ValueError("scope evidence offsets must either both be present or both be absent")
        if start is not None and end is not None and end <= start:
            raise ValueError("scope evidence end must be greater than start")
        return self


class ProcurementEvidence(StrictModel):
    evidence_id: str
    component_id: str
    notice_id: str
    publication_date: date
    award_date: date | None = None
    contract_date: date | None = None
    title: str
    scope_description: str | None = None
    cpv_codes: tuple[str, ...] = ()
    contract_nature: str | None = None
    procedure_type: str | None = None
    procedure_value_eur: int | None = Field(default=None, ge=0)
    estimated_value_eur: int | None = Field(default=None, ge=0)
    base_value_eur: int | None = Field(default=None, ge=0)
    awarded_value_eur: int | None = Field(default=None, ge=0)
    place_of_performance: str | None = None
    nuts_code: str | None = None
    municipality: str | None = None
    contracting_authority_name: str | None = None
    project_reference: str | None = None
    source_url: str
    evidence_field: EvidenceField | None = None
    evidence_text: str | None = None
    evidence_start: int | None = Field(default=None, ge=0)
    evidence_end: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_evidence_span(self) -> "ProcurementEvidence":
        span_values = (
            self.evidence_field,
            self.evidence_text,
            self.evidence_start,
            self.evidence_end,
        )
        if all(value is None for value in span_values):
            return self
        if any(value is None for value in span_values):
            raise ValueError(
                "procurement evidence field, text and offsets must be present together"
            )
        assert self.evidence_field is not None
        assert self.evidence_text is not None
        assert self.evidence_start is not None
        assert self.evidence_end is not None
        if self.evidence_end <= self.evidence_start:
            raise ValueError("procurement evidence end must be greater than start")
        source_text = (
            self.title
            if self.evidence_field is EvidenceField.TITLE
            else self.scope_description
        )
        if source_text is None:
            raise ValueError("procurement evidence field points to an absent source field")
        if self.evidence_end > len(source_text):
            raise ValueError("procurement evidence offsets exceed the source field")
        if source_text[self.evidence_start : self.evidence_end] != self.evidence_text:
            raise ValueError("procurement evidence text must match the exact source span")
        return self


class ComponentAssessment(StrictModel):
    component_id: str
    state: ComponentState
    cutoff_date: date
    rationale: str
    evidence_ids: tuple[str, ...] = ()
    coverage_note: str


class ProjectAssessment(StrictModel):
    operation_code: str
    state: ProjectState
    cutoff_date: date
    components: tuple[ComponentAssessment, ...]
