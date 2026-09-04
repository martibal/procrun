#!/usr/bin/env python3
"""Run the complete non-web ProcRun delivery pipeline."""

from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path

from procrun.production_delivery import run_live_delivery


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--database-url",
        default=os.environ.get("PROCRUN_DATABASE_URL"),
        help="PostgreSQL DSN; defaults to PROCRUN_DATABASE_URL.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/var/lib/procrun/published/runway.jsonl"),
    )
    parser.add_argument("--cutoff", type=date.fromisoformat)
    return parser.parse_args()


def main() -> int:
    args = _args()
    if not args.database_url:
        raise SystemExit("PROCRUN_DATABASE_URL or --database-url is required")
    summary = run_live_delivery(
        database_url=args.database_url,
        output_path=args.output,
        cutoff_date=args.cutoff,
    )
    print(json.dumps(summary.__dict__, default=str, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
