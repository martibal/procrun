from procrun.component_engine import (
    COMPONENT_RULE_VERSION,
    ComponentDomain,
    cpv_matches_prefixes,
    extract_components,
)
from procrun.domain import FundingProject


def project(scope: str, operation_code: str = "PACS-FC-TEST") -> FundingProject:
    return FundingProject(
        operation_code=operation_code,
        project_scope_text=scope,
        source_url="https://example.invalid/project",
    )


def categories(result) -> set[str]:
    return {item.component.category for item in result.components}


def test_water_rules_extract_exact_source_spans() -> None:
    scope = (
        "A operação inclui bombas e válvulas. "
        "Prevê também automação e monitorização da instalação."
    )
    result = extract_components(project(scope), (ComponentDomain.WATER_WASTEWATER,))

    assert categories(result) == {
        "water_wastewater:pumps",
        "water_wastewater:valves",
        "water_wastewater:automation_control",
        "water_wastewater:monitoring",
    }
    assert result.model_fallback_required is False
    assert result.unmatched_scope_spans == ()
    for item in result.components:
        assert item.component.scope_evidence == item.evidence_spans[0].text
        for span in item.evidence_spans:
            assert scope[span.start : span.end] == span.text


def test_repeated_signalling_phrases_canonicalize_to_one_component() -> None:
    scope = (
        "A empreitada inclui sinalização ferroviária. "
        "A sinalização será renovada em toda a linha."
    )
    result = extract_components(project(scope), (ComponentDomain.RAIL_TRANSPORT,))
    signalling = [
        item
        for item in result.components
        if item.component.category == "rail_transport:signalling"
    ]

    assert len(signalling) == 1
    assert len(signalling[0].evidence_spans) == 2


def test_port_and_energy_domains_can_coexist() -> None:
    scope = (
        "O terminal receberá shore power e painéis fotovoltaicos. "
        "O edifício terá AVAC e iluminação LED."
    )
    result = extract_components(
        project(scope),
        (ComponentDomain.PORTS_COASTAL, ComponentDomain.ENERGY_EFFICIENCY),
    )

    assert "ports_coastal:shore_power" in categories(result)
    assert "ports_coastal:photovoltaic" in categories(result)
    assert "energy_efficiency:photovoltaic" in categories(result)
    assert "energy_efficiency:hvac" in categories(result)
    assert "energy_efficiency:lighting" in categories(result)


def test_no_rule_match_requests_model_fallback_without_guessing() -> None:
    result = extract_components(
        project("Intervenção técnica específica sem termos taxonómicos congelados."),
        (ComponentDomain.WATER_WASTEWATER,),
    )

    assert result.components == ()
    assert result.model_fallback_required is True
    assert len(result.unmatched_scope_spans) == 1
    assert result.rule_version == COMPONENT_RULE_VERSION


def test_component_ids_are_deterministic_across_runs() -> None:
    item = project("Instalação de bombas e válvulas.", operation_code="PT2030-123")
    first = extract_components(item, (ComponentDomain.WATER_WASTEWATER,))
    second = extract_components(item, (ComponentDomain.WATER_WASTEWATER,))

    assert [entry.component.component_id for entry in first.components] == [
        entry.component.component_id for entry in second.components
    ]


def test_phrase_boundaries_avoid_substring_false_positive() -> None:
    result = extract_components(
        project("The scheduled maintenance does not include new luminaires."),
        (ComponentDomain.ENERGY_EFFICIENCY,),
    )

    assert "energy_efficiency:lighting" not in categories(result)


def test_cpv_prefix_matching_uses_digits_and_hierarchy() -> None:
    result = extract_components(
        project("A operação inclui bombas."),
        (ComponentDomain.WATER_WASTEWATER,),
    )
    pumps = next(
        item for item in result.components if item.component.category.endswith(":pumps")
    )

    assert cpv_matches_prefixes("42122130-0", pumps.cpv_prefixes)
    assert not cpv_matches_prefixes("45234100-7", pumps.cpv_prefixes)


def test_domains_are_required_instead_of_inferred_from_free_text() -> None:
    try:
        extract_components(project("bombas"), ())
    except ValueError as exc:
        assert "at least one component domain" in str(exc)
    else:
        raise AssertionError("empty domains must fail closed")


def test_unmatched_sentence_requests_fallback_without_discarding_rule_matches() -> None:
    scope = "A operação inclui bombas. Inclui ainda uma intervenção técnica especial."
    result = extract_components(project(scope), (ComponentDomain.WATER_WASTEWATER,))

    assert "water_wastewater:pumps" in categories(result)
    assert result.model_fallback_required is True
    assert [span.text for span in result.unmatched_scope_spans] == [
        "Inclui ainda uma intervenção técnica especial."
    ]
