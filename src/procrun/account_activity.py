"""Customer-control-plane schema used by the 'since last visit' summary.

These tables contain account workflow state only. They do not widen the intelligence-plane
customer-safe or source boundaries.
"""

from __future__ import annotations

from typing import Any

from psycopg import Connection

ACCOUNT_ACTIVITY_MIGRATION_ID = "004_account_activity_summary"

_MIGRATION = r"""
CREATE TABLE IF NOT EXISTS procrun.accounts (
    account_id text PRIMARY KEY,
    last_active_summary_at timestamptz
);
ALTER TABLE procrun.accounts
    ADD COLUMN IF NOT EXISTS last_active_summary_at timestamptz;

CREATE TABLE IF NOT EXISTS procrun.component_matches (
    account_id text NOT NULL REFERENCES procrun.accounts(account_id) ON DELETE CASCADE,
    component_id text NOT NULL,
    first_matched_at timestamptz NOT NULL,
    PRIMARY KEY (account_id, component_id)
);
ALTER TABLE procrun.component_matches
    ADD COLUMN IF NOT EXISTS first_matched_at timestamptz;
CREATE INDEX IF NOT EXISTS component_matches_since_idx
    ON procrun.component_matches (account_id, first_matched_at);

CREATE TABLE IF NOT EXISTS procrun.saved_opportunities (
    account_id text NOT NULL REFERENCES procrun.accounts(account_id) ON DELETE CASCADE,
    component_id text NOT NULL,
    state_at_last_summary text CHECK (
        state_at_last_summary IS NULL
        OR state_at_last_summary IN ('OPEN', 'CLOSED', 'UNRESOLVED')
    ),
    PRIMARY KEY (account_id, component_id)
);
ALTER TABLE procrun.saved_opportunities
    ADD COLUMN IF NOT EXISTS state_at_last_summary text;
"""


def apply_account_activity_migration(conn: Connection[Any]) -> None:
    """Apply the minimal control-plane state required for daily account summaries."""

    with conn.transaction():
        applied = conn.execute(
            "SELECT 1 FROM procrun.schema_migrations WHERE migration_id = %s",
            (ACCOUNT_ACTIVITY_MIGRATION_ID,),
        ).fetchone()
        if applied is not None:
            return
        conn.execute(_MIGRATION)
        conn.execute(
            "INSERT INTO procrun.schema_migrations (migration_id) VALUES (%s)",
            (ACCOUNT_ACTIVITY_MIGRATION_ID,),
        )
