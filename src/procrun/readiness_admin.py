"""Administrative import path for Readiness Dossier source packages and benchmark snapshots.

This CLI deliberately accepts only already-curated, non-PII JSON artifacts. It performs no
human contact and no beneficiary lookup. Source-package refreshes and benchmark snapshots are
append-only production records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import psycopg

from procrun.migrations import apply_all_migrations
from procrun.readiness_benchmark import BenchmarkObservation
from procrun.readiness_persistence import (
    insert_benchmark_membership,
    insert_benchmark_snapshot,
    insert_invalidation,
    insert_source_package,
)
from procrun.readiness_source import (
    PublishedRequirement,
    RequirementKind,
    SourceDocument,
    SourcePackage,
    package_manifest,
    package_sha256,
)


def _database_url() -> str:
    value = os.environ.get("PROCRUN_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("PROCRUN_DATABASE_URL is required")
    return value


def _load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _parse_source_package(data: dict[str, Any]) -> SourcePackage:
    documents = tuple(
        SourceDocument(
            document_id=str(item["document_id"]),
            document_type=str(item["document_type"]),
            title=str(item["title"]),
            public_url=str(item["public_url"]),
            sha256=str(item["sha256"]),
            observed_at=datetime.fromisoformat(str(item["observed_at"])),
        )
        for item in data["documents"]
    )
    requirements = tuple(
        PublishedRequirement(
            requirement_id=str(item["requirement_id"]),
            kind=RequirementKind(str(item["kind"])),
            label=str(item["label"]),
            source_document_id=str(item["source_document_id"]),
            source_citation=str(item["source_citation"]),
            source_text=str(item["source_text"]),
            scope_note=str(item["scope_note"]),
            boundary_value=None if item.get("boundary_value") is None else int(item["boundary_value"]),
        )
        for item in data["requirements"]
    )
    package = SourcePackage(
        source_package_id=str(data["source_package_id"]),
        bando_code=str(data["bando_code"]),
        benchmark_cohort_id=str(data["benchmark_cohort_id"]),
        version=int(data["version"]),
        verified_at=datetime.fromisoformat(str(data["verified_at"])),
        documents=documents,
        requirements=requirements,
        completeness_attested=bool(data["completeness_attested"]),
    )
    if not package.completeness_attested:
        raise ValueError("production source-package import requires completeness_attested=true")
    return package


def import_source_package(path: str) -> str:
    raw = _load_json(path)
    if not isinstance(raw, dict):
        raise ValueError("source package must be a JSON object")
    package = _parse_source_package(raw)
    manifest = package_manifest(package)
    digest = package_sha256(package)
    with psycopg.connect(_database_url()) as conn:
        apply_all_migrations(conn)
        insert_source_package(
            conn,
            source_package_id=package.source_package_id,
            bando_code=package.bando_code,
            benchmark_cohort_id=package.benchmark_cohort_id,
            version=package.version,
            verified_at=package.verified_at,
            refresh_due_at=package.refresh_due_at,
            completeness_attested=package.completeness_attested,
            package_sha256=digest,
            manifest=manifest,
        )
    return digest


def invalidate_source_package(source_package_id: str, reason: str, invalidated_at: str) -> str:
    timestamp = datetime.fromisoformat(invalidated_at)
    if timestamp.tzinfo is None:
        raise ValueError("invalidated_at must include a timezone")
    invalidation_id = str(uuid4())
    with psycopg.connect(_database_url()) as conn:
        apply_all_migrations(conn)
        insert_invalidation(
            conn,
            invalidation_id=invalidation_id,
            source_package_id=source_package_id,
            invalidated_at=timestamp,
            reason=reason,
        )
    return invalidation_id


def _canonical_snapshot_payload(data: dict[str, Any]) -> bytes:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def import_benchmark_snapshot(path: str) -> str:
    raw = _load_json(path)
    if not isinstance(raw, dict):
        raise ValueError("benchmark snapshot must be a JSON object")
    rows = raw.get("memberships")
    if not isinstance(rows, list):
        raise ValueError("memberships must be a JSON list")
    snapshot_id = str(raw["snapshot_id"])
    data_through = date.fromisoformat(str(raw["data_through"]))
    ingested_at = datetime.fromisoformat(str(raw["ingested_at"]))
    if ingested_at.tzinfo is None:
        raise ValueError("ingested_at must include a timezone")
    canonical = _canonical_snapshot_payload(raw)
    digest = hashlib.sha256(canonical).hexdigest()
    with psycopg.connect(_database_url()) as conn:
        apply_all_migrations(conn)
        insert_benchmark_snapshot(
            conn,
            snapshot_id=snapshot_id,
            data_through=data_through,
            ingested_at=ingested_at,
            raw_record_count=len(rows),
            canonical_sha256=digest,
        )
        seen: set[tuple[str, str]] = set()
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("each benchmark membership must be an object")
            cohort_id = str(row["cohort_id"])
            operation_code = str(row["operation_code"])
            key = (cohort_id, operation_code)
            if key in seen:
                raise ValueError(f"duplicate benchmark membership {key!r}")
            seen.add(key)
            start = None if row.get("project_start") is None else date.fromisoformat(str(row["project_start"]))
            end = None if row.get("project_end") is None else date.fromisoformat(str(row["project_end"]))
            funding = row.get("approved_funding_eur")
            insert_benchmark_membership(
                conn,
                snapshot_id=snapshot_id,
                cohort_id=cohort_id,
                observation=BenchmarkObservation(
                    operation_code=operation_code,
                    approved_funding_eur=None if funding is None else int(funding),
                    project_start=start,
                    project_end=end,
                    project_title=None if row.get("project_title") is None else str(row["project_title"]),
                    source_url=None if row.get("source_url") is None else str(row["source_url"]),
                ),
            )
    return digest


def main() -> None:
    parser = argparse.ArgumentParser(prog="procrun-readiness-admin")
    sub = parser.add_subparsers(dest="command", required=True)

    source = sub.add_parser("import-source-package")
    source.add_argument("path")

    invalidate = sub.add_parser("invalidate-source-package")
    invalidate.add_argument("source_package_id")
    invalidate.add_argument("--reason", required=True)
    invalidate.add_argument("--at", required=True)

    snapshot = sub.add_parser("import-benchmark-snapshot")
    snapshot.add_argument("path")

    args = parser.parse_args()
    if args.command == "import-source-package":
        print(import_source_package(args.path))
    elif args.command == "invalidate-source-package":
        print(invalidate_source_package(args.source_package_id, args.reason, args.at))
    elif args.command == "import-benchmark-snapshot":
        print(import_benchmark_snapshot(args.path))
    else:  # pragma: no cover
        raise AssertionError("unreachable command")


if __name__ == "__main__":
    main()
