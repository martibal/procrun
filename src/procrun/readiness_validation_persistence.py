"""Persistence for immutable Readiness Dossier commercial release validation."""

from __future__ import annotations

from typing import Any

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from procrun.readiness_validation import ReadinessValidationRelease, validation_manifest, validation_sha256

MIGRATION_SQL = r"""
CREATE TABLE IF NOT EXISTS procrun_readiness.validation_releases (
    validation_id text PRIMARY KEY,
    bando_code text NOT NULL,
    source_package_id text NOT NULL REFERENCES procrun_readiness.source_packages(source_package_id),
    source_package_sha256 char(64) NOT NULL CHECK (source_package_sha256 ~ '^[0-9a-f]{64}$'),
    benchmark_snapshot_id text NOT NULL REFERENCES procrun_readiness.benchmark_snapshots(snapshot_id),
    benchmark_snapshot_sha256 char(64) NOT NULL CHECK (benchmark_snapshot_sha256 ~ '^[0-9a-f]{64}$'),
    validated_at timestamptz NOT NULL,
    validation_sha256 char(64) NOT NULL CHECK (validation_sha256 ~ '^[0-9a-f]{64}$'),
    manifest jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (source_package_id, benchmark_snapshot_id)
);

DROP TRIGGER IF EXISTS validation_releases_immutable ON procrun_readiness.validation_releases;
CREATE TRIGGER validation_releases_immutable
BEFORE UPDATE OR DELETE ON procrun_readiness.validation_releases
FOR EACH ROW EXECUTE FUNCTION procrun_readiness.reject_immutable_mutation();
"""


def apply_readiness_validation_migration(conn: Connection[Any]) -> None:
    with conn.cursor() as cur:
        cur.execute(MIGRATION_SQL)
    conn.commit()


def insert_validation_release(conn: Connection[Any], release: ReadinessValidationRelease) -> str:
    digest = validation_sha256(release)
    manifest = validation_manifest(release)
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO procrun_readiness.validation_releases
            (validation_id,bando_code,source_package_id,source_package_sha256,
             benchmark_snapshot_id,benchmark_snapshot_sha256,validated_at,validation_sha256,manifest)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                release.validation_id,
                release.bando_code,
                release.source_package_id,
                release.source_package_sha256,
                release.benchmark_snapshot_id,
                release.benchmark_snapshot_sha256,
                release.validated_at,
                digest,
                Jsonb(manifest),
            ),
        )
    return digest


def load_matching_validation_release(
    conn: Connection[Any],
    *,
    bando_code: str,
    source_package_id: str,
    source_package_sha256: str,
    benchmark_snapshot_id: str,
    benchmark_snapshot_sha256: str,
) -> dict[str, object] | None:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT validation_id, validation_sha256, manifest
            FROM procrun_readiness.validation_releases
            WHERE bando_code = %s
              AND source_package_id = %s
              AND source_package_sha256 = %s
              AND benchmark_snapshot_id = %s
              AND benchmark_snapshot_sha256 = %s
            LIMIT 1
            """,
            (
                bando_code,
                source_package_id,
                source_package_sha256,
                benchmark_snapshot_id,
                benchmark_snapshot_sha256,
            ),
        )
        row = cur.fetchone()
    if row is None:
        return None
    manifest = row["manifest"]
    if not isinstance(manifest, dict):
        raise TypeError("stored validation release manifest is invalid")
    if manifest.get("status") != "RELEASED":
        return None
    return {
        "validation_id": str(row["validation_id"]),
        "validation_sha256": str(row["validation_sha256"]),
        "manifest": manifest,
    }
