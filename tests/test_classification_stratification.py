from datetime import date

import pytest
from pydantic import ValidationError

from procrun.classification_stratification import (
    ComponentCountBand,
    DescriptionPrecisionBand,
    ProcurementBand,
    ScopeLengthBand,
    StratificationError,
    StratificationRecord,
    select_stratified_benchmark,
)
from procrun.domain import FundingProject, ProjectState


def _project(code: str, i: int) -> FundingProject:
    return FundingProject(
        operation_code=code,
        project_title=f"Project {i}",
        project_start=date(2025, 1, 1),
        approved_funding_eur=1000 + i,
        project_scope_text=f"Scope {i}",
        fund="FESR",
        programme="PR FESR Lombardia 2021-2027",
        objective=None,
        theme=None,
        region="Lombardia",
        municipality=None,
        nuts_code="ITC4",
        source_url="https://example.test/source.zip",
    )


def _records() -> tuple[StratificationRecord, ...]:
    domains = (
        "water_wastewater",
        "rail_transport",
        "ports_coastal",
        "energy_efficiency",
        "resilience_fire",
    )
    component_counts = (
        ComponentCountBand.ZERO,
        ComponentCountBand.ONE,
        ComponentCountBand.MULTI,
        ComponentCountBand.AMBIGUOUS,
    )
    rows = []
    for i in range(16):
        component_count = component_counts[i % len(component_counts)]
        record_domains = () if component_count is ComponentCountBand.ZERO else (
            domains[i % len(domains)],
        )
        rows.append(
            StratificationRecord(
                operation_code=f"OP-{i:02d}",
                domains=record_domains,
                scope_length_band=(
                    ScopeLengthBand.SHORT if i % 2 == 0 else ScopeLengthBand.LONG
                ),
                component_count_band=component_count,
                procurement_band=(
                    ProcurementBand.KNOWN_PROCUREMENT,
                    ProcurementBand.NO_RELEVANT_TED_FOUND,
                    ProcurementBand.AMBIGUOUS_CANDIDATE,
                )[i % 3],
                expected_project_state=(
                    ProjectState.UNRESOLVED
                    if component_count in {ComponentCountBand.ZERO, ComponentCountBand.AMBIGUOUS}
                    else ProjectState.CLOSED
                ),
                geography="Lombardia" if i < 8 else "Sardegna",
                size_band="SMALL" if i % 2 == 0 else "LARGE",
                time_band="EARLY" if i < 8 else "LATE",
                description_precision_band=(
                    DescriptionPrecisionBand.HIGH
                    if i % 2 == 0
                    else DescriptionPrecisionBand.LOW
                ),
                rationale="Independent screening rationale",
            )
        )
    return tuple(rows)


def test_stratified_selection_is_deterministic_and_covers_required_strata() -> None:
    records = _records()
    projects = tuple(_project(record.operation_code, i) for i, record in enumerate(records))

    first = select_stratified_benchmark(
        projects,
        records,
        selection_seed="round-001",
        target_size=12,
    )
    second = select_stratified_benchmark(
        tuple(reversed(projects)),
        tuple(reversed(records)),
        selection_seed="round-001",
        target_size=12,
    )

    assert [p.operation_code for p in first.projects] == [
        p.operation_code for p in second.projects
    ]
    assert len(first.projects) == 12
    counts = {record.component_count_band for record in first.records}
    assert counts == {
        ComponentCountBand.ZERO,
        ComponentCountBand.ONE,
        ComponentCountBand.MULTI,
        ComponentCountBand.AMBIGUOUS,
    }


def test_missing_domain_fails_closed() -> None:
    records = tuple(
        record.model_copy(
            update={
                "domains": tuple(
                    domain for domain in record.domains if domain != "ports_coastal"
                )
            }
        )
        for record in _records()
    )
    projects = tuple(_project(record.operation_code, i) for i, record in enumerate(records))

    with pytest.raises(StratificationError, match="missing supported domains"):
        select_stratified_benchmark(
            projects,
            records,
            selection_seed="round-001",
            target_size=12,
        )


def test_record_set_must_match_screening_pool_exactly() -> None:
    records = _records()
    projects = tuple(_project(record.operation_code, i) for i, record in enumerate(records[:-1]))

    with pytest.raises(StratificationError, match="exactly one stratification record"):
        select_stratified_benchmark(
            projects,
            records,
            selection_seed="round-001",
            target_size=12,
        )


def test_zero_component_count_cannot_claim_supported_domain() -> None:
    with pytest.raises(ValidationError, match="ZERO component-count"):
        StratificationRecord(
            operation_code="OP-ZERO",
            domains=("energy_efficiency",),
            scope_length_band=ScopeLengthBand.SHORT,
            component_count_band=ComponentCountBand.ZERO,
            procurement_band=ProcurementBand.AMBIGUOUS_CANDIDATE,
            expected_project_state=ProjectState.UNRESOLVED,
            geography="Lombardia",
            size_band="SMALL",
            time_band="LATE",
            description_precision_band=DescriptionPrecisionBand.LOW,
            rationale="No defensible component",
        )
