"""Deterministic project-state aggregation.

Component OPEN/CLOSED decisions must be evidence rules, not model predictions. This module
only aggregates already-assessed component states to the project-level state.
"""

from datetime import date

from procrun.domain import ComponentAssessment, ComponentState, ProjectAssessment, ProjectState


def aggregate_project_state(
    operation_code: str,
    cutoff_date: date,
    components: tuple[ComponentAssessment, ...],
) -> ProjectAssessment:
    if not components:
        return ProjectAssessment(
            operation_code=operation_code,
            state=ProjectState.UNRESOLVED,
            cutoff_date=cutoff_date,
            components=(),
        )

    states = {component.state for component in components}

    if states == {ComponentState.CLOSED}:
        project_state = ProjectState.CLOSED
    elif states == {ComponentState.OPEN}:
        project_state = ProjectState.OPEN
    elif len(states) > 1:
        project_state = ProjectState.PARTIAL
    else:
        project_state = ProjectState.UNRESOLVED

    return ProjectAssessment(
        operation_code=operation_code,
        state=project_state,
        cutoff_date=cutoff_date,
        components=components,
    )
