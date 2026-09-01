from datetime import datetime, timezone

import pytest

from procrun.ledger import canonical_json, content_sha256


def test_hash_is_independent_of_mapping_order() -> None:
    assert content_sha256({"b": 2, "a": 1}) == content_sha256({"a": 1, "b": 2})


def test_datetime_hash_normalizes_to_utc() -> None:
    first = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)
    assert canonical_json(first) == '"2026-09-01T12:00:00Z"'


def test_naive_datetime_is_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        canonical_json(datetime(2026, 9, 1, 12, 0))
