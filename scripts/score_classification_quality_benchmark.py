#!/usr/bin/env python3
"""Score the canonical ProcRun classification-quality benchmark.

The scorer is intentionally conservative. It does not infer missing human judgements,
and it refuses PASS when sample-size or reference-truth reliability requirements are unmet.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

MIN_BENCHMARK_N = 300
MIN_DOUBLE_REVIEW_N = 30
MIN_CATEGORY_N = 20
MIN_OVERALL_PRECISION = 0.95
MIN_OPEN_PRECISION = 0.95
MAX_WRONG_DOMAIN_RATE = 0.02
MAX_DUPLICATE_RATE = 0.01
MIN_CATEGORY_PRECISION = 0.90
MIN_AGREEMENT = 0.90

YES = {"yes", "y", "true", "1"}
NO = {"no", "n", "false", "0"}
STATES = {"OPEN", "CLOSED", "UNRESOLVED"}


@dataclass(frozen=True)
class ScoredRow:
    predicted_category: str
    predicted_sector: str
    predicted_state: str
    need_present: bool
    correct_category: str
    correct_sector: str
    correct_state: str
    evidence_sufficient: bool
    duplicate: bool
    over_specific: bool
    reviewer: str
    reviewer_2: str
    need_present_2: str
    correct_category_2: str
    correct_sector_2: str
    correct_state_2: str
    evidence_sufficient_2: str


def _bool(value: str, field: str) -> bool:
    normalized = value.strip().casefold()
    if normalized in YES:
        return True
    if normalized in NO:
        return False
    raise ValueError(f"{field} must be yes/no, got {value!r}")


def _required(row: dict[str, str], field: str) -> str:
    value = (row.get(field) or "").strip()
    if not value:
        raise ValueError(f"missing required field {field}")
    return value


def _row(raw: dict[str, str]) -> ScoredRow:
    predicted_state = _required(raw, "predicted_state").upper()
    correct_state = _required(raw, "correct_state").upper()
    if predicted_state not in STATES:
        raise ValueError(f"unsupported predicted_state {predicted_state!r}")
    if correct_state not in STATES:
        raise ValueError(f"unsupported correct_state {correct_state!r}")

    return ScoredRow(
        predicted_category=_required(raw, "predicted_category"),
        predicted_sector=(raw.get("predicted_sector") or "").strip(),
        predicted_state=predicted_state,
        need_present=_bool(_required(raw, "need_present"), "need_present"),
        correct_category=(raw.get("correct_need_category") or "").strip(),
        correct_sector=(raw.get("correct_sector_or_null") or "").strip(),
        correct_state=correct_state,
        evidence_sufficient=_bool(_required(raw, "evidence_sufficient"), "evidence_sufficient"),
        duplicate=_bool(_required(raw, "duplicate"), "duplicate"),
        over_specific=_bool(_required(raw, "over_specific"), "over_specific"),
        reviewer=_required(raw, "reviewer"),
        reviewer_2=(raw.get("reviewer_2") or "").strip(),
        need_present_2=(raw.get("need_present_2") or "").strip(),
        correct_category_2=(raw.get("correct_need_category_2") or "").strip(),
        correct_sector_2=(raw.get("correct_sector_or_null_2") or "").strip(),
        correct_state_2=(raw.get("correct_state_2") or "").strip().upper(),
        evidence_sufficient_2=(raw.get("evidence_sufficient_2") or "").strip(),
    )


def load_rows(path: Path) -> list[ScoredRow]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return [_row(raw) for raw in reader]


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _classification_correct(row: ScoredRow) -> bool:
    if not row.need_present:
        return False
    if row.correct_category and row.predicted_category != row.correct_category:
        return False
    if row.correct_sector != row.predicted_sector:
        return False
    return True


def _open_correct(row: ScoredRow) -> bool:
    return (
        row.predicted_state == "OPEN"
        and row.need_present
        and row.evidence_sufficient
        and row.correct_state == "OPEN"
        and _classification_correct(row)
    )


def _agreement(rows: Iterable[ScoredRow]) -> dict[str, float | None]:
    double = [row for row in rows if row.reviewer_2]
    fields: dict[str, list[bool]] = {
        "need_present": [],
        "category": [],
        "sector": [],
        "state": [],
        "evidence_sufficient": [],
    }
    for row in double:
        fields["need_present"].append(
            row.need_present == _bool(row.need_present_2, "need_present_2")
        )
        fields["category"].append(row.correct_category == row.correct_category_2)
        fields["sector"].append(row.correct_sector == row.correct_sector_2)
        fields["state"].append(row.correct_state == row.correct_state_2)
        fields["evidence_sufficient"].append(
            row.evidence_sufficient
            == _bool(row.evidence_sufficient_2, "evidence_sufficient_2")
        )
    return {
        field: _ratio(sum(values), len(values)) if values else None
        for field, values in fields.items()
    }


def score(rows: list[ScoredRow]) -> dict[str, object]:
    predicted_n = len(rows)
    correct_n = sum(_classification_correct(row) for row in rows)
    overall_precision = _ratio(correct_n, predicted_n)

    open_rows = [row for row in rows if row.predicted_state == "OPEN"]
    open_precision = _ratio(sum(_open_correct(row) for row in open_rows), len(open_rows))

    need_supported = [row for row in rows if row.need_present]
    wrong_domain = sum(
        bool(row.predicted_sector or row.correct_sector)
        and row.predicted_sector != row.correct_sector
        for row in need_supported
    )
    wrong_domain_rate = _ratio(wrong_domain, len(need_supported))
    duplicate_rate = _ratio(sum(row.duplicate for row in rows), predicted_n)
    over_specificity_rate = _ratio(sum(row.over_specific for row in rows), predicted_n)
    false_positive_rate = _ratio(sum(not row.need_present for row in rows), predicted_n)

    state_confusion: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        state_confusion[row.predicted_state][row.correct_state] += 1

    state_precision: dict[str, float | None] = {}
    for state in sorted(STATES):
        predicted = [row for row in rows if row.predicted_state == state]
        state_precision[state] = _ratio(
            sum(row.correct_state == state for row in predicted), len(predicted)
        )

    by_category: dict[str, list[ScoredRow]] = defaultdict(list)
    for row in rows:
        by_category[row.predicted_category].append(row)
    category_metrics = {
        category: {
            "n": len(items),
            "precision": _ratio(sum(_classification_correct(item) for item in items), len(items)),
            "validated": len(items) >= MIN_CATEGORY_N,
        }
        for category, items in sorted(by_category.items())
    }

    double_review_n = sum(bool(row.reviewer_2) for row in rows)
    agreement = _agreement(rows)

    checks = {
        "benchmark_n": predicted_n >= MIN_BENCHMARK_N,
        "overall_precision": overall_precision is not None
        and overall_precision >= MIN_OVERALL_PRECISION,
        "open_precision": open_precision is not None and open_precision >= MIN_OPEN_PRECISION,
        "wrong_domain_rate": wrong_domain_rate is not None
        and wrong_domain_rate <= MAX_WRONG_DOMAIN_RATE,
        "duplicate_rate": duplicate_rate is not None and duplicate_rate <= MAX_DUPLICATE_RATE,
        "double_review_n": double_review_n >= MIN_DOUBLE_REVIEW_N,
        "agreement": double_review_n >= MIN_DOUBLE_REVIEW_N
        and all(value is not None and value >= MIN_AGREEMENT for value in agreement.values()),
        "category_precision": all(
            metric["precision"] is not None and metric["precision"] >= MIN_CATEGORY_PRECISION
            for metric in category_metrics.values()
            if metric["validated"]
        ),
    }

    return {
        "sample_size": predicted_n,
        "overall_precision": overall_precision,
        "open_precision": open_precision,
        "state_precision": state_precision,
        "state_confusion": {key: dict(value) for key, value in state_confusion.items()},
        "wrong_domain_rate": wrong_domain_rate,
        "over_specificity_rate": over_specificity_rate,
        "false_positive_rate": false_positive_rate,
        "duplicate_rate": duplicate_rate,
        "double_review_n": double_review_n,
        "inter_rater_raw_agreement": agreement,
        "categories": category_metrics,
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = score(load_rows(args.benchmark))
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
