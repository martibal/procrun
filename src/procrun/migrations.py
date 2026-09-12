"""Canonical database migration entrypoint for ProcRun production state."""

from typing import Any

from psycopg import Connection

from procrun.evidence_provenance import apply_evidence_provenance_migration
from procrun.ledger import apply_migrations as apply_ledger_migrations
from procrun.readiness_persistence import apply_readiness_migration


def apply_all_migrations(conn: Connection[Any]) -> None:
    """Apply every production migration required by ProcRun production contracts."""

    apply_ledger_migrations(conn)
    apply_evidence_provenance_migration(conn)
    apply_readiness_migration(conn)
