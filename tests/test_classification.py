from datetime import date

from procrun.classification import aggregate_project_state
from procrun.domain import (
    ComponentAssessment,
    ComponentState,
    ProjectState,
)

CUTOFF = date(2026, 7, 31)


def component(component_id: str, state: ComponentState) -> ComponentAssessment:
    return ComponentAssessment(
        component_id=component_id,
        state=state,
        cutoff_date=CUTOFF,
        rationale="fixture",
        evidence_ids=(),
        coverage_note="fixture coverage",
    )


def test_all_closed_is_closed() -> None:
    result = aggregate_project_state(
        "OP-1",
        CUTOFF,
        (
            component("a", ComponentState.CLOSED),
            component("b", ComponentState.CLOSED),
        ),
    )
    assert result.state is ProjectState.CLOSED


def test_all_open_is_open() -> None:
    result = aggregate_project_state(
        "OP-1",
        CUTOFF,
        (component("a", ComponentState.OPEN), component("b", ComponentState.OPEN)),
    )
    assert result.state is ProjectState.OPEN


def test_open_and_closed_is_partial() -> None:
    result = aggregate_project_state(
        "PACS-FC-04022300",
        CUTOFF,
        (
            component("crossing-a", ComponentState.CLOSED),
            component("crossing-b", ComponentState.OPEN),
        ),
    )
    assert result.state is ProjectState.PARTIAL


def test_closed_and_unresolved_is_partial_not_open() -> None:
    result = aggregate_project_state(
        "OP-1",
        CUTOFF,
        (
            component("a", ComponentState.CLOSED),
            component("b", ComponentState.UNRESOLVED),
        ),
    )
    assert result.state is ProjectState.PARTIAL


def test_only_unresolved_is_unresolved() -> None:
    result = aggregate_project_state(
        "OP-1", CUTOFF, (component("a", ComponentState.UNRESOLVED),)
    )
    assert result.state is ProjectState.UNRESOLVED


def test_no_components_fails_closed_to_unresolved() -> None:
    result = aggregate_project_state("OP-1", CUTOFF, ())
    assert result.state is ProjectState.UNRESOLVED
