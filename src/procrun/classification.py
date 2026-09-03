"""Deterministic project-state aggregation.

Component OPEN/CLOSED decisions must be evidence rules, not model predictions. Project aggregation is
also fail-closed: any unresolved component makes the project aggregate UNRESOLVED. PARTIAL is reserved
for the commercially meaningful and fully resolved mixture of OPEN and CLOSED components.
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

    if ComponentState.UNRESOLVED in states:
        project_state = ProjectState.UNRESOLVED
    elif states == {ComponentState.CLOSED}:
        project_state = ProjectState.CLOSED
    elif states == {ComponentState.OPEN}:
        project_state = ProjectState.OPEN
    elif states == {ComponentState.OPEN, ComponentState.CLOSED}:
        project_state = ProjectState.PARTIAL
    else:
        project_state = ProjectState.UNRESOLVED

    return ProjectAssessment(
        operation_code=operation_code,
        state=project_state,
        cutoff_date=cutoff_date,
        components=components,
    )
