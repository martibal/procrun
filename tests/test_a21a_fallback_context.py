from procrun.a21a_fallback_context import FallbackContextCase, summarize_existing_context


def test_existing_context_summary_counts_only_weak_title_cases() -> None:
    cases: list[FallbackContextCase] = [
        FallbackContextCase(
            title_utility="NOT_USEFUL",
            project_title="ALFA",
            specific_objective="Energy efficiency",
            intervention_category="Building renovation",
        ),
        FallbackContextCase(
            title_utility="NOT_USEFUL",
            project_title="BETA",
            specific_objective=None,
            intervention_category="BETA",
        ),
        FallbackContextCase(
            title_utility="CLEAR",
            project_title="Upgrade water network",
            specific_objective="Water resilience",
            intervention_category="Water infrastructure",
        ),
    ]

    summary = summarize_existing_context(cases)

    assert summary == {
        "weak_cases": 2,
        "objective_present": 1,
        "intervention_present": 2,
        "either_present": 2,
        "both_present": 1,
        "objective_distinct_from_title": 1,
        "intervention_distinct_from_title": 1,
        "objective_unique_values": 1,
        "intervention_unique_values": 2,
    }
