"""Public API contracts for the Funded Project Comparables paywall boundary.

The free preview contract intentionally contains no sample count, percentile,
statistics, comparable names or project identifiers. Those belong to the paid
report surface only.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CohortTier(StrEnum):
    SAME_BANDO = "SAME_BANDO"
    SAME_ACTION_INTERVENTION = "SAME_ACTION_INTERVENTION"
    SAME_ACTION = "SAME_ACTION"


class ReferenceAvailability(StrEnum):
    FULL = "FULL"
    LIMITED = "LIMITED"
    REFERENCE_ONLY = "REFERENCE_ONLY"


class CohortSelection(StrictApiModel):
    tier: CohortTier
    bando_code: str | None = None
    action_code: str | None = None
    intervention_code: str | None = None

    @model_validator(mode="after")
    def require_tier_keys(self) -> CohortSelection:
        if self.tier is CohortTier.SAME_BANDO and not self.bando_code:
            raise ValueError("SAME_BANDO requires bando_code")
        if (
            self.tier is CohortTier.SAME_ACTION_INTERVENTION
            and (not self.action_code or not self.intervention_code)
        ):
            raise ValueError(
                "SAME_ACTION_INTERVENTION requires action_code and intervention_code"
            )
        if self.tier is CohortTier.SAME_ACTION and not self.action_code:
            raise ValueError("SAME_ACTION requires action_code")
        return self


class BenchmarkComputeRequest(StrictApiModel):
    proposed_funding_eur: int = Field(ge=0)
    proposed_duration_months: int | None = Field(default=None, ge=0)
    cohort_selection: CohortSelection


class BenchmarkPreviewResponse(StrictApiModel):
    """Leakage-safe response allowed before payment."""

    status: Literal["ANALYSIS_AVAILABLE"] = "ANALYSIS_AVAILABLE"
    reference_availability: ReferenceAvailability
    message: str


class ReportCreateRequest(StrictApiModel):
    """Paid report creation request after the payment layer authorizes the purchase."""

    proposed_funding_eur: int = Field(ge=0)
    proposed_duration_months: int | None = Field(default=None, ge=0)
    cohort_selection: CohortSelection
    snapshot_id: str


class ReportCreateResponse(StrictApiModel):
    report_id: str
    canonical_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
