from datetime import date

from procrun.component_engine import ComponentDomain, extract_components
from procrun.domain import ComponentState, FundingProject, ProjectState
from procrun.runway import ComponentCoverage, assess_project_runway


def test_unmatched_project_scope_does_not_poison_resolved_component() -> None:
    project = FundingProject(
        operation_code="IT-TEST-001",
        project_title="LED lighting and charging infrastructure",
        approved_funding_eur=100_000,
        project_scope_text=(
            "Replacement of existing lighting with LED lighting. "
            "Installation of charging infrastructure for service vehicles."
        ),
        programme="PR FESR Lombardia 2021-2027",
        region="Lombardia",
        source_url="https://example.invalid/project",
    )

    extraction = extract_components(project, (ComponentDomain.ENERGY_EFFICIENCY,))
    assert extraction.model_fallback_required is True
    lighting = next(
        item.component
        for item in extraction.components
        if item.component.category == "energy_efficiency:lighting"
    )
    coverage = ComponentCoverage(
        required_source_ids=frozenset({"ted_search_api"}),
        complete_source_ids=frozenset({"ted_search_api"}),
        boundary_resolved=True,
        note="Complete TED query universe through cutoff.",
    )

    result = assess_project_runway(
        project,
        domains=(ComponentDomain.ENERGY_EFFICIENCY,),
        cutoff_date=date(2026, 9, 8),
        evidence_by_component={lighting.component_id: ()},
        coverage_by_component={lighting.component_id: coverage},
    )

    assert len(result.components) == 1
    assert result.components[0].match.assessment.state is ComponentState.OPEN
    assert result.assessment.state is ProjectState.UNRESOLVED


def test_specific_grouped_component_boundary_still_withholds() -> None:
    project = FundingProject(
        operation_code="IT-TEST-002",
        project_title="Rail crossing works",
        approved_funding_eur=1_000_000,
        project_scope_text=(
            "Suppression of 2 passagens de nível: PK 60+090 and PK 66+019."
        ),
        programme="Test",
        region="Lombardia",
        source_url="https://example.invalid/project-2",
    )

    extraction = extract_components(project, (ComponentDomain.RAIL_TRANSPORT,))
    crossing = next(
        item.component
        for item in extraction.components
        if item.component.category == "rail_transport:crossings"
    )
    coverage = ComponentCoverage(
        required_source_ids=frozenset({"ted_search_api"}),
        complete_source_ids=frozenset({"ted_search_api"}),
        boundary_resolved=True,
        note="Complete TED query universe through cutoff.",
    )

    result = assess_project_runway(
        project,
        domains=(ComponentDomain.RAIL_TRANSPORT,),
        cutoff_date=date(2026, 9, 8),
        evidence_by_component={crossing.component_id: ()},
        coverage_by_component={crossing.component_id: coverage},
    )

    assert result.components[0].match.assessment.state is ComponentState.UNRESOLVED
    assert result.assessment.state is ProjectState.UNRESOLVED
