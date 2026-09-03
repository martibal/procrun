from datetime import date

import pytest

from procrun.component_engine import ComponentDomain, extract_components
from procrun.domain import ComponentState, FundingProject, ProcurementEvidence, ProjectState
from procrun.read_model import build_runway_read_model
from procrun.runway import ComponentCoverage, RunwayInvariantError, assess_project_runway

PROJECT = FundingProject(
    operation_code="PRR-C02-I01-TEST",
    project_title="Modernizacao da rede de agua",
    project_start=date(2026, 1, 1),
    project_end=date(2026, 12, 31),
    approved_funding_eur=5_000_000,
    project_scope_text=(
        "Instalacao de bombas e sistemas de bombagem na rede. "
        "Substituicao de válvulas nos principais trocos."
    ),
    programme="PRR",
    region="Lisboa",
    nuts_code="PT17",
    source_url="https://example.invalid/project/PRR-C02-I01-TEST",
)
CUTOFF = date(2026, 9, 1)


def _components():
    result = extract_components(PROJECT, (ComponentDomain.WATER_WASTEWATER,))
    return {item.component.category: item.component for item in result.components}


def _pump_evidence(component_id: str) -> ProcurementEvidence:
    return ProcurementEvidence(
        evidence_id="ted-123-pumps",
        component_id=component_id,
        notice_id="123456-2026",
        publication_date=date(2026, 6, 1),
        title="Equipamentos para modernizacao da rede de agua",
        scope_description="Fornecimento de bombas e sistemas de bombagem para a rede.",
        cpv_codes=("42122000",),
        estimated_value_eur=850_000,
        nuts_code="PT170",
        project_reference=PROJECT.operation_code,
        source_url="https://ted.europa.eu/en/notice/-/detail/123456-2026",
    )


def _coverage(ids: tuple[str, ...], *, complete: bool = True):
    return {
        component_id: ComponentCoverage(
            complete=complete,
            boundary_resolved=True,
            note="TED iteration complete through cutoff." if complete else "TED coverage incomplete.",
        )
        for component_id in ids
    }


def test_end_to_end_runway_produces_exact_evidence_and_stable_safe_read_model() -> None:
    components = _components()
    pump = components["water_wastewater:pumps"]
    valve = components["water_wastewater:valves"]
    coverage = _coverage((pump.component_id, valve.component_id))

    result = assess_project_runway(
        PROJECT,
        domains=(ComponentDomain.WATER_WASTEWATER,),
        cutoff_date=CUTOFF,
        evidence_by_component={pump.component_id: (_pump_evidence(pump.component_id),)},
        coverage_by_component=coverage,
    )
    public = build_runway_read_model(result)
    repeated = build_runway_read_model(result)

    by_category = {item.category: item for item in public.components}
    assert by_category["water_wastewater:pumps"].state is ComponentState.CLOSED
    assert by_category["water_wastewater:valves"].state is ComponentState.OPEN
    assert public.state is ProjectState.PARTIAL
    assert public.content_hash == repeated.content_hash
    assert len(public.content_hash) == 64

    pump_public = by_category["water_wastewater:pumps"]
    assert len(pump_public.procurement_matches) == 1
    procurement_span = pump_public.procurement_matches[0].evidence
    assert procurement_span.source_field == "scope_description"
    assert "bombas" in procurement_span.text.casefold()
    source = _pump_evidence(pump.component_id).scope_description
    assert source is not None
    assert source[procurement_span.start : procurement_span.end] == procurement_span.text

    project_span = pump_public.project_evidence
    assert PROJECT.project_scope_text[project_span.start : project_span.end] == project_span.text

    serialized = public.model_dump(mode="json")
    forbidden_names = {
        "buyer_name",
        "buyer-name",
        "contracting_authority_name",
        "beneficiary",
        "contact_person",
        "email",
        "phone",
        "iterationNextToken",
        "raw_response",
    }

    def walk(value: object) -> None:
        if isinstance(value, dict):
            assert not forbidden_names.intersection(value)
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(serialized)


def test_incomplete_coverage_can_never_create_open() -> None:
    components = _components()
    ids = tuple(component.component_id for component in components.values())
    result = assess_project_runway(
        PROJECT,
        domains=(ComponentDomain.WATER_WASTEWATER,),
        cutoff_date=CUTOFF,
        evidence_by_component={},
        coverage_by_component=_coverage(ids, complete=False),
    )
    assert all(
        item.match.assessment.state is ComponentState.UNRESOLVED for item in result.components
    )
    assert result.assessment.state is ProjectState.UNRESOLVED


def test_missing_explicit_coverage_fails_before_a_state_is_built() -> None:
    with pytest.raises(RunwayInvariantError, match="explicit procurement coverage"):
        assess_project_runway(
            PROJECT,
            domains=(ComponentDomain.WATER_WASTEWATER,),
            cutoff_date=CUTOFF,
            evidence_by_component={},
            coverage_by_component={},
        )


def test_exact_project_reference_without_component_text_cannot_close_component() -> None:
    components = _components()
    pump = components["water_wastewater:pumps"]
    evidence = _pump_evidence(pump.component_id).model_copy(
        update={"scope_description": "Trabalhos gerais sem referencia ao equipamento."}
    )
    coverage = _coverage(tuple(item.component_id for item in components.values()))
    result = assess_project_runway(
        PROJECT,
        domains=(ComponentDomain.WATER_WASTEWATER,),
        cutoff_date=CUTOFF,
        evidence_by_component={pump.component_id: (evidence,)},
        coverage_by_component=coverage,
    )
    pump_result = next(
        item for item in result.components if item.extracted.component.component_id == pump.component_id
    )
    assert pump_result.match.assessment.state is ComponentState.OPEN
