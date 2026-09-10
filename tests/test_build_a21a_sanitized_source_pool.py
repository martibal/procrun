from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timezone

import pytest

from procrun.collectors.opencoesione import OpenCoesioneBatch, OpenCoesioneOperation
from scripts import build_a21a_sanitized_source_pool as builder
from scripts.validate_a21a_sanitized_source_pool import validate


def _operation() -> OpenCoesioneOperation:
    return OpenCoesioneOperation(
        operation_id="ITC4-001",
        cup="A11B22000010001",
        operation_name="Riqualificazione energetica edificio pubblico",
        operation_summary="Intervento di efficientamento energetico dell'edificio pubblico.",
        start_date=None,
        end_date=None,
        total_cost_eur=None,
        eligible_expenditure_eur=None,
        eu_cofinancing_rate=None,
        fund="FESR",
        specific_objective=None,
        postcode=None,
        country="IT",
        intervention_category=None,
        list_updated_on=date(2026, 8, 31),
        source_url="https://opencoesione.gov.it/it/opendata/beneficiari/2021-2027/beneficiari_PR_FESR_LOMBARDIA.zip",
    )


def _batch(*operations: OpenCoesioneOperation) -> OpenCoesioneBatch:
    rows = operations or (_operation(),)
    return OpenCoesioneBatch(
        operations=tuple(rows),
        observed_at=datetime(2026, 9, 10, tzinfo=timezone.utc),
        source_url=rows[0].source_url,
        source_sha256="a" * 64,
        list_updated_on=date(2026, 8, 31),
    )


def test_builder_emits_valid_prebuilt_sanitized_resource(monkeypatch) -> None:
    monkeypatch.setattr(builder, "collect_open_coesione_live", _batch)
    document = builder.build_source_pool()

    assert document["pii_review_status"] == "ZERO_PII_CONFIRMED"
    assert document["engine_output_present"] is False
    provenance = document["sanitization_provenance"]
    assert provenance["transport_kind"] == "prebuilt_sanitized_resource"
    assert provenance["download_then_filter_used"] is False
    assert provenance["publisher_resource_sha256"] == "a" * 64
    assert provenance["publisher_zero_pii_contract"] == "opencoesione-art49-minimum-rgs-v1"

    cases = document["cases"]
    assert cases == [
        {
            "operation_code": "ITC4-001",
            "project_title": "Riqualificazione energetica edificio pubblico",
            "project_scope_text": "Intervento di efficientamento energetico dell'edificio pubblico.",
            "region": "Lombardia",
            "municipality": None,
            "nuts_code": "ITC4",
            "source_url": _batch().source_url,
            "language": "it",
        }
    ]
    assert validate(document)["ingress_pass"] is True


def test_exact_duplicate_source_rows_are_collapsed(monkeypatch) -> None:
    operation = _operation()
    monkeypatch.setattr(builder, "collect_open_coesione_live", lambda: _batch(operation, operation))
    document = builder.build_source_pool()
    assert len(document["cases"]) == 1
    assert validate(document)["ingress_pass"] is True


def test_conflicting_duplicate_source_rows_fail_closed(monkeypatch) -> None:
    operation = _operation()
    conflict = replace(operation, operation_summary="Conflicting source wording")
    monkeypatch.setattr(builder, "collect_open_coesione_live", lambda: _batch(operation, conflict))
    with pytest.raises(RuntimeError, match="conflicting OpenCoesione rows"):
        builder.build_source_pool()
