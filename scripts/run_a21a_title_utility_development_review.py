"""Reproduce the frozen A21a development sample and score its title-utility review.

This is development diagnostics only. It does not run the component extractor, classifier,
matching engine, evidence retriever, or any sealed A21 holdout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from scripts.build_a21a_live_sintesi_development_sample import build_source_pool
from scripts.prepare_a21a_evidence_development_set import build

ALLOWED_LABELS = {"CLEAR", "PARTIAL", "NOT_USEFUL"}


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def reproduce_sample(sample_size: int = 60) -> dict[str, object]:
    source_pool = build_source_pool()
    development_set = build(source_pool, sample_size=sample_size)
    development_set["live_source_id"] = source_pool["source_id"]
    development_set["live_source_sha256"] = source_pool["source_sha256"]
    development_set["live_list_updated_on"] = source_pool["list_updated_on"]
    development_set["canonical_sha256"] = hashlib.sha256(
        _canonical_bytes(development_set)
    ).hexdigest()
    return development_set


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", type=Path, required=True)
    args = parser.parse_args()

    review = json.loads(args.review.read_text(encoding="utf-8"))
    if review.get("engine_output_used_for_review") is not False:
        raise ValueError("development title review must remain source-only")
    if review.get("sealed_holdout_touched") is not False:
        raise ValueError("sealed holdout must remain untouched")

    sample = reproduce_sample(sample_size=int(review["case_count"]))
    if sample["live_source_sha256"] != review["live_source_sha256"]:
        raise ValueError("live source SHA changed; frozen review cannot be reused")
    if sample["canonical_sha256"] != review["sample_canonical_sha256"]:
        raise ValueError("development sample changed; frozen review cannot be reused")

    sample_ids = [str(case["case_id"]) for case in sample["cases"]]
    rows = review.get("cases")
    if not isinstance(rows, list):
        raise ValueError("review cases must be a list")
    labels_by_id: dict[str, str] = {}
    for row in rows:
        case_id = str(row.get("case_id") or "")
        label = str(row.get("label") or "")
        if case_id in labels_by_id:
            raise ValueError(f"duplicate reviewed case: {case_id}")
        if label not in ALLOWED_LABELS:
            raise ValueError(f"invalid title utility label: {label}")
        labels_by_id[case_id] = label
    if set(labels_by_id) != set(sample_ids):
        raise ValueError("review case IDs do not exactly match frozen development sample")

    counts = Counter(labels_by_id.values())
    total = len(sample_ids)
    clear_or_partial = counts["CLEAR"] + counts["PARTIAL"]

    print(f"A21A_TITLE_UTILITY_REVIEW_CASES={total}")
    print(f"A21A_TITLE_UTILITY_CLEAR={counts['CLEAR']}")
    print(f"A21A_TITLE_UTILITY_PARTIAL={counts['PARTIAL']}")
    print(f"A21A_TITLE_UTILITY_NOT_USEFUL={counts['NOT_USEFUL']}")
    print(f"A21A_TITLE_UTILITY_CLEAR_PCT={counts['CLEAR'] / total:.6f}")
    print(f"A21A_TITLE_UTILITY_CLEAR_OR_PARTIAL={clear_or_partial}")
    print(f"A21A_TITLE_UTILITY_CLEAR_OR_PARTIAL_PCT={clear_or_partial / total:.6f}")
    print(f"A21A_TITLE_UTILITY_NOT_USEFUL_PCT={counts['NOT_USEFUL'] / total:.6f}")
    print(f"A21A_LIVE_SOURCE_SHA256={sample['live_source_sha256']}")
    print(f"A21A_SAMPLE_CANONICAL_SHA256={sample['canonical_sha256']}")
    print("A21A_ENGINE_OUTPUT_USED_FOR_REVIEW=false")
    print("A21A_SEALED_HOLDOUT_TOUCHED=false")
    print("A21A_FINAL_GATE=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
