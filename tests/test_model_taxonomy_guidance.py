from procrun.component_engine import RULES, ComponentDomain
from procrun.llama_adapter import _prompt
from procrun.model_fallback import (
    MODEL_CATEGORY_GUIDANCE_VERSION,
    AllowedComponentCategory,
    LocalModelRequest,
    ModelPromptSpan,
)


def _category(domain: ComponentDomain, category: str) -> AllowedComponentCategory:
    rule = next(item for item in RULES if item.domain is domain and item.category == category)
    return AllowedComponentCategory(
        domain=rule.domain,
        category=rule.category,
        label=rule.label,
    )


def test_model_guidance_covers_every_frozen_taxonomy_category() -> None:
    assert MODEL_CATEGORY_GUIDANCE_VERSION == "component-model-guidance-v1"

    categories = [
        AllowedComponentCategory(
            domain=rule.domain,
            category=rule.category,
            label=rule.label,
        )
        for rule in RULES
    ]

    assert len(categories) == len(RULES)
    assert all(category.selection_rule.strip() for category in categories)
    assert all("selection_rule" in category.model_dump() for category in categories)


def test_model_guidance_disambiguates_known_neighbor_categories() -> None:
    automation = _category(ComponentDomain.WATER_WASTEWATER, "automation_control")
    signalling = _category(ComponentDomain.RAIL_TRANSPORT, "signalling")
    marine = _category(ComponentDomain.PORTS_COASTAL, "marine_works")
    sensors = _category(ComponentDomain.RESILIENCE_FIRE, "sensors_cameras")

    assert "monitoring" in automation.selection_rule
    assert "traction" in signalling.selection_rule
    assert "civil_works" in marine.selection_rule
    assert "vehicles" in sensors.selection_rule


def test_prompt_serializes_selection_rules_with_allowed_categories() -> None:
    text = "Será instalado um controlador lógico programável."
    request = LocalModelRequest(
        operation_code="BENCH-GUIDANCE",
        source_sha256="a" * 64,
        domains=(ComponentDomain.WATER_WASTEWATER,),
        unmatched_scope_spans=(
            ModelPromptSpan(start=0, end=len(text), text=text),
        ),
        allowed_categories=(
            _category(ComponentDomain.WATER_WASTEWATER, "automation_control"),
            _category(ComponentDomain.WATER_WASTEWATER, "monitoring"),
        ),
    )

    prompt = _prompt(request)

    assert '"selection_rule":' in prompt
    assert "automatic or remote command and control" in prompt
    assert "measurement, sensing" in prompt
