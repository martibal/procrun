from datetime import date
from decimal import Decimal

import pytest

from procrun.collectors.opencoesione import OpenCoesioneOperation
from procrun.domain import FundingProject
from scripts.export_a21_project_universe import _a21_projects


def _operation(
    *,
    local_id: str = "CUP-1---100",
    cup: str = "CUP-1",
    eligible: str = "1000.00",
) -> OpenCoesioneOperation:
    return OpenCoesioneOperation(
        operation_id=local_id,
        cup=cup,
        operation_name="Example operation",
        operation_summary="Example scope",
        start_date=date(2025, 1, 1),
        end_date=None,
        total_cost_eur=Decimal(eligible),
        eligible_expenditure_eur=Decimal(eligible),
        eu_cofinancing_rate=None,
        fund="ERDF",
        specific_objective="objective",
        postcode=None,
        country="IT",
        intervention_category="category",
        list_updated_on=date(2026, 9, 9),
        source_url="https://example.test/source.zip",
    )


def _project(operation_code: str = "CUP-1") -> FundingProject:
    return FundingProject(
        operation_code=operation_code,
        project_title="Example operation",
        project_start=date(2025, 1, 1),
        approved_funding_eur=1000,
        project_scope_text="Example scope",
        fund="ERDF",
        programme="PR FESR Lombardia 2021-2027",
        objective="objective",
        theme="category",
        region="Lombardia",
        nuts_code="ITC4",
        source_url="https://example.test/source.zip",
    )


def test_a21_uses_local_operation_identifier_and_collapses_exact_duplicates() -> None:
    operation = _operation()
    projects = _a21_projects(
        (operation, operation),
        (_project(), _project()),
    )

    assert len(projects) == 1
    assert projects[0].operation_code == "CUP-1---100"


def test_a21_fails_closed_on_conflicting_rows_for_same_local_identifier() -> None:
    first = _operation()
    second = _operation(eligible="2000.00")

    with pytest.raises(RuntimeError, match="conflicting OpenCoesione rows"):
        _a21_projects(
            (first, second),
            (_project(), _project()),
        )
