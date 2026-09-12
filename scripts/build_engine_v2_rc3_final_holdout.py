from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

RC3_FINAL_HOLDOUT_SEED = "engine-v2-rc3-final-holdout-v1"


def _rank(operation_code: str, seed: str) -> str:
    return hashlib.sha256(f"{seed}\0{operation_code}".encode()).hexdigest()


def _canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-pool", type=Path, required=True)
    parser.add_argument("--development", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--size", type=int, default=1000)
    parser.add_argument("--seed", default=RC3_FINAL_HOLDOUT_SEED)
    args = parser.parse_args()

    source = json.loads(args.source_pool.read_text(encoding="utf-8"))
    development = json.loads(args.development.read_text(encoding="utf-8"))
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))

    if candidate.get("candidate_id") != "engine-v2-rc3":
        raise RuntimeError("unexpected RC3 candidate")
    if candidate.get("model", {}).get("family") != "charword":
        raise RuntimeError("RC3 family drift")
    if candidate.get("model", {}).get("decision_threshold") != 0.631623:
        raise RuntimeError("RC3 threshold drift")

    source_cases = source.get("cases")
    development_cases = development.get("cases")
    if not isinstance(source_cases, list) or not source_cases:
        raise ValueError("source pool must contain cases")
    if not isinstance(development_cases, list) or not development_cases:
        raise ValueError("RC3 development must contain cases")

    consumed = {str(case["operation_code"]) for case in development_cases}
    if len(consumed) != 2200:
        raise RuntimeError(f"expected 2200 consumed cases, got {len(consumed)}")

    eligible = [
        case for case in source_cases if str(case["operation_code"]) not in consumed
    ]
    if len(eligible) != 2105:
        raise RuntimeError(f"expected 2105 untouched cases, got {len(eligible)}")
    if args.size < 1 or args.size > len(eligible):
        raise ValueError("RC3 holdout size exceeds untouched population")

    ranked = sorted(
        eligible,
        key=lambda case: (
            _rank(str(case["operation_code"]), args.seed),
            str(case["operation_code"]),
        ),
    )
    selected = ranked[: args.size]
    overlap = {str(case["operation_code"]) for case in selected} & consumed
    if overlap:
        raise RuntimeError(f"consumed overlap detected: {sorted(overlap)}")

    holdout = {
        "schema_version": "engine-v2-rc3-final-holdout-source-only-v1",
        "candidate_id": "engine-v2-rc3",
        "selection_seed": args.seed,
        "source_pool_canonical_sha256": _canonical_sha(source),
        "development_canonical_sha256": _canonical_sha(development),
        "candidate_canonical_sha256": _canonical_sha(candidate),
        "consumed_case_count": len(consumed),
        "untouched_population_before_holdout": len(eligible),
        "untouched_population_after_holdout": len(eligible) - len(selected),
        "consumed_overlap_count": 0,
        "engine_output_present": False,
        "pii_review_status": source.get("pii_review_status"),
        "case_count": len(selected),
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
        json.dumps(holdout, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )
    print(f"ENGINE_V2_RC3_FINAL_HOLDOUT_CASES={len(selected)}")
    print(f"ENGINE_V2_RC3_FINAL_HOLDOUT_SHA256={_canonical_sha(holdout)}")
    print(f"ENGINE_V2_RC3_UNTOUCHED_REMAINING={len(eligible) - len(selected)}")
    print("ENGINE_V2_RC3_FINAL_HOLDOUT_OVERLAP=0")
    print("ENGINE_V2_RC3_FINAL_HOLDOUT_ENGINE_OUTPUT_PRESENT=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
