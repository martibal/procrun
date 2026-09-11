from procrun.component_engine import (
    ComponentDomain,
    StructuredComponentSuggestion,
    StructuredSignalSource,
)
from procrun.domain import FundingProject
from procrun.italian_normalization import (
    ITALIAN_NORMALIZATION_VERSION,
    normalize_italian_text,
    normalize_italian_token,
)
from procrun.phase_r_morphology import TASK_D_RULE_VERSION, task_d_morphology_evidence


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


def test_normalization_is_versioned_and_deterministic() -> None:
    text = "Riqualificazioni energetiche"
    first = normalize_italian_text(text)
    second = normalize_italian_text(text)
    assert first == second == ("riqualific", "energet")
    assert ITALIAN_NORMALIZATION_VERSION == "italian-morphology-v1"


def test_normalization_reduces_gender_and_number() -> None:
    assert normalize_italian_token("energetico") == "energet"
    assert normalize_italian_token("energetica") == "energet"
    assert normalize_italian_token("energetici") == "energet"
    assert normalize_italian_token("energetiche") == "energet"


def test_normalization_reduces_administrative_verb_family() -> None:
    assert normalize_italian_token("riqualificare") == "riqualific"
    assert normalize_italian_token("riqualificato") == "riqualific"
    assert normalize_italian_token("riqualificata") == "riqualific"
    assert normalize_italian_token("riqualificazione") == "riqualific"


def test_task_d_matches_inflected_source_and_recovers_exact_offsets() -> None:
    text = "Interventi per riqualificazioni energetiche degli edifici pubblici."
    evidence = task_d_morphology_evidence(_project(text), (_energy_signal(),))
    assert len(evidence) == 1
    assert evidence[0].text == "riqualificazioni energetiche"
    assert text[evidence[0].start : evidence[0].end] == evidence[0].text
    assert evidence[0].normalized_source == evidence[0].normalized_rule
    assert evidence[0].rule_version == TASK_D_RULE_VERSION


def test_task_d_normalizes_rule_and_source_not_only_one_side() -> None:
    evidence = task_d_morphology_evidence(
        _project("RIQUALIFICATO ENERGETICO edificio comunale"),
        (_energy_signal(),),
    )
    assert len(evidence) == 1
    assert evidence[0].normalized_rule == ("riqualific", "energet")
    assert evidence[0].normalized_source == ("riqualific", "energet")


def test_task_d_requires_compatible_structured_signal() -> None:
    assert task_d_morphology_evidence(_project("riqualificazioni energetiche"), ()) == ()


def test_task_d_rejects_incompatible_structured_domain() -> None:
    water_signal = StructuredComponentSuggestion(
        domain=ComponentDomain.WATER_WASTEWATER,
        label="Water",
        source=StructuredSignalSource.SPECIFIC_OBJECTIVE,
        mapping_key="RSO2.5",
        source_value="RSO2.5",
    )
    assert (
        task_d_morphology_evidence(
            _project("riqualificazioni energetiche"),
            (water_signal,),
        )
        == ()
    )
