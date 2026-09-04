from datetime import date

from procrun.component_engine import ComponentDomain, extract_components
from procrun.domain import ComponentState, FundingProject
from procrun.read_model import build_runway_read_model
from procrun.runway import ComponentCoverage, assess_project_runway


def test_canonical_open_explanation_is_exactly_ted_scoped() -> None:
    project = FundingProject(
        operation_code="IT-TEST-1",
        project_title="Water network upgrade",
        project_start=date(2026, 1, 1),
        project_end=date(2027, 12, 31),
        approved_funding_eur=1_000_000,
        project_scope_text="Installation of pumps.",
        programme="test",
        region="Lombardia",
        source_url="https://example.test/project",
    )
    extracted = extract_components(project, (ComponentDomain.WATER_WASTEWATER,))
    assert len(extracted.components) == 1
    component_id = extracted.components[0].component.component_id
    cutoff = date(2026, 9, 4)
    result = assess_project_runway(
        project,
        domains=(ComponentDomain.WATER_WASTEWATER,),
        cutoff_date=cutoff,
        evidence_by_component={},
        coverage_by_component={
            component_id: ComponentCoverage(
                required_source_ids=frozenset({"ted_search_api"}),
                complete_source_ids=frozenset({"ted_search_api"}),
                boundary_resolved=True,
                note="Coverage: TED.",
            )
        },
    )
    public = build_runway_read_model(result)
    component = public.components[0]
    assert component.state is ComponentState.OPEN
    assert component.state_explanation == "No relevant procurement found in TED as of 2026-09-04."
    assert "approved indexed sources" not in public.model_dump_json()
