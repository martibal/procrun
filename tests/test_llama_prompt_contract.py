from procrun.component_engine import ComponentDomain
from procrun.llama_adapter import LLAMA_ADAPTER_VERSION, _prompt
from procrun.model_fallback import (
    AllowedComponentCategory,
    LocalModelRequest,
    ModelPromptSpan,
)


def test_prompt_requires_minimal_exact_evidence_and_explicit_abstention() -> None:
    text = "Será instalada telemetria para operação remota."
    request = LocalModelRequest(
        operation_code="BENCH-PROMPT",
        source_sha256="a" * 64,
        domains=(ComponentDomain.WATER_WASTEWATER,),
        unmatched_scope_spans=(
            ModelPromptSpan(start=0, end=len(text), text=text),
        ),
        allowed_categories=(
            AllowedComponentCategory(
                domain=ComponentDomain.WATER_WASTEWATER,
                category="automation_control",
                label="Automation and control",
            ),
        ),
    )

    prompt = _prompt(request)

    assert LLAMA_ADAPTER_VERSION == "llama-component-benchmark-v4"
    assert "shortest contiguous phrase" in prompt
    assert "never copy the surrounding sentence" in prompt
    assert "absolute offsets" in prompt
    assert "empty proposals array" in prompt
    assert "maintenance" in prompt
    assert "generic or undefined technical activities" in prompt
    assert text in prompt
