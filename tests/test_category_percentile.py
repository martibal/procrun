from datetime import date

import pytest

from procrun.category_baselines import (
    ClosedDurationSample,
    category_percentile_position,
)


def sample(
    component_id: str,
    category: str,
    duration_days: int,
) -> ClosedDurationSample:
    opened_at = date(2026, 1, 1)
    return ClosedDurationSample(
        component_id=component_id,
        category=category,
        opened_at=opened_at,
        closed_at=date.fromordinal(opened_at.toordinal() + duration_days),
        duration_days=duration_days,
    )


def test_percentile_uses_exact_category_only() -> None:
    samples = (
        sample("a", "lighting", 10),
        sample("b", "lighting", 20),
        sample("c", "lighting", 30),
        sample("d", "hvac", 500),
    )

    result = category_percentile_position(
        samples,
        category="lighting",
        current_age_days=25,
    )

    assert result is not None
    assert result.category == "lighting"
    assert result.current_age_days == 25
    assert result.n == 3
    assert result.percentile == pytest.approx(66.6666666667)


def test_percentile_uses_midrank_for_ties() -> None:
    samples = (
        sample("a", "lighting", 10),
        sample("b", "lighting", 20),
        sample("c", "lighting", 20),
        sample("d", "lighting", 30),
    )

    result = category_percentile_position(
        samples,
        category="lighting",
        current_age_days=20,
    )

    assert result is not None
    assert result.n == 4
    assert result.percentile == 50.0


def test_percentile_below_all_observations_is_zero() -> None:
    samples = (
        sample("a", "lighting", 10),
        sample("b", "lighting", 20),
    )

    result = category_percentile_position(
        samples,
        category="lighting",
        current_age_days=5,
    )

    assert result is not None
    assert result.percentile == 0.0


def test_percentile_above_all_observations_is_one_hundred() -> None:
    samples = (
        sample("a", "lighting", 10),
        sample("b", "lighting", 20),
    )

    result = category_percentile_position(
        samples,
        category="lighting",
        current_age_days=30,
    )

    assert result is not None
    assert result.percentile == 100.0


def test_percentile_returns_none_without_comparable_history() -> None:
    samples = (
        sample("a", "hvac", 10),
    )

    result = category_percentile_position(
        samples,
        category="lighting",
        current_age_days=20,
    )

    assert result is None


def test_percentile_rejects_negative_current_age() -> None:
    with pytest.raises(ValueError):
        category_percentile_position(
            (),
            category="lighting",
            current_age_days=-1,
        )