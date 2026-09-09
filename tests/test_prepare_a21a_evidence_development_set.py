from __future__ import annotations

import copy

import pytest

from scripts.prepare_a21a_evidence_development_set import build


def _pool() -> dict:
    return {
        "schema_version": "a21a-sanitized-source-pool-v1",
        "pii_review_status": "ZERO_PII_CONFIRMED",
        "engine_output_present": False,
        "cases": [
            {
                "operation_code": f"OP-{i}",
                "project_title": f"Project {i}",
                "project_scope_text": f"Testo del progetto {i} con procedura di gara.",
                "region": "Lombardia",
                "municipality": None,
                "nuts_code": None,
                "source_url": f"https://example.invalid/{i}",
                "language": "it",
            }
            for i in range(1, 7)
        ],
    }


def test_builder_is_deterministic_and_blind() -> None:
    first = build(_pool(), sample_size=4)
    second = build(_pool(), sample_size=4)
    assert first == second
    assert first["case_count"] == 4
    assert first["engine_output_used_for_gold"] is False
    assert all(
        case["adjudication"] == {
            "relevant_excerpts": [],
            "adjudication_status": "PENDING_BLIND_REVIEW",
        }
        for case in first["cases"]
    )


def test_builder_rejects_unconfirmed_pii_status() -> None:
    pool = _pool()
    pool["pii_review_status"] = "UNKNOWN"
    with pytest.raises(ValueError, match="ZERO_PII_CONFIRMED"):
        build(pool, sample_size=2)


def test_builder_rejects_engine_output() -> None:
    pool = _pool()
    pool["engine_output_present"] = True
    with pytest.raises(ValueError, match="must not contain extractor"):
        build(pool, sample_size=2)


def test_builder_rejects_duplicate_operation_code() -> None:
    pool = _pool()
    duplicate = copy.deepcopy(pool["cases"][0])
    pool["cases"].append(duplicate)
    with pytest.raises(ValueError, match="unique"):
        build(pool, sample_size=2)


def test_builder_refuses_invalid_sample_size() -> None:
    with pytest.raises(ValueError, match="sample size"):
        build(_pool(), sample_size=99)
