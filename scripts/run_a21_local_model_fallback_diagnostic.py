"""Run the pinned local-model fallback on the frozen A21 200-case development benchmark.

Diagnostic only. This runner refuses sealed holdout input, never invokes procurement/state
classification, and only evaluates cases that the deterministic v2 extractor marks for fallback.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from procrun.component_engine import COMPONENT_RULE_VERSION, ComponentDomain, extract_components
from procrun.domain import FundingProject
from procrun.llama_adapter import (
    LlamaAdapterError,
    LlamaBenchmarkResult,
    PreparedLlamaRuntime,
    prepare_llama_benchmark_runtime,
    run_llama_component_benchmark,
)
from procrun.model_fallback import (
    ModelFallbackError,
    apply_model_proposals,
    build_local_model_request,
)
from procrun.model_registry import SELECTED_COMPONENT_MODEL

EXPECTED_BENCHMARK_SCHEMA = "a21-final-benchmark-v1"
EXPECTED_DETERMINISTIC_SCHEMA = "a21-component-extraction-benchmark-report-v1"
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


def _domains(case: dict[str, Any]) -> tuple[ComponentDomain, ...]:
    adjudication = case.get("adjudication")
    if not isinstance(adjudication, dict):
        raise ValueError("case lacks adjudication")
    values = adjudication.get("domains")
    if not isinstance(values, list):
        raise ValueError("case lacks adjudicated domains")
    return tuple(ComponentDomain(str(value)) for value in values)


def _gold_categories(case: dict[str, Any]) -> frozenset[str]:
    adjudication = case.get("adjudication")
    if not isinstance(adjudication, dict):
        raise ValueError("case lacks adjudication")
    components = adjudication.get("components")
    if not isinstance(components, list):
        raise ValueError("case lacks adjudicated components")
    values: set[str] = set()
    for component in components:
        if not isinstance(component, dict):
            raise ValueError("adjudicated component must be an object")
        domain = str(component.get("domain") or "").strip()
        category = str(component.get("category") or "").strip()
        if not domain or not category:
            raise ValueError("adjudicated component lacks domain/category")
        values.add(category if ":" in category else f"{domain}:{category}")
    return frozenset(values)


def _predicted_categories(extraction: Any) -> frozenset[str]:
    return frozenset(item.component.category for item in extraction.components)


def _validate_inputs(
    benchmark: dict[str, Any],
    benchmark_sha256: str,
    deterministic: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    if benchmark.get("schema_version") != EXPECTED_BENCHMARK_SCHEMA:
        raise ValueError("runner accepts only the frozen A21 200-case benchmark schema")
    if benchmark.get("sealed") is True:
        raise ValueError("sealed holdout input is prohibited")
    if benchmark.get("engine_output_used") is not False:
        raise ValueError("benchmark must be engine-blind")
    cases = benchmark.get("cases")
    if not isinstance(cases, list) or len(cases) != EXPECTED_CASE_COUNT:
        raise ValueError(f"benchmark must contain exactly {EXPECTED_CASE_COUNT} cases")

    if deterministic.get("schema_version") != EXPECTED_DETERMINISTIC_SCHEMA:
        raise ValueError("deterministic report schema mismatch")
    if deterministic.get("benchmark_input_sha256") != benchmark_sha256:
        raise ValueError("deterministic report is not bound to this benchmark input")
    if deterministic.get("component_rule_version") != COMPONENT_RULE_VERSION:
        raise ValueError("deterministic report component rule version mismatch")
    if deterministic.get("local_model_used") is not False:
        raise ValueError("deterministic report must not already contain local-model output")
    if deterministic.get("sealed_holdout_used") is not False:
        raise ValueError("deterministic report indicates sealed holdout use")
    if deterministic.get("case_count") != EXPECTED_CASE_COUNT:
        raise ValueError("deterministic report case count mismatch")

    rows = deterministic.get("cases")
    if not isinstance(rows, list) or len(rows) != EXPECTED_CASE_COUNT:
        raise ValueError("deterministic report must contain one row per benchmark case")
    indexed: dict[int, dict[str, Any]] = {}
    for row in rows:
        number = row.get("case_number")
        if not isinstance(number, int) or number in indexed:
            raise ValueError("deterministic report contains invalid/duplicate case_number")
        indexed[number] = row
    return cases, indexed


def build_diagnostic_report(
    benchmark: dict[str, Any],
    benchmark_sha256: str,
    deterministic: dict[str, Any],
    deterministic_sha256: str,
    runtime: PreparedLlamaRuntime,
    *,
    cache_dir: Path | None = None,
) -> dict[str, Any]:
    cases, deterministic_rows = _validate_inputs(
        benchmark,
        benchmark_sha256,
        deterministic,
    )

    tp = fp = fn = 0
    exact_cases = 0
    fallback_case_count = 0
    inference_error_count = 0
    remaining_fallback_count = 0
    zero_gold_false_positive_cases = 0
    rows: list[dict[str, Any]] = []

    for case in cases:
        case_number = case.get("case_number")
        if not isinstance(case_number, int) or case_number not in deterministic_rows:
            raise ValueError("benchmark/deterministic case_number mismatch")
        deterministic_row = deterministic_rows[case_number]
        project = _project(case)
        if deterministic_row.get("operation_code") != project.operation_code:
            raise ValueError(f"operation_code mismatch for case {case_number}")
        domains = _domains(case)
        extraction = extract_components(project, domains) if domains else None
        deterministic_predicted = (
            _predicted_categories(extraction) if extraction is not None else frozenset()
        )
        recorded_predicted = frozenset(deterministic_row.get("predicted_categories") or [])
        if deterministic_predicted != recorded_predicted:
            raise ValueError(f"deterministic extraction drift for case {case_number}")

        fallback_required = bool(
            extraction is not None and extraction.model_fallback_required
        )
        if fallback_required != bool(deterministic_row.get("model_fallback_required")):
            raise ValueError(f"fallback flag drift for case {case_number}")

        combined = deterministic_predicted
        accepted: list[dict[str, Any]] = []
        inference_error: str | None = None
        cache_hit: bool | None = None
        elapsed_seconds: float | None = None
        still_requires_fallback = False

        if fallback_required:
            fallback_case_count += 1
            assert extraction is not None
            request = build_local_model_request(project, extraction)
            try:
                result: LlamaBenchmarkResult = run_llama_component_benchmark(
                    request,
                    runtime,
                    cache_dir=cache_dir,
                )
                merged = apply_model_proposals(
                    project,
                    extraction,
                    result.batch,
                    expected_model=runtime.model_spec.identity,
                )
                combined = _predicted_categories(merged.extraction)
                accepted = [
                    item.model_dump(mode="json") for item in merged.accepted_proposals
                ]
                cache_hit = result.cache_hit
                elapsed_seconds = result.elapsed_seconds
                still_requires_fallback = merged.extraction.model_fallback_required
                remaining_fallback_count += int(still_requires_fallback)
            except (LlamaAdapterError, ModelFallbackError) as exc:
                inference_error_count += 1
                still_requires_fallback = True
                remaining_fallback_count += 1
                inference_error = f"{type(exc).__name__}: {exc}"

        gold = _gold_categories(case)
        case_tp = len(gold & combined)
        case_fp = len(combined - gold)
        case_fn = len(gold - combined)
        tp += case_tp
        fp += case_fp
        fn += case_fn
        exact_cases += int(combined == gold and inference_error is None)
        if not gold and combined:
            zero_gold_false_positive_cases += 1

        rows.append(
            {
                "case_number": case_number,
                "operation_code": project.operation_code,
                "gold_categories": sorted(gold),
                "deterministic_categories": sorted(deterministic_predicted),
                "combined_categories": sorted(combined),
                "fallback_required": fallback_required,
                "accepted_model_proposals": accepted,
                "still_requires_fallback": still_requires_fallback,
                "cache_hit": cache_hit,
                "elapsed_seconds": elapsed_seconds,
                "inference_error": inference_error,
                "true_positive": case_tp,
                "false_positive": case_fp,
                "false_negative": case_fn,
                "exact_semantic_match": combined == gold and inference_error is None,
            }
        )

    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    return {
        "schema_version": "a21-local-model-fallback-diagnostic-v1",
        "diagnostic_only": True,
        "benchmark_input_sha256": benchmark_sha256,
        "deterministic_report_sha256": deterministic_sha256,
        "component_rule_version": COMPONENT_RULE_VERSION,
        "model_id": runtime.model_spec.identity.model_id,
        "model_artifact_sha256": runtime.model_spec.identity.artifact_sha256,
        "llama_cli_sha256": runtime.llama_cli_sha256,
        "sealed_holdout_used": False,
        "procurement_classifier_used": False,
        "project_state_classifier_used": False,
        "case_count": len(cases),
        "fallback_case_count": fallback_case_count,
        "inference_error_count": inference_error_count,
        "remaining_fallback_case_count": remaining_fallback_count,
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "component_precision": precision,
        "component_recall": recall,
        "exact_semantic_case_match_count": exact_cases,
        "exact_semantic_case_match_rate": exact_cases / len(cases),
        "zero_gold_false_positive_case_count": zero_gold_false_positive_cases,
        "cases": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--deterministic-report", type=Path, required=True)
    parser.add_argument("--llama-cli", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path)
    args = parser.parse_args()

    benchmark_raw = args.benchmark.read_bytes()
    deterministic_raw = args.deterministic_report.read_bytes()
    benchmark = json.loads(benchmark_raw.decode("utf-8"))
    deterministic = json.loads(deterministic_raw.decode("utf-8"))

    runtime = prepare_llama_benchmark_runtime(
        llama_cli_path=args.llama_cli,
        model_path=args.model,
        model_spec=SELECTED_COMPONENT_MODEL,
    )
    report = build_diagnostic_report(
        benchmark,
        _sha256_bytes(benchmark_raw),
        deterministic,
        _sha256_bytes(deterministic_raw),
        runtime,
        cache_dir=args.cache_dir,
    )
    report["report_canonical_sha256"] = _canonical_sha(report)
    text = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8", newline="")

    print(f"A21_FALLBACK_CASES={report['fallback_case_count']}")
    print(f"MODEL_ID={report['model_id']}")
    print(f"MODEL_SHA256={report['model_artifact_sha256']}")
    print(f"LLAMA_CLI_SHA256={report['llama_cli_sha256']}")
    print(f"INFERENCE_ERRORS={report['inference_error_count']}")
    print(f"REMAINING_FALLBACK_CASES={report['remaining_fallback_case_count']}")
    print(f"TP={report['true_positive']}")
    print(f"FP={report['false_positive']}")
    print(f"FN={report['false_negative']}")
    print(f"COMPONENT_PRECISION={report['component_precision']}")
    print(f"COMPONENT_RECALL={report['component_recall']}")
    print(f"ZERO_GOLD_FALSE_POSITIVE_CASES={report['zero_gold_false_positive_case_count']}")
    print("PROCUREMENT_CLASSIFIER_USED=NO")
    print("PROJECT_STATE_CLASSIFIER_USED=NO")
    print("SEALED_HOLDOUT_USED=NO")
    print("REPORT_SHA256=" + hashlib.sha256(text.encode("utf-8")).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
