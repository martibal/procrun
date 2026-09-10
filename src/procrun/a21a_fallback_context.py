"""Aggregate-only diagnostics for already-admitted A21a fallback context."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypedDict


class FallbackContextCase(TypedDict):
    title_utility: str
    project_title: str
    specific_objective: str | None
    intervention_category: str | None


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _distinct(value: str | None, title: str) -> bool:
    cleaned = _clean(value)
    return bool(cleaned) and cleaned.casefold() != title.strip().casefold()


def summarize_existing_context(
    cases: Iterable[FallbackContextCase],
) -> dict[str, int]:
    """Summarize field availability for title cases already judged NOT_USEFUL.

    This deliberately measures availability and distinctness only. It does not claim that an
    objective or intervention category is itself useful customer evidence.
    """

    weak = [case for case in cases if case["title_utility"] == "NOT_USEFUL"]
    objective_values = {
        _clean(case["specific_objective"])
        for case in weak
        if _clean(case["specific_objective"])
    }
    intervention_values = {
        _clean(case["intervention_category"])
        for case in weak
        if _clean(case["intervention_category"])
    }

    objective_present = sum(bool(_clean(case["specific_objective"])) for case in weak)
    intervention_present = sum(
        bool(_clean(case["intervention_category"])) for case in weak
    )
    either_present = sum(
        bool(_clean(case["specific_objective"]) or _clean(case["intervention_category"]))
        for case in weak
    )
    both_present = sum(
        bool(_clean(case["specific_objective"]) and _clean(case["intervention_category"]))
        for case in weak
    )
    objective_distinct = sum(
        _distinct(case["specific_objective"], case["project_title"]) for case in weak
    )
    intervention_distinct = sum(
        _distinct(case["intervention_category"], case["project_title"]) for case in weak
    )

    return {
        "weak_cases": len(weak),
        "objective_present": objective_present,
        "intervention_present": intervention_present,
        "either_present": either_present,
        "both_present": both_present,
        "objective_distinct_from_title": objective_distinct,
        "intervention_distinct_from_title": intervention_distinct,
        "objective_unique_values": len(objective_values),
        "intervention_unique_values": len(intervention_values),
    }
