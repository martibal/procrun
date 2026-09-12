"""Deterministic historical dimensioning for funded project comparables."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum
from statistics import median

ENGINE_VERSION = "readiness-benchmark-v2"


class SampleTier(StrEnum):
    FULL_BENCHMARK = "FULL_BENCHMARK"
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


def completed_calendar_months(
    start: date | None,
    end: date | None,
) -> tuple[int | None, ExclusionReason | None]:
    if start is None:
        return None, ExclusionReason.MISSING_START_DATE
    if end is None:
        return None, ExclusionReason.MISSING_END_DATE
    if end < start:
        return None, ExclusionReason.INVALID_DATE_ORDER
    months = (end.year - start.year) * 12 + end.month - start.month
    if end.day < start.day:
        months -= 1
    return months, None


def sample_tier(n: int) -> SampleTier:
    if n >= 30:
        return SampleTier.FULL_BENCHMARK
    if n >= 15:
        return SampleTier.DESCRIPTIVE_ONLY
    return SampleTier.REFERENCE_ONLY


def _nearest_rank(values: tuple[int, ...], numerator: int, denominator: int) -> int:
    ordered = sorted(values)
    rank = (numerator * len(ordered) + denominator - 1) // denominator
    rank = max(1, min(len(ordered), rank))
    return ordered[rank - 1]


def _median_string(values: tuple[int, ...]) -> str:
    return str(Decimal(str(median(values))))


def _ecdf(values: tuple[int, ...], value: int) -> tuple[int, int, int]:
    count = sum(1 for item in values if item <= value)
    n = len(values)
    return count, n, count * 10_000 // n


def _summary(values: tuple[int, ...], user_value: int | None) -> dict[str, object]:
    tier = sample_tier(len(values))
    base: dict[str, object] = {"n": len(values), "tier": tier.value}
    if tier is SampleTier.REFERENCE_ONLY:
        return base
    base.update({"median": _median_string(values), "min": min(values), "max": max(values)})
    if tier is SampleTier.FULL_BENCHMARK:
        base.update(
            {
                "q1": _nearest_rank(values, 1, 4),
                "q3": _nearest_rank(values, 3, 4),
                "p90": _nearest_rank(values, 9, 10),
            }
        )
        if user_value is not None:
            count, n, bps = _ecdf(values, user_value)
            base["user_position"] = {"count_lte": count, "n": n, "basis_points": bps}
    return base


def compute_historical_dimensioning(
    observations: tuple[BenchmarkObservation, ...],
    *,
    proposed_funding_eur: int,
    proposed_duration_months: int | None,
    comparable_limit: int = 10,
) -> dict[str, object]:
    """Return descriptive historical context; never an outcome or recommendation."""
    if proposed_funding_eur < 0:
        raise ValueError("proposed_funding_eur must be non-negative")
    if proposed_duration_months is not None and proposed_duration_months < 0:
        raise ValueError("proposed_duration_months must be non-negative")

    prepared: list[dict[str, object]] = []
    funding_values: list[int] = []
    duration_values: list[int] = []
    for observation in sorted(observations, key=lambda item: item.operation_code):
        duration, duration_reason = completed_calendar_months(
            observation.project_start, observation.project_end
        )
        funding_reason = (
            ExclusionReason.MISSING_FUNDING if observation.approved_funding_eur is None else None
        )
        if observation.approved_funding_eur is not None:
            funding_values.append(observation.approved_funding_eur)
        if duration is not None:
            duration_values.append(duration)
        prepared.append(
            {
                "operation_code": observation.operation_code,
                "approved_funding_eur": observation.approved_funding_eur,
                "duration_months": duration,
                "funding_exclusion_reason": None if funding_reason is None else funding_reason.value,
                "duration_exclusion_reason": None if duration_reason is None else duration_reason.value,
                "project_title": observation.project_title,
                "source_url": observation.source_url,
            }
        )

    funding_tuple = tuple(funding_values)
    duration_tuple = tuple(duration_values)
    closest_funding: list[tuple[int, int, str, dict[str, object]]] = []
    if funding_tuple:
        _, _, user_bps = _ecdf(funding_tuple, proposed_funding_eur)
        for item in prepared:
            funding = item["approved_funding_eur"]
            if not isinstance(funding, int):
                continue
            _, _, project_bps = _ecdf(funding_tuple, funding)
            closest_funding.append(
                (
                    abs(project_bps - user_bps),
                    abs(funding - proposed_funding_eur),
                    str(item["operation_code"]),
                    item,
                )
            )
    closest_funding.sort(key=lambda row: (row[0], row[1], row[2]))

    closest_joint: list[tuple[int, int, int, str, dict[str, object]]] = []
    if proposed_duration_months is not None and len(duration_tuple) >= 15 and funding_tuple:
        _, _, user_funding_bps = _ecdf(funding_tuple, proposed_funding_eur)
        _, _, user_duration_bps = _ecdf(duration_tuple, proposed_duration_months)
        for item in prepared:
            funding = item["approved_funding_eur"]
            duration = item["duration_months"]
            if not isinstance(funding, int) or not isinstance(duration, int):
                continue
            _, _, f_bps = _ecdf(funding_tuple, funding)
            _, _, d_bps = _ecdf(duration_tuple, duration)
            # Frozen v1 comparable contract: 70% funding-position distance, 30% duration-position distance.
            weighted_distance = 7 * abs(f_bps - user_funding_bps) + 3 * abs(d_bps - user_duration_bps)
            closest_joint.append(
                (
                    weighted_distance,
                    abs(funding - proposed_funding_eur),
                    abs(duration - proposed_duration_months),
                    str(item["operation_code"]),
                    item,
                )
            )
        closest_joint.sort(key=lambda row: (row[0], row[1], row[2], row[3]))

    high_end = [
        item
        for item in sorted(
            prepared,
            key=lambda row: (
                10**30
                if not isinstance(row["approved_funding_eur"], int)
                else row["approved_funding_eur"],
                str(row["operation_code"]),
            ),
        )
        if isinstance(item["approved_funding_eur"], int)
        and item["approved_funding_eur"] >= proposed_funding_eur
    ]

    return {
        "engine_version": ENGINE_VERSION,
        "governance": {
            "funding": {"n": len(funding_tuple), "tier": sample_tier(len(funding_tuple)).value},
            "duration": {"n": len(duration_tuple), "tier": sample_tier(len(duration_tuple)).value},
        },
        "funding": _summary(funding_tuple, proposed_funding_eur) if funding_tuple else {"n": 0, "tier": SampleTier.REFERENCE_ONLY.value},
        "duration": _summary(duration_tuple, proposed_duration_months) if duration_tuple else {"n": 0, "tier": SampleTier.REFERENCE_ONLY.value},
        "comparables": {
            "closest_by_funding": [row[3] for row in closest_funding[:comparable_limit]],
            "closest_joint": [row[4] for row in closest_joint[:comparable_limit]],
            "at_or_above_proposed_funding": high_end,
        },
        "observations": prepared,
        "language_contract": (
            "Historical descriptive comparison only. It is not a prediction, recommendation, "
            "qualification decision, or proof that a project cost is reasonable."
        ),
    }
