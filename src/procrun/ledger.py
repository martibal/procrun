"""Append-only PostgreSQL evidence ledger for Procurement Runway Phase A."""

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from psycopg import Connection
from psycopg.types.json import Jsonb
from pydantic import BaseModel

from procrun.domain import (
    ComponentAssessment,
    FundingProject,
    ProcurementEvidence,
    ProjectAssessment,
    PurchaseComponent,
)
from procrun.source_contracts import require_live_source

LEDGER_SCHEMA_VERSION = "phase-a-ledger-v1"
_PROCRUN_NAMESPACE = uuid5(NAMESPACE_URL, "https://procrun.internal/ledger/v1")


class LedgerInvariantError(RuntimeError):
    """Raised when an append would violate a ledger provenance invariant."""


@dataclass(frozen=True)
class VersionWrite:
    version_id: UUID
    content_sha256: str
    inserted: bool
    supersedes_version_id: UUID | None


def _utc_iso(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime values used by the ledger must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return _jsonable(value.model_dump(mode="json"))
    if isinstance(value, datetime):
        return _utc_iso(value)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [_jsonable(item) for item in value]
    return value


def canonical_json(value: Any) -> str:
    """Return stable UTF-8 JSON used for all ledger hashes."""

    return json.dumps(
        _jsonable(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def content_sha256(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _version_uuid(
    kind: str,
    logical_id: str,
    digest: str,
    supersedes_version_id: UUID | None,
) -> UUID:
    predecessor = "ROOT" if supersedes_version_id is None else str(supersedes_version_id)
    return uuid5(
        _PROCRUN_NAMESPACE,
        f"{kind}:{logical_id}:{digest}:{predecessor}",
    )


def _require_sha256(value: str, field_name: str) -> None:
    if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise ValueError(f"{field_name} must be a lowercase SHA-256 hex digest")


_MIGRATION_001 = r"""
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE procrun.source_record_versions (
    version_id uuid PRIMARY KEY,
    logical_key text NOT NULL,
    source_id text NOT NULL,
    source_record_id text NOT NULL,
    record_kind text NOT NULL CHECK (record_kind IN ('funding_project', 'procurement_evidence')),
    source_url text NOT NULL,
    source_first_seen_at timestamptz,
    schema_version text NOT NULL,
    normalized_fields jsonb NOT NULL,
    content_sha256 char(64) NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    supersedes_version_id uuid REFERENCES procrun.source_record_versions(version_id),
    inserted_at timestamptz NOT NULL DEFAULT now(),
    CHECK (supersedes_version_id IS NULL OR supersedes_version_id <> version_id)
);
CREATE INDEX source_record_logical_idx
    ON procrun.source_record_versions (logical_key, inserted_at DESC);
CREATE INDEX source_record_hash_idx
    ON procrun.source_record_versions (logical_key, content_sha256);

CREATE TABLE procrun.source_retrievals (
    retrieval_id uuid PRIMARY KEY,
    source_version_id uuid NOT NULL REFERENCES procrun.source_record_versions(version_id),
    run_key text,
    retrieved_at timestamptz NOT NULL,
    inserted_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (source_version_id, run_key)
);

CREATE TABLE procrun.funding_project_versions (
    version_id uuid PRIMARY KEY,
    operation_code text NOT NULL,
    source_record_version_id uuid NOT NULL REFERENCES procrun.source_record_versions(version_id),
    as_of timestamptz NOT NULL,
    first_seen_at timestamptz,
    temporal_provenance text NOT NULL CHECK (temporal_provenance IN ('RESOLVED', 'UNRESOLVED')),
    project_title text,
    project_start date,
    project_end date,
    approved_funding_eur bigint CHECK (approved_funding_eur IS NULL OR approved_funding_eur >= 0),
    executed_funding_eur bigint CHECK (executed_funding_eur IS NULL OR executed_funding_eur >= 0),
    project_scope_text text NOT NULL,
    fund text,
    programme text,
    objective text,
    theme text,
    region text,
    municipality text,
    nuts_code text,
    content_sha256 char(64) NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    supersedes_version_id uuid REFERENCES procrun.funding_project_versions(version_id),
    inserted_at timestamptz NOT NULL DEFAULT now(),
    CHECK (supersedes_version_id IS NULL OR supersedes_version_id <> version_id),
    CHECK (temporal_provenance <> 'RESOLVED' OR first_seen_at IS NOT NULL)
);
CREATE INDEX funding_project_logical_idx
    ON procrun.funding_project_versions (operation_code, inserted_at DESC);
CREATE INDEX funding_project_title_trgm_idx
    ON procrun.funding_project_versions USING gin (project_title gin_trgm_ops);
CREATE INDEX funding_project_scope_fts_idx
    ON procrun.funding_project_versions
    USING gin (to_tsvector('simple', project_scope_text));

CREATE TABLE procrun.component_versions (
    version_id uuid PRIMARY KEY,
    component_id text NOT NULL,
    operation_code text NOT NULL,
    as_of timestamptz NOT NULL,
    category text NOT NULL,
    description text NOT NULL,
    scope_evidence text NOT NULL,
    extractor_version text NOT NULL,
    content_sha256 char(64) NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    supersedes_version_id uuid REFERENCES procrun.component_versions(version_id),
    inserted_at timestamptz NOT NULL DEFAULT now(),
    CHECK (supersedes_version_id IS NULL OR supersedes_version_id <> version_id)
);
CREATE INDEX component_logical_idx
    ON procrun.component_versions (component_id, inserted_at DESC);
CREATE INDEX component_description_trgm_idx
    ON procrun.component_versions USING gin (description gin_trgm_ops);

CREATE TABLE procrun.procurement_evidence_versions (
    version_id uuid PRIMARY KEY,
    evidence_id text NOT NULL,
    component_id text NOT NULL,
    as_of timestamptz NOT NULL,
    notice_id text NOT NULL,
    publication_date date NOT NULL,
    award_date date,
    contract_date date,
    title text NOT NULL,
    scope_description text,
    cpv_codes text[] NOT NULL DEFAULT '{}',
    contract_nature text,
    procedure_type text,
    procedure_value_eur bigint CHECK (procedure_value_eur IS NULL OR procedure_value_eur >= 0),
    estimated_value_eur bigint CHECK (estimated_value_eur IS NULL OR estimated_value_eur >= 0),
    base_value_eur bigint CHECK (base_value_eur IS NULL OR base_value_eur >= 0),
    awarded_value_eur bigint CHECK (awarded_value_eur IS NULL OR awarded_value_eur >= 0),
    place_of_performance text,
    nuts_code text,
    municipality text,
    contracting_authority_name text,
    project_reference text,
    source_record_version_id uuid NOT NULL REFERENCES procrun.source_record_versions(version_id),
    content_sha256 char(64) NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    supersedes_version_id uuid REFERENCES procrun.procurement_evidence_versions(version_id),
    inserted_at timestamptz NOT NULL DEFAULT now(),
    CHECK (supersedes_version_id IS NULL OR supersedes_version_id <> version_id)
);
CREATE INDEX procurement_evidence_component_idx
    ON procrun.procurement_evidence_versions (component_id, publication_date);
CREATE INDEX procurement_evidence_title_trgm_idx
    ON procrun.procurement_evidence_versions USING gin (title gin_trgm_ops);
CREATE INDEX procurement_evidence_title_fts_idx
    ON procrun.procurement_evidence_versions USING gin (to_tsvector('simple', title));

CREATE TABLE procrun.assessment_versions (
    version_id uuid PRIMARY KEY,
    assessment_id text NOT NULL,
    component_id text NOT NULL,
    operation_code text NOT NULL,
    state text NOT NULL CHECK (state IN ('OPEN', 'CLOSED', 'UNRESOLVED')),
    cutoff_date date NOT NULL,
    as_of timestamptz NOT NULL,
    rule_version text NOT NULL,
    model_version text,
    matching_candidates jsonb NOT NULL DEFAULT '[]'::jsonb,
    accepted_evidence_ids text[] NOT NULL DEFAULT '{}',
    accepted_evidence_version_ids uuid[] NOT NULL DEFAULT '{}',
    rejected_evidence jsonb NOT NULL DEFAULT '[]'::jsonb,
    rationale text NOT NULL,
    coverage_note text NOT NULL,
    content_sha256 char(64) NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    supersedes_version_id uuid REFERENCES procrun.assessment_versions(version_id),
    inserted_at timestamptz NOT NULL DEFAULT now(),
    CHECK (supersedes_version_id IS NULL OR supersedes_version_id <> version_id)
);
CREATE INDEX assessment_logical_idx
    ON procrun.assessment_versions (assessment_id, inserted_at DESC);
CREATE INDEX assessment_operation_idx
    ON procrun.assessment_versions (operation_code, cutoff_date, state);

CREATE TABLE procrun.project_assessment_versions (
    version_id uuid PRIMARY KEY,
    operation_code text NOT NULL,
    state text NOT NULL CHECK (state IN ('OPEN', 'CLOSED', 'PARTIAL', 'UNRESOLVED')),
    cutoff_date date NOT NULL,
    as_of timestamptz NOT NULL,
    classifier_version text NOT NULL,
    component_assessment_version_ids uuid[] NOT NULL,
    content_sha256 char(64) NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    supersedes_version_id uuid REFERENCES procrun.project_assessment_versions(version_id),
    inserted_at timestamptz NOT NULL DEFAULT now(),
    CHECK (supersedes_version_id IS NULL OR supersedes_version_id <> version_id)
);
CREATE INDEX project_assessment_logical_idx
    ON procrun.project_assessment_versions (operation_code, inserted_at DESC);

CREATE TABLE procrun.outcome_versions (
    version_id uuid PRIMARY KEY,
    outcome_id text NOT NULL,
    assessment_version_id uuid NOT NULL REFERENCES procrun.assessment_versions(version_id),
    procurement_evidence_version_id uuid NOT NULL
        REFERENCES procrun.procurement_evidence_versions(version_id),
    original_signal_at timestamptz NOT NULL,
    outcome_date date NOT NULL,
    lead_days integer NOT NULL CHECK (lead_days >= 0),
    as_of timestamptz NOT NULL,
    content_sha256 char(64) NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    supersedes_version_id uuid REFERENCES procrun.outcome_versions(version_id),
    inserted_at timestamptz NOT NULL DEFAULT now(),
    CHECK (supersedes_version_id IS NULL OR supersedes_version_id <> version_id)
);

CREATE TABLE procrun.run_manifests (
    version_id uuid PRIMARY KEY,
    run_key text NOT NULL,
    started_at timestamptz NOT NULL,
    completed_at timestamptz NOT NULL,
    schema_version text NOT NULL,
    classifier_version text NOT NULL,
    counts jsonb NOT NULL,
    input_sha256 char(64) NOT NULL CHECK (input_sha256 ~ '^[0-9a-f]{64}$'),
    output_sha256 char(64) NOT NULL CHECK (output_sha256 ~ '^[0-9a-f]{64}$'),
    manifest_sha256 char(64) NOT NULL CHECK (manifest_sha256 ~ '^[0-9a-f]{64}$'),
    supersedes_version_id uuid REFERENCES procrun.run_manifests(version_id),
    inserted_at timestamptz NOT NULL DEFAULT now(),
    CHECK (completed_at >= started_at),
    CHECK (supersedes_version_id IS NULL OR supersedes_version_id <> version_id)
);
CREATE INDEX run_manifest_logical_idx
    ON procrun.run_manifests (run_key, inserted_at DESC);

CREATE OR REPLACE FUNCTION procrun.reject_ledger_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'Procurement Runway ledger is append-only: % on %.% is prohibited',
        TG_OP, TG_TABLE_SCHEMA, TG_TABLE_NAME
        USING ERRCODE = '55000';
END;
$$;

CREATE TRIGGER source_record_versions_append_only
BEFORE UPDATE OR DELETE ON procrun.source_record_versions
FOR EACH ROW EXECUTE FUNCTION procrun.reject_ledger_mutation();
CREATE TRIGGER source_retrievals_append_only
BEFORE UPDATE OR DELETE ON procrun.source_retrievals
FOR EACH ROW EXECUTE FUNCTION procrun.reject_ledger_mutation();
CREATE TRIGGER funding_project_versions_append_only
BEFORE UPDATE OR DELETE ON procrun.funding_project_versions
FOR EACH ROW EXECUTE FUNCTION procrun.reject_ledger_mutation();
CREATE TRIGGER component_versions_append_only
BEFORE UPDATE OR DELETE ON procrun.component_versions
FOR EACH ROW EXECUTE FUNCTION procrun.reject_ledger_mutation();
CREATE TRIGGER procurement_evidence_versions_append_only
BEFORE UPDATE OR DELETE ON procrun.procurement_evidence_versions
FOR EACH ROW EXECUTE FUNCTION procrun.reject_ledger_mutation();
CREATE TRIGGER assessment_versions_append_only
BEFORE UPDATE OR DELETE ON procrun.assessment_versions
FOR EACH ROW EXECUTE FUNCTION procrun.reject_ledger_mutation();
CREATE TRIGGER project_assessment_versions_append_only
BEFORE UPDATE OR DELETE ON procrun.project_assessment_versions
FOR EACH ROW EXECUTE FUNCTION procrun.reject_ledger_mutation();
CREATE TRIGGER outcome_versions_append_only
BEFORE UPDATE OR DELETE ON procrun.outcome_versions
FOR EACH ROW EXECUTE FUNCTION procrun.reject_ledger_mutation();
CREATE TRIGGER run_manifests_append_only
BEFORE UPDATE OR DELETE ON procrun.run_manifests
FOR EACH ROW EXECUTE FUNCTION procrun.reject_ledger_mutation();
"""


def apply_migrations(conn: Connection[Any]) -> None:
    """Apply versioned Phase-A schema migrations transactionally."""

    with conn.transaction():
        conn.execute("CREATE SCHEMA IF NOT EXISTS procrun")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS procrun.schema_migrations (
                migration_id text PRIMARY KEY,
                applied_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        applied = conn.execute(
            "SELECT 1 FROM procrun.schema_migrations WHERE migration_id = %s",
            ("001_phase_a_ledger",),
        ).fetchone()
        if applied is None:
            conn.execute(_MIGRATION_001)
            conn.execute(
                "INSERT INTO procrun.schema_migrations (migration_id) VALUES (%s)",
                ("001_phase_a_ledger",),
            )


def _current_version(
    conn: Connection[Any],
    table: str,
    logical_column: str,
    logical_id: str,
) -> tuple[UUID, str, UUID | None] | None:
    allowed = {
        ("source_record_versions", "logical_key"),
        ("funding_project_versions", "operation_code"),
        ("component_versions", "component_id"),
        ("procurement_evidence_versions", "evidence_id"),
        ("assessment_versions", "assessment_id"),
        ("project_assessment_versions", "operation_code"),
        ("outcome_versions", "outcome_id"),
        ("run_manifests", "run_key"),
    }
    if (table, logical_column) not in allowed:
        raise ValueError("unsupported ledger version table")
    row = conn.execute(
        f"""
        SELECT current.version_id, current.content_sha256, current.supersedes_version_id
        FROM procrun.{table} AS current
        WHERE current.{logical_column} = %s
          AND NOT EXISTS (
              SELECT 1 FROM procrun.{table} AS newer
              WHERE newer.supersedes_version_id = current.version_id
          )
        ORDER BY current.inserted_at DESC
        LIMIT 1
        """,
        (logical_id,),
    ).fetchone()
    if row is None:
        return None
    predecessor = None if row[2] is None else UUID(str(row[2]))
    return UUID(str(row[0])), str(row[1]).strip(), predecessor


def _plan_version(
    *,
    kind: str,
    logical_id: str,
    digest: str,
    current: tuple[UUID, str, UUID | None] | None,
) -> VersionWrite:
    if current is not None and current[1] == digest:
        return VersionWrite(current[0], digest, False, current[2])
    supersedes = None if current is None else current[0]
    version_id = _version_uuid(kind, logical_id, digest, supersedes)
    return VersionWrite(version_id, digest, True, supersedes)


def record_source_snapshot(
    conn: Connection[Any],
    *,
    source_id: str,
    source_record_id: str,
    source_url: str,
    retrieved_at: datetime,
    normalized: FundingProject | ProcurementEvidence,
    schema_version: str,
    run_key: str | None = None,
) -> VersionWrite:
    """Persist one allowlisted source content version plus an immutable retrieval observation."""

    require_live_source(source_id)
    _utc_iso(retrieved_at)
    payload = normalized.model_dump(mode="json")
    logical_key = f"{source_id}:{source_record_id}"
    record_kind = (
        "funding_project" if isinstance(normalized, FundingProject) else "procurement_evidence"
    )
    digest = content_sha256(
        {
            "source_id": source_id,
            "source_record_id": source_record_id,
            "record_kind": record_kind,
            "source_url": source_url,
            "schema_version": schema_version,
            "normalized_fields": payload,
        }
    )
    current = _current_version(conn, "source_record_versions", "logical_key", logical_key)
    plan = _plan_version(kind="source", logical_id=logical_key, digest=digest, current=current)
    first_seen = normalized.first_seen_at if isinstance(normalized, FundingProject) else None
    if first_seen is not None:
        _utc_iso(first_seen)

    if plan.inserted:
        conn.execute(
            """
            INSERT INTO procrun.source_record_versions (
                version_id, logical_key, source_id, source_record_id, record_kind, source_url,
                source_first_seen_at, schema_version, normalized_fields, content_sha256,
                supersedes_version_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (version_id) DO NOTHING
            """,
            (
                plan.version_id,
                logical_key,
                source_id,
                source_record_id,
                record_kind,
                source_url,
                first_seen,
                schema_version,
                Jsonb(payload),
                digest,
                plan.supersedes_version_id,
            ),
        )
    retrieval_key = run_key if run_key is not None else _utc_iso(retrieved_at)
    retrieval_id = _version_uuid(
        "retrieval",
        str(plan.version_id),
        content_sha256(retrieval_key),
        None,
    )
    conn.execute(
        """
        INSERT INTO procrun.source_retrievals (
            retrieval_id, source_version_id, run_key, retrieved_at
        ) VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        (retrieval_id, plan.version_id, run_key, retrieved_at),
    )
    return plan


def append_funding_project_version(
    conn: Connection[Any],
    *,
    project: FundingProject,
    source_record_version_id: UUID,
    as_of: datetime,
) -> VersionWrite:
    _utc_iso(as_of)
    if project.first_seen_at is not None:
        _utc_iso(project.first_seen_at)
    source_kind = conn.execute(
        "SELECT record_kind FROM procrun.source_record_versions WHERE version_id = %s",
        (source_record_version_id,),
    ).fetchone()
    if source_kind is None or source_kind[0] != "funding_project":
        raise LedgerInvariantError(
            "funding project version requires funding-project source provenance"
        )
    digest = content_sha256(
        {
            "project": project,
            "source_record_version_id": str(source_record_version_id),
        }
    )
    current = _current_version(
        conn,
        "funding_project_versions",
        "operation_code",
        project.operation_code,
    )
    plan = _plan_version(
        kind="funding-project",
        logical_id=project.operation_code,
        digest=digest,
        current=current,
    )
    if not plan.inserted:
        return plan
    conn.execute(
        """
        INSERT INTO procrun.funding_project_versions (
            version_id, operation_code, source_record_version_id, as_of, first_seen_at,
            temporal_provenance, project_title, project_start, project_end,
            approved_funding_eur, executed_funding_eur, project_scope_text, fund, programme,
            objective, theme, region, municipality, nuts_code, content_sha256,
            supersedes_version_id
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s
        )
        ON CONFLICT (version_id) DO NOTHING
        """,
        (
            plan.version_id,
            project.operation_code,
            source_record_version_id,
            as_of,
            project.first_seen_at,
            project.temporal_provenance.value,
            project.project_title,
            project.project_start,
            project.project_end,
            project.approved_funding_eur,
            project.executed_funding_eur,
            project.project_scope_text,
            project.fund,
            project.programme,
            project.objective,
            project.theme,
            project.region,
            project.municipality,
            project.nuts_code,
            digest,
            plan.supersedes_version_id,
        ),
    )
    return plan


def append_component_version(
    conn: Connection[Any],
    *,
    component: PurchaseComponent,
    as_of: datetime,
    extractor_version: str,
) -> VersionWrite:
    _utc_iso(as_of)
    digest = content_sha256(
        {
            "component": component,
            "extractor_version": extractor_version,
        }
    )
    current = _current_version(conn, "component_versions", "component_id", component.component_id)
    plan = _plan_version(
        kind="component",
        logical_id=component.component_id,
        digest=digest,
        current=current,
    )
    if not plan.inserted:
        return plan
    conn.execute(
        """
        INSERT INTO procrun.component_versions (
            version_id, component_id, operation_code, as_of, category, description,
            scope_evidence, extractor_version, content_sha256, supersedes_version_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (version_id) DO NOTHING
        """,
        (
            plan.version_id,
            component.component_id,
            component.operation_code,
            as_of,
            component.category,
            component.description,
            component.scope_evidence,
            extractor_version,
            digest,
            plan.supersedes_version_id,
        ),
    )
    return plan


def append_procurement_evidence_version(
    conn: Connection[Any],
    *,
    evidence: ProcurementEvidence,
    source_record_version_id: UUID,
    as_of: datetime,
) -> VersionWrite:
    _utc_iso(as_of)
    source_kind = conn.execute(
        "SELECT record_kind FROM procrun.source_record_versions WHERE version_id = %s",
        (source_record_version_id,),
    ).fetchone()
    if source_kind is None or source_kind[0] != "procurement_evidence":
        raise LedgerInvariantError("procurement evidence requires procurement source provenance")
    digest = content_sha256(
        {
            "evidence": evidence,
            "source_record_version_id": str(source_record_version_id),
        }
    )
    current = _current_version(
        conn,
        "procurement_evidence_versions",
        "evidence_id",
        evidence.evidence_id,
    )
    plan = _plan_version(
        kind="evidence",
        logical_id=evidence.evidence_id,
        digest=digest,
        current=current,
    )
    if not plan.inserted:
        return plan
    conn.execute(
        """
        INSERT INTO procrun.procurement_evidence_versions (
            version_id, evidence_id, component_id, as_of, notice_id, publication_date,
            award_date, contract_date, title, scope_description, cpv_codes, contract_nature,
            procedure_type, procedure_value_eur, estimated_value_eur, base_value_eur,
            awarded_value_eur, place_of_performance, nuts_code, municipality,
            contracting_authority_name, project_reference, source_record_version_id,
            content_sha256, supersedes_version_id
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (version_id) DO NOTHING
        """,
        (
            plan.version_id,
            evidence.evidence_id,
            evidence.component_id,
            as_of,
            evidence.notice_id,
            evidence.publication_date,
            evidence.award_date,
            evidence.contract_date,
            evidence.title,
            evidence.scope_description,
            list(evidence.cpv_codes),
            evidence.contract_nature,
            evidence.procedure_type,
            evidence.procedure_value_eur,
            evidence.estimated_value_eur,
            evidence.base_value_eur,
            evidence.awarded_value_eur,
            evidence.place_of_performance,
            evidence.nuts_code,
            evidence.municipality,
            evidence.contracting_authority_name,
            evidence.project_reference,
            source_record_version_id,
            digest,
            plan.supersedes_version_id,
        ),
    )
    return plan


def append_assessment_version(
    conn: Connection[Any],
    *,
    assessment_id: str,
    operation_code: str,
    assessment: ComponentAssessment,
    as_of: datetime,
    rule_version: str,
    model_version: str | None,
    matching_candidates: Sequence[Mapping[str, Any]],
    accepted_evidence_version_ids: Sequence[UUID],
    rejected_evidence: Sequence[Mapping[str, Any]],
) -> VersionWrite:
    _utc_iso(as_of)
    digest = content_sha256(
        {
            "assessment": assessment,
            "operation_code": operation_code,
            "rule_version": rule_version,
            "model_version": model_version,
            "matching_candidates": matching_candidates,
            "accepted_evidence_version_ids": [
                str(version_id) for version_id in accepted_evidence_version_ids
            ],
            "rejected_evidence": rejected_evidence,
        }
    )
    current = _current_version(conn, "assessment_versions", "assessment_id", assessment_id)
    plan = _plan_version(
        kind="assessment",
        logical_id=assessment_id,
        digest=digest,
        current=current,
    )
    if not plan.inserted:
        return plan
    conn.execute(
        """
        INSERT INTO procrun.assessment_versions (
            version_id, assessment_id, component_id, operation_code, state, cutoff_date,
            as_of, rule_version, model_version, matching_candidates, accepted_evidence_ids,
            accepted_evidence_version_ids, rejected_evidence, rationale, coverage_note,
            content_sha256,
            supersedes_version_id
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (version_id) DO NOTHING
        """,
        (
            plan.version_id,
            assessment_id,
            assessment.component_id,
            operation_code,
            assessment.state.value,
            assessment.cutoff_date,
            as_of,
            rule_version,
            model_version,
            Jsonb(_jsonable(matching_candidates)),
            list(assessment.evidence_ids),
            list(accepted_evidence_version_ids),
            Jsonb(_jsonable(rejected_evidence)),
            assessment.rationale,
            assessment.coverage_note,
            digest,
            plan.supersedes_version_id,
        ),
    )
    return plan


def append_project_assessment_version(
    conn: Connection[Any],
    *,
    assessment: ProjectAssessment,
    component_assessment_version_ids: Sequence[UUID],
    as_of: datetime,
    classifier_version: str,
) -> VersionWrite:
    _utc_iso(as_of)
    if len(component_assessment_version_ids) != len(assessment.components):
        raise LedgerInvariantError(
            "project assessment must reference one component-assessment version per component"
        )
    digest = content_sha256(
        {
            "assessment": assessment,
            "component_assessment_version_ids": [
                str(version_id) for version_id in component_assessment_version_ids
            ],
            "classifier_version": classifier_version,
        }
    )
    current = _current_version(
        conn,
        "project_assessment_versions",
        "operation_code",
        assessment.operation_code,
    )
    plan = _plan_version(
        kind="project-assessment",
        logical_id=assessment.operation_code,
        digest=digest,
        current=current,
    )
    if not plan.inserted:
        return plan
    conn.execute(
        """
        INSERT INTO procrun.project_assessment_versions (
            version_id, operation_code, state, cutoff_date, as_of, classifier_version,
            component_assessment_version_ids, content_sha256, supersedes_version_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (version_id) DO NOTHING
        """,
        (
            plan.version_id,
            assessment.operation_code,
            assessment.state.value,
            assessment.cutoff_date,
            as_of,
            classifier_version,
            list(component_assessment_version_ids),
            digest,
            plan.supersedes_version_id,
        ),
    )
    return plan


def append_outcome_version(
    conn: Connection[Any],
    *,
    outcome_id: str,
    assessment_version_id: UUID,
    procurement_evidence_version_id: UUID,
    original_signal_at: datetime,
    outcome_date: date,
    as_of: datetime,
) -> VersionWrite:
    _utc_iso(original_signal_at)
    _utc_iso(as_of)
    lead_days = (outcome_date - original_signal_at.date()).days
    if lead_days < 0:
        raise ValueError("outcome_date cannot predate the original signal")
    digest = content_sha256(
        {
            "assessment_version_id": str(assessment_version_id),
            "procurement_evidence_version_id": str(procurement_evidence_version_id),
            "original_signal_at": original_signal_at,
            "outcome_date": outcome_date,
            "lead_days": lead_days,
        }
    )
    current = _current_version(conn, "outcome_versions", "outcome_id", outcome_id)
    plan = _plan_version(
        kind="outcome",
        logical_id=outcome_id,
        digest=digest,
        current=current,
    )
    if not plan.inserted:
        return plan
    conn.execute(
        """
        INSERT INTO procrun.outcome_versions (
            version_id, outcome_id, assessment_version_id,
            procurement_evidence_version_id, original_signal_at, outcome_date,
            lead_days, as_of, content_sha256, supersedes_version_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (version_id) DO NOTHING
        """,
        (
            plan.version_id,
            outcome_id,
            assessment_version_id,
            procurement_evidence_version_id,
            original_signal_at,
            outcome_date,
            lead_days,
            as_of,
            digest,
            plan.supersedes_version_id,
        ),
    )
    return plan


def append_run_manifest(
    conn: Connection[Any],
    *,
    run_key: str,
    started_at: datetime,
    completed_at: datetime,
    classifier_version: str,
    counts: Mapping[str, int],
    input_sha256: str,
    output_sha256: str,
    schema_version: str = LEDGER_SCHEMA_VERSION,
) -> VersionWrite:
    _utc_iso(started_at)
    _utc_iso(completed_at)
    if completed_at < started_at:
        raise ValueError("completed_at cannot predate started_at")
    _require_sha256(input_sha256, "input_sha256")
    _require_sha256(output_sha256, "output_sha256")
    if any(value < 0 for value in counts.values()):
        raise ValueError("manifest counts cannot be negative")
    digest = content_sha256(
        {
            "run_key": run_key,
            "schema_version": schema_version,
            "classifier_version": classifier_version,
            "counts": counts,
            "input_sha256": input_sha256,
            "output_sha256": output_sha256,
        }
    )
    current = _current_version(conn, "run_manifests", "run_key", run_key)
    plan = _plan_version(
        kind="manifest",
        logical_id=run_key,
        digest=digest,
        current=current,
    )
    if not plan.inserted:
        return plan
    conn.execute(
        """
        INSERT INTO procrun.run_manifests (
            version_id, run_key, started_at, completed_at, schema_version,
            classifier_version, counts, input_sha256, output_sha256, manifest_sha256,
            supersedes_version_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (version_id) DO NOTHING
        """,
        (
            plan.version_id,
            run_key,
            started_at,
            completed_at,
            schema_version,
            classifier_version,
            Jsonb(dict(counts)),
            input_sha256,
            output_sha256,
            digest,
            plan.supersedes_version_id,
        ),
    )
    return plan
