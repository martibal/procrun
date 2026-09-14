from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

RC2_FINAL_HOLDOUT_SEED = "engine-v2-rc2-final-holdout-v1"


def _rank(operation_code: str, seed: str) -> str:
    return hashlib.sha256(f"{seed}\0{operation_code}".encode()).hexdigest()


def _canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _codes(document: dict[str, Any], name: str) -> set[str]:
    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError(f"{name} must contain cases")
    return {str(case["operation_code"]) for case in cases}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-pool", type=Path, required=True)
    parser.add_argument("--rc1-development", type=Path, required=True)
    parser.add_argument("--rc1-holdout", type=Path, required=True)
    parser.add_argument("--rc2-development", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--size", type=int, default=800)
    parser.add_argument("--seed", default=RC2_FINAL_HOLDOUT_SEED)
    args = parser.parse_args()

    source = json.loads(args.source_pool.read_text(encoding="utf-8"))
    rc1_dev = json.loads(args.rc1_development.read_text(encoding="utf-8"))
    rc1_holdout = json.loads(args.rc1_holdout.read_text(encoding="utf-8"))
    rc2_dev = json.loads(args.rc2_development.read_text(encoding="utf-8"))
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))

    if candidate.get("candidate_id") != "engine-v2-rc2":
        raise RuntimeError("unexpected frozen candidate")
    if candidate.get("model", {}).get("decision_threshold") != 0.569344:
        raise RuntimeError("RC2 threshold drift")

    source_cases = source.get("cases")
    if not isinstance(source_cases, list) or not source_cases:
        raise ValueError("source pool must contain cases")

    rc1_dev_codes = _codes(rc1_dev, "RC1 development")
    rc1_holdout_codes = _codes(rc1_holdout, "RC1 holdout")
    rc2_dev_codes = _codes(rc2_dev, "RC2 development")
    excluded = rc1_dev_codes | rc1_holdout_codes | rc2_dev_codes
    if len(excluded) != 1400:
        raise RuntimeError(f"expected 1400 consumed cases, got {len(excluded)}")

    eligible = [case for case in source_cases if str(case["operation_code"]) not in excluded]
    if args.size < 1 or args.size > len(eligible):
        raise ValueError("RC2 final holdout size exceeds eligible population")

    ranked = sorted(
        eligible,
        key=lambda case: (
            _rank(str(case["operation_code"]), args.seed),
            str(case["operation_code"]),
        ),
    )
    selected = ranked[: args.size]
    selected_codes = {str(case["operation_code"]) for case in selected}
    overlap = selected_codes & excluded
    if overlap:
        raise RuntimeError(f"consumed-case overlap detected: {sorted(overlap)}")

    document = {
        "schema_version": "engine-v2-rc2-final-holdout-source-only-v1",
        "candidate_id": "engine-v2-rc2",
        "selection_seed": args.seed,
        "source_pool_canonical_sha256": _canonical_sha(source),
        "candidate_canonical_sha256": _canonical_sha(candidate),
        "rc1_development_canonical_sha256": _canonical_sha(rc1_dev),
        "rc1_holdout_canonical_sha256": _canonical_sha(rc1_holdout),
        "rc2_development_canonical_sha256": _canonical_sha(rc2_dev),
        "consumed_case_count": len(excluded),
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
        json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )
    print(f"ENGINE_V2_RC2_FINAL_HOLDOUT_CASES={len(selected)}")
    print(f"ENGINE_V2_RC2_FINAL_HOLDOUT_SHA256={_canonical_sha(document)}")
    print(f"ENGINE_V2_RC2_FINAL_HOLDOUT_EXCLUDED={len(excluded)}")
    print("ENGINE_V2_RC2_FINAL_HOLDOUT_OVERLAP=0")
    print("ENGINE_V2_RC2_FINAL_HOLDOUT_ENGINE_OUTPUT_PRESENT=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
