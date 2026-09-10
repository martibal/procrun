"""Build a blind A21a development sample from the approved OpenCoesione SINTESI_PROG route.

The script deliberately creates source-only cases. It does not run component extraction,
classification, matching, or evidence retrieval before the blind review set is frozen.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from prepare_a21a_evidence_development_set import build

from procrun.a21_identity import a21_projects_by_local_operation_id
from procrun.collectors.opencoesione import to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live

SOURCE_POOL_SCHEMA = "a21a-sanitized-source-pool-v1"


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def build_source_pool() -> dict[str, object]:
    batch = collect_open_coesione_live()
    mapped_projects = to_funding_projects(batch)
    projects = a21_projects_by_local_operation_id(batch.operations, mapped_projects)

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


def _utility_counts(cases: list[dict[str, object]]) -> dict[str, int]:
    scope_equals_title = 0
    scope_distinct_from_title = 0
    scope_length_ge_100 = 0
    scope_length_ge_200 = 0
    for case in cases:
        title = str(case["project_title"]).strip()
        scope = str(case["project_scope_text"]).strip()
        if scope == title:
            scope_equals_title += 1
        else:
            scope_distinct_from_title += 1
        if len(scope) >= 100:
            scope_length_ge_100 += 1
        if len(scope) >= 200:
            scope_length_ge_200 += 1
    return {
        "scope_equals_title": scope_equals_title,
        "scope_distinct_from_title": scope_distinct_from_title,
        "scope_length_ge_100": scope_length_ge_100,
        "scope_length_ge_200": scope_length_ge_200,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-size", type=int, default=60)
    args = parser.parse_args()

    source_pool = build_source_pool()
    source_cases = source_pool["cases"]
    assert isinstance(source_cases, list)
    source_utility = _utility_counts(source_cases)

    development_set = build(source_pool, sample_size=args.sample_size)
    sample_cases = development_set["cases"]
    assert isinstance(sample_cases, list)
    sample_source_cases = [case["source"] for case in sample_cases]
    sample_utility = _utility_counts(sample_source_cases)

    development_set["live_source_id"] = source_pool["source_id"]
    development_set["live_source_sha256"] = source_pool["source_sha256"]
    development_set["live_list_updated_on"] = source_pool["list_updated_on"]
    development_set["canonical_sha256"] = hashlib.sha256(
        _canonical_bytes(development_set)
    ).hexdigest()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(development_set, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )

    # Deliberately log only counts/hashes, never project title or SINTESI_PROG text.
    print(f"A21A_LIVE_SOURCE_CASES={source_pool['case_count']}")
    print(f"A21A_BLIND_SAMPLE_CASES={development_set['case_count']}")
    print(f"A21A_LIVE_SCOPE_EQUALS_TITLE={source_utility['scope_equals_title']}")
    print(
        "A21A_LIVE_SCOPE_DISTINCT_FROM_TITLE="
        f"{source_utility['scope_distinct_from_title']}"
    )
    print(f"A21A_LIVE_SCOPE_LENGTH_GE_100={source_utility['scope_length_ge_100']}")
    print(f"A21A_LIVE_SCOPE_LENGTH_GE_200={source_utility['scope_length_ge_200']}")
    print(f"A21A_SAMPLE_SCOPE_EQUALS_TITLE={sample_utility['scope_equals_title']}")
    print(
        "A21A_SAMPLE_SCOPE_DISTINCT_FROM_TITLE="
        f"{sample_utility['scope_distinct_from_title']}"
    )
    print(f"A21A_SAMPLE_SCOPE_LENGTH_GE_100={sample_utility['scope_length_ge_100']}")
    print(f"A21A_SAMPLE_SCOPE_LENGTH_GE_200={sample_utility['scope_length_ge_200']}")
    print(f"A21A_LIVE_SOURCE_SHA256={source_pool['source_sha256']}")
    print(f"A21A_LIVE_LIST_UPDATED_ON={source_pool['list_updated_on']}")
    print(f"A21A_SAMPLE_CANONICAL_SHA256={development_set['canonical_sha256']}")
    print("A21A_ENGINE_OUTPUT_USED_FOR_GOLD=false")
    print("A21A_SEALED_HOLDOUT_TOUCHED=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
