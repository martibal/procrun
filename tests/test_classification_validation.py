from procrun.classification_validation import (
    ClassificationValidationMetrics,
    ErrorClass,
    ErrorSeverity,
    GateDecision,
    ValidationError,
    evaluate_classification_release_gate,
    repeated_false_open_mechanisms,
)


def passing_metrics(**overrides: object) -> ClassificationValidationMetrics:
    values: dict[str, object] = {
        "real_project_count": 200,
        "qualifying_universe_count": 1000,
        "general_holdout_count": 50,
        "general_benchmark_count": 200,
        "dedicated_open_population_count": 80,
        "dedicated_open_adjudicated_count": 80,
        "dedicated_open_false_open_count": 0,
        "false_closed_count": 0,
        "holdout_closed_denominator": 40,
        "project_state_correct": 49,
        "project_state_total": 50,
        "component_state_correct": 190,
        "component_state_total": 200,
        "component_true_positive": 190,
        "component_false_positive": 2,
        "component_false_negative": 10,
        "accepted_closed_match_correct": 30,
        "accepted_closed_match_total": 30,
        "cutoff_integrity_correct": 20,
        "cutoff_integrity_total": 20,
        "coverage_fail_closed_correct": 20,
        "coverage_fail_closed_total": 20,
        "deterministic_runs": 3,
        "deterministic_outputs_identical": True,
        "adversarial_suite_complete": True,
        "gold_standard_frozen": True,
        "gold_standard_hash": "a" * 64,
        "benchmark_hash": "b" * 64,
        "regression_gate_installed": True,
    }
    values.update(overrides)
    return ClassificationValidationMetrics(**values)  # type: ignore[arg-type]


def test_fully_passing_release_candidate_is_go() -> None:
    result = evaluate_classification_release_gate(passing_metrics())
    assert result.decision is GateDecision.GO
    assert result.failures == ()


def test_any_false_open_is_no_go() -> None:
    result = evaluate_classification_release_gate(
        passing_metrics(dedicated_open_false_open_count=1)
    )
    assert result.decision is GateDecision.NO_GO
    assert any("false OPEN count must be zero" in failure for failure in result.failures)


def test_incomplete_open_population_blocks_release() -> None:
    result = evaluate_classification_release_gate(
        passing_metrics(dedicated_open_adjudicated_count=79)
    )
    assert result.decision is GateDecision.CONDITIONAL
    assert "dedicated OPEN safety population is not completely adjudicated" in result.failures


def test_zero_event_upper_bound_is_reported() -> None:
    metrics = passing_metrics(
        dedicated_open_population_count=100,
        dedicated_open_adjudicated_count=100,
    )
    assert metrics.false_open_upper_95 is not None
    assert 0.029 < metrics.false_open_upper_95 < 0.030


def test_zero_open_population_warns_but_can_pass() -> None:
    result = evaluate_classification_release_gate(
        passing_metrics(
            dedicated_open_population_count=0,
            dedicated_open_adjudicated_count=0,
        )
    )
    assert result.decision is GateDecision.GO
    assert any("no OPEN cases" in warning for warning in result.warnings)


def test_less_than_25_percent_holdout_blocks_release() -> None:
    result = evaluate_classification_release_gate(passing_metrics(general_holdout_count=49))
    assert result.decision is GateDecision.CONDITIONAL
    assert any("holdout below 25%" in failure for failure in result.failures)


def test_entire_small_universe_satisfies_project_count_rule() -> None:
    result = evaluate_classification_release_gate(
        passing_metrics(
            real_project_count=120,
            qualifying_universe_count=120,
            general_benchmark_count=120,
            general_holdout_count=30,
        )
    )
    assert result.decision is GateDecision.GO


def test_critical_error_forces_no_go_even_when_aggregate_metrics_pass() -> None:
    error = ValidationError(
        error_class=ErrorClass.CROSS_PROJECT_CONTAMINATION,
        severity=ErrorSeverity.CRITICAL,
        case_id="case-17",
        rule_id="phase-b-conservative-v2-exact-evidence",
    )
    result = evaluate_classification_release_gate(passing_metrics(errors=(error,)))
    assert result.decision is GateDecision.NO_GO


def test_same_false_open_mechanism_in_two_rounds_is_retirement_candidate() -> None:
    first = ValidationError(
        error_class=ErrorClass.FALSE_OPEN,
        severity=ErrorSeverity.CRITICAL,
        case_id="round1-case",
        rule_id="shared-cpv-open-boundary-v1",
    )
    second = ValidationError(
        error_class=ErrorClass.FALSE_OPEN,
        severity=ErrorSeverity.CRITICAL,
        case_id="round2-case",
        rule_id="shared-cpv-open-boundary-v1",
    )
    other = ValidationError(
        error_class=ErrorClass.FALSE_OPEN,
        severity=ErrorSeverity.CRITICAL,
        case_id="one-off-case",
        rule_id="one-off-v1",
    )

    retired = repeated_false_open_mechanisms(((first, other), (second,)))

    assert retired == frozenset({"shared-cpv-open-boundary-v1"})
