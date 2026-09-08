#!/usr/bin/env python3
"""Score completed human Phase M review sheets without post-hoc threshold changes."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

MIN_SAMPLE = 30
MIN_CLOSED_PRECISION = 0.90
MAX_OPEN_FALSE_NEGATIVE_RATE = 0.10

CLOSED_VERDICTS = {"CORRECT", "FALSE_CLOSED", "DOUBTFUL"}
OPEN_VERDICTS = {"CONFIRMED_ABSENCE", "FALSE_OPEN", "OUTSIDE_TED_COVERAGE"}


@dataclass(frozen=True)
class Score:
    reviewed: int
    numerator: int
    denominator: int
    rate: float
    excluded: int
    passed: bool


def _read(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _require_human_fields(rows: list[dict[str, str]], allowed: set[str], label: str) -> None:
    if len(rows) < MIN_SAMPLE:
        raise ValueError(f"{label} requires at least {MIN_SAMPLE} rows; found {len(rows)}")
    for index, row in enumerate(rows, start=1):
        verdict = (row.get("human_verdict") or "").strip().upper()
        if verdict not in allowed:
            raise ValueError(f"{label} row {index} has missing/invalid human_verdict: {verdict!r}")
        for field in ("human_reason", "reviewer", "reviewed_at"):
            if not (row.get(field) or "").strip():
                raise ValueError(f"{label} row {index} is missing {field}")


def score_closed(rows: list[dict[str, str]]) -> Score:
    _require_human_fields(rows, CLOSED_VERDICTS, "CLOSED")
    verdicts = [(row["human_verdict"] or "").strip().upper() for row in rows]
    correct = verdicts.count("CORRECT")
    false_closed = verdicts.count("FALSE_CLOSED")
    doubtful = verdicts.count("DOUBTFUL")
    denominator = correct + false_closed
    if denominator == 0:
        raise ValueError("CLOSED precision denominator is zero")
    precision = correct / denominator
    return Score(len(rows), correct, denominator, precision, doubtful, precision >= MIN_CLOSED_PRECISION)


def score_open(rows: list[dict[str, str]]) -> Score:
    _require_human_fields(rows, OPEN_VERDICTS, "OPEN")
    verdicts = [(row["human_verdict"] or "").strip().upper() for row in rows]
    false_open = verdicts.count("FALSE_OPEN")
    confirmed = verdicts.count("CONFIRMED_ABSENCE")
    outside = verdicts.count("OUTSIDE_TED_COVERAGE")
    denominator = false_open + confirmed
    if denominator == 0:
        raise ValueError("OPEN false-negative denominator is zero")
    false_negative_rate = false_open / denominator
    return Score(
        len(rows),
        false_open,
        denominator,
        false_negative_rate,
        outside,
        false_negative_rate <= MAX_OPEN_FALSE_NEGATIVE_RATE,
    )


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def render(closed: Score, open_: Score, closed_path: Path, open_path: Path) -> str:
    overall = closed.passed and open_.passed
    status = "PASS" if overall else "FAIL — remediation and a new pre-registered sample are required"
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return f"""
## {now} — Phase M human validation score

- CLOSED review file: `{closed_path.as_posix()}`
- OPEN review file: `{open_path.as_posix()}`
- Locked CLOSED threshold: >= 90.00%
- Locked OPEN false-negative threshold: <= 10.00%
- Minimum reviewed sample: n >= 30 per category

### CLOSED

- Reviewed: {closed.reviewed}
- Precision denominator (Correct + False CLOSED): {closed.denominator}
- Correct: {closed.numerator}
- Doubtful excluded from denominator: {closed.excluded}
- CLOSED precision: **{_pct(closed.rate)}**
- Threshold: **{'PASS' if closed.passed else 'FAIL'}**

### OPEN

- Reviewed: {open_.reviewed}
- False-negative denominator (Confirmed absence + False OPEN): {open_.denominator}
- False OPEN: {open_.numerator}
- Outside TED coverage excluded from denominator: {open_.excluded}
- OPEN false-negative rate: **{_pct(open_.rate)}**
- Threshold: **{'PASS' if open_.passed else 'FAIL'}**

### Overall Phase M result

**{status}**

A failed result does not terminate ProcRun. It activates the documented continuation rule: isolate the named root cause, implement a specific fix or materially different matching/data approach, and repeat the affected validation with a new deterministic sample without changing the locked thresholds.
""".strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--closed", type=Path, required=True)
    parser.add_argument("--open", dest="open_path", type=Path, required=True)
    parser.add_argument("--append-report", type=Path)
    args = parser.parse_args()

    closed = score_closed(_read(args.closed))
    open_ = score_open(_read(args.open_path))
    text = render(closed, open_, args.closed, args.open_path)
    print(text)

    if args.append_report:
        args.append_report.parent.mkdir(parents=True, exist_ok=True)
        with args.append_report.open("a", encoding="utf-8") as handle:
            handle.write("\n" + text)

    return 0 if closed.passed and open_.passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
