#!/usr/bin/env python3
"""Fail-closed compliance gate for infrastructure/network scripts.

This helper intentionally depends only on the standard-library-only compliance module so
it can run before the ProcRun virtual environment is installed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from procrun.compliance import (  # noqa: E402
    require_direct_dependency_reviews,
    require_external_service,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service")
    parser.add_argument("--dependencies", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    if not args.service and not args.dependencies:
        raise SystemExit("specify --service SERVICE_ID and/or --dependencies")

    if args.dependencies:
        require_direct_dependency_reviews()
    if args.service:
        require_external_service(args.service)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
