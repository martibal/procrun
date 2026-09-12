from datetime import date

from procrun.benchmark_reports import canonicalize_report
from procrun.funded_project_benchmark import (
    BenchmarkProject,
    GovernanceTier,
    UserProjectInput,
    compute_benchmark,
    full_calendar_months,
    governance_tier,
    right_sided_ecdf,
)


def _project(
    index: int,
    funding: int | None,
    months: int | None,
    *,
    action: str = "1.2.3",
    intervention: str = "013",
) -> BenchmarkProject:
    start = date(2025, 1, 15) if months is not None else None
    end = (
        date(2025 + (months or 0) // 12, 1 + (months or 0) % 12, 15)
        if months is not None
        else None
    )
    return BenchmarkProject(
        operation_code=f"OP-{index:03d}",
        project_title=f"Project {index}",
        source_url=f"https://example.invalid/{index}",
        bando_code="BANDO-1",
        action_code=action,
        intervention_code=intervention,
        approved_funding_eur=funding,
        project_start=start,
        project_end=end,
    )


def test_01_boundary_governance() -> None:
    assert governance_tier(14) is GovernanceTier.REFERENCE_ONLY
    assert governance_tier(15) is GovernanceTier.DESCRIPTIVE_ONLY
    assert governance_tier(29) is GovernanceTier.DESCRIPTIVE_ONLY
    assert governance_tier(30) is GovernanceTier.FULL_STATISTICAL


def test_02_independent_sample_sizes() -> None:
    projects = tuple(
        _project(i, 100_000 + i * 10_000, 12 if i < 12 else None) for i in range(45)
    )
    result = compute_benchmark(
        snapshot_id="snap",
        cohort_id="cohort",
        projects=projects,
        user_input=UserProjectInput(proposed_funding_eur=250_000, proposed_duration_months=12),
    )
    assert result.funding_governance.tier is GovernanceTier.FULL_STATISTICAL
    assert result.funding_governance.n == 45
    assert result.duration_governance.tier is GovernanceTier.REFERENCE_ONLY
    assert result.duration_governance.n == 12
    assert result.duration_result is not None
    assert result.duration_result.percentile is None


def test_03_right_sided_ecdf_ties() -> None:
    values = (100_000, 100_000, 100_000, 500_000)
    assert right_sided_ecdf(values, 100_000) == 0.75


def test_04_distance_tie_breaking_is_deterministic() -> None:
    projects = tuple(_project(i, 100_000 + i * 1_000, 12) for i in range(30))
    user = UserProjectInput(proposed_funding_eur=114_500, proposed_duration_months=12)
    first = compute_benchmark(snapshot_id="s", cohort_id="c", projects=projects, user_input=user)
    second = compute_benchmark(
        snapshot_id="s",
        cohort_id="c",
        projects=tuple(reversed(projects)),
        user_input=user,
    )
    assert [item.operation_code for item in first.closest_comparables] == [
        item.operation_code for item in second.closest_comparables
    ]


def test_05_rfc8785_hash_is_byte_identical() -> None:
    projects = tuple(_project(i, 100_000 + i * 5_000, 12) for i in range(30))
    result = compute_benchmark(
        snapshot_id="snap",
        cohort_id="cohort",
        projects=projects,
        user_input=UserProjectInput(proposed_funding_eur=150_000, proposed_duration_months=12),
    )
    canonical_a, digest_a, _ = canonicalize_report(result)
    for _ in range(1000):
        canonical_b, digest_b, _ = canonicalize_report(result)
        assert canonical_b == canonical_a
        assert digest_b == digest_a


def test_06_date_inversion_and_full_month_rule() -> None:
    assert full_calendar_months(date(2025, 1, 15), date(2025, 2, 14))[0] == 0
    assert full_calendar_months(date(2025, 1, 15), date(2025, 2, 15))[0] == 1
    assert full_calendar_months(date(2025, 1, 31), date(2025, 2, 28))[0] == 0
    assert full_calendar_months(date(2025, 1, 31), date(2025, 3, 31))[0] == 2
    months, reason = full_calendar_months(date(2025, 2, 1), date(2025, 1, 31))
    assert months is None
    assert reason is not None and reason.value == "INVALID_DATE_ORDER"


def test_07_same_calculation_has_same_hash() -> None:
    projects = tuple(_project(i, 200_000 + i * 2_000, 18) for i in range(30))
    result = compute_benchmark(
        snapshot_id="snap",
        cohort_id="cohort",
        projects=projects,
        user_input=UserProjectInput(proposed_funding_eur=230_000, proposed_duration_months=18),
    )
    _, digest_a, _ = canonicalize_report(result)
    _, digest_b, _ = canonicalize_report(result)
    assert digest_a == digest_b


def test_09_missing_funding_is_excluded_without_fallback() -> None:
    projects = tuple(
        [_project(0, None, 12)]
        + [_project(i, 100_000 + i, 12) for i in range(1, 30)]
    )
    result = compute_benchmark(
        snapshot_id="snap",
        cohort_id="cohort",
        projects=projects,
        user_input=UserProjectInput(proposed_funding_eur=100_010, proposed_duration_months=12),
    )
    assert result.funding_governance.n == 29
    assert result.exclusions["OP-000"] == ("MISSING_FUNDING",)


def test_high_end_order_is_funding_then_operation_code() -> None:
    projects = tuple(
        [
            _project(2, 200_000, 12),
            _project(1, 200_000, 12),
            _project(3, 300_000, 12),
        ]
        + [_project(i + 10, 100_000, 12) for i in range(27)]
    )
    result = compute_benchmark(
        snapshot_id="snap",
        cohort_id="cohort",
        projects=projects,
        user_input=UserProjectInput(proposed_funding_eur=200_000, proposed_duration_months=12),
    )
    assert [item.operation_code for item in result.high_end_comparables] == [
        "OP-001",
        "OP-002",
        "OP-003",
    ]
