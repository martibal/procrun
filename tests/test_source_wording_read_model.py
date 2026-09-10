import pytest

from procrun.domain import FundingProject
from procrun.read_model import (
    ReadModelInvariantError,
    SourceEvidenceType,
    _project_source_evidence,
)


def _project(*, title: str | None, scope: str) -> FundingProject:
    return FundingProject(
        operation_code="TEST-SOURCE-WORDING",
        project_title=title,
        project_scope_text=scope,
        source_url="https://example.invalid/project/TEST-SOURCE-WORDING",
    )


def test_identical_scope_and_title_are_exposed_once_as_project_title() -> None:
    project = _project(
        title="Realizzazione impianto fotovoltaico",
        scope="Realizzazione impianto fotovoltaico",
    )

    evidence = _project_source_evidence(project)

    assert evidence.source_type is SourceEvidenceType.PROJECT_TITLE
    assert evidence.source_field == "project_scope_text"
    assert evidence.text == project.project_title
    assert project.project_scope_text[evidence.start : evidence.end] == evidence.text
    assert evidence.source_url == project.source_url


def test_distinct_scope_is_truthfully_labeled_project_description() -> None:
    project = _project(
        title="Modernizzazione rete idrica",
        scope="Il progetto prevede nuove pompe e sistemi di controllo per la rete idrica.",
    )

    evidence = _project_source_evidence(project)

    assert evidence.source_type is SourceEvidenceType.PROJECT_DESCRIPTION
    assert evidence.text == project.project_scope_text
    assert project.project_scope_text[evidence.start : evidence.end] == evidence.text


def test_source_wording_offsets_preserve_exact_trimmed_span() -> None:
    project = _project(
        title="Realizzazione impianto fotovoltaico",
        scope="  Realizzazione impianto fotovoltaico  ",
    )

    evidence = _project_source_evidence(project)

    assert evidence.source_type is SourceEvidenceType.PROJECT_TITLE
    assert evidence.start == 2
    assert evidence.end == len(project.project_scope_text) - 2
    assert project.project_scope_text[evidence.start : evidence.end] == evidence.text


def test_empty_source_wording_fails_closed() -> None:
    project = _project(title="Titolo", scope="   ")

    with pytest.raises(ReadModelInvariantError, match="source wording is empty"):
        _project_source_evidence(project)
