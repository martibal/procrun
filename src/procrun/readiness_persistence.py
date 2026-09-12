"""PostgreSQL persistence for immutable Readiness Dossier v2 state."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime
from typing import Any

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from procrun.readiness_benchmark import BenchmarkObservation
from procrun.readiness_source import (
    PublishedRequirement,
    RequirementKind,
    SourceDocument,
    SourcePackage,
    SourceReuseMode,
)

MIGRATION_SQL = r"""
CREATE SCHEMA IF NOT EXISTS procrun_readiness;

CREATE TABLE IF NOT EXISTS procrun_readiness.source_packages (
    source_package_id text PRIMARY KEY,
    bando_code text NOT NULL,
    benchmark_cohort_id text NOT NULL,
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
    purchase_reference text NOT NULL CHECK (purchase_reference ~ '^[A-Za-z0-9_.:-]{1,128}$'),
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

DROP TRIGGER IF EXISTS source_package_invalidations_immutable
    ON procrun_readiness.source_package_invalidations;
CREATE TRIGGER source_package_invalidations_immutable
BEFORE UPDATE OR DELETE ON procrun_readiness.source_package_invalidations
FOR EACH ROW EXECUTE FUNCTION procrun_readiness.reject_immutable_mutation();

DROP TRIGGER IF EXISTS benchmark_snapshots_immutable ON procrun_readiness.benchmark_snapshots;
CREATE TRIGGER benchmark_snapshots_immutable
BEFORE UPDATE OR DELETE ON procrun_readiness.benchmark_snapshots
FOR EACH ROW EXECUTE FUNCTION procrun_readiness.reject_immutable_mutation();

DROP TRIGGER IF EXISTS benchmark_memberships_immutable
    ON procrun_readiness.benchmark_cohort_memberships;
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
    benchmark_cohort_id: str,
    version: int,
    verified_at: datetime,
    refresh_due_at: datetime,
    completeness_attested: bool,
    package_sha256: str,
    manifest: dict[str, object],
) -> None:
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO procrun_readiness.source_packages
            (source_package_id,bando_code,benchmark_cohort_id,version,verified_at,refresh_due_at,
             completeness_attested,package_sha256,manifest)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                source_package_id,
                bando_code,
                benchmark_cohort_id,
                version,
                verified_at,
                refresh_due_at,
                completeness_attested,
                package_sha256,
                Jsonb(manifest),
            ),
        )


def insert_invalidation(
    conn: Connection[Any],
    *,
    invalidation_id: str,
    source_package_id: str,
    invalidated_at: datetime,
    reason: str,
) -> None:
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO procrun_readiness.source_package_invalidations
            (invalidation_id,source_package_id,invalidated_at,reason)
            VALUES (%s,%s,%s,%s)
            """,
            (invalidation_id, source_package_id, invalidated_at, reason),
        )


def insert_benchmark_snapshot_bundle(
    conn: Connection[Any],
    *,
    snapshot_id: str,
    data_through: date,
    ingested_at: datetime,
    raw_record_count: int,
    canonical_sha256: str,
    memberships: Sequence[tuple[str, BenchmarkObservation]],
) -> None:
    """Insert snapshot metadata and every cohort membership in one transaction."""
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
        cur.executemany(
            """
            INSERT INTO procrun_readiness.benchmark_cohort_memberships
            (snapshot_id,cohort_id,operation_code,approved_funding_eur,project_start,project_end,
             project_title,source_url)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            rows,
        )


def insert_dossier(
    conn: Connection[Any],
    *,
    dossier_id: str,
    tenant_key: str,
    purchase_reference: str,
    source_package_id: str,
    benchmark_snapshot_id: str,
    created_at: datetime,
    canonicalization_version: str,
    canonical_sha256: str,
    canonical_jcs_bytes: bytes,
    canonical_payload: dict[str, object],
) -> None:
    with conn.transaction(), conn.cursor() as cur:
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


