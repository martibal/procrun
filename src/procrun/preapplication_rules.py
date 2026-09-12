"""Versioned rule engine for formal eligibility and technical/strategic screening.

Rules are authored only from public bando documents. Evaluation consumes only user-supplied
project/company facts. The module performs no external lookup and makes no binding legal decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Mapping


RULE_ENGINE_VERSION = "preapplication-rules-v1"
DISCLAIMER = (
    "Information screening only. This output is not binding legal, financial, or application advice."
)


class RuleOutcome(StrEnum):
    LIKELY_ELIGIBLE = "LIKELY_ELIGIBLE"
    LIKELY_NOT_ELIGIBLE = "LIKELY_NOT_ELIGIBLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class RuleKind(StrEnum):
    ALLOWED_VALUES = "ALLOWED_VALUES"
    MIN_NUMBER = "MIN_NUMBER"
    MAX_NUMBER = "MAX_NUMBER"
    BOOLEAN_REQUIRED = "BOOLEAN_REQUIRED"


@dataclass(frozen=True)
class RuleDefinition:
    rule_id: str
    module: str
    input_key: str
    kind: RuleKind
    public_source_url: str
    public_source_citation: str
    allowed_values: tuple[str, ...] = ()
    threshold: float | None = None
    required_boolean: bool | None = None
    customer_label: str = ""


@dataclass(frozen=True)
class RuleSet:
    ruleset_id: str
    bando_code: str
    version: int
    effective_from: datetime
    effective_to: datetime | None
    rules: tuple[RuleDefinition, ...]
    source_document_hashes: tuple[str, ...]


@dataclass(frozen=True)
class RuleEvaluation:
    rule_id: str
    outcome: RuleOutcome
    customer_label: str
    reason: str
    source_url: str
    source_citation: str


@dataclass(frozen=True)
class ModuleEvaluation:
    module: str
    outcome: RuleOutcome
    evaluations: tuple[RuleEvaluation, ...]
    disclaimer: str = DISCLAIMER


def _evaluate_rule(rule: RuleDefinition, inputs: Mapping[str, object]) -> RuleEvaluation:
    if rule.input_key not in inputs or inputs[rule.input_key] is None:
        return RuleEvaluation(
            rule_id=rule.rule_id,
            outcome=RuleOutcome.REVIEW_REQUIRED,
            customer_label=rule.customer_label,
            reason=f"Required input {rule.input_key!r} was not supplied.",
            source_url=rule.public_source_url,
            source_citation=rule.public_source_citation,
        )

    value = inputs[rule.input_key]
    passed: bool
    if rule.kind is RuleKind.ALLOWED_VALUES:
        passed = str(value) in rule.allowed_values
    elif rule.kind is RuleKind.MIN_NUMBER:
        if rule.threshold is None:
            raise ValueError(f"rule {rule.rule_id} lacks threshold")
        passed = float(value) >= rule.threshold
    elif rule.kind is RuleKind.MAX_NUMBER:
        if rule.threshold is None:
            raise ValueError(f"rule {rule.rule_id} lacks threshold")
        passed = float(value) <= rule.threshold
    elif rule.kind is RuleKind.BOOLEAN_REQUIRED:
        if rule.required_boolean is None:
            raise ValueError(f"rule {rule.rule_id} lacks required_boolean")
        passed = bool(value) is rule.required_boolean
    else:  # pragma: no cover - enum exhaustiveness guard
        raise ValueError(f"unsupported rule kind: {rule.kind}")

    return RuleEvaluation(
        rule_id=rule.rule_id,
        outcome=(RuleOutcome.LIKELY_ELIGIBLE if passed else RuleOutcome.LIKELY_NOT_ELIGIBLE),
        customer_label=rule.customer_label,
        reason=("Input satisfies the encoded public rule." if passed else "Input does not satisfy the encoded public rule."),
        source_url=rule.public_source_url,
        source_citation=rule.public_source_citation,
    )


def _aggregate(evaluations: tuple[RuleEvaluation, ...]) -> RuleOutcome:
    if not evaluations:
        return RuleOutcome.NOT_APPLICABLE
    if any(e.outcome is RuleOutcome.LIKELY_NOT_ELIGIBLE for e in evaluations):
        return RuleOutcome.LIKELY_NOT_ELIGIBLE
    if any(e.outcome is RuleOutcome.REVIEW_REQUIRED for e in evaluations):
        return RuleOutcome.REVIEW_REQUIRED
    return RuleOutcome.LIKELY_ELIGIBLE


def evaluate_ruleset(ruleset: RuleSet, inputs: Mapping[str, object]) -> tuple[ModuleEvaluation, ...]:
    """Evaluate one immutable ruleset without any external data access."""
    modules = sorted({rule.module for rule in ruleset.rules})
    results: list[ModuleEvaluation] = []
    for module in modules:
        evaluations = tuple(
            _evaluate_rule(rule, inputs) for rule in ruleset.rules if rule.module == module
        )
        results.append(
            ModuleEvaluation(
                module=module,
                outcome=_aggregate(evaluations),
                evaluations=evaluations,
            )
        )
    return tuple(results)
