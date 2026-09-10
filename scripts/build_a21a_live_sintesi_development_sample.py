"""Fail-closed legacy A21a live-sample entrypoint.

This entrypoint previously downloaded the complete OpenCoesione Lombardia ZIP and
then projected source fields locally. That path is incompatible with the current
A21a sanitized-source ingress contract, which forbids download-then-filter and
requires source-only material to be bounded before ProcRun receives it.
"""

from __future__ import annotations


BLOCK_REASON = (
    "A21a live SINTESI development sampling is disabled: the legacy path receives "
    "the full OpenCoesione ZIP before projection. Supply an approved remote "
    "a21a-sanitized-source-pool-v1 package produced without download-then-filter."
)


def build_source_pool() -> dict[str, object]:
    """Refuse legacy source-pool construction before any network access."""

    raise RuntimeError(BLOCK_REASON)


def main() -> int:
    raise RuntimeError(BLOCK_REASON)


if __name__ == "__main__":
    raise SystemExit(main())
