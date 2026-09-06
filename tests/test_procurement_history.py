import os
from datetime import date

import psycopg
import pytest

from procrun.domain import ComponentState
from procrun.migrations import apply_all_migrations
from procrun.procurement_history import (
    append_procurement_observation,
    should_store_observation,
)

DATABASE_URL = os.environ.get("PROCRUN_TEST_DATABASE_URL")


def test_observation_dedupe_rule() -> None:
    first = date(2026, 1, 1)
    assert should_store_observation(
        previous_state=None,
        previous_observed_at=None,
        state=ComponentState.OPEN,
        observed_at=first,
    )
    assert not should_store_observation(
        previous_state=ComponentState.OPEN,
        previous_observed_at=first,
        state=ComponentState.OPEN,
        observed_at=date(2026, 1, 2),
    )
    assert should_store_observation(
        previous_state=ComponentState.OPEN,
        previous_observed_at=first,
        state=ComponentState.CLOSED,
        observed_at=date(2026, 1, 2),
    )
    assert should_store_observation(
        previous_state=ComponentState.OPEN,
        previous_observed_at=first,
        state=ComponentState.OPEN,
        observed_at=date(2026, 1, 31),
    )


@pytest.mark.skipif(DATABASE_URL is None, reason="PostgreSQL integration DB not configured")
def test_observations_are_deduped_and_append_only() -> None:
    assert DATABASE_URL is not None
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        conn.execute("DROP SCHEMA IF EXISTS procrun CASCADE")
        apply_all_migrations(conn)

        first = append_procurement_observation(
            conn,
            component_id="cmp-history-test",
            operation_code="OP-HISTORY",
            observed_at=date(2026, 1, 1),
            state=ComponentState.OPEN,
            evidence_reference=None,
            evidence_url=None,
            evidence_excerpt=None,
            coverage_note="Coverage: TED.",
        )
        assert first is not None

        duplicate = append_procurement_observation(
            conn,
            component_id="cmp-history-test",
            operation_code="OP-HISTORY",
            observed_at=date(2026, 1, 2),
            state=ComponentState.OPEN,
            evidence_reference=None,
            evidence_url=None,
            evidence_excerpt=None,
            coverage_note="Coverage: TED.",
        )
        assert duplicate is None
        count_row = conn.execute(
            "SELECT count(*) FROM procrun.procurement_observations"
        ).fetchone()
        assert count_row is not None
        assert count_row[0] == 1

        closed = append_procurement_observation(
            conn,
            component_id="cmp-history-test",
            operation_code="OP-HISTORY",
            observed_at=date(2026, 1, 3),
            state=ComponentState.CLOSED,
            evidence_reference="85336-2026",
            evidence_url="https://ted.europa.eu/en/notice/85336-2026/pdf",
            evidence_excerpt="Notice publication number: 85336-2026",
            coverage_note="Coverage: TED.",
        )
        assert closed is not None

        with pytest.raises(psycopg.Error):
            conn.execute(
                "UPDATE procrun.procurement_observations "
                "SET coverage_note = 'changed' WHERE id = %s",
                (first.id,),
            )

        rows = conn.execute(
            "SELECT state, observed_at FROM procrun.procurement_observations "
            "ORDER BY observed_at"
        ).fetchall()
        assert rows == [("OPEN", date(2026, 1, 1)), ("CLOSED", date(2026, 1, 3))]


def test_closed_requires_verifiable_evidence() -> None:
    if DATABASE_URL is None:
        return
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        conn.execute("DROP SCHEMA IF EXISTS procrun CASCADE")
        apply_all_migrations(conn)
        with pytest.raises(ValueError):
            append_procurement_observation(
                conn,
                component_id="cmp-invalid-closed",
                operation_code="OP-INVALID",
                observed_at=date(2026, 1, 1),
                state=ComponentState.CLOSED,
                evidence_reference=None,
                evidence_url=None,
                evidence_excerpt=None,
                coverage_note="Coverage: TED.",
            )
