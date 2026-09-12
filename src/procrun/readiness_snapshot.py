"""Build a no-PII benchmark snapshot from admitted FundingProject records.

Cohort membership is supplied explicitly from an already-qualified structured source. This module
never infers bando/action membership from project text, titles, geography, timing, or similarity.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, date, datetime

from procrun.domain import FundingProject

SNAPSHOT_SCHEMA_VERSION = "readiness-benchmark-snapshot-v2"


def build_snapshot_payload(
    *,
    snapshot_id: str,
    data_through: date,
    ingested_at: datetime,
    projects: tuple[FundingProject, ...],
    cohort_memberships: Mapping[str, tuple[str, ...]],
    funding_source_id: str,
    funding_source_sha256: str,
    cohort_source_id: str,
    cohort_source_sha256: str,
) -> tuple[dict[str, object], bytes, str]:
    """Freeze exact project facts plus externally proven cohort memberships."""
    if ingested_at.tzinfo is None:
        raise ValueError("ingested_at must be timezone-aware")
    for label, digest in (
        ("funding_source_sha256", funding_source_sha256),
        ("cohort_source_sha256", cohort_source_sha256),
    ):
        if len(digest) != 64:
            raise ValueError(f"{label} must contain 64 hex characters")
        int(digest, 16)

    by_operation: dict[str, FundingProject] = {}
    for project in projects:
        if project.operation_code in by_operation:
            raise ValueError(f"duplicate FundingProject operation_code {project.operation_code!r}")
        by_operation[project.operation_code] = project

    unknown = set(cohort_memberships) - set(by_operation)
    if unknown:
        raise ValueError(f"cohort membership references unknown operations: {sorted(unknown)}")

    memberships: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for operation_code in sorted(cohort_memberships):
        project = by_operation[operation_code]
        for cohort_id in sorted(set(cohort_memberships[operation_code])):
            if not cohort_id:
                raise ValueError("cohort ids must be non-empty")
            key = (cohort_id, operation_code)
            if key in seen:
                raise ValueError(f"duplicate cohort membership {key!r}")
            seen.add(key)
            memberships.append(
                {
                    "cohort_id": cohort_id,
                    "operation_code": operation_code,
                    "approved_funding_eur": project.approved_funding_eur,
                    "project_start": (
                        None if project.project_start is None else project.project_start.isoformat()
                    ),
                    "project_end": (
                        None if project.project_end is None else project.project_end.isoformat()
                    ),
                    "project_title": project.project_title,
                    "source_url": project.source_url,
                }
            )

    payload: dict[str, object] = {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "snapshot_id": snapshot_id,
        "data_through": data_through.isoformat(),
        "ingested_at": ingested_at.astimezone(UTC).isoformat(),
        "raw_record_count": len(projects),
        "source_binding": {
            "funding_source_id": funding_source_id,
            "funding_source_sha256": funding_source_sha256,
            "cohort_source_id": cohort_source_id,
            "cohort_source_sha256": cohort_source_sha256,
            "cohort_membership_semantics": (
                "Explicit structured-source membership only; no semantic or fuzzy inference."
            ),
        },
        "memberships": memberships,
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return payload, canonical, hashlib.sha256(canonical).hexdigest()
