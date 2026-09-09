"""Run the ProcRun 2.0 source-evidence extractor against a frozen A21a development benchmark.

This runner is intentionally separate from A21b classification validation. It measures only whether
ProcRun retrieves customer-useful, verbatim project-document evidence with exact provenance.

The runner refuses sealed holdout material. A sealed holdout remains inaccessible until the
pre-registered A21a thresholds and release-candidate extractor are frozen.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from procrun.domain import FundingProject
from procrun.evidence_retrieval import EVIDENCE_RETRIEVAL_VERSION, extract_source_evidence

EXPECTED_SCHEMA_VERSION = "a21a-evidence-benchmark-v1"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _source(case: dict[str, Any]) -> dict[str, Any]:
    source = case.get("source")
    if not isinstance(source, dict):
        raise ValueError(f"case {case.get('case_id')} lacks source")
    return source


def _gold(case: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    adjudication = case.get("adjudication")
    if not isinstance(adjudication, dict):
        raise ValueError(f"case {case.get('case_id')} lacks adjudication")
    excerpts = adjudication.get("relevant_excerpts")
    if not isinstance(excerpts, list):
        raise ValueError(f"case {case.get('case_id')} lacks relevant_excerpts")
    return tuple(excerpts)


def _validate_gold_span(source_text: str, excerpt: dict[str, Any], case_id: Any) -> tuple[int, int, str]:
    start = excerpt.get("start_offset")
    end = excerpt.get("end_offset")
    text = excerpt.get("text")
    if not isinstance(start, int) or not isinstance(end, int) or not isinstance(text, str):
        raise ValueError(f"case {case_id} has invalid gold excerpt")
    if start < 0 or end <= start or end > len(source_text):
        raise ValueError(f"case {case_id} has out-of-range gold excerpt")
    if source_text[start:end] != text:
        raise ValueError(f"case {case_id} gold excerpt is not an exact source span")
    return start, end, text


def _project(case: dict[str, Any]) -> FundingProject:
    source = _source(case)
    operation_code = str(case.get("operation_code") or "").strip()
    scope = source.get("project_scope_text")
    source_url = source.get("source_url")
    if not operation_code or not isinstance(scope, str) or not scope.strip():
        raise ValueError(f"case {case.get('case_id')} has invalid project source text")
    if not isinstance(source_url, str) or not source_url.strip():
        raise ValueError(f"case {case.get('case_id')} lacks source_url")
    return FundingProject(
        operation_code=operation_code,
        project_title=source.get("project_title"),
        project_scope_text=scope,
        region=source.get("region"),
        municipality=source.get("municipality"),
        nuts_code=source.get("nuts_code"),
        source_url=source_url,
    )


def _overlaps(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return max(a_start, b_start) < min(a_end, b_end)


def build_report(document: dict[str, Any], input_sha256: str) -> dict[str, Any]:
    if document.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        raise ValueError("runner accepts only the frozen A21a evidence benchmark schema")
    if document.get("sealed") is True:
        raise ValueError("sealed A21a holdout input is prohibited")
    if document.get("engine_output_used_for_gold") is not False:
        raise ValueError("A21a gold must be adjudicated without extractor output")
    if document.get("pii_review_status") != "ZERO_PII_CONFIRMED":
        raise ValueError("A21a benchmark requires explicit ZERO_PII_CONFIRMED status")

    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("A21a benchmark requires at least one case")

    seen_case_ids: set[str] = set()
    predicted_excerpt_count = 0
    relevant_predicted_count = 0
    exact_gold_match_count = 0
    gold_excerpt_count = 0
    gold_positive_cases = 0
    gold_positive_cases_with_hit = 0
    gold_negative_cases = 0
    gold_negative_cases_with_prediction = 0
    exact_span_integrity_failures = 0
    provenance_failures = 0
    translation_violations = 0
    determinism_failures = 0
    rows: list[dict[str, Any]] = []

    for case in cases:
        case_id = str(case.get("case_id") or "").strip()
        if not case_id or case_id in seen_case_ids:
            raise ValueError("A21a case_id values must be non-empty and unique")
        seen_case_ids.add(case_id)

        project = _project(case)
        source_text = project.project_scope_text
        gold_spans = tuple(
            _validate_gold_span(source_text, excerpt, case_id) for excerpt in _gold(case)
        )
        gold_excerpt_count += len(gold_spans)

        original_language = str(_source(case).get("language") or "it")
        first = extract_source_evidence(project, original_language=original_language)
        second = extract_source_evidence(project, original_language=original_language)
        third = extract_source_evidence(project, original_language=original_language)
        if first != second or first != third:
            determinism_failures += 1

        predicted_excerpt_count += len(first)
        if gold_spans:
            gold_positive_cases += 1
        else:
            gold_negative_cases += 1
            if first:
                gold_negative_cases_with_prediction += 1

        case_relevant_predictions = 0
        case_exact_matches = 0
        matched_gold_indices: set[int] = set()
        predicted_rows: list[dict[str, Any]] = []

        for predicted in first:
            if source_text[predicted.start_offset : predicted.end_offset] != predicted.original_text:
                exact_span_integrity_failures += 1
            if (
                predicted.source_url != project.source_url
                or predicted.source_field != "project_scope_text"
            ):
                provenance_failures += 1
            if predicted.english_translation is not None:
                translation_violations += 1

            relevant = False
            exact = False
            for index, (gold_start, gold_end, gold_text) in enumerate(gold_spans):
                if _overlaps(predicted.start_offset, predicted.end_offset, gold_start, gold_end):
                    relevant = True
                    matched_gold_indices.add(index)
                if (
                    predicted.start_offset == gold_start
                    and predicted.end_offset == gold_end
                    and predicted.original_text == gold_text
                ):
                    exact = True

            case_relevant_predictions += int(relevant)
            case_exact_matches += int(exact)
            predicted_rows.append(
                {
                    "text": predicted.original_text,
                    "start_offset": predicted.start_offset,
                    "end_offset": predicted.end_offset,
                    "relevant_overlap": relevant,
                    "exact_gold_match": exact,
                }
            )

        relevant_predicted_count += case_relevant_predictions
        exact_gold_match_count += case_exact_matches
        if gold_spans and matched_gold_indices:
            gold_positive_cases_with_hit += 1

        rows.append(
            {
                "case_id": case_id,
                "operation_code": project.operation_code,
                "gold_excerpt_count": len(gold_spans),
                "matched_gold_excerpt_count": len(matched_gold_indices),
                "predicted_excerpt_count": len(first),
                "relevant_predicted_count": case_relevant_predictions,
                "exact_gold_match_count": case_exact_matches,
                "predictions": predicted_rows,
            }
        )

    evidence_precision = (
        relevant_predicted_count / predicted_excerpt_count if predicted_excerpt_count else None
    )
    gold_excerpt_recall = (
        sum(row["matched_gold_excerpt_count"] for row in rows) / gold_excerpt_count
        if gold_excerpt_count
        else None
    )
    gold_positive_case_recall = (
        gold_positive_cases_with_hit / gold_positive_cases if gold_positive_cases else None
    )
    negative_case_false_positive_rate = (
        gold_negative_cases_with_prediction / gold_negative_cases if gold_negative_cases else None
    )

    hard_integrity_pass = (
        exact_span_integrity_failures == 0
        and provenance_failures == 0
        and translation_violations == 0
        and determinism_failures == 0
    )

    return {
        "schema_version": "a21a-evidence-benchmark-report-v1",
        "benchmark_input_sha256": input_sha256,
        "extractor_version": EVIDENCE_RETRIEVAL_VERSION,
        "sealed_holdout_used": False,
        "case_count": len(cases),
        "gold_positive_case_count": gold_positive_cases,
        "gold_negative_case_count": gold_negative_cases,
        "gold_excerpt_count": gold_excerpt_count,
        "predicted_excerpt_count": predicted_excerpt_count,
        "relevant_predicted_count": relevant_predicted_count,
        "exact_gold_match_count": exact_gold_match_count,
        "gold_positive_cases_with_hit": gold_positive_cases_with_hit,
        "gold_negative_cases_with_prediction": gold_negative_cases_with_prediction,
        "evidence_precision": evidence_precision,
        "gold_excerpt_recall": gold_excerpt_recall,
        "gold_positive_case_recall": gold_positive_case_recall,
        "negative_case_false_positive_rate": negative_case_false_positive_rate,
        "exact_span_integrity_failures": exact_span_integrity_failures,
        "provenance_failures": provenance_failures,
        "translation_violations": translation_violations,
        "determinism_failures": determinism_failures,
        "hard_integrity_pass": hard_integrity_pass,
        "threshold_gate_evaluated": False,
        "threshold_gate_note": (
            "Numerical relevance/recall thresholds must be preregistered and frozen before the "
            "fresh final A21a evaluation. This development runner reports metrics but does not "
            "declare product GO."
        ),
        "cases": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    raw = args.input.read_bytes()
    document = json.loads(raw.decode("utf-8"))
    report = build_report(document, _sha256_bytes(raw))
    report["report_canonical_sha256"] = _canonical_sha(report)

    text = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8", newline="")

    print(f"A21A_CASES={report['case_count']}")
    print(f"EXTRACTOR_VERSION={report['extractor_version']}")
    print(f"EVIDENCE_PRECISION={report['evidence_precision']}")
    print(f"GOLD_EXCERPT_RECALL={report['gold_excerpt_recall']}")
    print(f"GOLD_POSITIVE_CASE_RECALL={report['gold_positive_case_recall']}")
    print(f"NEGATIVE_CASE_FALSE_POSITIVE_RATE={report['negative_case_false_positive_rate']}")
    print(f"EXACT_SPAN_INTEGRITY_FAILURES={report['exact_span_integrity_failures']}")
    print(f"PROVENANCE_FAILURES={report['provenance_failures']}")
    print(f"TRANSLATION_VIOLATIONS={report['translation_violations']}")
    print(f"DETERMINISM_FAILURES={report['determinism_failures']}")
    print(f"HARD_INTEGRITY_PASS={report['hard_integrity_pass']}")
    print("SEALED_HOLDOUT_USED=NO")
    print("A21A_THRESHOLD_GATE_EVALUATED=NO")
    print("REPORT_SHA256=" + hashlib.sha256(text.encode("utf-8")).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
