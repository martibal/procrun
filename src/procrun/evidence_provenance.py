"""Append-only persistence for exact customer-verifiable source spans."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from psycopg import Connection

from procrun.domain import ProcurementEvidence, PurchaseComponent

EVIDENCE_PROVENANCE_MIGRATION_ID = "002_exact_source_spans"

_MIGRATION = r"""
CREATE TABLE procrun.component_source_spans (
    component_version_id uuid PRIMARY KEY
        REFERENCES procrun.component_versions(version_id),
    source_field text NOT NULL CHECK (source_field = 'project_scope_text'),
    start_offset integer NOT NULL CHECK (start_offset >= 0),
    end_offset integer NOT NULL CHECK (end_offset > start_offset),
    evidence_text text NOT NULL,
    inserted_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE procrun.procurement_source_spans (
    procurement_evidence_version_id uuid PRIMARY KEY
        REFERENCES procrun.procurement_evidence_versions(version_id),
    source_field text NOT NULL CHECK (source_field IN ('title', 'scope_description')),
    start_offset integer NOT NULL CHECK (start_offset >= 0),
    end_offset integer NOT NULL CHECK (end_offset > start_offset),
    evidence_text text NOT NULL,
    inserted_at timestamptz NOT NULL DEFAULT now()
);

CREATE TRIGGER component_source_spans_append_only
BEFORE UPDATE OR DELETE ON procrun.component_source_spans
FOR EACH ROW EXECUTE FUNCTION procrun.reject_ledger_mutation();

CREATE TRIGGER procurement_source_spans_append_only
BEFORE UPDATE OR DELETE ON procrun.procurement_source_spans
FOR EACH ROW EXECUTE FUNCTION procrun.reject_ledger_mutation();
"""


class EvidenceProvenanceError(ValueError):
    """Raised when a persisted exact span is missing or inconsistent."""


@dataclass(frozen=True)
class PersistedSpan:
    source_field: str
    start: int
    end: int
    text: str


def apply_evidence_provenance_migration(conn: Connection[Any]) -> None:
    """Apply the exact-source-span migration after the base ledger migration."""

    with conn.transaction():
        applied = conn.execute(
            "SELECT 1 FROM procrun.schema_migrations WHERE migration_id = %s",
            (EVIDENCE_PROVENANCE_MIGRATION_ID,),
        ).fetchone()
        if applied is not None:
            return
        conn.execute(_MIGRATION)
        conn.execute(
            "INSERT INTO procrun.schema_migrations (migration_id) VALUES (%s)",
            (EVIDENCE_PROVENANCE_MIGRATION_ID,),
        )


def append_component_source_span(
    conn: Connection[Any],
    *,
    component_version_id: UUID,
    component: PurchaseComponent,
) -> PersistedSpan:
    """Persist the exact project-scope span attached to a component version."""

    start = component.scope_evidence_start
    end = component.scope_evidence_end
    if start is None or end is None:
        raise EvidenceProvenanceError("component lacks exact source offsets")
    span = PersistedSpan(
        source_field=component.scope_source_field,
        start=start,
        end=end,
        text=component.scope_evidence,
    )
    conn.execute(
        """
        INSERT INTO procrun.component_source_spans (
            component_version_id, source_field, start_offset, end_offset, evidence_text
        ) VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (component_version_id) DO NOTHING
        """,
        (component_version_id, span.source_field, span.start, span.end, span.text),
    )
    return span


def append_procurement_source_span(
    conn: Connection[Any],
    *,
    procurement_evidence_version_id: UUID,
    evidence: ProcurementEvidence,
) -> PersistedSpan:
    """Persist the exact source span that supports an accepted procurement match."""

    if (
        evidence.evidence_field is None
        or evidence.evidence_text is None
        or evidence.evidence_start is None
        or evidence.evidence_end is None
    ):
        raise EvidenceProvenanceError("procurement evidence lacks an exact source span")
    span = PersistedSpan(
        source_field=evidence.evidence_field.value,
        start=evidence.evidence_start,
        end=evidence.evidence_end,
        text=evidence.evidence_text,
    )
    conn.execute(
        """
        INSERT INTO procrun.procurement_source_spans (
            procurement_evidence_version_id, source_field, start_offset, end_offset, evidence_text
        ) VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (procurement_evidence_version_id) DO NOTHING
        """,
        (
            procurement_evidence_version_id,
            span.source_field,
            span.start,
            span.end,
            span.text,
        ),
    )
    return span


def load_component_source_span(
    conn: Connection[Any], component_version_id: UUID
) -> PersistedSpan:
    row = conn.execute(
        """
        SELECT source_field, start_offset, end_offset, evidence_text
        FROM procrun.component_source_spans
        WHERE component_version_id = %s
        """,
        (component_version_id,),
    ).fetchone()
    if row is None:
        raise EvidenceProvenanceError("component source span is not persisted")
    return PersistedSpan(str(row[0]), int(row[1]), int(row[2]), str(row[3]))


def load_procurement_source_span(
    conn: Connection[Any], procurement_evidence_version_id: UUID
) -> PersistedSpan:
    row = conn.execute(
        """
        SELECT source_field, start_offset, end_offset, evidence_text
        FROM procrun.procurement_source_spans
        WHERE procurement_evidence_version_id = %s
        """,
        (procurement_evidence_version_id,),
    ).fetchone()
    if row is None:
        raise EvidenceProvenanceError("procurement source span is not persisted")
    return PersistedSpan(str(row[0]), int(row[1]), int(row[2]), str(row[3]))
