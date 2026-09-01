"""Bounded local-runtime storage helpers.

The developer machine is a client, not the permanent data warehouse. Runtime caches are
explicitly disposable and must remain below the configured project budget.
"""

from pathlib import Path

DEFAULT_LOCAL_RUNTIME_LIMIT_BYTES = 20 * 1024**3


class LocalStorageBudgetExceeded(RuntimeError):
    """Raised before a runtime job writes into an already-over-budget local data area."""


def directory_size_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    total = 0
    for item in path.rglob("*"):
        if item.is_file() and not item.is_symlink():
            total += item.stat().st_size
    return total


def assert_runtime_budget(
    path: Path, *, limit_bytes: int = DEFAULT_LOCAL_RUNTIME_LIMIT_BYTES
) -> int:
    """Return current size or fail before further runtime writes if the limit is exceeded."""

    current = directory_size_bytes(path)
    if current > limit_bytes:
        raise LocalStorageBudgetExceeded(
            f"runtime data is {current} bytes; configured limit is {limit_bytes} bytes"
        )
    return current
