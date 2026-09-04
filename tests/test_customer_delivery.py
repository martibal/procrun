from datetime import date

import pytest

from procrun.component_engine import ComponentDomain, extract_components
from procrun.customer_delivery import (
    DeliveryInvariantError,
    SupplierProfile,
    build_opportunity_feed,
    export_runway_csv,
)
from procrun.domain import FundingProject
from procrun.read_model import build_runway_read_model
from procrun.runway import ComponentCoverage, assess_project_runway


def _public_project():
    project = FundingProject(
        operation_code="IT-DELIVERY-1",
        project_title="Pump modernization",
        project_start=date(2026, 1, 1),
        project_end=date(2027, 12, 31),
        approved_funding_eur=900_000,
        project_scope_text="Installation of pumps.",
        programme="PR FESR Lombardia 2021-2027",
        region="Lombardia",
        source_url="https://example.test/project",
    )
    extracted = extract_components(project, (ComponentDomain.WATER_WASTEWATER,))
    component_id = extracted.components[0].component.component_id
    result = assess_project_runway(
        project,
        domains=(ComponentDomain.WATER_WASTEWATER,),
        cutoff_date=date(2026, 9, 4),
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
    return build_runway_read_model(result)


def test_feed_uses_profile_only_for_relevance_not_state() -> None:
    project = _public_project()
    profile = SupplierProfile(
        account_subject="acct_1",
        organization_name="Pump Supplier S.p.A.",
        country_code="ITA",
        component_categories=("water_wastewater:pumps",),
    )
    feed = build_opportunity_feed((project,), profile)
    assert len(feed) == 1
    assert feed[0].state == project.state
    assert feed[0].matched_categories == ("water_wastewater:pumps",)
    assert feed[0].content_hash == project.content_hash


def test_csv_is_deterministic_customer_safe_and_ted_scoped() -> None:
    project = _public_project()
    first = export_runway_csv((project,))
    second = export_runway_csv((project,))
    assert first == second
    assert "No relevant procurement found in TED as of 2026-09-04." in first
    lowered = first.casefold()
    for forbidden in ("beneficiary", "contact", "buyer", "raw_response"):
        assert forbidden not in lowered


def test_delivery_rejects_broadened_open_copy() -> None:
    project = _public_project()
    bad_component = project.components[0].model_copy(
        update={"state_explanation": "No procurement found."}
    )
    bad = project.model_copy(update={"components": (bad_component,)})
    with pytest.raises(DeliveryInvariantError, match="TED-scoped"):
        export_runway_csv((bad,))
