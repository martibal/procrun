"""Canonical database migration entrypoint for ProcRun production state."""

from typing import Any

from psycopg import Connection

from procrun.evidence_provenance import apply_evidence_provenance_migration
from procrun.ledger import apply_migrations as apply_ledger_migrations


def apply_all_migrations(conn: Connection[Any]) -> None:
    """Apply every production migration required by the web-facing runway contract."""

    apply_ledger_migrations(conn)
    apply_evidence_provenance_migration(conn)
