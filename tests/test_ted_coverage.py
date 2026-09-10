from datetime import date

import pytest

from procrun.coverage import (
    CoverageScope,
    UnsupportedCoverageScopeError,
    make_open_assessment,
    ted_open_wording,
)
from procrun.domain import ComponentState


def test_open_wording_is_exactly_rule_bounded_to_ted() -> None:
    cutoff = date(2026, 9, 4)
    wording = (
        "No procurement match satisfying ProcRun's frozen exact-evidence rules "
        "was found in TED as of 2026-09-04."
    )
    assert ted_open_wording(cutoff) == wording
    assessment = make_open_assessment(
        component_id="component-1",
        cutoff_date=cutoff,
        coverage_scope=CoverageScope.TED,
    )
    assert assessment.state is ComponentState.OPEN
    assert assessment.rationale == wording
    assert "rule-bounded observation" in assessment.coverage_note
    assert "does not establish absence" in assessment.coverage_note


def test_no_broader_coverage_scope_exists_in_mvp() -> None:
    assert tuple(CoverageScope) == (CoverageScope.TED,)


def test_runtime_rejects_non_ted_scope_even_if_type_is_bypassed() -> None:
    with pytest.raises(UnsupportedCoverageScopeError):
        make_open_assessment(
            component_id="component-1",
            cutoff_date=date(2026, 9, 4),
            coverage_scope="PORTUGAL_NATIONAL",  # type: ignore[arg-type]
        )
