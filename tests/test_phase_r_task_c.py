from procrun.component_engine import ComponentDomain, StructuredComponentSuggestion, StructuredSignalSource
from procrun.domain import FundingProject
from procrun.phase_r_phrase_expansion import TASK_C_RULE_VERSION, task_c_phrase_evidence


def _project(text: str) -> FundingProject:
    return FundingProject(
        operation_code="P1",
        project_scope_text=text,
        objective="RSO2.1 - Promuovere l'efficienza energetica",
        source_url="https://example.test/project",
    )


def _energy_signal() -> StructuredComponentSuggestion:
    return StructuredComponentSuggestion(
        domain=ComponentDomain.ENERGY_EFFICIENCY,
        label="Energy efficiency",
        source=StructuredSignalSource.SPECIFIC_OBJECTIVE,
        mapping_key="RSO2.1",
        source_value="RSO2.1 - Promuovere l'efficienza energetica",
    )


def test_task_c_accepts_exact_measured_phrase_with_compatible_structured_signal() -> None:
    text = "Lavori di efficientamento energetico della scuola primaria"
    evidence = task_c_phrase_evidence(_project(text), (_energy_signal(),))
    assert len(evidence) == 1
    assert evidence[0].text == "efficientamento energetico"
    assert text[evidence[0].start : evidence[0].end] == evidence[0].text
    assert evidence[0].rule_version == TASK_C_RULE_VERSION


def test_task_c_accepts_riqualificazione_energetica_case_insensitively() -> None:
    evidence = task_c_phrase_evidence(
        _project("RIQUALIFICAZIONE ENERGETICA edificio comunale"),
        (_energy_signal(),),
    )
    assert len(evidence) == 1
    assert evidence[0].phrase == "riqualificazione energetica"


def test_task_c_phrase_alone_never_counts_without_structured_signal() -> None:
    evidence = task_c_phrase_evidence(_project("efficientamento energetico"), ())
    assert evidence == ()


def test_task_c_does_not_promote_generic_corpus_tokens() -> None:
    for text in (
        "riqualificazione della scuola",
        "efficientamento del municipio",
        "ristrutturazione edificio scolastico",
        "lavori comunali",
    ):
        assert task_c_phrase_evidence(_project(text), (_energy_signal(),)) == ()


def test_task_c_rejects_incompatible_structured_domain() -> None:
    water_signal = StructuredComponentSuggestion(
        domain=ComponentDomain.WATER_WASTEWATER,
        label="Water and wastewater",
        source=StructuredSignalSource.SPECIFIC_OBJECTIVE,
        mapping_key="RSO2.5",
        source_value="RSO2.5",
    )
    assert task_c_phrase_evidence(_project("efficientamento energetico"), (water_signal,)) == ()
