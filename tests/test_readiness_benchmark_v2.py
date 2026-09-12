from datetime import date

from procrun.readiness_benchmark import (
    BenchmarkObservation,
    SampleTier,
    completed_calendar_months,
    compute_historical_dimensioning,
    sample_tier,
)


def _observations(n: int) -> tuple[BenchmarkObservation, ...]:
    return tuple(
        BenchmarkObservation(
            operation_code=f"OP-{i:03d}",
            approved_funding_eur=100_000 + i * 10_000,
            project_start=date(2025, 1, 15),
            project_end=date(2026, 1, 15),
            project_title=f"Project {i}",
            source_url=f"https://example.invalid/{i}",
        )
        for i in range(n)
    )


def _end_after_completed_months(months: int) -> date:
    absolute_month = months
    return date(2025 + absolute_month // 12, 1 + absolute_month % 12, 1)


def test_sample_governance_boundaries_are_frozen() -> None:
    assert sample_tier(14) is SampleTier.REFERENCE_ONLY
    assert sample_tier(15) is SampleTier.DESCRIPTIVE_ONLY
    assert sample_tier(29) is SampleTier.DESCRIPTIVE_ONLY
    assert sample_tier(30) is SampleTier.FULL_BENCHMARK


def test_completed_calendar_month_rule() -> None:
    assert completed_calendar_months(date(2025, 1, 15), date(2025, 2, 14))[0] == 0
    assert completed_calendar_months(date(2025, 1, 15), date(2025, 2, 15))[0] == 1
    assert completed_calendar_months(date(2025, 1, 31), date(2025, 2, 28))[0] == 0
    assert completed_calendar_months(date(2025, 1, 31), date(2025, 3, 31))[0] == 2
    value, reason = completed_calendar_months(date(2025, 3, 1), date(2025, 2, 1))
    assert value is None
    assert reason is not None and reason.value == "INVALID_DATE_ORDER"


def test_full_benchmark_exposes_position_but_small_samples_do_not() -> None:
    full = compute_historical_dimensioning(
        _observations(30), proposed_funding_eur=250_000, proposed_duration_months=12
    )
    assert full["funding"]["tier"] == "FULL_BENCHMARK"
    assert "user_position" in full["funding"]

    small = compute_historical_dimensioning(
        _observations(14), proposed_funding_eur=250_000, proposed_duration_months=12
    )
    assert small["funding"] == {"n": 14, "tier": "REFERENCE_ONLY"}


def test_ties_use_right_ecdf_and_output_is_deterministic() -> None:
    values = (100_000, 100_000, 100_000, 500_000)
    obs = tuple(
        BenchmarkObservation(
            operation_code=f"T-{i}",
            approved_funding_eur=value,
            project_start=date(2025, 1, 1),
            project_end=date(2026, 1, 1),
        )
        for i, value in enumerate(values)
    )
    expanded = obs * 8
    result_a = compute_historical_dimensioning(
        expanded, proposed_funding_eur=100_000, proposed_duration_months=12
    )
    result_b = compute_historical_dimensioning(
        tuple(reversed(expanded)), proposed_funding_eur=100_000, proposed_duration_months=12
    )
    assert result_a == result_b
    assert result_a["funding"]["user_position"]["basis_points"] == 7500


def test_joint_comparable_ranking_locks_frozen_70_30_position_distance() -> None:
    """A 50/50 rewrite would reverse OP-008 and OP-009; the frozen 70/30 rule must not."""
    duration_rank_by_funding_rank = {8: 10, 10: 8, 9: 12, 12: 9}
    observations = tuple(
        BenchmarkObservation(
            operation_code=f"OP-{rank:03d}",
            approved_funding_eur=rank * 100_000,
            project_start=date(2025, 1, 1),
            project_end=_end_after_completed_months(
                duration_rank_by_funding_rank.get(rank, rank)
            ),
        )
        for rank in range(1, 21)
    )

    result = compute_historical_dimensioning(
        observations,
        proposed_funding_eur=1_000_000,
        proposed_duration_months=10,
        comparable_limit=20,
    )
    joint = result["comparables"]["closest_joint"]
    operation_codes = [row["operation_code"] for row in joint]

    assert operation_codes.index("OP-009") < operation_codes.index("OP-008")
