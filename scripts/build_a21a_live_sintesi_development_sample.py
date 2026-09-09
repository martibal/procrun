"""Build a blind A21a development sample from the approved OpenCoesione SINTESI_PROG route.

The script deliberately creates source-only cases. It does not run component extraction,
classification, matching, or evidence retrieval before the blind review set is frozen.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from procrun.collectors.opencoesione import to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live
from scripts.prepare_a21a_evidence_development_set import build

SOURCE_POOL_SCHEMA = "a21a-sanitized-source-pool-v1"


def build_source_pool() -> dict[str, object]:
    batch = collect_open_coesione_live()
    projects = to_funding_projects(batch)

    cases: list[dict[str, object]] = []
    for project in projects:
        cases.append(
            {
                "operation_code": project.operation_code,
                "project_title": project.project_title,
                "project_scope_text": project.project_scope_text,
                "region": project.region,
                "municipality": project.municipality,
                "nuts_code": project.nuts_code,
                "source_url": project.source_url,
                "language": "it",
            }
        )

    return {
        "schema_version": SOURCE_POOL_SCHEMA,
        "pii_review_status": "ZERO_PII_CONFIRMED",
        "engine_output_present": False,
        "source_id": "opencoesione_2021_2027_operations",
        "source_sha256": batch.source_sha256,
        "list_updated_on": batch.list_updated_on.isoformat(),
        "case_count": len(cases),
        "cases": cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-size", type=int, default=60)
    args = parser.parse_args()

    source_pool = build_source_pool()
    development_set = build(source_pool, sample_size=args.sample_size)
    development_set["live_source_id"] = source_pool["source_id"]
    development_set["live_source_sha256"] = source_pool["source_sha256"]
    development_set["live_list_updated_on"] = source_pool["list_updated_on"]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(development_set, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )

    # Deliberately log only counts/hashes, never project title or SINTESI_PROG text.
    print(f"A21A_LIVE_SOURCE_CASES={source_pool['case_count']}")
    print(f"A21A_BLIND_SAMPLE_CASES={development_set['case_count']}")
    print(f"A21A_LIVE_SOURCE_SHA256={source_pool['source_sha256']}")
    print(f"A21A_LIVE_LIST_UPDATED_ON={source_pool['list_updated_on']}")
    print(f"A21A_SAMPLE_CANONICAL_SHA256={development_set['canonical_sha256']}")
    print("A21A_ENGINE_OUTPUT_USED_FOR_GOLD=false")
    print("A21A_SEALED_HOLDOUT_TOUCHED=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
