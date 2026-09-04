from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from procrun.collectors.opencoesione import OpenCoesioneBatch, OpenCoesioneOperation
from procrun.collectors.ted import TedCollectionResult
from procrun.domain import ComponentState, ProjectState
from procrun.production_delivery import (
    ProductionDeliveryError,
    build_live_runway_results,
    collect_complete_ted_italy,
    ted_italy_query,
)
from procrun.read_model import build_runway_read_model


def _batch() -> OpenCoesioneBatch:
    operation = OpenCoesioneOperation(
        operation_id="OP-1",
        cup="CUP1",
        operation_name="Water upgrade",
        operation_summary="New pumps.",
        start_date=date(2026, 1, 1),
        end_date=date(2027, 12, 31),
        total_cost_eur=Decimal("1000000"),
        eligible_expenditure_eur=Decimal("800000"),
        eu_cofinancing_rate=Decimal("0.6"),
        fund="FESR",
        specific_objective="OBJ",
        postcode="20100",
        country="IT",
        intervention_category="Water",
        list_updated_on=date(2026, 8, 31),
        source_url="https://opencoesione.gov.it/source.zip",
    )
    return OpenCoesioneBatch(
        operations=(operation,),
        observed_at=datetime(2026, 9, 4, 12, tzinfo=timezone.utc),
        source_url=operation.source_url,
        source_sha256="a" * 64,
        list_updated_on=operation.list_updated_on,
    )


def _ted(*, records: tuple[dict[str, object], ...]) -> TedCollectionResult:
    return TedCollectionResult(
        records=records,
        total_notice_count=len(records),
        pages_fetched=1,
        complete=True,
        stop_reason="complete",
    )


def test_ted_italy_query_is_bounded_to_program_and_cutoff() -> None:
    assert ted_italy_query(date(2026, 9, 4)) == (
        "buyer-country = ITA AND publication-date >= 20210101 "
        "AND publication-date <= 20260904"
    )


def test_incomplete_ted_universe_is_never_admitted(monkeypatch: pytest.MonkeyPatch) -> None:
    incomplete = TedCollectionResult(
        records=(),
        total_notice_count=10,
        pages_fetched=1,
        complete=False,
        stop_reason="missing_iteration_token",
    )
    monkeypatch.setattr(
        "procrun.production_delivery.collect_ted_notices", lambda *args, **kwargs: incomplete
    )
    with pytest.raises(ProductionDeliveryError, match="coverage is incomplete"):
        collect_complete_ted_italy(date(2026, 9, 4))


def test_complete_empty_ted_yields_exact_ted_scoped_open() -> None:
    result = build_live_runway_results(
        _batch(), _ted(records=()), cutoff_date=date(2026, 9, 4)
    )[0]
    model = build_runway_read_model(result)
    assert model.operation_code == "CUP1"
    assert model.state is ProjectState.OPEN
    assert model.components[0].state is ComponentState.OPEN
    assert model.components[0].state_explanation == (
        "No relevant procurement found in TED as of 2026-09-04."
    )
    assert "does not establish absence outside TED" in model.components[0].coverage_note


def test_exact_cup_plus_component_source_span_closes_component() -> None:
    record: dict[str, object] = {
        "notice_id": "12345-2026",
        "publication_date": "2026-02-01",
        "award_date": None,
        "contract_date": None,
        "title": "Supply of pumps",
        "scope_description": "Pumps for CUP1 water upgrade",
        "cpv_codes": ["42122000"],
        "contract_nature": "supplies",
        "procedure_type": "open",
        "procedure_value_eur": None,
        "estimated_value_eur": 500000,
        "base_value_eur": None,
        "awarded_value_eur": None,
        "place_of_performance": None,
        "nuts_code": "ITC4",
        "municipality": None,
        "project_reference": "CUP1",
        "source_url": "https://ted.europa.eu/en/notice/-/detail/12345-2026",
    }
    result = build_live_runway_results(
        _batch(), _ted(records=(record,)), cutoff_date=date(2026, 9, 4)
    )[0]
    model = build_runway_read_model(result)
    assert model.state is ProjectState.CLOSED
    component = model.components[0]
    assert component.state is ComponentState.CLOSED
    assert len(component.procurement_matches) == 1
    assert component.procurement_matches[0].project_reference == "CUP1"
    assert component.procurement_matches[0].evidence.text in {
        "Supply of pumps",
        "Pumps for CUP1 water upgrade",
    }
