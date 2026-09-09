"""Prepare a blind A21a evidence-retrieval development set from sanctioned sanitized sources."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

INPUT_SCHEMA = "a21a-sanitized-source-pool-v1"
OUTPUT_SCHEMA = "a21a-evidence-development-set-v1"
SEED = "a21a-evidence-development-set-v1"


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _rank(case: dict[str, Any]) -> str:
    operation_code = str(case.get("operation_code") or "").strip()
    scope = str(case.get("project_scope_text") or "")
    return hashlib.sha256(f"{SEED}|{operation_code}|{scope}".encode()).hexdigest()


def build(document: dict[str, Any], *, sample_size: int) -> dict[str, Any]:
    if document.get("schema_version") != INPUT_SCHEMA:
        raise ValueError("unsupported A21a sanitized source pool schema")
    if document.get("pii_review_status") != "ZERO_PII_CONFIRMED":
        raise ValueError("source pool must be explicitly ZERO_PII_CONFIRMED")
    if document.get("engine_output_present") is not False:
        raise ValueError("source pool must not contain extractor or classifier output")

    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("source pool requires cases")
    if sample_size < 1 or sample_size > len(cases):
        raise ValueError("invalid sample size")

    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("case must be an object")
        operation_code = str(case.get("operation_code") or "").strip()
        scope = case.get("project_scope_text")
        source_url = case.get("source_url")
        if not operation_code or operation_code in seen:
            raise ValueError("operation_code values must be non-empty and unique")
        if not isinstance(scope, str) or not scope.strip():
            raise ValueError(f"{operation_code}: project_scope_text required")
        if not isinstance(source_url, str) or not source_url.strip():
            raise ValueError(f"{operation_code}: source_url required")
        seen.add(operation_code)
        normalized.append(
            {
                "operation_code": operation_code,
                "project_title": case.get("project_title"),
                "project_scope_text": scope,
                "region": case.get("region"),
                "municipality": case.get("municipality"),
                "nuts_code": case.get("nuts_code"),
                "source_url": source_url,
                "language": str(case.get("language") or "it"),
            }
        )

    selected = sorted(normalized, key=_rank)[:sample_size]
    output_cases = []
    for index, case in enumerate(selected, start=1):
        output_cases.append(
            {
                "case_id": f"A21A-DEV-{index:04d}",
                "operation_code": case["operation_code"],
                "source": case,
                "adjudication": {
                    "relevant_excerpts": [],
                    "adjudication_status": "PENDING_BLIND_REVIEW",
                },
            }
        )

    return {
        "schema_version": OUTPUT_SCHEMA,
        "sealed": False,
        "engine_output_used_for_gold": False,
        "pii_review_status": "ZERO_PII_CONFIRMED",
        "selection_seed": SEED,
        "source_pool_case_count": len(normalized),
        "case_count": len(output_cases),
        "cases": output_cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-size", type=int, required=True)
    args = parser.parse_args()

    raw = args.input.read_bytes()
    document = json.loads(raw.decode("utf-8"))
    result = build(document, sample_size=args.sample_size)
    result["source_pool_sha256"] = hashlib.sha256(raw).hexdigest()
    result["canonical_sha256"] = hashlib.sha256(_canonical_bytes(result)).hexdigest()
    text = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8", newline="")
    print(f"A21A_DEVELOPMENT_CASES={result['case_count']}")
    print(f"A21A_SOURCE_POOL_CASES={result['source_pool_case_count']}")
    print(f"A21A_CANONICAL_SHA256={result['canonical_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
