"""Append-only procurement observation history and sync-run logging."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from psycopg import Connection
from psycopg.types.json import Jsonb

from procrun.domain import ComponentState

PROCUREMENT_HISTORY_MIGRATION_ID = "003_procurement_observation_history"

_MIGRATION = r"""
CREATE TABLE procrun.procurement_observations (
    id uuid PRIMARY KEY,
    component_id text NOT NULL,
    operation_code text NOT NULL,
    observed_at date NOT NULL,
    state text NOT NULL CHECK (state IN ('OPEN', 'CLOSED', 'UNRESOLVED')),
    evidence_reference text,
    evidence_url text,
    evidence_excerpt text,
    coverage_note text NOT NULL,
    correction_of_id uuid REFERENCES procrun.procurement_observations(id),
    correction_reason text,
    inserted_at timestamptz NOT NULL DEFAULT now(),
    CHECK (
        state <> 'CLOSED'
        OR (
            evidence_reference IS NOT NULL
            AND evidence_url IS NOT NULL
            AND evidence_excerpt IS NOT NULL
        )
    ),
    CHECK (
        (correction_of_id IS NULL AND correction_reason IS NULL)
        OR (correction_of_id IS NOT NULL AND correction_reason IS NOT NULL)
    )
);
CREATE INDEX procurement_observations_component_idx
    ON procrun.procurement_observations (component_id, observed_at, inserted_at);
CREATE INDEX procurement_observations_operation_idx
    ON procrun.procurement_observations (operation_code, observed_at);

CREATE TRIGGER procurement_observations_append_only
BEFORE UPDATE OR DELETE ON procrun.procurement_observations
FOR EACH ROW EXECUTE FUNCTION procrun.reject_ledger_mutation();

CREATE TABLE procrun.sync_runs (
    id uuid PRIMARY KEY,
    job_name text NOT NULL CHECK (job_name IN ('ted_daily', 'opencoesione_bimonthly')),
    started_at timestamptz NOT NULL,
    completed_at timestamptz NOT NULL,
    status text NOT NULL CHECK (status IN ('SUCCESS', 'ERROR')),
    row_count integer NOT NULL CHECK (row_count >= 0),
    detail jsonb NOT NULL DEFAULT '{}'::jsonb,
    error_message text,
    inserted_at timestamptz NOT NULL DEFAULT now(),
    CHECK (completed_at >= started_at),
    CHECK ((status = 'ERROR') = (error_message IS NOT NULL))
);
CREATE INDEX sync_runs_job_idx
    ON procrun.sync_runs (job_name, completed_at DESC);

CREATE TRIGGER sync_runs_append_only
BEFORE UPDATE OR DELETE ON procrun.sync_runs
FOR EACH ROW EXECUTE FUNCTION procrun.reject_ledger_mutation();
"""


@dataclass(frozen=True)
class ProcurementObservation:
    id: UUID
    component_id: str
    operation_code: str
    observed_at: date
    state: ComponentState
    evidence_reference: str | None
    evidence_url: str | None
    evidence_excerpt: str | None
    coverage_note: str
    correction_of_id: UUID | None = None
    correction_reason: str | None = None


def apply_procurement_history_migration(conn: Connection[Any]) -> None:
    """Apply the append-only observation/sync-run migration."""

    with conn.transaction():
        applied = conn.execute(
            "SELECT 1 FROM procrun.schema_migrations WHERE migration_id = %s",
            (PROCUREMENT_HISTORY_MIGRATION_ID,),
        ).fetchone()
        if applied is not None:
            return
        conn.execute(_MIGRATION)
        conn.execute(
            "INSERT INTO procrun.schema_migrations (migration_id) VALUES (%s)",
            (PROCUREMENT_HISTORY_MIGRATION_ID,),
        )


def should_store_observation(
    *,
    previous_state: ComponentState | None,
    previous_observed_at: date | None,
    state: ComponentState,
    observed_at: date,
) -> bool:
    """Store state transitions and a 30-day heartbeat for unchanged states."""

    if previous_state is None or previous_observed_at is None:
        return True
    if observed_at < previous_observed_at:
        raise ValueError("normal observations cannot move backwards in time")
    if state is not previous_state:
        return True
    return (observed_at - previous_observed_at).days >= 30


def append_procurement_observation(
    conn: Connection[Any],
    *,
    component_id: str,
    operation_code: str,
    observed_at: date,
    state: ComponentState,
    evidence_reference: str | None,
    evidence_url: str | None,
    evidence_excerpt: str | None,
    coverage_note: str,
    correction_of_id: UUID | None = None,
    correction_reason: str | None = None,
) -> ProcurementObservation | None:
    """Append one immutable observation when the transition/30-day rule requires it."""

    if state is ComponentState.CLOSED and not all(
        (evidence_reference, evidence_url, evidence_excerpt)
    ):
        raise ValueError("CLOSED observations require reference, URL and exact evidence excerpt")
    if (correction_of_id is None) != (correction_reason is None):
        raise ValueError("correction id and reason must be supplied together")

    previous = conn.execute(
        """
        SELECT state, observed_at
        FROM procrun.procurement_observations
        WHERE component_id = %s
        ORDER BY observed_at DESC, inserted_at DESC
        LIMIT 1
        """,
        (component_id,),
    ).fetchone()
    previous_state = ComponentState(str(previous[0])) if previous is not None else None
    previous_date = previous[1] if previous is not None else None

    if correction_of_id is None and not should_store_observation(
        previous_state=previous_state,
        previous_observed_at=previous_date,
        state=state,
        observed_at=observed_at,
    ):
        return None

    observation = ProcurementObservation(
        id=uuid4(),
        component_id=component_id,
        operation_code=operation_code,
        observed_at=observed_at,
        state=state,
        evidence_reference=evidence_reference,
        evidence_url=evidence_url,
        evidence_excerpt=evidence_excerpt,
        coverage_note=coverage_note,
        correction_of_id=correction_of_id,
        correction_reason=correction_reason,
    )
    conn.execute(
        """
        INSERT INTO procrun.procurement_observations (
            id, component_id, operation_code, observed_at, state,
            evidence_reference, evidence_url, evidence_excerpt, coverage_note,
            correction_of_id, correction_reason
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            observation.id,
            observation.component_id,
            observation.operation_code,
            observation.observed_at,
            observation.state.value,
            observation.evidence_reference,
            observation.evidence_url,
            observation.evidence_excerpt,
            observation.coverage_note,
            observation.correction_of_id,
            observation.correction_reason,
        ),
    )
    return observation


