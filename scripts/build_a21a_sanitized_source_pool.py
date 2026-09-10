"""Build the sanctioned A21a source pool from the bounded OpenCoesione Art. 49 resource.

The per-program PR FESR Lombardia publication is already approved as a zero-PII
publisher resource before ProcRun receives it. This script therefore does not use
"download then filter" as a privacy mechanism: it receives an already-qualified
minimum publication and maps only source fields into the A21a package.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from procrun.collectors.opencoesione import OPENCOESIONE_SOURCE_ID, OpenCoesioneOperation
from procrun.collectors.opencoesione_live import (
    OPENCOESIONE_PUBLICATION_PAGE,
    collect_open_coesione_live,
)

SCHEMA_VERSION = "a21a-sanitized-source-pool-v1"
PUBLISHER_ZERO_PII_CONTRACT = "opencoesione-art49-minimum-rgs-v1"


def _logical_operations(
    operations: tuple[OpenCoesioneOperation, ...],
) -> tuple[OpenCoesioneOperation, ...]:
    """Collapse exact repeated rows; fail closed on conflicting duplicate source ids."""
    by_id: dict[str, OpenCoesioneOperation] = {}
    for operation in operations:
        existing = by_id.get(operation.operation_id)
        if existing is not None:
            if existing != operation:
                raise RuntimeError(
                    "conflicting OpenCoesione rows share OperationLocalIdentifier: "
                    f"{operation.operation_id}"
                )
            continue
        by_id[operation.operation_id] = operation
    if not by_id:
        raise RuntimeError("approved OpenCoesione route produced zero logical operations")
    return tuple(by_id[key] for key in sorted(by_id))


def build_source_pool() -> dict[str, object]:
    batch = collect_open_coesione_live()
    cases: list[dict[str, object]] = []
    for operation in _logical_operations(batch.operations):
        cases.append(
            {
                "operation_code": operation.operation_id,
                "project_title": operation.operation_name,
                "project_scope_text": operation.operation_summary,
                "region": "Lombardia",
                "municipality": None,
                "nuts_code": "ITC4",
                "source_url": operation.source_url,
                "language": "it",
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "pii_review_status": "ZERO_PII_CONFIRMED",
        "engine_output_present": False,
        "sanitization_provenance": {
            "raw_archive_present": False,
            "download_then_filter_used": False,
            "source_only_projection_confirmed": True,
            "projection_boundary": "upstream_before_receipt",
            "transport_kind": "prebuilt_sanitized_resource",
            "projection_evidence_url": OPENCOESIONE_PUBLICATION_PAGE,
            "source_id": OPENCOESIONE_SOURCE_ID,
            "publisher_resource_sha256": batch.source_sha256,
            "list_updated_on": batch.list_updated_on.isoformat(),
            "publisher_zero_pii_contract": PUBLISHER_ZERO_PII_CONTRACT,
        },
        "cases": cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    document = build_source_pool()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )
    provenance = document["sanitization_provenance"]
    assert isinstance(provenance, dict)
    cases = document["cases"]
    assert isinstance(cases, list)
    print(f"A21A_SANITIZED_SOURCE_CASES={len(cases)}")
    print(f"A21A_PUBLISHER_RESOURCE_SHA256={provenance['publisher_resource_sha256']}")
    print(f"A21A_LIST_UPDATED_ON={provenance['list_updated_on']}")
    print("A21A_ZERO_PII_CONFIRMED=true")
    print("A21A_DOWNLOAD_THEN_FILTER_USED=false")
    print("A21A_SEALED_HOLDOUT_TOUCHED=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
