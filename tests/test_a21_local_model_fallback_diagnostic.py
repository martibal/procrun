from __future__ import annotations

import copy

import pytest

from scripts.run_a21_local_model_fallback_diagnostic import (
    COMPONENT_RULE_VERSION,
    EXPECTED_BENCHMARK_SCHEMA,
    EXPECTED_CASE_COUNT,
    EXPECTED_DETERMINISTIC_SCHEMA,
    _validate_inputs,
)


def _inputs() -> tuple[dict[str, object], dict[str, object]]:
    cases = [
        {
            "case_number": index,
            "operation_code": f"OP-{index:03d}",
        }
        for index in range(1, EXPECTED_CASE_COUNT + 1)
    ]
    benchmark: dict[str, object] = {
        "schema_version": EXPECTED_BENCHMARK_SCHEMA,
        "sealed": False,
        "engine_output_used": False,
        "cases": cases,
    }
    deterministic: dict[str, object] = {
        "schema_version": EXPECTED_DETERMINISTIC_SCHEMA,
        "benchmark_input_sha256": "a" * 64,
        "component_rule_version": COMPONENT_RULE_VERSION,
        "local_model_used": False,
        "sealed_holdout_used": False,
        "case_count": EXPECTED_CASE_COUNT,
        "cases": [
            {
                "case_number": index,
                "operation_code": f"OP-{index:03d}",
                "predicted_categories": [],
                "model_fallback_required": False,
            }
            for index in range(1, EXPECTED_CASE_COUNT + 1)
        ],
    }
    return benchmark, deterministic


def test_a21_fallback_diagnostic_accepts_only_bound_unsealed_inputs() -> None:
    benchmark, deterministic = _inputs()
    cases, indexed = _validate_inputs(benchmark, "a" * 64, deterministic)
    assert len(cases) == EXPECTED_CASE_COUNT
    assert len(indexed) == EXPECTED_CASE_COUNT


def test_a21_fallback_diagnostic_refuses_sealed_holdout() -> None:
    benchmark, deterministic = _inputs()
    sealed = copy.deepcopy(benchmark)
    sealed["sealed"] = True
    with pytest.raises(ValueError, match="sealed holdout"):
        _validate_inputs(sealed, "a" * 64, deterministic)


def test_a21_fallback_diagnostic_refuses_unbound_deterministic_report() -> None:
    benchmark, deterministic = _inputs()
    with pytest.raises(ValueError, match="not bound"):
        _validate_inputs(benchmark, "b" * 64, deterministic)