def _source_package_from_manifest(manifest: dict[str, Any]) -> SourcePackage:
    raw_documents = manifest.get("documents")
    raw_requirements = manifest.get("requirements")
    if not isinstance(raw_documents, list) or not isinstance(raw_requirements, list):
        raise TypeError("stored source package manifest lists are invalid")
    documents = tuple(
        SourceDocument(
            document_id=str(item["document_id"]),
            document_type=str(item["document_type"]),
            title=str(item["title"]),
            public_url=str(item["public_url"]),
            sha256=str(item["sha256"]),
            observed_at=datetime.fromisoformat(str(item["observed_at"])),
            reuse_mode=SourceReuseMode(str(item["reuse_mode"])),
            reuse_basis_url=str(item["reuse_basis_url"]),
            reuse_basis_note=str(item["reuse_basis_note"]),
        )
        for item in raw_documents
        if isinstance(item, dict)
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
            boundary_value=(
                None if item.get("boundary_value") is None else int(item["boundary_value"])
            ),
        )
        for item in raw_requirements
        if isinstance(item, dict)
    )
    if len(documents) != len(raw_documents) or len(requirements) != len(raw_requirements):
        raise TypeError("stored source package manifest contains non-object entries")
    return SourcePackage(
        source_package_id=str(manifest["source_package_id"]),
        bando_code=str(manifest["bando_code"]),
        benchmark_cohort_id=str(manifest["benchmark_cohort_id"]),
        version=int(manifest["version"]),
        verified_at=datetime.fromisoformat(str(manifest["verified_at"])),
        documents=documents,
        requirements=requirements,
        completeness_attested=bool(manifest["completeness_attested"]),
    )


def load_latest_source_package(conn: Connection[Any], bando_code: str) -> SourcePackage | None:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT manifest
            FROM procrun_readiness.source_packages
            WHERE bando_code=%s
            ORDER BY version DESC
            LIMIT 1
            """,
            (bando_code,),
        )
        row = cur.fetchone()
    if row is None:
        return None
    manifest = row["manifest"]
    if not isinstance(manifest, dict):
        raise TypeError("stored source package manifest must be an object")
    return _source_package_from_manifest(manifest)


def load_latest_invalidation_at(
    conn: Connection[Any], source_package_id: str
) -> datetime | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT max(invalidated_at)
            FROM procrun_readiness.source_package_invalidations
            WHERE source_package_id=%s
            """,
            (source_package_id,),
        )
        row = cur.fetchone()
    if row is None or row[0] is None:
        return None
    value = row[0]
    if not isinstance(value, datetime):
        raise TypeError("stored invalidation timestamp must be datetime")
    return value


def load_benchmark_snapshot_metadata(
    conn: Connection[Any], snapshot_id: str
) -> tuple[str, str] | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT data_through, canonical_sha256
            FROM procrun_readiness.benchmark_snapshots
            WHERE snapshot_id=%s
            """,
            (snapshot_id,),
        )
        row = cur.fetchone()
    if row is None:
        return None
    return str(row[0]), str(row[1])


def load_benchmark_observations(
    conn: Connection[Any], *, snapshot_id: str, cohort_id: str
) -> tuple[BenchmarkObservation, ...]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT operation_code, approved_funding_eur, project_start, project_end,
                   project_title, source_url
            FROM procrun_readiness.benchmark_cohort_memberships
            WHERE snapshot_id=%s AND cohort_id=%s
            ORDER BY operation_code
            """,
            (snapshot_id, cohort_id),
        )
        rows = cur.fetchall()
    return tuple(
        BenchmarkObservation(
            operation_code=str(row[0]),
            approved_funding_eur=None if row[1] is None else int(row[1]),
            project_start=row[2],
            project_end=row[3],
            project_title=None if row[4] is None else str(row[4]),
            source_url=None if row[5] is None else str(row[5]),
        )
        for row in rows
    )
