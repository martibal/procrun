#!/usr/bin/env python3
"""Refresh the admitted OpenCoesione Lombardia cache on the source's bimonthly cadence."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg

from procrun.collectors.opencoesione_live import (
    DEFAULT_CACHE_PATH,
    refresh_open_coesione_cache,
)
from procrun.migrations import apply_all_migrations
from procrun.procurement_history import record_sync_run


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.environ.get("PROCRUN_DATABASE_URL"))
    parser.add_argument(
        "--cache",
        type=Path,
        default=Path(
            os.environ.get("PROCRUN_OPENCOESIONE_CACHE", str(DEFAULT_CACHE_PATH))
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = _args()
    if not args.database_url:
        raise SystemExit("PROCRUN_DATABASE_URL or --database-url is required")
    started_at = datetime.now(timezone.utc)
    try:
        batch = refresh_open_coesione_cache(cache_path=args.cache)
        completed_at = datetime.now(timezone.utc)
        with psycopg.connect(args.database_url) as conn:
            apply_all_migrations(conn)
            with conn.transaction():
                record_sync_run(
                    conn,
                    job_name="opencoesione_bimonthly",
                    started_at=started_at,
                    completed_at=completed_at,
                    status="SUCCESS",
                    row_count=len(batch.operations),
                    detail={
                        "list_updated_on": batch.list_updated_on.isoformat(),
                        "source_sha256": batch.source_sha256,
                    },
                )
        print(
            json.dumps(
                {"status": "SUCCESS", "rows": len(batch.operations)}, sort_keys=True
            )
        )
        return 0
    except Exception as exc:
        completed_at = datetime.now(timezone.utc)
        try:
            with psycopg.connect(args.database_url) as conn:
                apply_all_migrations(conn)
                with conn.transaction():
                    record_sync_run(
                        conn,
                        job_name="opencoesione_bimonthly",
                        started_at=started_at,
                        completed_at=completed_at,
                        status="ERROR",
                        row_count=0,
                        error_message=f"{type(exc).__name__}: {exc}",
                    )
        finally:
            raise


if __name__ == "__main__":
    raise SystemExit(main())
