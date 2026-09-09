from procrun.classification import aggregate_project_state
from procrun.domain import ComponentAssessment, ComponentState, ProjectState
from datetime import date


def _component(component_id: str, state: ComponentState) -> ComponentAssessment:
    return ComponentAssessment(
        component_id=component_id,
        state=state,
        cutoff_date=date(2026, 9, 9),
        rationale="test",
        coverage_note="test",
    )


def test_taxonomy_v2_does_not_change_project_state_aggregation_contract() -> None:
    assert aggregate_project_state("P", date(2026, 9, 9), ()) .state is ProjectState.UNRESOLVED
    assert aggregate_project_state(
        "P", date(2026, 9, 9), (_component("a", ComponentState.OPEN),)
    ).state is ProjectState.OPEN
    assert aggregate_project_state(
        "P", date(2026, 9, 9), (_component("a", ComponentState.CLOSED),)
    ).state is ProjectState.CLOSED
    assert aggregate_project_state(
        "P",
        date(2026, 9, 9),
        (_component("a", ComponentState.OPEN), _component("b", ComponentState.CLOSED)),
    ).state is ProjectState.PARTIAL
    assert aggregate_project_state(
        "P",
        date(2026, 9, 9),
        (_component("a", ComponentState.OPEN), _component("b", ComponentState.UNRESOLVED)),
    ).state is ProjectState.UNRESOLVED
