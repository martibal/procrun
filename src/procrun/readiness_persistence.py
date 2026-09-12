"""PostgreSQL persistence for immutable Readiness Dossier v2 state."""

from __future__ import annotations

from typing import Any

from psycopg import Connection
from psycopg.types.json import Jsonb


MIGRATION_SQL = r"""
CREATE SCHEMA IF NOT EXISTS procrun_readiness;

CREATE TABLE IF NOT EXISTS procrun_readiness.source_packages (
    source_package_id text PRIMARY KEY,
    bando_code text NOT NULL,
    version integer NOT NULL CHECK (version >= 1),
    verified_at timestamptz NOT NULL,
    refresh_due_at timestamptz NOT NULL,
    completeness_attested boolean NOT NULL,
    package_sha256 char(64) NOT NULL CHECK (package_sha256 ~ '^[0-9a-f]{64}$'),
    manifest jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (bando_code, version)
);

CREATE TABLE IF NOT EXISTS procrun_readiness.source_package_invalidations (
    invalidation_id uuid PRIMARY KEY,
    source_package_id text NOT NULL REFERENCES procrun_readiness.source_packages(source_package_id),
    invalidated_at timestamptz NOT NULL,
    reason text NOT NULL CHECK (length(reason) BETWEEN 1 AND 2000),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS readiness_invalidations_package_idx
    ON procrun_readiness.source_package_invalidations(source_package_id, invalidated_at DESC);

CREATE TABLE IF NOT EXISTS procrun_readiness.benchmark_snapshots (
    snapshot_id text PRIMARY KEY,
    data_through date NOT NULL,
    ingested_at timestamptz NOT NULL,
    raw_record_count integer NOT NULL CHECK (raw_record_count >= 0),
    canonical_sha256 char(64) NOT NULL CHECK (canonical_sha256 ~ '^[0-9a-f]{64}$')
);

CREATE TABLE IF NOT EXISTS procrun_readiness.benchmark_cohort_memberships (
    snapshot_id text NOT NULL REFERENCES procrun_readiness.benchmark_snapshots(snapshot_id),
    cohort_id text NOT NULL,
    operation_code text NOT NULL,
    approved_funding_eur bigint NULL CHECK (approved_funding_eur IS NULL OR approved_funding_eur >= 0),
    project_start date NULL,
    project_end date NULL,
    project_title text NULL,
    source_url text NULL,
    PRIMARY KEY (snapshot_id, cohort_id, operation_code)
);

CREATE INDEX IF NOT EXISTS readiness_cohort_lookup_idx
    ON procrun_readiness.benchmark_cohort_memberships(snapshot_id, cohort_id);

CREATE TABLE IF NOT EXISTS procrun_readiness.dossiers (
    dossier_id uuid PRIMARY KEY,
    tenant_key text NOT NULL CHECK (tenant_key ~ '^org_[0-9a-f]{32}$'),
    purchase_reference text NOT NULL CHECK (length(purchase_reference) BETWEEN 1 AND 512),
    source_package_id text NOT NULL REFERENCES procrun_readiness.source_packages(source_package_id),
    benchmark_snapshot_id text NOT NULL REFERENCES procrun_readiness.benchmark_snapshots(snapshot_id),
    created_at timestamptz NOT NULL,
    canonicalization_version text NOT NULL,
    canonical_sha256 char(64) NOT NULL CHECK (canonical_sha256 ~ '^[0-9a-f]{64}$'),
    canonical_jcs_bytes bytea NOT NULL,
    canonical_payload jsonb NOT NULL
);

CREATE INDEX IF NOT EXISTS readiness_dossiers_tenant_idx
    ON procrun_readiness.dossiers(tenant_key, created_at DESC);

CREATE OR REPLACE FUNCTION procrun_readiness.reject_immutable_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'readiness records are append-only';
END;
$$;

DROP TRIGGER IF EXISTS source_packages_immutable ON procrun_readiness.source_packages;
CREATE TRIGGER source_packages_immutable
BEFORE UPDATE OR DELETE ON procrun_readiness.source_packages
FOR EACH ROW EXECUTE FUNCTION procrun_readiness.reject_immutable_mutation();

DROP TRIGGER IF EXISTS benchmark_snapshots_immutable ON procrun_readiness.benchmark_snapshots;
CREATE TRIGGER benchmark_snapshots_immutable
BEFORE UPDATE OR DELETE ON procrun_readiness.benchmark_snapshots
FOR EACH ROW EXECUTE FUNCTION procrun_readiness.reject_immutable_mutation();

DROP TRIGGER IF EXISTS benchmark_memberships_immutable ON procrun_readiness.benchmark_cohort_memberships;
CREATE TRIGGER benchmark_memberships_immutable
BEFORE UPDATE OR DELETE ON procrun_readiness.benchmark_cohort_memberships
FOR EACH ROW EXECUTE FUNCTION procrun_readiness.reject_immutable_mutation();

DROP TRIGGER IF EXISTS dossiers_immutable ON procrun_readiness.dossiers;
CREATE TRIGGER dossiers_immutable
BEFORE UPDATE OR DELETE ON procrun_readiness.dossiers
FOR EACH ROW EXECUTE FUNCTION procrun_readiness.reject_immutable_mutation();
"""


def apply_readiness_migration(conn: Connection[Any]) -> None:
    with conn.cursor() as cur:
        cur.execute(MIGRATION_SQL)
    conn.commit()


def insert_source_package(
    conn: Connection[Any],
    *,
    source_package_id: str,
    bando_code: str,
    version: int,
    verified_at: object,
    refresh_due_at: object,
    completeness_attested: bool,
    package_sha256: str,
    manifest: dict[str, object],
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO procrun_readiness.source_packages
            (source_package_id,bando_code,version,verified_at,refresh_due_at,
             completeness_attested,package_sha256,manifest)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                source_package_id,
                bando_code,
                version,
                verified_at,
                refresh_due_at,
                completeness_attested,
                package_sha256,
                Jsonb(manifest),
            ),
        )
    conn.commit()


def insert_invalidation(
    conn: Connection[Any],
    *,
    invalidation_id: str,
    source_package_id: str,
    invalidated_at: object,
    reason: str,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO procrun_readiness.source_package_invalidations
            (invalidation_id,source_package_id,invalidated_at,reason)
            VALUES (%s,%s,%s,%s)
            """,
            (invalidation_id, source_package_id, invalidated_at, reason),
        )
    conn.commit()


def insert_dossier(
    conn: Connection[Any],
    *,
    dossier_id: str,
    tenant_key: str,
    purchase_reference: str,
    source_package_id: str,
    benchmark_snapshot_id: str,
    created_at: object,
    canonicalization_version: str,
    canonical_sha256: str,
    canonical_jcs_bytes: bytes,
    canonical_payload: dict[str, object],
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO procrun_readiness.dossiers
            (dossier_id,tenant_key,purchase_reference,source_package_id,benchmark_snapshot_id,
             created_at,canonicalization_version,canonical_sha256,canonical_jcs_bytes,canonical_payload)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                dossier_id,
                tenant_key,
                purchase_reference,
                source_package_id,
                benchmark_snapshot_id,
                created_at,
                canonicalization_version,
                canonical_sha256,
                canonical_jcs_bytes,
                Jsonb(canonical_payload),
            ),
        )
    conn.commit()
