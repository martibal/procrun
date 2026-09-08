"""Persisted supplier-profile state for deterministic customer relevance matching.

The profile contains company/workflow configuration only. Personal contact, billing identity, and
source-derived personal data are outside this schema.
"""

from __future__ import annotations

from typing import Any

from psycopg import Connection

SUPPLIER_PROFILE_MIGRATION_ID = "005_supplier_profiles"

_MIGRATION = r"""
CREATE TABLE IF NOT EXISTS procrun.supplier_profiles (
    account_id text PRIMARY KEY REFERENCES procrun.accounts(account_id) ON DELETE CASCADE,
    company_name text NOT NULL CHECK (length(btrim(company_name)) > 0),
    target_market text NOT NULL CHECK (target_market = 'LOMBARDIA'),
    category_prefixes text[] NOT NULL DEFAULT '{}',
    cpv_include text[] NOT NULL DEFAULT '{}',
    cpv_exclude text[] NOT NULL DEFAULT '{}',
    min_project_value_eur bigint CHECK (
        min_project_value_eur IS NULL OR min_project_value_eur >= 0
    ),
    max_project_value_eur bigint CHECK (
        max_project_value_eur IS NULL OR max_project_value_eur >= 0
    ),
    completed_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CHECK (
        max_project_value_eur IS NULL
        OR min_project_value_eur IS NULL
        OR max_project_value_eur >= min_project_value_eur
    )
);
CREATE INDEX IF NOT EXISTS supplier_profiles_market_idx
    ON procrun.supplier_profiles (target_market);
"""


def apply_supplier_profile_migration(conn: Connection[Any]) -> None:
    """Apply the account-scoped Supplier Profile persistence contract."""

    with conn.transaction():
        applied = conn.execute(
            "SELECT 1 FROM procrun.schema_migrations WHERE migration_id = %s",
            (SUPPLIER_PROFILE_MIGRATION_ID,),
        ).fetchone()
        if applied is not None:
            return
        conn.execute(_MIGRATION)
        conn.execute(
            "INSERT INTO procrun.schema_migrations (migration_id) VALUES (%s)",
            (SUPPLIER_PROFILE_MIGRATION_ID,),
        )
