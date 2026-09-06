#!/usr/bin/env python3
"""Local acceptance check for append-only procurement history."""

from __future__ import annotations

import argparse
from datetime import date
from urllib.parse import urlparse

import psycopg

from procrun.domain import ComponentState
from procrun.migrations import apply_all_migrations
from procrun.procurement_history import append_procurement_observation

_LOCAL_DSN = "postgresql://procrun:procrun-local-only@127.0.0.1:5432/procrun"


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=_LOCAL_DSN)
    return parser.parse_args()


def _require_known_local_database(database_url: str) -> None:
    parsed = urlparse(database_url)
    safe = (
        parsed.hostname in {"127.0.0.1", "localhost"}
        and parsed.port == 5432
        and parsed.username == "procrun"
        and parsed.password == "procrun-local-only"
        and parsed.path == "/procrun"
    )
    if not safe:
        raise SystemExit(
            "Refusing destructive acceptance check: use the exact compose.yml local-test DSN"
        )


def main() -> int:
    args = _args()
    _require_known_local_database(args.database_url)

    with psycopg.connect(args.database_url, autocommit=True) as conn:
        conn.execute("DROP SCHEMA IF EXISTS procrun CASCADE")
        apply_all_migrations(conn)
        first = append_procurement_observation(
            conn,
            component_id="cmp-local-history-check",
            operation_code="LOCAL-HISTORY",
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
            component_id="cmp-local-history-check",
            operation_code="LOCAL-HISTORY",
            observed_at=date(2026, 1, 2),
            state=ComponentState.OPEN,
            evidence_reference=None,
            evidence_url=None,
            evidence_excerpt=None,
            coverage_note="Coverage: TED.",
        )
        if duplicate is not None:
            raise SystemExit("DEDUPE CHECK: FAILED")
        print("DEDUPE CHECK: PASS")

        try:
            conn.execute(
                "UPDATE procrun.procurement_observations "
                "SET coverage_note = 'changed' WHERE id = %s",
                (first.id,),
            )
        except psycopg.Error:
            print("APPEND-ONLY UPDATE CHECK: PASS")
        else:
            raise SystemExit("APPEND-ONLY UPDATE CHECK: FAILED")

        try:
            conn.execute(
                "DELETE FROM procrun.procurement_observations WHERE id = %s",
                (first.id,),
            )
        except psycopg.Error:
            print("APPEND-ONLY DELETE CHECK: PASS")
        else:
            raise SystemExit("APPEND-ONLY DELETE CHECK: FAILED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
