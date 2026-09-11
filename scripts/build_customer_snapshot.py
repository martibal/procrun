#!/usr/bin/env python3
"""Build the real customer-safe runway snapshot for local/web use.

This uses the same approved OpenCoesione ingress, complete TED Italy collection,
evidence-bounded runway logic and frozen customer read-model contract as the
infrastructure-closure proof. It intentionally does not persist the intelligence
ledger or run the three-pass closure proof; its only purpose is to materialize the
customer-safe JSONL that the web application consumes.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from procrun.a21_identity import a21_projects_by_local_operation_id
from procrun.collectors.opencoesione import to_funding_projects
from procrun.collectors.opencoesione_live import collect_open_coesione_live
from procrun.ledger import content_sha256
from procrun.production_delivery import (
    PRODUCTION_DELIVERY_VERSION,
    build_live_runway_results,
    collect_complete_ted_italy,
    write_customer_safe_jsonl,
)
from procrun.read_model import READ_MODEL_VERSION, build_runway_read_model


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("web/data/customer-runway.jsonl"),
        help="Customer-safe JSONL consumed by the web app.",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("web/data/customer-runway.summary.json"),
        help="Local snapshot metadata.",
    )
    args = parser.parse_args()

    started = datetime.now(timezone.utc)
    cutoff = started.date()

    print("[1/4] Collecting approved OpenCoesione project resource...", flush=True)
    batch = collect_open_coesione_live()
    logical_projects = a21_projects_by_local_operation_id(
        batch.operations,
        to_funding_projects(batch),
    )
    print(f"      logical projects: {len(logical_projects)}", flush=True)

    print("[2/4] Collecting complete TED Italy universe...", flush=True)
    ted = collect_complete_ted_italy(cutoff)
    if not ted.complete:
        raise RuntimeError(
            "TED collection is incomplete; customer snapshot publication is prohibited"
        )
    print(
        f"      TED records: {len(ted.records)} across {ted.pages_fetched} pages",
        flush=True,
    )

    print("[3/4] Building evidence-bounded customer read model...", flush=True)
    results = build_live_runway_results(batch, ted, cutoff_date=cutoff)
    if len(results) != len(logical_projects):
        raise RuntimeError(
            f"project omission detected: results={len(results)}, "
            f"projects={len(logical_projects)}"
        )
    models = tuple(build_runway_read_model(result) for result in results)
    if len({model.operation_code for model in models}) != len(models):
        raise RuntimeError("duplicate logical project identity in customer snapshot")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    output_sha256 = write_customer_safe_jsonl(args.output, models)
    output_lines = args.output.read_text(encoding="utf-8").splitlines()
    if len(output_lines) != len(models):
        raise RuntimeError("customer JSONL line count does not equal logical project count")

    completed = datetime.now(timezone.utc)
    counts: dict[str, int] = {}
    for model in models:
        key = model.state.value
        counts[key] = counts.get(key, 0) + 1
    model_set_sha256 = content_sha256(
        [model.model_dump(mode="json") for model in models]
    )
    summary = {
        "schema_version": "customer-runway-local-snapshot-v1",
        "generated_at": completed.isoformat(),
        "cutoff_date": cutoff.isoformat(),
        "project_count": len(models),
        "project_state_counts": counts,
        "ted_record_count": len(ted.records),
        "ted_page_count": ted.pages_fetched,
        "ted_complete": ted.complete,
        "source_resource_sha256": batch.source_sha256,
        "output_sha256": output_sha256,
        "model_set_sha256": model_set_sha256,
        "production_delivery_version": PRODUCTION_DELIVERY_VERSION,
        "read_model_version": READ_MODEL_VERSION,
        "elapsed_seconds": round((completed - started).total_seconds(), 3),
    }
    if model_set_sha256 != output_sha256:
        raise RuntimeError(
            "customer JSONL hash differs from in-memory customer read-model hash"
        )
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )

    print("[4/4] Customer snapshot ready.", flush=True)
    print(f"      projects: {len(models)}", flush=True)
    print(f"      output:   {args.output.resolve()}", flush=True)
    print(f"      sha256:   {output_sha256}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
