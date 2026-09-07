from datetime import date

from procrun.category_baseline import (
    BaselineObservation,
    build_category_baselines,
    completed_open_intervals,
)
from procrun.domain import ComponentState


def obs(
    component_id: str,
    category: str,
    observed_at: date,
    state: ComponentState,
    *,
    correction: bool = False,
) -> BaselineObservation:
    return BaselineObservation(
        category=category,
        component_id=component_id,
        observed_at=observed_at,
        state=state,
        is_correction=correction,
    )


def test_category_baseline_reports_n_p25_median_p75() -> None:
    observations = (
        obs("a", "lighting", date(2026, 1, 1), ComponentState.OPEN),
        obs("a", "lighting", date(2026, 1, 11), ComponentState.CLOSED),
        obs("b", "lighting", date(2026, 1, 1), ComponentState.OPEN),
        obs("b", "lighting", date(2026, 1, 21), ComponentState.CLOSED),
        obs("c", "lighting", date(2026, 1, 1), ComponentState.OPEN),
        obs("c", "lighting", date(2026, 1, 31), ComponentState.CLOSED),
    )

    result = build_category_baselines(observations)

    assert len(result) == 1
    baseline = result[0]
    assert baseline.category == "lighting"
    assert baseline.n == 3
    assert baseline.p25_days == 15.0
    assert baseline.median_days == 20.0
    assert baseline.p75_days == 25.0


def test_open_heartbeat_does_not_reset_interval_start() -> None:
    observations = (
        obs("a", "lighting", date(2026, 1, 1), ComponentState.OPEN),
        obs("a", "lighting", date(2026, 1, 31), ComponentState.OPEN),
        obs("a", "lighting", date(2026, 2, 10), ComponentState.CLOSED),
    )

    intervals = completed_open_intervals(observations)

    assert len(intervals) == 1
    assert intervals[0].opened_at == date(2026, 1, 1)
    assert intervals[0].duration_days == 40


def test_still_open_component_is_censored() -> None:
    observations = (
        obs("a", "lighting", date(2026, 1, 1), ComponentState.OPEN),
        obs("a", "lighting", date(2026, 1, 31), ComponentState.OPEN),
    )

    assert completed_open_intervals(observations) == ()


def test_open_to_unresolved_is_censored() -> None:
    observations = (
        obs("a", "lighting", date(2026, 1, 1), ComponentState.OPEN),
        obs("a", "lighting", date(2026, 1, 10), ComponentState.UNRESOLVED),
        obs("a", "lighting", date(2026, 1, 20), ComponentState.CLOSED),
    )

    assert completed_open_intervals(observations) == ()


def test_component_with_correction_is_excluded() -> None:
    observations = (
        obs("a", "lighting", date(2026, 1, 1), ComponentState.OPEN),
        obs(
            "a",
            "lighting",
            date(2026, 1, 5),
            ComponentState.OPEN,
            correction=True,
        ),
        obs("a", "lighting", date(2026, 1, 20), ComponentState.CLOSED),
    )

    assert completed_open_intervals(observations) == ()


def test_closed_without_observed_open_is_excluded() -> None:
    observations = (
        obs("a", "lighting", date(2026, 1, 20), ComponentState.CLOSED),
    )

    assert completed_open_intervals(observations) == ()


def test_categories_are_calculated_separately() -> None:
    observations = (
        obs("a", "lighting", date(2026, 1, 1), ComponentState.OPEN),
        obs("a", "lighting", date(2026, 1, 11), ComponentState.CLOSED),
        obs("b", "hvac", date(2026, 1, 1), ComponentState.OPEN),
        obs("b", "hvac", date(2026, 2, 10), ComponentState.CLOSED),
    )

    result = build_category_baselines(observations)

    assert [(item.category, item.n, item.median_days) for item in result] == [
        ("hvac", 1, 40.0),
        ("lighting", 1, 10.0),
    ]