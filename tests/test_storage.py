from pathlib import Path

import pytest

from procrun.storage import LocalStorageBudgetExceeded, assert_runtime_budget


def test_empty_runtime_directory_is_zero(tmp_path: Path) -> None:
    assert assert_runtime_budget(tmp_path, limit_bytes=1) == 0


def test_runtime_budget_fails_before_more_writes(tmp_path: Path) -> None:
    (tmp_path / "cache.bin").write_bytes(b"1234")
    with pytest.raises(LocalStorageBudgetExceeded):
        assert_runtime_budget(tmp_path, limit_bytes=3)
