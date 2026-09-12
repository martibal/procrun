"""Persistence schema for ProcRun pre-application assessment v1."""

from __future__ import annotations

from typing import Any

from psycopg import Connection


DDL = """
CREATE TABLE IF NOT EXISTS benchmark_source_snapshots (
    snapshot_id VARCHAR(64) PRIMARY KEY,
    source_name VARCHAR(64) NOT NULL DEFAULT 'OpenCoesione_PR_FESR_Lombardia',
    data_through_date DATE NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    raw_record_count INTEGER NOT NULL CHECK (raw_record_count >= 0),
    canonical_hash CHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS benchmark_cohort_memberships (
    cohort_id VARCHAR(128) NOT NULL,
    snapshot_id VARCHAR(64) NOT NULL REFERENCES benchmark_source_snapshots(snapshot_id),
    operation_code VARCHAR(128) NOT NULL,
    bando_code VARCHAR(128) NOT NULL,
    action_code VARCHAR(128) NOT NULL,
    intervention_code VARCHAR(128) NOT NULL,
    approved_funding_eur BIGINT NULL CHECK (approved_funding_eur >= 0),
    duration_months INTEGER NULL CHECK (duration_months >= 0),
    funding_exclusion_reason VARCHAR(64) NULL,
    duration_exclusion_reason VARCHAR(64) NULL,
    PRIMARY KEY (cohort_id, operation_code, snapshot_id)
);

CREATE INDEX IF NOT EXISTS idx_benchmark_cohort_lookup
ON benchmark_cohort_memberships (snapshot_id, bando_code, action_code, intervention_code);

CREATE TABLE IF NOT EXISTS preapplication_rulesets (
    ruleset_id VARCHAR(128) PRIMARY KEY,
    bando_code VARCHAR(128) NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    effective_from TIMESTAMPTZ NOT NULL,
    effective_to TIMESTAMPTZ NULL,
    source_document_hashes JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (bando_code, version)
);

CREATE TABLE IF NOT EXISTS preapplication_rules (
    ruleset_id VARCHAR(128) NOT NULL REFERENCES preapplication_rulesets(ruleset_id),
    rule_id VARCHAR(128) NOT NULL,
    module VARCHAR(64) NOT NULL,
    input_key VARCHAR(128) NOT NULL,
    kind VARCHAR(64) NOT NULL,
    rule_payload JSONB NOT NULL,
    public_source_url TEXT NOT NULL,
    public_source_citation TEXT NOT NULL,
    customer_label TEXT NOT NULL,
    PRIMARY KEY (ruleset_id, rule_id)
);

CREATE TABLE IF NOT EXISTS benchmark_reports (
    report_id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    snapshot_id VARCHAR(64) NOT NULL REFERENCES benchmark_source_snapshots(snapshot_id),
    ruleset_id VARCHAR(128) NULL REFERENCES preapplication_rulesets(ruleset_id),
    engine_version VARCHAR(64) NOT NULL,
    schema_version VARCHAR(32) NOT NULL,
    canonicalization_version VARCHAR(64) NOT NULL,
    canonical_sha256 CHAR(64) NOT NULL,
    canonical_jcs_bytes BYTEA NOT NULL,
    canonical_payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_benchmark_reports_sha256
ON benchmark_reports (canonical_sha256);
"""


def apply_preapplication_migration(conn: Connection[Any]) -> None:
    """Create append-only benchmark/report/ruleset structures.

    Application code must never UPDATE an existing ruleset or report record; a changed rule
    or source snapshot gets a new identifier/version.
    """
    with conn.cursor() as cursor:
        cursor.execute(DDL)
    conn.commit()
