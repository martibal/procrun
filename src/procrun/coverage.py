"""Coverage-bound negative-search semantics for customer-visible OPEN states."""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from procrun.domain import ComponentAssessment, ComponentState


class CoverageScope(StrEnum):
    TED = "TED"


class UnsupportedCoverageScopeError(ValueError):
    """Raised when code attempts to create a broader OPEN claim than the MVP supports."""


def ted_open_wording(cutoff_date: date) -> str:
    return f"No relevant procurement found in TED as of {cutoff_date.isoformat()}."


def make_open_assessment(
    *,
    component_id: str,
    cutoff_date: date,
    coverage_scope: CoverageScope,
    evidence_ids: tuple[str, ...] = (),
) -> ComponentAssessment:
    """Create OPEN only under the permanent MVP TED coverage boundary."""
    if coverage_scope is not CoverageScope.TED:
        raise UnsupportedCoverageScopeError(
            "MVP OPEN may only be created from complete TED-scoped negative-search coverage"
        )
    wording = ted_open_wording(cutoff_date)
    return ComponentAssessment(
        component_id=component_id,
        state=ComponentState.OPEN,
        cutoff_date=cutoff_date,
        rationale=wording,
        evidence_ids=evidence_ids,
        coverage_note=(
            wording
            + " This does not establish absence outside TED, including purely national "
            "or below-threshold procedures."
        ),
    )
