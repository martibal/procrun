import os
from datetime import date, datetime, timezone
from uuid import uuid4

import psycopg
import pytest

from procrun.category_baselines import (
    ClosedDurationSample,
    build_category_baselines,
    load_category_baselines,
    percentile,
)
from procrun.domain import ComponentState
from procrun.migrations import apply_all_migrations
from procrun.procurement_history import append_procurement_observation

DATABASE_URL = os.environ.get("PROCRUN_TEST_DATABASE_URL")


def test_percentile_and_category_baseline_are_deterministic() -> None:
    assert percentile([40, 10, 30, 20], 0.25) == 17.5
    assert percentile([40, 10, 30, 20], 0.50) == 25.0
    assert percentile([40, 10, 30, 20], 0.75) == 32.5

    samples = tuple(
        ClosedDurationSample(
            component_id=f"cmp-{days}",
            category="energy_efficiency:lighting",
            opened_at=date(2026, 1, 1),
            closed_at=date(2026, 1, 1).fromordinal(date(2026, 1, 1).toordinal() + days),
            duration_days=days,
        )
        for days in (40, 10, 30, 20)
    )
    baseline = build_category_baselines(samples)[0]
    assert baseline.n == 4
    assert baseline.p25_days == 17.5
    assert baseline.median_days == 25.0
    assert baseline.p75_days == 32.5


def _insert_component(conn: psycopg.Connection[tuple[object, ...]], component_id: str) -> None:
    conn.execute(
        """
        INSERT INTO procrun.component_versions (
            version_id, component_id, operation_code, as_of, category, description,
            scope_evidence, extractor_version, content_sha256
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            uuid4(),
            component_id,
            f"OP-{component_id}",
            datetime(2026, 1, 1, tzinfo=timezone.utc),
            "energy_efficiency:lighting",
            "Lighting",
            "LED lighting",
            "component-taxonomy-v1",
            "a" * 64,
        ),
    )


@pytest.mark.skipif(DATABASE_URL is None, reason="PostgreSQL integration DB not configured")
def test_database_baseline_uses_effective_history_and_exact_category() -> None:
    assert DATABASE_URL is not None
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        conn.execute("DROP SCHEMA IF EXISTS procrun CASCADE")
        apply_all_migrations(conn)

        for index, days in enumerate((10, 20, 30, 40), start=1):
            component_id = f"cmp-baseline-{index}"
            _insert_component(conn, component_id)
            opened = append_procurement_observation(
                conn,
                component_id=component_id,
                operation_code=f"OP-{component_id}",
                observed_at=date(2026, 1, 1),
                state=ComponentState.OPEN,
                evidence_reference=None,
                evidence_url=None,
                evidence_excerpt=None,
                coverage_note="Coverage: TED.",
            )
            assert opened is not None
            closed = append_procurement_observation(
                conn,
                component_id=component_id,
                operation_code=f"OP-{component_id}",
                observed_at=date(2026, 1, 1).fromordinal(date(2026, 1, 1).toordinal() + days),
                state=ComponentState.CLOSED,
                evidence_reference=f"NOTICE-{index}",
                evidence_url=f"https://ted.europa.eu/en/notice/{index}",
                evidence_excerpt=f"accepted evidence {index}",
                coverage_note="Coverage: TED.",
            )
            assert closed is not None

        baseline = load_category_baselines(conn)[0]
        assert baseline.category == "energy_efficiency:lighting"
        assert baseline.n == 4
        assert baseline.p25_days == 17.5
        assert baseline.median_days == 25.0
        assert baseline.p75_days == 32.5
