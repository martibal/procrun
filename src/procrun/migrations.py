"""Canonical database migration entrypoint for ProcRun production state."""

from typing import Any

from psycopg import Connection

from procrun.account_activity import apply_account_activity_migration
from procrun.evidence_provenance import apply_evidence_provenance_migration
from procrun.ledger import apply_migrations as apply_ledger_migrations
from procrun.procurement_history import (
    apply_procurement_history_migration,
    record_latest_assessments_as_observations,
)


def _seed_current_procurement_history(conn: Connection[Any]) -> None:
    """Seed the immutable history once from the latest accepted production assessments."""

    existing = conn.execute(
        "SELECT count(*) FROM procrun.procurement_observations"
    ).fetchone()
    if existing is not None and int(existing[0]) > 0:
        return

    latest = conn.execute(
        "SELECT max(cutoff_date) FROM procrun.assessment_versions"
    ).fetchone()
    if latest is None or latest[0] is None:
        return

    inserted = record_latest_assessments_as_observations(conn, latest[0])
    if inserted == 0:
        raise RuntimeError(
            "latest production assessments exist but procurement history backfill inserted zero rows"
        )


def apply_all_migrations(conn: Connection[Any]) -> None:
    """Apply every production migration required by the web-facing runway contract."""

    apply_ledger_migrations(conn)
    apply_evidence_provenance_migration(conn)
    apply_procurement_history_migration(conn)
    with conn.transaction():
        _seed_current_procurement_history(conn)
    apply_account_activity_migration(conn)
