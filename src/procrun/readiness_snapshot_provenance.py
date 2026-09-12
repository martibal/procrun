"""Immutable source-binding provenance for readiness benchmark snapshots."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime
from typing import Any

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from procrun.readiness_benchmark import BenchmarkObservation

PROVENANCE_SQL = """
CREATE TABLE IF NOT EXISTS procrun_readiness.benchmark_snapshot_source_bindings (
    snapshot_id text PRIMARY KEY REFERENCES procrun_readiness.benchmark_snapshots(snapshot_id),
    source_binding jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

DROP TRIGGER IF EXISTS benchmark_snapshot_source_bindings_immutable
    ON procrun_readiness.benchmark_snapshot_source_bindings;
CREATE TRIGGER benchmark_snapshot_source_bindings_immutable
BEFORE UPDATE OR DELETE ON procrun_readiness.benchmark_snapshot_source_bindings
FOR EACH ROW EXECUTE FUNCTION procrun_readiness.reject_immutable_mutation();
"""


def apply_snapshot_provenance_migration(conn: Connection[Any]) -> None:
    with conn.cursor() as cur:
        cur.execute(PROVENANCE_SQL)
    conn.commit()


def insert_snapshot_bundle_with_provenance(
    conn: Connection[Any],
    *,
    snapshot_id: str,
    data_through: date,
    ingested_at: datetime,
    raw_record_count: int,
    canonical_sha256: str,
    source_binding: dict[str, object],
    memberships: Sequence[tuple[str, BenchmarkObservation]],
) -> None:
    """Persist snapshot, source binding and memberships atomically."""
    rows = [
        (
            snapshot_id,
            cohort_id,
            observation.operation_code,
            observation.approved_funding_eur,
            observation.project_start,
            observation.project_end,
            observation.project_title,
            observation.source_url,
        )
        for cohort_id, observation in memberships
    ]
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO procrun_readiness.benchmark_snapshots
            (snapshot_id,data_through,ingested_at,raw_record_count,canonical_sha256)
            VALUES (%s,%s,%s,%s,%s)
            """,
            (snapshot_id, data_through, ingested_at, raw_record_count, canonical_sha256),
        )
        cur.execute(
            """
            INSERT INTO procrun_readiness.benchmark_snapshot_source_bindings
            (snapshot_id,source_binding)
            VALUES (%s,%s)
            """,
            (snapshot_id, Jsonb(source_binding)),
        )
        cur.executemany(
            """
            INSERT INTO procrun_readiness.benchmark_cohort_memberships
            (snapshot_id,cohort_id,operation_code,approved_funding_eur,project_start,project_end,
             project_title,source_url)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            rows,
        )


def load_snapshot_source_binding(
    conn: Connection[Any], snapshot_id: str
) -> dict[str, object] | None:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT source_binding
            FROM procrun_readiness.benchmark_snapshot_source_bindings
            WHERE snapshot_id=%s
            """,
            (snapshot_id,),
        )
        row = cur.fetchone()
    if row is None:
        return None
    value = row["source_binding"]
    if not isinstance(value, dict):
        raise TypeError("stored benchmark source binding must be an object")
    return value
