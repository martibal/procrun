"""Canonical report persistence primitives for Funded Project Comparables v1."""

from __future__ import annotations

import json
from hashlib import sha256
from typing import Any, Final
from uuid import UUID, uuid4

import rfc8785  # type: ignore[import-untyped]
from psycopg import Connection
from psycopg.types.json import Jsonb

from procrun.funded_project_benchmark import BenchmarkCalculation

REPORT_SCHEMA_VERSION: Final = "funded-project-report-v1.0.0"

_MIGRATION = r"""
CREATE TABLE IF NOT EXISTS procrun.benchmark_source_snapshots (
    snapshot_id text PRIMARY KEY,
    source_name text NOT NULL DEFAULT 'OpenCoesione_PR_FESR_Lombardia',
    data_through_date date NOT NULL,
    ingested_at timestamptz NOT NULL DEFAULT now(),
    raw_record_count integer NOT NULL CHECK (raw_record_count >= 0),
    canonical_hash char(64) NOT NULL CHECK (canonical_hash ~ '^[0-9a-f]{64}$')
);

CREATE TABLE IF NOT EXISTS procrun.benchmark_cohort_memberships (
    cohort_id text NOT NULL,
    snapshot_id text NOT NULL REFERENCES procrun.benchmark_source_snapshots(snapshot_id),
    operation_code text NOT NULL,
    bando_code text NOT NULL,
    action_code text NOT NULL,
    intervention_code text NOT NULL,
    approved_funding_eur bigint CHECK (approved_funding_eur IS NULL OR approved_funding_eur >= 0),
    duration_months integer CHECK (duration_months IS NULL OR duration_months >= 0),
    funding_exclusion_reason text,
    duration_exclusion_reason text,
    PRIMARY KEY (cohort_id, operation_code, snapshot_id)
);
CREATE INDEX IF NOT EXISTS benchmark_cohort_lookup_idx
    ON procrun.benchmark_cohort_memberships (snapshot_id, bando_code, action_code, intervention_code);

CREATE TABLE IF NOT EXISTS procrun.benchmark_reports (
    report_id uuid PRIMARY KEY,
    created_at timestamptz NOT NULL DEFAULT now(),
    snapshot_id text NOT NULL REFERENCES procrun.benchmark_source_snapshots(snapshot_id),
    engine_version text NOT NULL,
    schema_version text NOT NULL,
    canonical_sha256 char(64) NOT NULL CHECK (canonical_sha256 ~ '^[0-9a-f]{64}$'),
    canonical_jcs_bytes bytea NOT NULL,
    canonical_payload jsonb NOT NULL
);
CREATE INDEX IF NOT EXISTS benchmark_reports_sha256_idx
    ON procrun.benchmark_reports (canonical_sha256);
"""


def apply_benchmark_migration(conn: Connection[Any]) -> None:
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS procrun")
        cur.execute(_MIGRATION)
    conn.commit()


def canonical_payload(calculation: BenchmarkCalculation) -> dict[str, Any]:
    return {
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "calculation": calculation.model_dump(mode="json"),
    }


def canonicalize_report(calculation: BenchmarkCalculation) -> tuple[bytes, str, dict[str, Any]]:
    payload = canonical_payload(calculation)
    canonical_bytes = rfc8785.dumps(payload)
    digest = sha256(canonical_bytes).hexdigest()
    return canonical_bytes, digest, payload


def persist_report(
    conn: Connection[Any],
    calculation: BenchmarkCalculation,
    *,
    report_id: UUID | None = None,
) -> tuple[UUID, str]:
    canonical_bytes, digest, payload = canonicalize_report(calculation)
    resolved_report_id = report_id or uuid4()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO procrun.benchmark_reports (
                report_id, snapshot_id, engine_version, schema_version,
                canonical_sha256, canonical_jcs_bytes, canonical_payload
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                resolved_report_id,
                calculation.snapshot_id,
                calculation.engine_version,
                REPORT_SCHEMA_VERSION,
                digest,
                canonical_bytes,
                Jsonb(payload),
            ),
        )
    conn.commit()
    return resolved_report_id, digest


def verify_persisted_report(
    *,
    canonical_jcs_bytes: bytes,
    canonical_sha256: str,
    canonical_payload_json: dict[str, Any],
) -> bool:
    if sha256(canonical_jcs_bytes).hexdigest() != canonical_sha256:
        return False
    try:
        parsed = json.loads(canonical_jcs_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False
    if parsed != canonical_payload_json:
        return False
    return rfc8785.dumps(parsed) == canonical_jcs_bytes
