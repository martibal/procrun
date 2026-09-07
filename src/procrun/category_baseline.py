"""Deterministic historical duration baselines by procurement component category.

The baseline uses only the existing append-only procurement observation history
and canonical component category. It does not ingest new sources or widen the
customer-safe data boundary.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date
from math import floor
from typing import Any

from psycopg import Connection

from procrun.domain import ComponentState


@dataclass(frozen=True)
class BaselineObservation:
    """Minimal customer-safe history row required for baseline computation."""

    category: str
    component_id: str
    observed_at: date
    state: ComponentState
    is_correction: bool = False


@dataclass(frozen=True)
class CompletedOpenInterval:
    """One clean observed OPEN -> CLOSED interval."""

    category: str
    component_id: str
    opened_at: date
    closed_at: date
    duration_days: int


@dataclass(frozen=True)
class CategoryDurationBaseline:
    """Observed duration distribution for one component category."""

    category: str
    n: int
    p25_days: float
    median_days: float
    p75_days: float


def _percentile_cont(values: Sequence[int], percentile: float) -> float:
    """Continuous percentile using deterministic Type-7 linear interpolation."""

    if not values:
        raise ValueError("percentile requires at least one value")
    if not 0.0 <= percentile <= 1.0:
        raise ValueError("percentile must be between 0 and 1")

    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])

    position = (len(ordered) - 1) * percentile
    lower = floor(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower

    return float(ordered[lower] + (ordered[upper] - ordered[lower]) * fraction)


def completed_open_intervals(
    observations: Iterable[BaselineObservation],
) -> tuple[CompletedOpenInterval, ...]:
    """Return only clean, completed OPEN -> CLOSED intervals.

    Rules:
    - the first observed OPEN starts the interval;
    - repeated OPEN observations/heartbeats do not reset it;
    - evidence-only changes with unchanged state do not reset it;
    - OPEN -> UNRESOLVED is censored and excluded;
    - still-OPEN components are censored and excluded;
    - components containing any explicit correction row are excluded;
    - CLOSED without a prior observed OPEN is excluded.
    """

    grouped: dict[str, list[BaselineObservation]] = defaultdict(list)
    for observation in observations:
        grouped[observation.component_id].append(observation)

    completed: list[CompletedOpenInterval] = []

    for component_id, rows in grouped.items():
        ordered = sorted(rows, key=lambda item: item.observed_at)

        if any(item.is_correction for item in ordered):
            continue

        opened_at: date | None = None

        for item in ordered:
            if opened_at is None:
                if item.state is ComponentState.OPEN:
                    opened_at = item.observed_at
                continue

            if item.state is ComponentState.OPEN:
                continue

            if item.state is ComponentState.UNRESOLVED:
                opened_at = None
                break

            if item.state is ComponentState.CLOSED:
                duration = (item.observed_at - opened_at).days
                if duration < 0:
                    raise ValueError(
                        f"observation history moved backwards for component {component_id}"
                    )
                completed.append(
                    CompletedOpenInterval(
                        category=item.category,
                        component_id=component_id,
                        opened_at=opened_at,
                        closed_at=item.observed_at,
                        duration_days=duration,
                    )
                )
                break

    return tuple(sorted(completed, key=lambda item: (item.category, item.component_id)))


def build_category_baselines(
    observations: Iterable[BaselineObservation],
) -> tuple[CategoryDurationBaseline, ...]:
    """Build median / p25 / p75 / n for every category with completed history."""

    intervals = completed_open_intervals(observations)

    durations_by_category: dict[str, list[int]] = defaultdict(list)
    for interval in intervals:
        durations_by_category[interval.category].append(interval.duration_days)

    result: list[CategoryDurationBaseline] = []
    for category in sorted(durations_by_category):
        durations = durations_by_category[category]
        result.append(
            CategoryDurationBaseline(
                category=category,
                n=len(durations),
                p25_days=_percentile_cont(durations, 0.25),
                median_days=_percentile_cont(durations, 0.50),
                p75_days=_percentile_cont(durations, 0.75),
            )
        )

    return tuple(result)


def load_category_baselines(
    conn: Connection[Any],
) -> tuple[CategoryDurationBaseline, ...]:
    """Load baseline inputs from existing canonical append-only tables."""

    rows = conn.execute(
        """
        WITH latest_components AS (
            SELECT DISTINCT ON (component_id)
                component_id,
                category
            FROM procrun.component_versions
            ORDER BY component_id, as_of DESC, inserted_at DESC
        )
        SELECT
            c.category,
            o.component_id,
            o.observed_at,
            o.state,
            (o.correction_of_id IS NOT NULL) AS is_correction
        FROM procrun.procurement_observations o
        JOIN latest_components c
          ON c.component_id = o.component_id
        ORDER BY
            c.category,
            o.component_id,
            o.observed_at,
            o.inserted_at,
            o.id
        """
    ).fetchall()

    observations = tuple(
        BaselineObservation(
            category=str(category),
            component_id=str(component_id),
            observed_at=observed_at,
            state=ComponentState(str(state)),
            is_correction=bool(is_correction),
        )
        for category, component_id, observed_at, state, is_correction in rows
    )

    return build_category_baselines(observations)