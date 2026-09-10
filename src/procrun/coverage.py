"""Coverage-bound semantics for customer-visible rule-bounded OPEN states."""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from procrun.domain import ComponentAssessment, ComponentState


class CoverageScope(StrEnum):
    TED = "TED"


class UnsupportedCoverageScopeError(ValueError):
    """Raised when code attempts to create a broader OPEN claim than the product proves."""


def ted_open_wording(cutoff_date: date) -> str:
    """Return the strongest negative claim ProcRun can prove without subjective absence claims."""

    return (
        "No procurement match satisfying ProcRun's frozen exact-evidence rules was found in TED "
        f"as of {cutoff_date.isoformat()}."
    )


def make_open_assessment(
    *,
    component_id: str,
    cutoff_date: date,
    coverage_scope: CoverageScope,
    evidence_ids: tuple[str, ...] = (),
) -> ComponentAssessment:
    """Create OPEN only under complete TED coverage and rule-bounded semantics."""

    if coverage_scope is not CoverageScope.TED:
        raise UnsupportedCoverageScopeError(
            "OPEN may only be created from complete TED-scoped rule-bounded coverage"
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
            + " This is a rule-bounded observation. It does not establish absence of procurement "
            "outside TED or under different wording/classification."
        ),
    )
