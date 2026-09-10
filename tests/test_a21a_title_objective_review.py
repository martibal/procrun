import json
from pathlib import Path

FIXTURE = Path("tests/fixtures/a21a_title_objective_utility_development_review_v1.json")


def test_title_objective_review_is_source_only_and_holdout_safe() -> None:
    review = json.loads(FIXTURE.read_text(encoding="utf-8"))

    assert review["case_count"] == 14
    assert review["engine_output_used_for_review"] is False
    assert review["sealed_holdout_touched"] is False
    assert review["new_source_fields_received"] is False
    assert review["context_promoted_to_evidence"] is False
    assert review["blind_sample_canonical_sha256"] == (
        "d014391f1e6f0f4e10bc0041352a4ea15fb12e4fe03cc974d31709a2c0dee02b"
    )


def test_specific_objective_recovers_no_weak_title_to_clear() -> None:
    review = json.loads(FIXTURE.read_text(encoding="utf-8"))
    labels = [case["label"] for case in review["cases"]]

    assert len(labels) == 14
    assert labels.count("CLEAR") == 0
    assert labels.count("PARTIAL") == 6
    assert labels.count("NOT_USEFUL") == 8
    assert set(labels) <= {"CLEAR", "PARTIAL", "NOT_USEFUL"}


def test_review_contains_exact_frozen_weak_case_ids() -> None:
    review = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert {case["case_id"] for case in review["cases"]} == {
        "A21A-DEV-0005",
        "A21A-DEV-0013",
        "A21A-DEV-0025",
        "A21A-DEV-0027",
        "A21A-DEV-0028",
        "A21A-DEV-0032",
        "A21A-DEV-0034",
        "A21A-DEV-0035",
        "A21A-DEV-0038",
        "A21A-DEV-0041",
        "A21A-DEV-0052",
        "A21A-DEV-0054",
        "A21A-DEV-0055",
        "A21A-DEV-0058",
    }
