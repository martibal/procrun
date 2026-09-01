"""Core immutable domain objects for Procurement Runway."""

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ComponentState(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
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
    first_seen_at: datetime
    project_start: date | None = None
    project_end: date | None = None
    approved_funding_eur: int | None = Field(default=None, ge=0)
    executed_funding_eur: int | None = Field(default=None, ge=0)
    project_scope_text: str
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
    title: str
    cpv_codes: tuple[str, ...] = ()
    procedure_value_eur: int | None = Field(default=None, ge=0)
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
