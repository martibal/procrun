import os
from datetime import date

import psycopg
import pytest

from procrun.benchmark_reports import (
    apply_benchmark_migration,
    persist_report,
    verify_persisted_report,
)
from procrun.funded_project_benchmark import (
    BenchmarkProject,
    UserProjectInput,
    compute_benchmark,
)

DATABASE_URL = os.environ.get("PROCRUN_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    DATABASE_URL is None,
    reason="PostgreSQL integration DB not configured",
)


def connect() -> psycopg.Connection[tuple[object, ...]]:
    assert DATABASE_URL is not None
    return psycopg.connect(DATABASE_URL, autocommit=True)


def _calculation():
    projects = tuple(
        BenchmarkProject(
            operation_code=f"OP-{i:03d}",
            project_title=f"Project {i}",
            source_url=f"https://example.invalid/{i}",
            bando_code="BANDO-1",
            action_code="1.2.3",
            intervention_code="013",
            approved_funding_eur=100_000 + i * 10_000,
            project_start=date(2025, 1, 15),
            project_end=date(2026, 1, 15),
        )
        for i in range(30)
    )
    return compute_benchmark(
        snapshot_id="snap-v1",
        cohort_id="SAME_BANDO:BANDO-1",
        projects=projects,
        user_input=UserProjectInput(
            proposed_funding_eur=250_000,
            proposed_duration_months=12,
        ),
    )


def _reset() -> None:
    with connect() as conn:
        conn.execute("DROP SCHEMA IF EXISTS procrun CASCADE")
        apply_benchmark_migration(conn)
        conn.execute(
            """
            INSERT INTO procrun.benchmark_source_snapshots (
                snapshot_id, data_through_date, raw_record_count, canonical_hash
            ) VALUES (%s, %s, %s, %s)
            """,
            ("snap-v1", date(2026, 9, 12), 4305, "a" * 64),
        )


def test_07_report_ids_are_independent_from_calculation_hash() -> None:
    _reset()
    calculation = _calculation()
    with connect() as conn:
        first_id, first_hash = persist_report(conn, calculation)
        second_id, second_hash = persist_report(conn, calculation)
        assert first_id != second_id
        assert first_hash == second_hash
        rows = conn.execute(
            "SELECT report_id, canonical_sha256 FROM procrun.benchmark_reports ORDER BY created_at"
        ).fetchall()
        assert len(rows) == 2
        assert {row[1] for row in rows} == {first_hash}


def test_08_canonical_bytes_survive_database_roundtrip() -> None:
    _reset()
    calculation = _calculation()
    with connect() as conn:
        report_id, expected_hash = persist_report(conn, calculation)
        row = conn.execute(
            """
            SELECT canonical_jcs_bytes, canonical_sha256, canonical_payload
            FROM procrun.benchmark_reports
            WHERE report_id = %s
            """,
            (report_id,),
        ).fetchone()
        assert row is not None
        canonical_bytes, digest, payload = row
        assert isinstance(canonical_bytes, bytes)
        assert digest == expected_hash
        assert isinstance(payload, dict)
        assert verify_persisted_report(
            canonical_jcs_bytes=canonical_bytes,
            canonical_sha256=digest,
            canonical_payload_json=payload,
        )
