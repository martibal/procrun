"""Deterministic Funded Project Comparables v1 calculation engine.

This module is deliberately independent from HTTP and rendering. It consumes an
explicit, frozen cohort and returns one immutable calculation payload. UI/PDF/Excel
must render the payload rather than recomputing statistics.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from math import floor
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

ENGINE_VERSION: Final = "funded-project-comparables-v1.0.0"
SCHEMA_VERSION: Final = "funded-project-benchmark-schema-v1.0.0"


class GovernanceTier(StrEnum):
    FULL_STATISTICAL = "FULL_STATISTICAL"
    DESCRIPTIVE_ONLY = "DESCRIPTIVE_ONLY"
    REFERENCE_ONLY = "REFERENCE_ONLY"


class ExclusionReason(StrEnum):
    MISSING_FUNDING = "MISSING_FUNDING"
    MISSING_START_DATE = "MISSING_START_DATE"
    MISSING_END_DATE = "MISSING_END_DATE"
    INVALID_DATE_ORDER = "INVALID_DATE_ORDER"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class BenchmarkProject(StrictModel):
    operation_code: str
    project_title: str | None = None
    source_url: str
    bando_code: str
    action_code: str
    intervention_code: str
    approved_funding_eur: int | None = Field(default=None, ge=0)
    project_start: date | None = None
    project_end: date | None = None


class UserProjectInput(StrictModel):
    proposed_funding_eur: int = Field(ge=0)
    proposed_duration_months: int | None = Field(default=None, ge=0)


class ComparableResult(StrictModel):
    operation_code: str
    project_title: str | None
    source_url: str
    approved_funding_eur: int | None
    duration_months: int | None
    distance: float | None = None
    abs_funding_diff_eur: int | None = None
    abs_duration_diff_months: int | None = None


class VariableGovernance(StrictModel):
    n: int = Field(ge=0)
    tier: GovernanceTier


class StatisticalResult(StrictModel):
    user_value: int
    percentile: float | None = None
    median: float | None = None
    q1: float | None = None
    q3: float | None = None
    p90: float | None = None
    minimum: int | None = None
    maximum: int | None = None


class CohortCompositionRow(StrictModel):
    action_code: str
    intervention_code: str
    count: int = Field(ge=1)


class BenchmarkCalculation(StrictModel):
    engine_version: str = ENGINE_VERSION
    schema_version: str = SCHEMA_VERSION
    snapshot_id: str
    cohort_id: str
    cohort_size: int
    composition: tuple[CohortCompositionRow, ...]
    funding_governance: VariableGovernance
    duration_governance: VariableGovernance
    funding_result: StatisticalResult | None
    duration_result: StatisticalResult | None
    closest_comparables: tuple[ComparableResult, ...]
    high_end_comparables: tuple[ComparableResult, ...]
    exclusions: dict[str, tuple[str, ...]]


@dataclass(frozen=True)
class _PreparedProject:
    project: BenchmarkProject
    duration_months: int | None
    funding_exclusion: ExclusionReason | None
    duration_exclusion: ExclusionReason | None


def full_calendar_months(
    start_date: date | None, end_date: date | None
) -> tuple[int | None, ExclusionReason | None]:
    """Return completed calendar months under the locked v1 rule."""

    if start_date is None:
        return None, ExclusionReason.MISSING_START_DATE
    if end_date is None:
        return None, ExclusionReason.MISSING_END_DATE
    if end_date < start_date:
        return None, ExclusionReason.INVALID_DATE_ORDER
    base_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    return base_months - (1 if end_date.day < start_date.day else 0), None


def governance_tier(n: int) -> GovernanceTier:
    if n >= 30:
        return GovernanceTier.FULL_STATISTICAL
    if n >= 15:
        return GovernanceTier.DESCRIPTIVE_ONLY
    return GovernanceTier.REFERENCE_ONLY


def right_sided_ecdf(values: tuple[int, ...], x: int) -> float:
    """P(x) = count(X_i <= x) / n. Caller must provide a non-empty population."""

    if not values:
        raise ValueError("ECDF requires at least one observation")
    return sum(value <= x for value in values) / len(values)


def _type7_quantile(values: tuple[int, ...], probability: float) -> float:
    """Deterministic Hyndman-Fan type 7 quantile (R/NumPy default semantics)."""

    if not values:
        raise ValueError("quantile requires at least one observation")
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be between 0 and 1")
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    h = (len(ordered) - 1) * probability
    lower = floor(h)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = h - lower
    return ordered[lower] + fraction * (ordered[upper] - ordered[lower])


def _statistics(values: tuple[int, ...], user_value: int, tier: GovernanceTier) -> StatisticalResult:
    if tier is GovernanceTier.REFERENCE_ONLY:
        return StatisticalResult(user_value=user_value)
    if tier is GovernanceTier.DESCRIPTIVE_ONLY:
        return StatisticalResult(
            user_value=user_value,
            median=_type7_quantile(values, 0.5),
            minimum=min(values),
            maximum=max(values),
        )
    return StatisticalResult(
        user_value=user_value,
        percentile=round(right_sided_ecdf(values, user_value) * 100.0, 6),
        median=_type7_quantile(values, 0.5),
        q1=_type7_quantile(values, 0.25),
        q3=_type7_quantile(values, 0.75),
        p90=_type7_quantile(values, 0.90),
        minimum=min(values),
        maximum=max(values),
    )


def _prepare(project: BenchmarkProject) -> _PreparedProject:
    duration, duration_exclusion = full_calendar_months(project.project_start, project.project_end)
    funding_exclusion = (
        ExclusionReason.MISSING_FUNDING if project.approved_funding_eur is None else None
    )
    return _PreparedProject(project, duration, funding_exclusion, duration_exclusion)


def _composition(projects: tuple[BenchmarkProject, ...]) -> tuple[CohortCompositionRow, ...]:
    counts: dict[tuple[str, str], int] = {}
    for project in projects:
        key = (project.action_code, project.intervention_code)
        counts[key] = counts.get(key, 0) + 1
    return tuple(
        CohortCompositionRow(action_code=action, intervention_code=intervention, count=count)
        for (action, intervention), count in sorted(counts.items())
    )


def compute_benchmark(
    *,
    snapshot_id: str,
    cohort_id: str,
    projects: tuple[BenchmarkProject, ...],
    user_input: UserProjectInput,
    max_closest: int = 10,
) -> BenchmarkCalculation:
    """Compute one deterministic benchmark from an already-selected frozen cohort."""

    if not projects:
        raise ValueError("benchmark cohort must contain at least one project")
    if max_closest < 1:
        raise ValueError("max_closest must be positive")

    prepared = tuple(_prepare(project) for project in projects)
    funding_values_list: list[int] = []
    duration_values_list: list[int] = []
    for item in prepared:
        if item.project.approved_funding_eur is not None:
            funding_values_list.append(item.project.approved_funding_eur)
        if item.duration_months is not None:
            duration_values_list.append(item.duration_months)
    funding_values = tuple(funding_values_list)
    duration_values = tuple(duration_values_list)
    funding_tier = governance_tier(len(funding_values))
    duration_tier = governance_tier(len(duration_values))

    funding_result = (
        _statistics(funding_values, user_input.proposed_funding_eur, funding_tier)
        if funding_values
        else None
    )
    duration_result = None
    if user_input.proposed_duration_months is not None and duration_values:
        duration_result = _statistics(
            duration_values,
            user_input.proposed_duration_months,
            duration_tier,
        )

    use_duration_distance = (
        user_input.proposed_duration_months is not None
        and duration_tier is not GovernanceTier.REFERENCE_ONLY
        and bool(duration_values)
    )
    user_funding_percentile = (
        right_sided_ecdf(funding_values, user_input.proposed_funding_eur)
        if funding_values
        else None
    )
    user_duration_percentile = (
        right_sided_ecdf(duration_values, user_input.proposed_duration_months)
        if use_duration_distance and user_input.proposed_duration_months is not None
        else None
    )

    closest_candidates: list[ComparableResult] = []
    for item in prepared:
        funding = item.project.approved_funding_eur
        if funding is None or user_funding_percentile is None:
            continue
        funding_distance = abs(right_sided_ecdf(funding_values, funding) - user_funding_percentile)
        duration_diff: int | None = None
        if (
            use_duration_distance
            and item.duration_months is not None
            and user_duration_percentile is not None
        ):
            duration_distance = abs(
                right_sided_ecdf(duration_values, item.duration_months) - user_duration_percentile
            )
            distance = 0.7 * funding_distance + 0.3 * duration_distance
            assert user_input.proposed_duration_months is not None
            duration_diff = abs(item.duration_months - user_input.proposed_duration_months)
        else:
            distance = funding_distance
        closest_candidates.append(
            ComparableResult(
                operation_code=item.project.operation_code,
                project_title=item.project.project_title,
                source_url=item.project.source_url,
                approved_funding_eur=funding,
                duration_months=item.duration_months,
                distance=round(distance, 12),
                abs_funding_diff_eur=abs(funding - user_input.proposed_funding_eur),
                abs_duration_diff_months=duration_diff,
            )
        )

    closest_candidates.sort(
        key=lambda item: (
            item.distance if item.distance is not None else float("inf"),
            item.abs_funding_diff_eur if item.abs_funding_diff_eur is not None else float("inf"),
            item.abs_duration_diff_months if item.abs_duration_diff_months is not None else float("inf"),
            item.operation_code,
        )
    )

    high_end = [
        ComparableResult(
            operation_code=item.project.operation_code,
            project_title=item.project.project_title,
            source_url=item.project.source_url,
            approved_funding_eur=item.project.approved_funding_eur,
            duration_months=item.duration_months,
        )
        for item in prepared
        if item.project.approved_funding_eur is not None
        and item.project.approved_funding_eur >= user_input.proposed_funding_eur
    ]
    high_end.sort(key=lambda item: (item.approved_funding_eur or 0, item.operation_code))

    exclusions: dict[str, tuple[str, ...]] = {}
    for item in prepared:
        reasons = tuple(
            reason.value
            for reason in (item.funding_exclusion, item.duration_exclusion)
            if reason is not None
        )
        if reasons:
            exclusions[item.project.operation_code] = reasons

    return BenchmarkCalculation(
        snapshot_id=snapshot_id,
        cohort_id=cohort_id,
        cohort_size=len(projects),
        composition=_composition(projects),
        funding_governance=VariableGovernance(n=len(funding_values), tier=funding_tier),
        duration_governance=VariableGovernance(n=len(duration_values), tier=duration_tier),
        funding_result=funding_result,
        duration_result=duration_result,
        closest_comparables=tuple(closest_candidates[:max_closest]),
        high_end_comparables=tuple(high_end),
        exclusions=exclusions,
    )
