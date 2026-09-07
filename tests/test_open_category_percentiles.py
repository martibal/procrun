from datetime import date

import pytest

from procrun.category_baselines import (
    ClosedDurationSample,
    CurrentOpenComponent,
    build_open_category_percentiles,
)


def closed_sample(
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


def test_current_open_component_gets_exact_category_percentile() -> None:
    current = (
        CurrentOpenComponent(
            component_id="current-lighting",
            category="lighting",
            opened_at=date(2026, 1, 1),
        ),
    )

    history = (
        closed_sample("a", "lighting", 10),
        closed_sample("b", "lighting", 20),
        closed_sample("c", "lighting", 30),
        closed_sample("x", "hvac", 500),
    )

    result = build_open_category_percentiles(
        current,
        history,
        as_of_date=date(2026, 1, 26),
    )

    assert len(result) == 1
    item = result[0]
    assert item.component_id == "current-lighting"
    assert item.category == "lighting"
    assert item.current_age_days == 25
    assert item.n == 3
    assert item.percentile == pytest.approx(66.6666666667)


def test_component_without_comparable_history_is_omitted() -> None:
    current = (
        CurrentOpenComponent(
            component_id="current-lighting",
            category="lighting",
            opened_at=date(2026, 1, 1),
        ),
    )

    result = build_open_category_percentiles(
        current,
        (closed_sample("a", "hvac", 10),),
        as_of_date=date(2026, 1, 20),
    )

    assert result == ()


def test_future_open_date_is_rejected() -> None:
    current = (
        CurrentOpenComponent(
            component_id="future",
            category="lighting",
            opened_at=date(2026, 2, 1),
        ),
    )

    with pytest.raises(ValueError):
        build_open_category_percentiles(
            current,
            (closed_sample("a", "lighting", 10),),
            as_of_date=date(2026, 1, 31),
        )


def test_results_are_deterministically_sorted() -> None:
    current = (
        CurrentOpenComponent(
            component_id="b",
            category="lighting",
            opened_at=date(2026, 1, 16),
        ),
        CurrentOpenComponent(
            component_id="a",
            category="lighting",
            opened_at=date(2026, 1, 1),
        ),
    )

    history = (
        closed_sample("h1", "lighting", 10),
        closed_sample("h2", "lighting", 20),
        closed_sample("h3", "lighting", 30),
    )

    result = build_open_category_percentiles(
        current,
        history,
        as_of_date=date(2026, 1, 31),
    )

    assert [item.component_id for item in result] == ["a", "b"]
    assert result[0].percentile > result[1].percentile


def test_output_contains_no_qualitative_delay_label() -> None:
    current = (
        CurrentOpenComponent(
            component_id="a",
            category="lighting",
            opened_at=date(2026, 1, 1),
        ),
    )

    result = build_open_category_percentiles(
        current,
        (
            closed_sample("h1", "lighting", 10),
            closed_sample("h2", "lighting", 20),
        ),
        as_of_date=date(2026, 2, 1),
    )

    assert len(result) == 1
    rendered = repr(result[0]).lower()

    for forbidden in ("delayed", "late", "overdue", "mature"):
        assert forbidden not in rendered