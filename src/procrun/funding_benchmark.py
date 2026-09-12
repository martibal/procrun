"""Deterministic funded-project benchmark engine for ProcRun v1.

This module is intentionally independent from the legacy procurement classification path.
It consumes already-admitted project facts and produces a frozen, descriptive benchmark payload.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from math import inf
from statistics import median

ENGINE_VERSION = "funded-project-benchmark-v1"


class GovernanceTier(StrEnum):
    FULL_STATISTICAL = "FULL_STATISTICAL"
    DESCRIPTIVE_ONLY = "DESCRIPTIVE_ONLY"
    REFERENCE_ONLY = "REFERENCE_ONLY"


class ExclusionReason(StrEnum):
    MISSING_FUNDING = "MISSING_FUNDING"
    MISSING_START_DATE = "MISSING_START_DATE"
    MISSING_END_DATE = "MISSING_END_DATE"
    INVALID_DATE_ORDER = "INVALID_DATE_ORDER"


@dataclass(frozen=True)
class BenchmarkObservation:
    operation_code: str
    approved_funding_eur: int | None
    project_start: date | None
    project_end: date | None
    project_title: str | None = None
    source_url: str | None = None


@dataclass(frozen=True)
class PreparedObservation:
    operation_code: str
    approved_funding_eur: int | None
    duration_months: int | None
    funding_exclusion_reason: ExclusionReason | None
    duration_exclusion_reason: ExclusionReason | None
    project_title: str | None
    source_url: str | None


@dataclass(frozen=True)
class Comparable:
    operation_code: str
    approved_funding_eur: int | None
    duration_months: int | None
    distance: float | None
    project_title: str | None
    source_url: str | None


def completed_calendar_months(
    start: date | None, end: date | None
) -> tuple[int | None, ExclusionReason | None]:
    """Return completed calendar months using the frozen v1 rule."""
    if start is None:
        return None, ExclusionReason.MISSING_START_DATE
    if end is None:
        return None, ExclusionReason.MISSING_END_DATE
    if end < start:
        return None, ExclusionReason.INVALID_DATE_ORDER
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        months -= 1
    return months, None


def prepare_observation(observation: BenchmarkObservation) -> PreparedObservation:
    duration, duration_reason = completed_calendar_months(
        observation.project_start, observation.project_end
    )
    funding_reason = (
        ExclusionReason.MISSING_FUNDING
        if observation.approved_funding_eur is None
        else None
    )
    return PreparedObservation(
        operation_code=observation.operation_code,
        approved_funding_eur=observation.approved_funding_eur,
        duration_months=duration,
        funding_exclusion_reason=funding_reason,
        duration_exclusion_reason=duration_reason,
        project_title=observation.project_title,
        source_url=observation.source_url,
    )


def governance_tier(n: int) -> GovernanceTier:
    if n >= 30:
        return GovernanceTier.FULL_STATISTICAL
    if n >= 15:
        return GovernanceTier.DESCRIPTIVE_ONLY
    return GovernanceTier.REFERENCE_ONLY


def right_ecdf(values: tuple[int, ...], x: int) -> float:
    """Right-sided empirical CDF P(x)=#{Xi<=x}/n."""
    if not values:
        raise ValueError("ECDF requires at least one observation")
    return sum(1 for value in values if value <= x) / len(values)


def _nearest_rank(values: tuple[int, ...], percentile: float) -> int:
    """Deterministic nearest-rank percentile for report display."""
    if not values:
        raise ValueError("percentile requires at least one observation")
    ordered = sorted(values)
    rank = max(1, min(len(ordered), int((percentile * len(ordered)) + 0.999999999999)))
    return ordered[rank - 1]


def _summary(
    values: tuple[int, ...], tier: GovernanceTier, user_value: int | None
) -> dict[str, object]:
    if tier is GovernanceTier.REFERENCE_ONLY:
        return {"n": len(values), "tier": tier.value}

    result: dict[str, object] = {
        "n": len(values),
        "tier": tier.value,
        "median": median(values),
        "min": min(values),
        "max": max(values),
    }
    if tier is GovernanceTier.FULL_STATISTICAL:
        result.update(
            {
                "q1": _nearest_rank(values, 0.25),
                "q3": _nearest_rank(values, 0.75),
                "p90": _nearest_rank(values, 0.90),
                "user_percentile": (
                    None if user_value is None else right_ecdf(values, user_value)
                ),
            }
        )
    return result


