"""Core immutable domain objects for Procurement Runway."""

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


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
