"""Run the deterministic component extractor against the frozen A21 development benchmark.

This is a post-remediation diagnostic only. It deliberately refuses a sealed holdout document and
never invokes the local-model fallback or procurement/state classifier.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from procrun.component_engine import COMPONENT_RULE_VERSION, ComponentDomain, extract_components
from procrun.domain import FundingProject

EXPECTED_SCHEMA_VERSION = "a21-final-benchmark-v1"
EXPECTED_CASE_COUNT = 200


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _source_value(case: dict[str, Any], key: str) -> Any:
    source = case.get("source_context")
    if isinstance(source, dict) and key in source:
        return source[key]
    return case.get(key)


def _gold_categories(case: dict[str, Any]) -> frozenset[str]:
    adjudication = case.get("adjudication")
    if not isinstance(adjudication, dict):
        raise ValueError(f"case {case.get('case_number')} lacks adjudication")
    components = adjudication.get("components")
    if not isinstance(components, list):
        raise ValueError(f"case {case.get('case_number')} lacks adjudicated components")

    categories: set[str] = set()
    for component in components:
        if not isinstance(component, dict):
            raise ValueError("adjudicated component must be an object")
        domain = str(component.get("domain") or "").strip()
        category = str(component.get("category") or "").strip()
        if not domain or not category:
            raise ValueError(
                f"case {case.get('case_number')} contains a component without domain/category"
            )
        namespaced = category if ":" in category else f"{domain}:{category}"
        categories.add(namespaced)
    return frozenset(categories)


def _domains(case: dict[str, Any]) -> tuple[ComponentDomain, ...]:
    adjudication = case.get("adjudication")
    if not isinstance(adjudication, dict):
        raise ValueError("case lacks adjudication")
    values = adjudication.get("domains")
    if not isinstance(values, list):
        raise ValueError("case lacks adjudicated domains")
    return tuple(ComponentDomain(str(value)) for value in values)


def _project(case: dict[str, Any]) -> FundingProject:
    operation_code = str(case.get("operation_code") or "").strip()
    scope = _source_value(case, "project_scope_text")
    if not operation_code or not isinstance(scope, str) or not scope.strip():
        raise ValueError(f"invalid benchmark source case {case.get('case_number')}")
    return FundingProject(
        operation_code=operation_code,
        project_title=_source_value(case, "project_title"),
        project_scope_text=scope,
        region=_source_value(case, "region"),
        municipality=_source_value(case, "municipality"),
        nuts_code=_source_value(case, "nuts_code"),
        source_url=str(_source_value(case, "source_url") or "https://example.invalid/a21-benchmark"),
    )


def build_report(document: dict[str, Any], input_sha256: str) -> dict[str, Any]:
    if document.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        raise ValueError("runner accepts only the frozen A21 200-case benchmark schema")
    if document.get("sealed") is True:
        raise ValueError("sealed holdout input is prohibited")
    if document.get("engine_output_used") is not False:
        raise ValueError("benchmark must be engine-blind")

    cases = document.get("cases")
    if not isinstance(cases, list) or len(cases) != EXPECTED_CASE_COUNT:
        raise ValueError(f"benchmark must contain exactly {EXPECTED_CASE_COUNT} cases")

    tp = fp = fn = 0
    exact_cases = 0
    fallback_cases = 0
    zero_gold_cases = 0
    zero_gold_false_positive_cases = 0
    by_domain: dict[str, Counter[str]] = defaultdict(Counter)
    rows: list[dict[str, Any]] = []

    for case in cases:
        gold = _gold_categories(case)
        domains = _domains(case)
        project = _project(case)

        if domains:
            extraction = extract_components(project, domains)
            predicted = frozenset(item.component.category for item in extraction.components)
            fallback_required = extraction.model_fallback_required
        else:
            predicted = frozenset()
            fallback_required = False

        case_tp = len(gold & predicted)
        case_fp = len(predicted - gold)
        case_fn = len(gold - predicted)
        tp += case_tp
        fp += case_fp
        fn += case_fn
        exact_cases += int(predicted == gold)
        fallback_cases += int(fallback_required)

        if not gold:
            zero_gold_cases += 1
            zero_gold_false_positive_cases += int(bool(predicted))

        for category in gold | predicted:
            domain = category.split(":", 1)[0]
            by_domain[domain]["tp"] += int(category in gold and category in predicted)
            by_domain[domain]["fp"] += int(category in predicted and category not in gold)
            by_domain[domain]["fn"] += int(category in gold and category not in predicted)

        rows.append(
            {
                "case_number": case.get("case_number"),
                "operation_code": project.operation_code,
                "gold_categories": sorted(gold),
                "predicted_categories": sorted(predicted),
                "true_positive": case_tp,
                "false_positive": case_fp,
                "false_negative": case_fn,
                "exact_semantic_match": predicted == gold,
                "model_fallback_required": fallback_required,
            }
        )

    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None

    return {
        "schema_version": "a21-component-extraction-benchmark-report-v1",
        "benchmark_input_sha256": input_sha256,
        "component_rule_version": COMPONENT_RULE_VERSION,
        "local_model_used": False,
        "procurement_classifier_used": False,
        "project_state_classifier_used": False,
        "sealed_holdout_used": False,
        "case_count": len(cases),
        "gold_component_count": tp + fn,
        "predicted_component_count": tp + fp,
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "component_precision": precision,
        "component_recall": recall,
        "exact_semantic_case_match_count": exact_cases,
        "exact_semantic_case_match_rate": exact_cases / len(cases),
        "model_fallback_required_case_count": fallback_cases,
        "zero_gold_case_count": zero_gold_cases,
        "zero_gold_false_positive_case_count": zero_gold_false_positive_cases,
        "by_domain": {key: dict(sorted(value.items())) for key, value in sorted(by_domain.items())},
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

    print(f"A21_COMPONENT_BENCHMARK_CASES={report['case_count']}")
    print(f"COMPONENT_RULE_VERSION={report['component_rule_version']}")
    print(f"GOLD_COMPONENTS={report['gold_component_count']}")
    print(f"PREDICTED_COMPONENTS={report['predicted_component_count']}")
    print(f"TP={report['true_positive']}")
    print(f"FP={report['false_positive']}")
    print(f"FN={report['false_negative']}")
    print(f"COMPONENT_PRECISION={report['component_precision']}")
    print(f"COMPONENT_RECALL={report['component_recall']}")
    print(f"EXACT_CASE_MATCH_RATE={report['exact_semantic_case_match_rate']}")
    print(f"MODEL_FALLBACK_REQUIRED_CASES={report['model_fallback_required_case_count']}")
    print(f"ZERO_GOLD_FALSE_POSITIVE_CASES={report['zero_gold_false_positive_case_count']}")
    print("LOCAL_MODEL_USED=NO")
    print("SEALED_HOLDOUT_USED=NO")
    print("REPORT_SHA256=" + hashlib.sha256(text.encode("utf-8")).hexdigest())
    print("A21_COMPONENT_EXTRACTION_BENCHMARK=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
