from procrun.domain import FundingProject
from procrun.read_model import SourceEvidenceType, _project_source_evidence


def test_programme_objective_never_replaces_weak_project_title_as_evidence() -> None:
    project = FundingProject(
        operation_code="A21A-WEAK-TITLE",
        project_title="Intervento Attuativo",
        project_scope_text="Intervento Attuativo",
        objective="RSO1.2-Cogliere i vantaggi della digitalizzazione",
        source_url="https://example.invalid/approved-source",
    )

    evidence = _project_source_evidence(project)

    assert evidence.source_type is SourceEvidenceType.PROJECT_TITLE
    assert evidence.text == "Intervento Attuativo"
    assert project.objective not in evidence.text


def test_programme_objective_does_not_upgrade_title_to_description() -> None:
    project = FundingProject(
        operation_code="A21A-BRAND-TITLE",
        project_title="TECHWOOD",
        project_scope_text="TECHWOOD",
        objective="RSO1.3-Crescita sostenibile e competitività delle PMI",
        source_url="https://example.invalid/approved-source",
    )

    evidence = _project_source_evidence(project)

    assert evidence.source_type is SourceEvidenceType.PROJECT_TITLE
    assert evidence.text == project.project_title
