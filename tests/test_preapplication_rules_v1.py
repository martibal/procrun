from datetime import datetime, timezone

from procrun.preapplication_rules import (
    DISCLAIMER,
    RuleDefinition,
    RuleKind,
    RuleOutcome,
    RuleSet,
    evaluate_ruleset,
)


def _ruleset() -> RuleSet:
    return RuleSet(
        ruleset_id="BANDO-X:v1",
        bando_code="BANDO-X",
        version=1,
        effective_from=datetime(2026, 1, 1, tzinfo=timezone.utc),
        effective_to=None,
        source_document_hashes=("a" * 64,),
        rules=(
            RuleDefinition(
                rule_id="formal-investment-min",
                module="FORMAL_ELIGIBILITY",
                input_key="investment_eur",
                kind=RuleKind.MIN_NUMBER,
                threshold=100_000,
                public_source_url="https://example.invalid/bando",
                public_source_citation="Section 3.1",
                customer_label="Minimum investment",
            ),
            RuleDefinition(
                rule_id="technical-dnsh",
                module="TECHNICAL_STRATEGIC_MATCH",
                input_key="dnsh_confirmed",
                kind=RuleKind.BOOLEAN_REQUIRED,
                required_boolean=True,
                public_source_url="https://example.invalid/bando",
                public_source_citation="Section 5.2",
                customer_label="DNSH requirement",
            ),
        ),
    )


def test_rules_are_evaluated_only_from_supplied_input() -> None:
    modules = evaluate_ruleset(
        _ruleset(), {"investment_eur": 150_000, "dnsh_confirmed": True}
    )
    assert [module.outcome for module in modules] == [
        RuleOutcome.LIKELY_ELIGIBLE,
        RuleOutcome.LIKELY_ELIGIBLE,
    ]
    assert all(module.disclaimer == DISCLAIMER for module in modules)


def test_missing_input_requires_review_not_imputation() -> None:
    modules = evaluate_ruleset(_ruleset(), {"investment_eur": 150_000})
    technical = next(module for module in modules if module.module == "TECHNICAL_STRATEGIC_MATCH")
    assert technical.outcome is RuleOutcome.REVIEW_REQUIRED
    assert technical.evaluations[0].reason.startswith("Required input")


def test_explicit_rule_failure_is_likely_not_eligible() -> None:
    modules = evaluate_ruleset(
        _ruleset(), {"investment_eur": 99_999, "dnsh_confirmed": True}
    )
    formal = next(module for module in modules if module.module == "FORMAL_ELIGIBILITY")
    assert formal.outcome is RuleOutcome.LIKELY_NOT_ELIGIBLE
