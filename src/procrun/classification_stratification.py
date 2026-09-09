"""Independent stratification contract for the final A21 product benchmark."""

from __future__ import annotations

import hashlib
from enum import StrEnum
from typing import Final

from pydantic import BaseModel, ConfigDict, model_validator

from procrun.domain import FundingProject, ProjectState

SUPPORTED_COMPONENT_DOMAINS: Final[tuple[str, ...]] = (
    "water_wastewater",
    "rail_transport",
    "ports_coastal",
    "energy_efficiency",
    "resilience_fire",
)


class StratificationError(ValueError):
    """Raised when a proposed final A21 benchmark is not genuinely stratified."""


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ScopeLengthBand(StrEnum):
    SHORT = "SHORT"
    LONG = "LONG"


class ComponentCountBand(StrEnum):
    ZERO = "ZERO"
    ONE = "ONE"
    MULTI = "MULTI"
    AMBIGUOUS = "AMBIGUOUS"


class ProcurementBand(StrEnum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    KNOWN_PROCUREMENT = "KNOWN_PROCUREMENT"
    NO_RELEVANT_TED_FOUND = "NO_RELEVANT_TED_FOUND"
    AMBIGUOUS_CANDIDATE = "AMBIGUOUS_CANDIDATE"


class DescriptionPrecisionBand(StrEnum):
    HIGH = "HIGH"
    LOW = "LOW"


class StratificationRecord(FrozenModel):
    """Engine-independent screening result for one funded project."""

    operation_code: str
    domains: tuple[str, ...]
    scope_length_band: ScopeLengthBand
    component_count_band: ComponentCountBand
    procurement_band: ProcurementBand
    expected_project_state: ProjectState
    geography: str
    size_band: str
    time_band: str
    description_precision_band: DescriptionPrecisionBand
    rationale: str

    @model_validator(mode="after")
    def validate_record(self) -> StratificationRecord:
        if not self.operation_code.strip() or not self.rationale.strip():
            raise StratificationError("stratification record requires identity and rationale")
        if not self.geography.strip() or not self.size_band.strip() or not self.time_band.strip():
            raise StratificationError("geography, size_band and time_band must not be blank")
        unknown = set(self.domains) - set(SUPPORTED_COMPONENT_DOMAINS)
        if unknown:
            raise StratificationError(f"unknown component domains: {sorted(unknown)}")

        if self.component_count_band is ComponentCountBand.ZERO:
            if self.domains:
                raise StratificationError("ZERO component-count cases cannot claim supported domains")
            if self.procurement_band is not ProcurementBand.NOT_APPLICABLE:
                raise StratificationError(
                    "ZERO component-count cases require procurement NOT_APPLICABLE"
                )
            if self.expected_project_state is not ProjectState.UNRESOLVED:
                raise StratificationError(
                    "ZERO component-count cases require expected project state UNRESOLVED"
                )
        elif self.procurement_band is ProcurementBand.NOT_APPLICABLE:
            raise StratificationError(
                "procurement NOT_APPLICABLE is permitted only for ZERO component-count cases"
            )
        return self


class StratifiedSelection(FrozenModel):
    projects: tuple[FundingProject, ...]
    records: tuple[StratificationRecord, ...]


def _rank(seed: str, operation_code: str) -> str:
    return hashlib.sha256(f"{seed}\0{operation_code}".encode()).hexdigest()


def _coverage_values(records: tuple[StratificationRecord, ...]) -> dict[str, set[str]]:
    return {
        "domains": {domain for record in records for domain in record.domains},
        "scope_length": {record.scope_length_band.value for record in records},
        "component_count": {record.component_count_band.value for record in records},
        "procurement": {record.procurement_band.value for record in records},
        "expected_state": {record.expected_project_state.value for record in records},
        "geography": {record.geography for record in records},
        "size_band": {record.size_band for record in records},
        "time_band": {record.time_band for record in records},
        "description_precision": {
            record.description_precision_band.value for record in records
        },
    }


def validate_required_strata(records: tuple[StratificationRecord, ...]) -> None:
    coverage = _coverage_values(records)
    missing_domains = set(SUPPORTED_COMPONENT_DOMAINS) - coverage["domains"]
    if missing_domains:
        raise StratificationError(f"missing supported domains: {sorted(missing_domains)}")
    required_exact = {
        "scope_length": {"SHORT", "LONG"},
        "component_count": {"ZERO", "ONE", "MULTI", "AMBIGUOUS"},
        "procurement": {
            "KNOWN_PROCUREMENT",
            "NO_RELEVANT_TED_FOUND",
            "AMBIGUOUS_CANDIDATE",
        },
        "description_precision": {"HIGH", "LOW"},
    }
    for dimension, required in required_exact.items():
        missing = required - coverage[dimension]
        if missing:
            raise StratificationError(
                f"missing required {dimension} strata: {sorted(missing)}"
            )
    if ProjectState.UNRESOLVED.value not in coverage["expected_state"]:
        raise StratificationError("benchmark must include expected UNRESOLVED cases")
    for dimension in ("geography", "size_band", "time_band"):
        if len(coverage[dimension]) < 2:
            raise StratificationError(f"benchmark requires multiple {dimension} strata")


def _matches(record: StratificationRecord, dimension: str, value: str) -> bool:
    if dimension == "domain":
        return value in record.domains
    if dimension == "scope_length":
        return record.scope_length_band.value == value
    if dimension == "component_count":
        return record.component_count_band.value == value
    if dimension == "procurement":
        return record.procurement_band.value == value
    if dimension == "expected_state":
        return record.expected_project_state.value == value
    if dimension == "description_precision":
        return record.description_precision_band.value == value
    raise AssertionError(dimension)


def _dimension_value(record: StratificationRecord, dimension: str) -> str:
    return str(getattr(record, dimension))


def select_stratified_benchmark(
    projects: tuple[FundingProject, ...],
    records: tuple[StratificationRecord, ...],
    *,
    selection_seed: str,
    target_size: int = 200,
) -> StratifiedSelection:
    """Select deterministically while forcing every authoritative stratum into the result."""
    if not selection_seed.strip():
        raise StratificationError("selection_seed must not be blank")
    if target_size < 1:
        raise StratificationError("target_size must be positive")

    project_by_code = {project.operation_code: project for project in projects}
    if len(project_by_code) != len(projects):
        raise StratificationError("screening project pool contains duplicate operation codes")
    record_by_code = {record.operation_code: record for record in records}
    if len(record_by_code) != len(records):
        raise StratificationError("stratification records contain duplicate operation codes")
    if set(record_by_code) != set(project_by_code):
        raise StratificationError("every screening project requires exactly one stratification record")

    validate_required_strata(records)
    ranked = sorted(
        records,
        key=lambda record: (_rank(selection_seed, record.operation_code), record.operation_code),
    )

    selected: list[StratificationRecord] = []
    selected_codes: set[str] = set()

    requirements: list[tuple[str, str]] = []
    requirements.extend(("domain", value) for value in SUPPORTED_COMPONENT_DOMAINS)
    requirements.extend(("scope_length", value) for value in ("SHORT", "LONG"))
    requirements.extend(
        ("component_count", value) for value in ("ZERO", "ONE", "MULTI", "AMBIGUOUS")
    )
    requirements.extend(
        ("procurement", value)
        for value in (
            "KNOWN_PROCUREMENT",
            "NO_RELEVANT_TED_FOUND",
            "AMBIGUOUS_CANDIDATE",
        )
    )
    requirements.append(("expected_state", ProjectState.UNRESOLVED.value))
    requirements.extend(("description_precision", value) for value in ("HIGH", "LOW"))

    for dimension, value in requirements:
        if any(_matches(record, dimension, value) for record in selected):
            continue
        candidate = next(
            (record for record in ranked if _matches(record, dimension, value)),
            None,
        )
        if candidate is None:
            raise StratificationError(f"no candidate for required stratum {dimension}={value}")
        if candidate.operation_code not in selected_codes:
            selected.append(candidate)
            selected_codes.add(candidate.operation_code)

    for dimension in ("geography", "size_band", "time_band"):
        while len({_dimension_value(record, dimension) for record in selected}) < 2:
            current = {_dimension_value(record, dimension) for record in selected}
            candidate = next(
                (
                    record
                    for record in ranked
                    if record.operation_code not in selected_codes
                    and _dimension_value(record, dimension) not in current
                ),
                None,
            )
            if candidate is None:
                raise StratificationError(f"cannot cover multiple {dimension} strata")
            selected.append(candidate)
            selected_codes.add(candidate.operation_code)

    if len(selected) > target_size:
        raise StratificationError("target_size is too small to satisfy mandatory strata")

    for record in ranked:
        if len(selected) >= min(target_size, len(records)):
            break
        if record.operation_code not in selected_codes:
            selected.append(record)
            selected_codes.add(record.operation_code)

    selected_records = tuple(selected)
    validate_required_strata(selected_records)
    return StratifiedSelection(
        projects=tuple(project_by_code[record.operation_code] for record in selected_records),
        records=selected_records,
    )
