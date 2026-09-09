from __future__ import annotations

import pytest

from procrun.component_engine import EvidenceSpan
from procrun.domain import ProjectState
from procrun.read_model import ReadModelInvariantError, unresolved_source_evidence


def _span(source: str, text: str) -> EvidenceSpan:
    start = source.index(text)
    return EvidenceSpan(
        start=start,
        end=start + len(text),
        text=text,
        matched_phrases=(),
    )


def test_unresolved_project_exposes_exact_unmatched_source_text() -> None:
    source = (
        "Installazione di pompe e valvole. "
        "Sono previste inoltre ulteriori apparecchiature tecniche da definire."
    )
    unresolved_text = "Sono previste inoltre ulteriori apparecchiature tecniche da definire."

    evidence = unresolved_source_evidence(
        ProjectState.UNRESOLVED,
        source,
        (_span(source, unresolved_text),),
    )

    assert len(evidence) == 1
    assert evidence[0].text == unresolved_text
    assert source[evidence[0].start : evidence[0].end] == evidence[0].text


def test_unresolved_for_non_text_reason_does_not_invent_project_text_cause() -> None:
    source = "Installazione di pompe e valvole."

    assert unresolved_source_evidence(ProjectState.UNRESOLVED, source, ()) == ()


def test_resolved_project_does_not_expose_unmatched_text() -> None:
    source = "Intervento tecnico da definire."
    span = _span(source, source)

    assert unresolved_source_evidence(ProjectState.OPEN, source, (span,)) == ()


def test_duplicate_unmatched_span_is_exposed_once() -> None:
    source = "Intervento tecnico da definire."
    span = _span(source, source)

    evidence = unresolved_source_evidence(ProjectState.UNRESOLVED, source, (span, span))

    assert len(evidence) == 1
    assert evidence[0].text == source


def test_mismatched_span_fails_closed() -> None:
    source = "Testo sorgente corretto."
    invalid = EvidenceSpan(
        start=0,
        end=5,
        text="Altro",
        matched_phrases=(),
    )

    with pytest.raises(
        ReadModelInvariantError,
        match="must match the exact project source span",
    ):
        unresolved_source_evidence(ProjectState.UNRESOLVED, source, (invalid,))
