"""Category-level closed-duration baselines derived from append-only procurement history."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from math import floor
from typing import Any

from psycopg import Connection


@dataclass(frozen=True)
class ClosedDurationSample:
    component_id: str
    category: str
    opened_at: date
    closed_at: date
    duration_days: int


@dataclass(frozen=True)
class CategoryBaseline:
    category: str
    n: int
    p25_days: float
    median_days: float
    p75_days: float
    earliest_opened_at: date
    latest_closed_at: date


@dataclass(frozen=True)
class CategoryPercentilePosition:
    """Objective historical position of one current OPEN duration."""

    category: str
    current_age_days: int
    n: int
    percentile: float


def percentile(values: Sequence[int], q: float) -> float:
    """Return a deterministic linear-interpolated percentile for integer durations."""

    if not values:
        raise ValueError("percentile requires at least one value")
    if not 0 <= q <= 1:
        raise ValueError("percentile q must be between 0 and 1")
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = floor(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return float(ordered[lower] + (ordered[upper] - ordered[lower]) * weight)


def build_category_baselines(samples: Sequence[ClosedDurationSample]) -> tuple[CategoryBaseline, ...]:
    """Aggregate comparable CLOSED lifecycles by exact frozen taxonomy category."""

    grouped: dict[str, list[ClosedDurationSample]] = defaultdict(list)
    for sample in samples:
        if sample.duration_days < 0:
            raise ValueError("closed-duration samples cannot be negative")
        grouped[sample.category].append(sample)

    baselines: list[CategoryBaseline] = []
    for category in sorted(grouped):
        rows = grouped[category]
        durations = [row.duration_days for row in rows]
        baselines.append(
            CategoryBaseline(
                category=category,
                n=len(rows),
                p25_days=percentile(durations, 0.25),
                median_days=percentile(durations, 0.50),
                p75_days=percentile(durations, 0.75),
                earliest_opened_at=min(row.opened_at for row in rows),
                latest_closed_at=max(row.closed_at for row in rows),
            )
        )
    return tuple(baselines)


def category_percentile_position(
    samples: Sequence[ClosedDurationSample],
    *,
    category: str,
    current_age_days: int,
) -> CategoryPercentilePosition | None:
    """Return the empirical historical percentile for one current OPEN duration.

    Only completed historical OPEN-to-CLOSED durations from the exact same taxonomy
    category are compared. The result is descriptive only; it is not a probability
    of future procurement or a qualitative delay assessment.

    Ties use deterministic midrank:
        (count(duration < current) + 0.5 * count(duration == current)) / n
    """

    if current_age_days < 0:
        raise ValueError("current open duration cannot be negative")

    durations = sorted(
        sample.duration_days
        for sample in samples
        if sample.category == category
    )

    if not durations:
        return None

    below = sum(duration < current_age_days for duration in durations)
    equal = sum(duration == current_age_days for duration in durations)

    position = (below + 0.5 * equal) / len(durations)
    percentile_value = max(0.0, min(100.0, position * 100.0))

    return CategoryPercentilePosition(
        category=category,
        current_age_days=current_age_days,
        n=len(durations),
        percentile=percentile_value,
    )

def load_closed_duration_samples(conn: Connection[Any]) -> tuple[ClosedDurationSample, ...]:
    """Load one first effective OPEN-to-CLOSED duration per component.

    An observation that has later been explicitly corrected is not allowed to become a baseline
    endpoint. Correction rows themselves remain part of the effective history. Category comes only
    from the existing frozen component ledger; no source or customer-data boundary is widened.
    """

    rows = conn.execute(
        """
        WITH latest_component AS (
            SELECT DISTINCT ON (component_id)
                component_id, category
            FROM procrun.component_versions
            ORDER BY component_id, as_of DESC, inserted_at DESC
        ),
        effective_observation AS (
            SELECT o.*
            FROM procrun.procurement_observations o
            WHERE NOT EXISTS (
                SELECT 1
                FROM procrun.procurement_observations correction
                WHERE correction.correction_of_id = o.id
            )
        ),
        first_open AS (
            SELECT component_id, min(observed_at) AS opened_at
            FROM effective_observation
            WHERE state = 'OPEN'
            GROUP BY component_id
        ),
        first_close AS (
            SELECT first_open.component_id, min(o.observed_at) AS closed_at
            FROM first_open
            JOIN effective_observation o
              ON o.component_id = first_open.component_id
             AND o.state = 'CLOSED'
             AND o.observed_at >= first_open.opened_at
            GROUP BY first_open.component_id
        )
        SELECT
            first_open.component_id,
            latest_component.category,
            first_open.opened_at,
            first_close.closed_at,
            (first_close.closed_at - first_open.opened_at)::int AS duration_days
        FROM first_open
        JOIN first_close USING (component_id)
        JOIN latest_component USING (component_id)
        ORDER BY latest_component.category, first_open.component_id
        """
    ).fetchall()

    return tuple(
        ClosedDurationSample(
            component_id=str(row[0]),
            category=str(row[1]),
            opened_at=row[2],
            closed_at=row[3],
            duration_days=int(row[4]),
        )
        for row in rows
    )


def load_category_baselines(conn: Connection[Any]) -> tuple[CategoryBaseline, ...]:
    """Load and aggregate current category baselines from the immutable history."""

    return build_category_baselines(load_closed_duration_samples(conn))
