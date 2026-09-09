"""Machine-enforced release gate for empirical classification-engine validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ValidationInvariantError(ValueError):
    """Raised when a validation report cannot support a defensible release decision."""


class GateDecision(StrEnum):
    GO = "GO"
    NO_GO = "NO-GO"
    CONDITIONAL = "CONDITIONAL — REMEDIATION REQUIRED"


class ErrorSeverity(StrEnum):
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"


class ErrorClass(StrEnum):
    MISSED_COMPONENT = "MISSED_COMPONENT"
    INVENTED_COMPONENT = "INVENTED_COMPONENT"
    WRONG_PROJECT_MATCH = "WRONG_PROJECT_MATCH"
    WRONG_COMPONENT_MATCH = "WRONG_COMPONENT_MATCH"
    FALSE_OPEN = "FALSE_OPEN"
    FALSE_CLOSED = "FALSE_CLOSED"
    WRONG_PARTIAL = "WRONG_PARTIAL"
    WRONG_UNRESOLVED = "WRONG_UNRESOLVED"
    CUTOFF_LEAK = "CUTOFF_LEAK"
    INCOMPLETE_COVERAGE_OPEN = "INCOMPLETE_COVERAGE_OPEN"
    INVALID_EVIDENCE_SPAN = "INVALID_EVIDENCE_SPAN"
    POST_CUTOFF_CLOSE = "POST_CUTOFF_CLOSE"
    CROSS_PROJECT_CONTAMINATION = "CROSS_PROJECT_CONTAMINATION"
    NONDETERMINISM = "NONDETERMINISM"
    GOLD_STANDARD_ERROR = "GOLD_STANDARD_ERROR"


@dataclass(frozen=True)
class ValidationError:
    error_class: ErrorClass
    severity: ErrorSeverity
    case_id: str
    rule_id: str | None = None

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValidationInvariantError("validation error case_id must not be blank")
        if self.rule_id is not None and not self.rule_id.strip():
            raise ValidationInvariantError("validation error rule_id must not be blank")


@dataclass(frozen=True)
class ClassificationValidationMetrics:
    real_project_count: int
    qualifying_universe_count: int
    general_holdout_count: int
    general_benchmark_count: int
    dedicated_open_population_count: int
    dedicated_open_adjudicated_count: int
    dedicated_open_false_open_count: int
    false_closed_count: int
    holdout_closed_denominator: int
    project_state_correct: int
    project_state_total: int
    component_state_correct: int
    component_state_total: int
    component_true_positive: int
    component_false_positive: int
    component_false_negative: int
    accepted_closed_match_correct: int
    accepted_closed_match_total: int
    cutoff_integrity_correct: int
    cutoff_integrity_total: int
    coverage_fail_closed_correct: int
    coverage_fail_closed_total: int
    deterministic_runs: int
    deterministic_outputs_identical: bool
    adversarial_suite_complete: bool
    gold_standard_frozen: bool
    gold_standard_hash: str
    benchmark_hash: str
    regression_gate_installed: bool
    retired_open_mechanisms: tuple[str, ...] = ()
    errors: tuple[ValidationError, ...] = ()

    def __post_init__(self) -> None:
        integer_fields = (
            self.real_project_count,
            self.qualifying_universe_count,
            self.general_holdout_count,
            self.general_benchmark_count,
            self.dedicated_open_population_count,
            self.dedicated_open_adjudicated_count,
            self.dedicated_open_false_open_count,
            self.false_closed_count,
            self.holdout_closed_denominator,
            self.project_state_correct,
            self.project_state_total,
            self.component_state_correct,
            self.component_state_total,
            self.component_true_positive,
            self.component_false_positive,
            self.component_false_negative,
            self.accepted_closed_match_correct,
            self.accepted_closed_match_total,
            self.cutoff_integrity_correct,
            self.cutoff_integrity_total,
            self.coverage_fail_closed_correct,
            self.coverage_fail_closed_total,
            self.deterministic_runs,
        )
        if any(value < 0 for value in integer_fields):
            raise ValidationInvariantError("validation counts must be non-negative")
        if self.qualifying_universe_count < self.real_project_count:
            raise ValidationInvariantError("real_project_count cannot exceed qualifying universe")
        if self.general_holdout_count > self.general_benchmark_count:
            raise ValidationInvariantError("holdout cannot exceed general benchmark")
        if self.dedicated_open_adjudicated_count > self.dedicated_open_population_count:
            raise ValidationInvariantError("adjudicated OPEN count cannot exceed OPEN population")
        if self.dedicated_open_false_open_count > self.dedicated_open_adjudicated_count:
            raise ValidationInvariantError("false OPEN count cannot exceed adjudicated OPEN count")
        if self.false_closed_count > self.holdout_closed_denominator:
            raise ValidationInvariantError("false CLOSED count cannot exceed its denominator")
        for correct, total, label in (
            (self.project_state_correct, self.project_state_total, "project state"),
            (self.component_state_correct, self.component_state_total, "component state"),
            (self.accepted_closed_match_correct, self.accepted_closed_match_total, "accepted CLOSED match"),
            (self.cutoff_integrity_correct, self.cutoff_integrity_total, "cutoff integrity"),
            (self.coverage_fail_closed_correct, self.coverage_fail_closed_total, "coverage fail-closed"),
        ):
            if correct > total:
                raise ValidationInvariantError(f"{label} correct count cannot exceed total")
        if self.gold_standard_frozen and not self.gold_standard_hash.strip():
            raise ValidationInvariantError("frozen gold standard requires a non-empty hash")
        if self.gold_standard_frozen and not self.benchmark_hash.strip():
            raise ValidationInvariantError("frozen benchmark requires a non-empty hash")
        if any(not mechanism.strip() for mechanism in self.retired_open_mechanisms):
            raise ValidationInvariantError("retired OPEN mechanism identifiers must not be blank")

    @property
    def required_real_project_count(self) -> int:
        return min(200, self.qualifying_universe_count)

    @property
    def open_population_complete(self) -> bool:
        return self.dedicated_open_adjudicated_count == self.dedicated_open_population_count

    @property
    def false_open_rate(self) -> float:
        if self.dedicated_open_adjudicated_count == 0:
            return 0.0
        return self.dedicated_open_false_open_count / self.dedicated_open_adjudicated_count

    @property
    def false_open_upper_95(self) -> float | None:
        """One-sided exact upper bound when zero false OPEN events were observed.

        For zero observed events in n Bernoulli trials, solve (1-p)^n = 0.05.
        A non-zero false-OPEN count has no special zero-event bound and returns None.
        """

        n = self.dedicated_open_adjudicated_count
        if n == 0 or self.dedicated_open_false_open_count != 0:
            return None
        return 1.0 - 0.05 ** (1.0 / n)

    @staticmethod
    def _rate(numerator: int, denominator: int) -> float:
        if denominator == 0:
            return 0.0
        return numerator / denominator

    @property
    def false_closed_rate(self) -> float:
        return self._rate(self.false_closed_count, self.holdout_closed_denominator)

    @property
    def project_state_accuracy(self) -> float:
        return self._rate(self.project_state_correct, self.project_state_total)

    @property
    def component_state_accuracy(self) -> float:
        return self._rate(self.component_state_correct, self.component_state_total)

    @property
    def component_precision(self) -> float:
        return self._rate(
            self.component_true_positive,
            self.component_true_positive + self.component_false_positive,
        )

    @property
    def component_recall(self) -> float:
        return self._rate(
            self.component_true_positive,
            self.component_true_positive + self.component_false_negative,
        )

    @property
    def accepted_closed_match_precision(self) -> float:
        return self._rate(self.accepted_closed_match_correct, self.accepted_closed_match_total)

    @property
    def cutoff_integrity(self) -> float:
        return self._rate(self.cutoff_integrity_correct, self.cutoff_integrity_total)

    @property
    def coverage_fail_closed_integrity(self) -> float:
        return self._rate(self.coverage_fail_closed_correct, self.coverage_fail_closed_total)


@dataclass(frozen=True)
class GateEvaluation:
    decision: GateDecision
    failures: tuple[str, ...]
    warnings: tuple[str, ...]


def evaluate_classification_release_gate(metrics: ClassificationValidationMetrics) -> GateEvaluation:
    """Apply the frozen classification-engine product-validation thresholds."""

    failures: list[str] = []
    warnings: list[str] = []

    critical_errors = tuple(
        error for error in metrics.errors if error.severity is ErrorSeverity.CRITICAL
    )
    if critical_errors:
        failures.append(f"critical validation errors present: {len(critical_errors)}")

    if metrics.real_project_count < metrics.required_real_project_count:
        failures.append(
            "insufficient real-project benchmark: "
            f"{metrics.real_project_count} < {metrics.required_real_project_count}"
        )

    required_holdout = (metrics.general_benchmark_count + 3) // 4
    if metrics.general_holdout_count < required_holdout:
        failures.append(
            f"general holdout below 25%: {metrics.general_holdout_count} < {required_holdout}"
        )

    if not metrics.gold_standard_frozen:
        failures.append("gold standard is not frozen")
    if not metrics.open_population_complete:
        failures.append("dedicated OPEN safety population is not completely adjudicated")
    if metrics.dedicated_open_false_open_count != 0:
        failures.append(
            f"false OPEN count must be zero, got {metrics.dedicated_open_false_open_count}"
        )
    if metrics.false_closed_rate > 0.01:
        failures.append(f"false CLOSED rate exceeds 1%: {metrics.false_closed_rate:.4%}")
    if metrics.project_state_total == 0 or metrics.project_state_accuracy < 0.95:
        failures.append(
            f"project-state accuracy below 95%: {metrics.project_state_accuracy:.4%}"
        )
    if metrics.component_state_total == 0 or metrics.component_state_accuracy < 0.95:
        failures.append(
            f"component-state accuracy below 95%: {metrics.component_state_accuracy:.4%}"
        )
    if metrics.component_precision < 0.98:
        failures.append(f"component precision below 98%: {metrics.component_precision:.4%}")
    if metrics.component_recall < 0.95:
        failures.append(f"component recall below 95%: {metrics.component_recall:.4%}")
    if (
        metrics.accepted_closed_match_total == 0
        or metrics.accepted_closed_match_precision != 1.0
    ):
        failures.append(
            "accepted CLOSED-match precision must be 100% with at least one evaluated match"
        )
    if metrics.cutoff_integrity_total == 0 or metrics.cutoff_integrity != 1.0:
        failures.append("cutoff integrity must be 100% with evaluated cutoff cases")
    if (
        metrics.coverage_fail_closed_total == 0
        or metrics.coverage_fail_closed_integrity != 1.0
    ):
        failures.append("coverage fail-closed integrity must be 100% with evaluated cases")
    if metrics.deterministic_runs < 3 or not metrics.deterministic_outputs_identical:
        failures.append("determinism requires at least three identical benchmark runs")
    if not metrics.adversarial_suite_complete:
        failures.append("frozen adversarial suite is incomplete")
    if not metrics.regression_gate_installed:
        failures.append("permanent classification regression gate is not installed")

    if metrics.dedicated_open_population_count == 0:
        warnings.append(
            "release candidate produced no OPEN cases; positive OPEN behaviour was not empirically validated"
        )
    if metrics.retired_open_mechanisms:
        warnings.append(
            "retired OPEN-producing mechanisms remain fail-closed: "
            + ", ".join(sorted(metrics.retired_open_mechanisms))
        )

    if failures:
        decision = GateDecision.NO_GO if critical_errors or metrics.dedicated_open_false_open_count else GateDecision.CONDITIONAL
    else:
        decision = GateDecision.GO

    return GateEvaluation(decision=decision, failures=tuple(failures), warnings=tuple(warnings))


def repeated_false_open_mechanisms(
    evaluation_round_errors: tuple[tuple[ValidationError, ...], ...],
) -> frozenset[str]:
    """Return causal mechanisms that produced false OPEN in at least two frozen rounds."""

    rounds_by_rule: dict[str, set[int]] = {}
    for round_index, errors in enumerate(evaluation_round_errors):
        for error in errors:
            if error.error_class is ErrorClass.FALSE_OPEN and error.rule_id is not None:
                rounds_by_rule.setdefault(error.rule_id, set()).add(round_index)
    return frozenset(rule_id for rule_id, rounds in rounds_by_rule.items() if len(rounds) >= 2)
