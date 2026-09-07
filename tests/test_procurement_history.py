import os
from datetime import date
from uuid import uuid4

import psycopg
import pytest

from procrun.domain import ComponentState
from procrun.migrations import apply_all_migrations
from procrun.procurement_history import (
    ProcurementObservation,
    append_procurement_observation,
    diff_procurement_observations,
    should_store_observation,
)

DATABASE_URL = os.environ.get("PROCRUN_TEST_DATABASE_URL")


def _observation(
    *,
    state: ComponentState,
    observed_at: date,
    evidence_reference: str | None = None,
    evidence_url: str | None = None,
    evidence_excerpt: str | None = None,
    coverage_note: str = "Coverage: TED.",
    correction_of_id=None,
    correction_reason: str | None = None,
) -> ProcurementObservation:
    return ProcurementObservation(
        id=uuid4(),
        component_id="cmp-history-test",
        operation_code="OP-HISTORY",
        observed_at=observed_at,
        state=state,
        evidence_reference=evidence_reference,
        evidence_url=evidence_url,
        evidence_excerpt=evidence_excerpt,
        coverage_note=coverage_note,
        correction_of_id=correction_of_id,
        correction_reason=correction_reason,
    )


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
    assert should_store_observation(
        previous_state=ComponentState.CLOSED,
        previous_observed_at=first,
        state=ComponentState.CLOSED,
        observed_at=date(2026, 1, 2),
        material_change=True,
    )


def test_diff_open_to_closed_is_state_change() -> None:
    previous = _observation(state=ComponentState.OPEN, observed_at=date(2026, 1, 1))
    current = _observation(
        state=ComponentState.CLOSED,
        observed_at=date(2026, 1, 2),
        evidence_reference="85336-2026",
        evidence_url="https://ted.europa.eu/en/notice/85336-2026/pdf",
        evidence_excerpt="Notice publication number: 85336-2026",
    )

    diff = diff_procurement_observations(previous, current)

    assert diff.kind == "STATE_CHANGED"
    assert diff.summary == "State changed from OPEN to CLOSED."
    assert "state" in diff.changed_fields
    assert "evidence_excerpt" in diff.changed_fields


def test_diff_same_state_new_evidence_is_evidence_change() -> None:
    previous = _observation(
        state=ComponentState.CLOSED,
        observed_at=date(2026, 1, 1),
        evidence_reference="1-2026",
        evidence_url="https://ted.europa.eu/en/notice/1-2026/pdf",
        evidence_excerpt="first accepted excerpt",
    )
    current = _observation(
        state=ComponentState.CLOSED,
        observed_at=date(2026, 1, 2),
        evidence_reference="2-2026",
        evidence_url="https://ted.europa.eu/en/notice/2-2026/pdf",
        evidence_excerpt="replacement accepted excerpt",
    )

    diff = diff_procurement_observations(previous, current)

    assert diff.kind == "EVIDENCE_CHANGED"
    assert diff.summary == "Procurement evidence changed while state remained CLOSED."


def test_diff_unchanged_heartbeat_is_not_material_change() -> None:
    previous = _observation(state=ComponentState.OPEN, observed_at=date(2026, 1, 1))
    current = _observation(state=ComponentState.OPEN, observed_at=date(2026, 1, 31))

    diff = diff_procurement_observations(previous, current)

    assert diff.kind == "HEARTBEAT"
    assert diff.changed_fields == ()
    assert diff.summary == "No material change; scheduled verification heartbeat."


def test_diff_correction_is_explicit_and_does_not_expose_reason() -> None:
    previous = _observation(
        state=ComponentState.CLOSED,
        observed_at=date(2026, 1, 2),
        evidence_reference="85336-2026",
        evidence_url="https://ted.europa.eu/en/notice/85336-2026/pdf",
        evidence_excerpt="Notice publication number: 85336-2026",
    )
    current = _observation(
        state=ComponentState.OPEN,
        observed_at=date(2026, 1, 3),
        correction_of_id=previous.id,
        correction_reason="internal free-form correction explanation",
    )

    diff = diff_procurement_observations(previous, current)

    assert diff.kind == "CORRECTION"
    assert diff.summary == (
        "Correction appended to the immutable history. State changed from CLOSED to OPEN."
    )
    assert "internal free-form" not in diff.summary


@pytest.mark.skipif(DATABASE_URL is None, reason="PostgreSQL integration DB not configured")
def test_observations_are_deduped_append_only_and_store_material_evidence_changes() -> None:
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

        evidence_change = append_procurement_observation(
            conn,
            component_id="cmp-history-test",
            operation_code="OP-HISTORY",
            observed_at=date(2026, 1, 4),
            state=ComponentState.CLOSED,
            evidence_reference="85336-2026",
            evidence_url="https://ted.europa.eu/en/notice/85336-2026/pdf",
            evidence_excerpt="Notice publication number: 85336-2026; accepted excerpt revised.",
            coverage_note="Coverage: TED.",
        )
        assert evidence_change is not None

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
        assert rows == [
            ("OPEN", date(2026, 1, 1)),
            ("CLOSED", date(2026, 1, 3)),
            ("CLOSED", date(2026, 1, 4)),
        ]


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
