"""Composition layer for ProcRun pre-application assessment v1.

The three customer-facing modules remain independent in their calculations but are frozen into
one report payload. This layer contains no source retrieval and no predictive logic.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict

from procrun.funding_benchmark import BenchmarkObservation, compute_benchmark
from procrun.preapplication_rules import DISCLAIMER, RuleSet, evaluate_ruleset

REPORT_SCHEMA_VERSION = "preapplication-assessment-v1"


def _scaled_percent(value: float | None) -> int | None:
    """Represent a 0..1 ratio as integer basis points for canonical persistence."""
    if value is None:
        return None
    return round(value * 10_000)


def _canonical_safe(value: object) -> object:
    """Remove floating-point values from benchmark output before report persistence."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return str(value)
    if isinstance(value, list):
        return [_canonical_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_canonical_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _canonical_safe(item) for key, item in value.items()}
    raise TypeError(f"unsupported report value: {type(value).__name__}")


def build_assessment_payload(
    *,
    snapshot_id: str,
    cohort_id: str,
    bando_code: str,
    observations: tuple[BenchmarkObservation, ...],
    proposed_funding_eur: int,
    proposed_duration_months: int | None,
    ruleset: RuleSet | None,
    self_reported_inputs: Mapping[str, object],
) -> dict[str, object]:
    """Build the single source-of-truth payload used by UI and report renderers."""
    benchmark = compute_benchmark(
        observations,
        proposed_funding_eur=proposed_funding_eur,
        proposed_duration_months=proposed_duration_months,
    )

    results = benchmark["results"]
    assert isinstance(results, dict)
    for variable in ("funding", "duration"):
        summary = results.get(variable)
        if isinstance(summary, dict) and "user_percentile" in summary:
            raw_percentile = summary.pop("user_percentile")
            if raw_percentile is None or isinstance(raw_percentile, float):
                summary["user_percentile_bps"] = _scaled_percent(raw_percentile)
            else:
                raise TypeError("unexpected percentile type")

    rule_modules: list[object] = []
    if ruleset is not None:
        rule_modules = [
            asdict(module) for module in evaluate_ruleset(ruleset, self_reported_inputs)
        ]

    payload: dict[str, object] = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "snapshot_id": snapshot_id,
        "cohort_id": cohort_id,
        "bando_code": bando_code,
        "user_inputs": {
            "proposed_funding_eur": proposed_funding_eur,
            "proposed_duration_months": proposed_duration_months,
        },
        "formal_and_technical_screening": rule_modules,
        "historical_dimensioning": benchmark,
        "disclaimer": DISCLAIMER,
    }
    safe_payload = _canonical_safe(payload)
    if not isinstance(safe_payload, dict):
        raise TypeError("assessment payload must remain a JSON object")
    return safe_payload
