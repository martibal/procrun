"""Additional readiness invariants that depend on the base readiness schema."""

from __future__ import annotations

from typing import Any

from psycopg import Connection

HARDENING_SQL = """
CREATE UNIQUE INDEX IF NOT EXISTS readiness_dossiers_purchase_once_idx
    ON procrun_readiness.dossiers(purchase_reference);
"""


def apply_readiness_hardening(conn: Connection[Any]) -> None:
    with conn.cursor() as cur:
        cur.execute(HARDENING_SQL)
    conn.commit()
