from __future__ import annotations

from datetime import date

import pytest

from procrun.domain import ComponentState, ProjectState
from procrun.read_model import (
    ReadModelInvariantError,
    RunwayComponent,
    SourceSpan,
    unresolved_source_evidence,
)


def _component(
    component_id: str,
    state: ComponentState,
    *,
    text: str,
    start: int,
) -> RunwayComponent:
    span = SourceSpan(
        source_field="project_scope_text",
        text=text,
        start=start,
        end=start + len(text),
    )
    return RunwayComponent(
        component_id=component_id,
        category="test-category",
        label="test component",
        state=state,
        cutoff_date=date(2026, 9, 10),
        project_evidence=span,
        procurement_matches=(),
        coverage_note="test coverage",
        state_explanation="test explanation",
    )


def test_unresolved_project_exposes_only_unresolved_component_source_text() -> None:
    unresolved = _component(
        "c1",
        ComponentState.UNRESOLVED,
        text="Il progetto prevede la fornitura e installazione di nuovi impianti.",
        start=12,
    )
    closed = _component(
        "c2",
        ComponentState.CLOSED,
        text="Sono conclusi i lavori civili.",
        start=100,
    )

    evidence = unresolved_source_evidence(ProjectState.UNRESOLVED, (unresolved, closed))

    assert evidence == (unresolved.project_evidence,)
    assert evidence[0].text == (
        "Il progetto prevede la fornitura e installazione di nuovi impianti."
    )


def test_duplicate_source_span_is_exposed_once() -> None:
    text = "È prevista una procedura per la fornitura delle apparecchiature."
    first = _component("c1", ComponentState.UNRESOLVED, text=text, start=20)
    second = _component("c2", ComponentState.UNRESOLVED, text=text, start=20)

    evidence = unresolved_source_evidence(ProjectState.UNRESOLVED, (first, second))

    assert evidence == (first.project_evidence,)


def test_resolved_project_does_not_expose_unresolved_column_text() -> None:
    component = _component(
        "c1",
        ComponentState.OPEN,
        text="È prevista una fornitura.",
        start=0,
    )

    assert unresolved_source_evidence(ProjectState.OPEN, (component,)) == ()


def test_unresolved_project_without_unresolved_component_fails_closed() -> None:
    component = _component(
        "c1",
        ComponentState.OPEN,
        text="È prevista una fornitura.",
        start=0,
    )

    with pytest.raises(
        ReadModelInvariantError,
        match="UNRESOLVED project must expose at least one unresolved component source span",
    ):
        unresolved_source_evidence(ProjectState.UNRESOLVED, (component,))
