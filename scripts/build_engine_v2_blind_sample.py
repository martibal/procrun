from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _score(operation_code: str, seed: str) -> str:
    return hashlib.sha256(f"{seed}\0{operation_code}".encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--size", type=int, default=200)
    parser.add_argument("--seed", default="engine-v2-clean-dev-v1")
    args = parser.parse_args()

    document: dict[str, Any] = json.loads(args.input.read_text(encoding="utf-8"))
    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("sanitized source pool must contain cases")
    if args.size < 1 or args.size > len(cases):
        raise ValueError("sample size must be between 1 and source-pool case count")

    ranked = sorted(
        cases,
        key=lambda case: (
            _score(str(case["operation_code"]), args.seed),
            str(case["operation_code"]),
        ),
    )
    selected = ranked[: args.size]
    sample = {
        "schema_version": "engine-v2-blind-development-sample-v1",
        "selection_seed": args.seed,
        "source_pool_schema_version": document.get("schema_version"),
        "pii_review_status": document.get("pii_review_status"),
        "engine_output_present": False,
        "sample_size": len(selected),
        "cases": [
            {
                "operation_code": case["operation_code"],
                "project_title": case.get("project_title"),
                "project_scope_text": case["project_scope_text"],
                "region": case.get("region"),
                "municipality": case.get("municipality"),
                "nuts_code": case.get("nuts_code"),
                "source_url": case["source_url"],
                "language": case.get("language", "it"),
                "blind_review": {
                    "contains_procurement_relevant_need": None,
                    "relevant_excerpts": [],
                    "adjudication_status": "PENDING_BLIND_REVIEW",
                },
            }
            for case in selected
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(sample, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )
    digest = hashlib.sha256(
        json.dumps(sample, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    print(f"ENGINE_V2_BLIND_SAMPLE_CASES={len(selected)}")
    print(f"ENGINE_V2_BLIND_SAMPLE_SHA256={digest}")
    print("ENGINE_V2_OUTPUT_PRESENT=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
