from pathlib import Path

import pytest

from scripts import build_a21a_live_sintesi_development_sample as legacy


def test_legacy_live_sample_builder_fails_closed_before_network_access() -> None:
    with pytest.raises(RuntimeError, match="disabled"):
        legacy.build_source_pool()


def test_legacy_live_sample_module_has_no_live_collector_import() -> None:
    text = Path("scripts/build_a21a_live_sintesi_development_sample.py").read_text(
        encoding="utf-8"
    )

    assert "collect_open_coesione_live" not in text
    assert "httpx" not in text
    assert "requests" not in text
    assert "download-then-filter" in text