def record_latest_assessments_as_observations(
    conn: Connection[Any], observed_at: date
) -> int:
    """Snapshot the day's latest component assessments into the immutable history."""

    rows = conn.execute(
        """
        SELECT DISTINCT ON (a.component_id)
            a.component_id,
            a.operation_code,
            a.state,
            a.coverage_note,
            a.accepted_evidence_version_ids
        FROM procrun.assessment_versions a
        WHERE a.cutoff_date = %s
        ORDER BY a.component_id, a.as_of DESC, a.inserted_at DESC
        """,
        (observed_at,),
    ).fetchall()

    inserted = 0
    for component_id, operation_code, state_text, coverage_note, evidence_version_ids in rows:
        state = ComponentState(str(state_text))
        reference: str | None = None
        url: str | None = None
        excerpt: str | None = None
        if state is ComponentState.CLOSED:
            if not evidence_version_ids:
                raise ValueError(f"CLOSED assessment lacks accepted evidence: {component_id}")
            evidence = conn.execute(
                """
                SELECT pe.notice_id, sr.source_url,
                       COALESCE(ps.evidence_text, sr.normalized_fields->>'evidence_text')
                FROM procrun.procurement_evidence_versions pe
                JOIN procrun.source_record_versions sr
                  ON sr.version_id = pe.source_record_version_id
                LEFT JOIN procrun.procurement_source_spans ps
                  ON ps.procurement_evidence_version_id = pe.version_id
                WHERE pe.version_id = %s
                """,
                (evidence_version_ids[0],),
            ).fetchone()
            if evidence is None or evidence[2] is None:
                raise ValueError(f"CLOSED evidence is not independently verifiable: {component_id}")
            reference, url, excerpt = str(evidence[0]), str(evidence[1]), str(evidence[2])

        write = append_procurement_observation(
            conn,
            component_id=str(component_id),
            operation_code=str(operation_code),
            observed_at=observed_at,
            state=state,
            evidence_reference=reference,
            evidence_url=url,
            evidence_excerpt=excerpt,
            coverage_note=str(coverage_note),
        )
        inserted += int(write is not None)
    return inserted


def record_sync_run(
    conn: Connection[Any],
    *,
    job_name: Literal["ted_daily", "opencoesione_bimonthly"],
    started_at: datetime,
    completed_at: datetime,
    status: Literal["SUCCESS", "ERROR"],
    row_count: int,
    detail: dict[str, Any] | None = None,
    error_message: str | None = None,
) -> UUID:
    """Append one immutable operational sync result."""

    if status == "ERROR" and not error_message:
        raise ValueError("ERROR sync runs require an error message")
    if status == "SUCCESS" and error_message is not None:
        raise ValueError("SUCCESS sync runs cannot carry an error message")
    run_id = uuid4()
    conn.execute(
        """
        INSERT INTO procrun.sync_runs (
            id, job_name, started_at, completed_at, status, row_count, detail, error_message
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            run_id,
            job_name,
            started_at,
            completed_at,
            status,
            row_count,
            Jsonb(detail or {}),
            error_message,
        ),
    )
    return run_id
