import os
from datetime import datetime, timezone

import psycopg
import pytest

from procrun.migrations import apply_all_migrations

DATABASE_URL = os.environ.get("PROCRUN_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(DATABASE_URL is None, reason="PostgreSQL integration DB not configured")


def test_account_activity_schema_and_daily_marker() -> None:
    assert DATABASE_URL is not None
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        conn.execute("DROP SCHEMA IF EXISTS procrun CASCADE")
        apply_all_migrations(conn)
        conn.execute("INSERT INTO procrun.accounts (account_id) VALUES ('acct-test')")
        conn.execute(
            "INSERT INTO procrun.component_matches (account_id, component_id, first_matched_at) "
            "VALUES ('acct-test', 'opp-new', %s)",
            (datetime(2026, 9, 7, 8, tzinfo=timezone.utc),),
        )
        conn.execute(
            "INSERT INTO procrun.saved_opportunities "
            "(account_id, component_id, state_at_last_summary) "
            "VALUES ('acct-test', 'opp-saved', 'OPEN')"
        )
        row = conn.execute(
            "SELECT last_active_summary_at FROM procrun.accounts WHERE account_id = 'acct-test'"
        ).fetchone()
        assert row == (None,)
        match = conn.execute(
            "SELECT first_matched_at FROM procrun.component_matches "
            "WHERE account_id = 'acct-test' AND component_id = 'opp-new'"
        ).fetchone()
        assert match is not None


def test_sync_runs_remain_independent_of_account_summary() -> None:
    assert DATABASE_URL is not None
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        conn.execute("DROP SCHEMA IF EXISTS procrun CASCADE")
        apply_all_migrations(conn)
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'procrun' "
                "AND tablename IN ('accounts','component_matches','saved_opportunities','sync_runs')"
            ).fetchall()
        }
        assert tables == {"accounts", "component_matches", "saved_opportunities", "sync_runs"}
