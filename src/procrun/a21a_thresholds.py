"""A21a product-quality threshold state.

The numerical values below are retained only as historical v1 provenance. Their preregistration
was invalidated on 2026-09-10 because the development results visible before the freeze came from
a subsequently disqualified download-then-filter lineage. No A21a report may pass this gate until
a clean independent development review has completed and a new threshold version is frozen.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from procrun.a21a_lineage import preregistration_ready


@dataclass(frozen=True)
class A21aThresholds:
    evidence_precision_min: float = 0.95
    gold_excerpt_recall_min: float = 0.90
    gold_positive_case_recall_min: float = 0.95
    negative_case_false_positive_rate_max: float = 0.05
    exact_span_integrity_failures_max: int = 0
    provenance_failures_max: int = 0
    translation_violations_max: int = 0
    determinism_failures_max: int = 0


# Historical values are preserved for auditability; they are not an active preregistration.
FROZEN_A21A_THRESHOLDS = A21aThresholds()
PREREGISTRATION_VERSION = "a21a-thresholds-v1-invalidated"


def evaluate_a21a_report(report: dict[str, Any]) -> dict[str, Any]:
    """Fail closed until a clean post-remediation preregistration exists."""

    thresholds = FROZEN_A21A_THRESHOLDS
    checks = {
        "clean_preregistration_lineage": preregistration_ready(),
        "evidence_precision": report.get("evidence_precision") is not None
        and report["evidence_precision"] >= thresholds.evidence_precision_min,
        "gold_excerpt_recall": report.get("gold_excerpt_recall") is not None
        and report["gold_excerpt_recall"] >= thresholds.gold_excerpt_recall_min,
        "gold_positive_case_recall": report.get("gold_positive_case_recall") is not None
        and report["gold_positive_case_recall"] >= thresholds.gold_positive_case_recall_min,
        "negative_case_false_positive_rate": report.get("negative_case_false_positive_rate") is not None
        and report["negative_case_false_positive_rate"]
        <= thresholds.negative_case_false_positive_rate_max,
        "exact_span_integrity": report.get("exact_span_integrity_failures")
        == thresholds.exact_span_integrity_failures_max,
        "provenance": report.get("provenance_failures") == thresholds.provenance_failures_max,
        "translation": report.get("translation_violations") == thresholds.translation_violations_max,
        "determinism": report.get("determinism_failures") == thresholds.determinism_failures_max,
        "hard_integrity": report.get("hard_integrity_pass") is True,
    }
    return {
        "preregistration_version": PREREGISTRATION_VERSION,
        "checks": checks,
        "pass": all(checks.values()),
    }
