from procrun.component_engine import COMPONENT_RULE_VERSION, RULES, ComponentDomain
from procrun.model_fallback import MODEL_CATEGORY_GUIDANCE_VERSION, model_category_selection_rule


def test_a21_v2_taxonomy_contains_battery_storage() -> None:
    keys = {(rule.domain, rule.category) for rule in RULES}
    assert (ComponentDomain.ENERGY_EFFICIENCY, "battery_storage") in keys
    assert COMPONENT_RULE_VERSION == "component-taxonomy-v2"


def test_a21_v2_model_guidance_covers_battery_storage() -> None:
    guidance = model_category_selection_rule(
        ComponentDomain.ENERGY_EFFICIENCY,
        "battery_storage",
    )
    assert "battery" in guidance.lower()
    assert MODEL_CATEGORY_GUIDANCE_VERSION == "component-model-guidance-v2"


def test_a21_v2_taxonomy_has_italian_coverage_in_every_domain() -> None:
    expected_phrase = {
        ComponentDomain.WATER_WASTEWATER: "pompe",
        ComponentDomain.RAIL_TRANSPORT: "segnalamento ferroviario",
        ComponentDomain.PORTS_COASTAL: "opere portuali",
        ComponentDomain.ENERGY_EFFICIENCY: "sistema di accumulo",
        ComponentDomain.RESILIENCE_FIRE: "telecamere",
    }
    for domain, phrase in expected_phrase.items():
        assert any(rule.domain is domain and phrase in rule.phrases for rule in RULES)
