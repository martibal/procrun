from datetime import date

from procrun.funding_benchmark import (
    BenchmarkObservation,
    ExclusionReason,
    GovernanceTier,
    completed_calendar_months,
    compute_benchmark,
    governance_tier,
    right_ecdf,
)


def _obs(i: int, funding: int | None = None, months: int | None = None) -> BenchmarkObservation:
    start = date(2025, 1, 15)
    end = None if months is None else date(2025 + (months // 12), 1 + (months % 12), 15)
    return BenchmarkObservation(
        operation_code=f"OP-{i:03d}",
        approved_funding_eur=funding,
        project_start=start if months is not None else None,
        project_end=end,
    )


def test_governance_boundaries() -> None:
    assert governance_tier(14) is GovernanceTier.REFERENCE_ONLY
    assert governance_tier(15) is GovernanceTier.DESCRIPTIVE_ONLY
    assert governance_tier(29) is GovernanceTier.DESCRIPTIVE_ONLY
    assert governance_tier(30) is GovernanceTier.FULL_STATISTICAL


def test_right_sided_ecdf_ties() -> None:
    values = (100_000, 100_000, 100_000, 500_000)
    assert right_ecdf(values, 100_000) == 0.75


def test_completed_calendar_month_rule() -> None:
    assert completed_calendar_months(date(2025, 1, 15), date(2025, 2, 14)) == (0, None)
    assert completed_calendar_months(date(2025, 1, 15), date(2025, 2, 15)) == (1, None)
    assert completed_calendar_months(date(2025, 1, 31), date(2025, 2, 28)) == (0, None)
    assert completed_calendar_months(date(2025, 1, 31), date(2025, 3, 31)) == (2, None)


def test_date_inversion_fails_closed() -> None:
    value, reason = completed_calendar_months(date(2025, 2, 1), date(2025, 1, 1))
    assert value is None
    assert reason is ExclusionReason.INVALID_DATE_ORDER


def test_independent_sample_governance() -> None:
    observations = tuple(
        BenchmarkObservation(
            operation_code=f"OP-{i:03d}",
            approved_funding_eur=100_000 + i,
            project_start=date(2025, 1, 1) if i < 12 else None,
            project_end=date(2026, 1, 1) if i < 12 else None,
        )
        for i in range(45)
    )
    result = compute_benchmark(
        observations,
        proposed_funding_eur=100_020,
        proposed_duration_months=12,
    )
    assert result["governance"]["funding"] == {"n": 45, "tier": "FULL_STATISTICAL"}
    assert result["governance"]["duration"] == {"n": 12, "tier": "REFERENCE_ONLY"}


def test_closest_and_high_end_order_are_deterministic() -> None:
    observations = (
        _obs(3, 900_000, 24),
        _obs(1, 850_000, 30),
        _obs(2, 850_000, 30),
        _obs(4, 1_000_000, 36),
    )
    result = compute_benchmark(
        observations,
        proposed_funding_eur=850_000,
        proposed_duration_months=30,
    )
    closest = result["comparables"]["closest"]
    assert [item["operation_code"] for item in closest[:2]] == ["OP-001", "OP-002"]
    high_end = result["comparables"]["high_end"]
    assert [item["operation_code"] for item in high_end] == [
        "OP-001",
        "OP-002",
        "OP-003",
        "OP-004",
    ]
