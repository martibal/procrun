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

    assert LLAMA_ADAPTER_VERSION == "llama-component-benchmark-v7"
    assert "inclusive start_token/end_token" in prompt
    assert "shortest contiguous token sequence" in prompt
    assert "Do not reproduce, translate, normalize" in prompt
    assert "do not calculate character offsets" in prompt
    assert "Python will reconstruct exact source_text" in prompt
    assert "empty proposals array" in prompt
    assert "maintenance" in prompt
    assert "generic or undefined technical activities" in prompt
    assert '"token_index":0' in prompt
    assert "/no_think" not in prompt
    assert text in prompt
