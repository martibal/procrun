import json
from pathlib import Path

import pytest

from procrun.a21a_lineage import (
    A21A_PREREGISTRATION_ACTIVE,
    CLEAN_V2_CASE_COUNT,
    CLEAN_V2_REVIEW_COMPLETE,
    CLEAN_V2_SAMPLE_SHA256,
    CLEAN_V2_SOURCE_POOL_SHA256,
    INVALIDATED_V1_SAMPLE_SHA256,
    INVALIDATED_V1_WEAK_SAMPLE_SHA256,
    preregistration_ready,
    require_clean_development_hash,
)

MANIFEST = Path("tests/fixtures/a21a_clean_development_lineage_v2.json")


def test_clean_v2_lineage_is_pinned_and_pending_independent_review() -> None:
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert document["source_pool_content_sha256"] == CLEAN_V2_SOURCE_POOL_SHA256
    assert document["development_sample_canonical_sha256"] == CLEAN_V2_SAMPLE_SHA256
    assert document["case_count"] == CLEAN_V2_CASE_COUNT == 60
    assert document["pii_review_status"] == "ZERO_PII_CONFIRMED"
    assert document["download_then_filter_used"] is False
    assert document["prior_review_labels_reused"] is False
    assert document["independent_review_complete"] is False
    assert document["threshold_preregistration_active"] is False


def test_known_contaminated_development_hashes_are_rejected() -> None:
    for value in (INVALIDATED_V1_SAMPLE_SHA256, INVALIDATED_V1_WEAK_SAMPLE_SHA256):
        with pytest.raises(ValueError, match="invalidated download-then-filter lineage"):
            require_clean_development_hash(value)


def test_only_clean_v2_baseline_is_accepted() -> None:
    require_clean_development_hash(CLEAN_V2_SAMPLE_SHA256)
    with pytest.raises(ValueError, match="not the frozen clean-v2 baseline"):
        require_clean_development_hash("0" * 64)


def test_preregistration_remains_locked_until_clean_review_and_refreeze() -> None:
    assert CLEAN_V2_REVIEW_COMPLETE is False
    assert A21A_PREREGISTRATION_ACTIVE is False
    assert preregistration_ready() is False
