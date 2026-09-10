from procrun.a21a_thresholds import (
    FROZEN_A21A_THRESHOLDS,
    PREREGISTRATION_VERSION,
    evaluate_a21a_report,
)


def _passing_report() -> dict[str, object]:
    return {
        "evidence_precision": 0.95,
        "gold_excerpt_recall": 0.90,
        "gold_positive_case_recall": 0.95,
        "negative_case_false_positive_rate": 0.05,
        "exact_span_integrity_failures": 0,
        "provenance_failures": 0,
        "translation_violations": 0,
        "determinism_failures": 0,
        "hard_integrity_pass": True,
    }


def test_historical_a21a_threshold_values_are_preserved_but_invalidated() -> None:
    thresholds = FROZEN_A21A_THRESHOLDS
    assert PREREGISTRATION_VERSION == "a21a-thresholds-v1-invalidated"
    assert thresholds.evidence_precision_min == 0.95
    assert thresholds.gold_excerpt_recall_min == 0.90
    assert thresholds.gold_positive_case_recall_min == 0.95
    assert thresholds.negative_case_false_positive_rate_max == 0.05
    assert thresholds.exact_span_integrity_failures_max == 0
    assert thresholds.provenance_failures_max == 0
    assert thresholds.translation_violations_max == 0
    assert thresholds.determinism_failures_max == 0


def test_a21a_gate_cannot_pass_on_invalidated_preregistration_lineage() -> None:
    result = evaluate_a21a_report(_passing_report())
    assert result["checks"]["clean_preregistration_lineage"] is False
    assert result["pass"] is False


def test_a21a_gate_remains_conjunctive_and_fail_closed() -> None:
    fields_and_bad_values = {
        "evidence_precision": 0.949999,
        "gold_excerpt_recall": 0.899999,
        "gold_positive_case_recall": 0.949999,
        "negative_case_false_positive_rate": 0.050001,
        "exact_span_integrity_failures": 1,
        "provenance_failures": 1,
        "translation_violations": 1,
        "determinism_failures": 1,
        "hard_integrity_pass": False,
    }
    for field, bad_value in fields_and_bad_values.items():
        report = _passing_report()
        report[field] = bad_value
        assert evaluate_a21a_report(report)["pass"] is False


def test_a21a_gate_fails_when_required_metric_is_missing() -> None:
    report = _passing_report()
    report.pop("evidence_precision")
    assert evaluate_a21a_report(report)["pass"] is False
