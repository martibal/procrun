"""Build a source-only blind sample for title + specific-objective utility review.

Development diagnostics only. The output contains only already-approved source fields for the
14 frozen A21a development cases whose title alone was previously judged NOT_USEFUL. It runs no
classification, matching, procurement-state, or evidence-retrieval engine and never touches the
sealed A21 holdout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from procrun.a21_identity import a21_projects_by_local_operation_id  # noqa: E402
from procrun.collectors.opencoesione import to_funding_projects  # noqa: E402
from procrun.collectors.opencoesione_live import collect_open_coesione_live  # noqa: E402
from scripts.run_a21a_title_utility_development_review import reproduce_sample  # noqa: E402


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def build(review_path: Path) -> dict[str, object]:
    review = json.loads(review_path.read_text(encoding="utf-8"))
    if review.get("engine_output_used_for_review") is not False:
        raise ValueError("title review must remain source-only")
    if review.get("sealed_holdout_touched") is not False:
        raise ValueError("sealed holdout must remain untouched")

    sample = reproduce_sample(sample_size=int(review["case_count"]))
    if sample["live_source_sha256"] != review["live_source_sha256"]:
        raise ValueError("live source SHA changed; blind sample cannot reuse frozen review")
    if sample["canonical_sha256"] != review["sample_canonical_sha256"]:
        raise ValueError("development sample changed; blind sample cannot reuse frozen review")

    weak_ids = {
        str(row["case_id"])
        for row in review["cases"]
        if str(row["label"]) == "NOT_USEFUL"
    }
    if len(weak_ids) != 14:
        raise ValueError(f"expected 14 frozen weak-title cases, found {len(weak_ids)}")

    batch = collect_open_coesione_live()
    mapped = to_funding_projects(batch)
    projects = a21_projects_by_local_operation_id(batch.operations, mapped)
    by_operation_code = {project.operation_code: project for project in projects}

    cases: list[dict[str, object]] = []
    for case in sample["cases"]:
        case_id = str(case["case_id"])
        if case_id not in weak_ids:
            continue
        source = case["source"]
        operation_code = str(source["operation_code"])
        project = by_operation_code.get(operation_code)
        if project is None:
            raise ValueError(f"frozen sample project missing from reproduced source: {case_id}")
        objective = (project.objective or "").strip()
        if not objective:
            raise ValueError(f"specific objective missing for frozen weak-title case: {case_id}")
        cases.append(
            {
                "case_id": case_id,
                "project_title": str(project.project_title or "").strip(),
                "specific_objective": objective,
                "source_url": project.source_url,
                "source_language": "it",
            }
        )

    cases.sort(key=lambda row: str(row["case_id"]))
    output: dict[str, object] = {
        "sample_version": "a21a-title-objective-blind-review-sample-v1",
        "purpose": (
            "Development-only blind review of whether exact project title plus exact specific "
            "objective provides useful source context for the 14 frozen weak-title cases."
        ),
        "case_count": len(cases),
        "cases": cases,
        "live_source_sha256": sample["live_source_sha256"],
        "parent_sample_canonical_sha256": sample["canonical_sha256"],
        "engine_output_present": False,
        "sealed_holdout_touched": False,
        "new_source_fields_received": False,
        "context_promoted_to_evidence": False,
    }
    output["canonical_sha256"] = hashlib.sha256(_canonical_bytes(output)).hexdigest()
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    output = build(args.review)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"A21A_TITLE_OBJECTIVE_BLIND_CASES={output['case_count']}")
    print(f"A21A_TITLE_OBJECTIVE_CANONICAL_SHA256={output['canonical_sha256']}")
    print(f"A21A_LIVE_SOURCE_SHA256={output['live_source_sha256']}")
    print("A21A_ENGINE_OUTPUT_PRESENT=false")
    print("A21A_SEALED_HOLDOUT_TOUCHED=false")
    print("A21A_NEW_SOURCE_FIELDS_RECEIVED=false")
    print("A21A_CONTEXT_PROMOTED_TO_EVIDENCE=false")
    print("A21A_FINAL_GATE=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
