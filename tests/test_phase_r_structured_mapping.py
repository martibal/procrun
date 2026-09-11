from procrun.component_engine import (
    ComponentDomain,
    structured_component_suggestions,
)
from procrun.domain import FundingProject
from procrun.eu_objective_mapping import MAPPING_VERSION, mappings_for


def _project(*, objective: str | None = None, theme: str | None = None) -> FundingProject:
    return FundingProject(
        operation_code="P1",
        project_scope_text="Testo senza frase di acquisto riconosciuta.",
        objective=objective,
        theme=theme,
        source_url="https://example.invalid/project",
    )


def test_rso21_maps_only_to_energy_efficiency() -> None:
    found = structured_component_suggestions(
        _project(objective="RSO2.1-Promuovere l'efficienza energetica"),
        tuple(ComponentDomain),
    )
    assert [(item.domain, item.mapping_key) for item in found] == [
        (ComponentDomain.ENERGY_EFFICIENCY, "RSO2.1")
    ]
    assert found[0].mapping_version == MAPPING_VERSION


def test_rso24_is_not_mapped_because_it_is_too_broad() -> None:
    assert structured_component_suggestions(
        _project(objective="RSO2.4-Promuovere l'adattamento ai cambiamenti climatici"),
        tuple(ComponentDomain),
    ) == ()


def test_fire_intervention_code_maps_to_fire_resilience() -> None:
    found = structured_component_suggestions(
        _project(theme="059 - rischi climatici: incendi"),
        tuple(ComponentDomain),
    )
    assert len(found) == 1
    assert found[0].domain is ComponentDomain.RESILIENCE_FIRE
    assert found[0].source_value == "059 - rischi climatici: incendi"


def test_rail_and_port_codes_are_distinct() -> None:
    rail = mappings_for(specific_objective=None, intervention_category="105 - ERTMS")
    port = mappings_for(specific_objective=None, intervention_category="110 - porti marittimi TEN-T")
    assert rail[0].domain == "rail_transport"
    assert port[0].domain == "ports_coastal"


def test_unknown_structured_values_never_create_suggestion() -> None:
    assert structured_component_suggestions(
        _project(objective="RSO1.3-Crescita PMI", theme="001 - ricerca"),
        tuple(ComponentDomain),
    ) == ()


def test_domain_filter_is_respected() -> None:
    found = structured_component_suggestions(
        _project(theme="065 - trattamento acque reflue"),
        [ComponentDomain.RAIL_TRANSPORT],
    )
    assert found == ()
