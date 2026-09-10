"""Measure whether already-admitted source metadata can help weak A21a titles.

This is development diagnostics only. It receives no new source fields, promotes no metadata field
to customer evidence, runs no interpretation engines, and never touches the sealed A21 holdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from procrun.a21_identity import a21_projects_by_local_operation_id  # noqa: E402
from procrun.a21a_fallback_context import (  # noqa: E402
    FallbackContextCase,
    summarize_existing_context,
)
from procrun.collectors.opencoesione import to_funding_projects  # noqa: E402
from procrun.collectors.opencoesione_live import collect_open_coesione_live  # noqa: E402
from scripts.run_a21a_title_utility_development_review import reproduce_sample  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", type=Path, required=True)
    args = parser.parse_args()

    review = json.loads(args.review.read_text(encoding="utf-8"))
    if review.get("engine_output_used_for_review") is not False:
        raise ValueError("title review must remain source-only")
    if review.get("sealed_holdout_touched") is not False:
        raise ValueError("sealed holdout must remain untouched")

    sample = reproduce_sample(sample_size=int(review["case_count"]))
    if sample["live_source_sha256"] != review["live_source_sha256"]:
        raise ValueError("live source SHA changed; diagnostic cannot reuse frozen review")
    if sample["canonical_sha256"] != review["sample_canonical_sha256"]:
        raise ValueError("development sample changed; diagnostic cannot reuse frozen review")

    labels = {str(row["case_id"]): str(row["label"]) for row in review["cases"]}
    batch = collect_open_coesione_live()
    mapped = to_funding_projects(batch)
    projects = a21_projects_by_local_operation_id(batch.operations, mapped)
    by_operation_code = {project.operation_code: project for project in projects}

    diagnostic_cases: list[FallbackContextCase] = []
    for case in sample["cases"]:
        case_id = str(case["case_id"])
        source = case["source"]
        operation_code = str(source["operation_code"])
        project = by_operation_code.get(operation_code)
        if project is None:
            raise ValueError(f"frozen sample project missing from reproduced source: {case_id}")
        diagnostic_cases.append(
            FallbackContextCase(
                title_utility=labels[case_id],
                project_title=str(project.project_title or ""),
                specific_objective=project.objective,
                intervention_category=project.theme,
            )
        )

    summary = summarize_existing_context(diagnostic_cases)
    for key, value in summary.items():
        print(f"A21A_EXISTING_CONTEXT_{key.upper()}={value}")
    print(f"A21A_LIVE_SOURCE_SHA256={sample['live_source_sha256']}")
    print(f"A21A_SAMPLE_CANONICAL_SHA256={sample['canonical_sha256']}")
    print("A21A_NEW_SOURCE_FIELDS_RECEIVED=false")
    print("A21A_CONTEXT_PROMOTED_TO_EVIDENCE=false")
    print("A21A_ENGINE_OUTPUT_USED=false")
    print("A21A_SEALED_HOLDOUT_TOUCHED=false")
    print("A21A_FINAL_GATE=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