def compute_benchmark(
    observations: Iterable[BenchmarkObservation],
    *,
    proposed_funding_eur: int,
    proposed_duration_months: int | None,
    closest_limit: int = 10,
) -> dict[str, object]:
    """Compute a descriptive, deterministic benchmark payload.

    No imputation, prediction, approval probability, or recommendation is produced.
    """
    if proposed_funding_eur < 0:
        raise ValueError("proposed_funding_eur must be non-negative")
    if proposed_duration_months is not None and proposed_duration_months < 0:
        raise ValueError("proposed_duration_months must be non-negative")

    prepared = tuple(
        sorted(
            (prepare_observation(observation) for observation in observations),
            key=lambda observation: observation.operation_code,
        )
    )
    funding_values = tuple(
        observation.approved_funding_eur
        for observation in prepared
        if observation.approved_funding_eur is not None
    )
    duration_values = tuple(
        observation.duration_months
        for observation in prepared
        if observation.duration_months is not None
    )
    funding_tier = governance_tier(len(funding_values))
    duration_tier = governance_tier(len(duration_values))

    use_duration_distance = proposed_duration_months is not None and len(duration_values) >= 15

    ranked: list[tuple[float, int, float, PreparedObservation]] = []
    for item in prepared:
        if item.approved_funding_eur is None:
            continue
        funding_distance = abs(
            right_ecdf(funding_values, item.approved_funding_eur)
            - right_ecdf(funding_values, proposed_funding_eur)
        )
        absolute_funding_diff = abs(item.approved_funding_eur - proposed_funding_eur)
        if use_duration_distance and item.duration_months is not None:
            assert proposed_duration_months is not None
            duration_distance = abs(
                right_ecdf(duration_values, item.duration_months)
                - right_ecdf(duration_values, proposed_duration_months)
            )
            distance = 0.7 * funding_distance + 0.3 * duration_distance
            duration_diff = float(abs(item.duration_months - proposed_duration_months))
        elif use_duration_distance:
            distance = funding_distance
            duration_diff = inf
        else:
            distance = funding_distance
            duration_diff = 0.0
        ranked.append((distance, absolute_funding_diff, duration_diff, item))

    ranked.sort(key=lambda row: (row[0], row[1], row[2], row[3].operation_code))
    closest = [
        Comparable(
            operation_code=item.operation_code,
            approved_funding_eur=item.approved_funding_eur,
            duration_months=item.duration_months,
            distance=distance,
            project_title=item.project_title,
            source_url=item.source_url,
        ).__dict__
        for distance, _, _, item in ranked[:closest_limit]
    ]

    high_end_items = sorted(
        (
            item
            for item in prepared
            if item.approved_funding_eur is not None
            and item.approved_funding_eur >= proposed_funding_eur
        ),
        key=lambda item: (item.approved_funding_eur, item.operation_code),
    )
    high_end = [
        Comparable(
            operation_code=item.operation_code,
            approved_funding_eur=item.approved_funding_eur,
            duration_months=item.duration_months,
            distance=None,
            project_title=item.project_title,
            source_url=item.source_url,
        ).__dict__
        for item in high_end_items
    ]

    exclusions = []
    for item in prepared:
        if item.funding_exclusion_reason is None and item.duration_exclusion_reason is None:
            continue
        exclusions.append(
            {
                "operation_code": item.operation_code,
                "funding": (
                    None
                    if item.funding_exclusion_reason is None
                    else item.funding_exclusion_reason.value
                ),
                "duration": (
                    None
                    if item.duration_exclusion_reason is None
                    else item.duration_exclusion_reason.value
                ),
            }
        )

    return {
        "engine_version": ENGINE_VERSION,
        "governance": {
            "funding": {"n": len(funding_values), "tier": funding_tier.value},
            "duration": {"n": len(duration_values), "tier": duration_tier.value},
        },
        "results": {
            "funding": _summary(funding_values, funding_tier, proposed_funding_eur),
            "duration": _summary(duration_values, duration_tier, proposed_duration_months),
        },
        "comparables": {"closest": closest, "high_end": high_end},
        "exclusions": exclusions,
        "language_contract": (
            "Historical descriptive comparison only; no approval prediction or funding "
            "recommendation."
        ),
    }
