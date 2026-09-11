"""Phase R Task D: normalized Italian phrase evidence."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final

from procrun.component_engine import ComponentDomain, StructuredComponentSuggestion
from procrun.domain import FundingProject
from procrun.italian_normalization import (
    ITALIAN_NORMALIZATION_VERSION,
    normalize_italian_text,
    normalized_tokens,
)
from procrun.phase_r_phrase_expansion import TASK_C_RULES

TASK_D_RULE_VERSION: Final = "phase-r-italian-morphology-v1"


@dataclass(frozen=True)
class TaskDMorphologyEvidence:
    domain: ComponentDomain
    phrase: str
    label: str
    start: int
    end: int
    text: str
    normalized_source: tuple[str, ...]
    normalized_rule: tuple[str, ...]
    rule_version: str = TASK_D_RULE_VERSION
    normalization_version: str = ITALIAN_NORMALIZATION_VERSION


def task_d_morphology_evidence(
    project: FundingProject,
    structured: Sequence[StructuredComponentSuggestion],
) -> tuple[TaskDMorphologyEvidence, ...]:
    """Return exact source spans whose normalized tokens match a compatible Task C rule."""

    allowed_domains = {item.domain for item in structured}
    source_tokens = normalized_tokens(project.project_scope_text)
    source_normalized = tuple(item.normalized for item in source_tokens)
    evidence: list[TaskDMorphologyEvidence] = []

    for rule in TASK_C_RULES:
        if rule.domain not in allowed_domains:
            continue
        normalized_rule = normalize_italian_text(rule.phrase)
        width = len(normalized_rule)
        if not width:
            continue
        for start_index in range(0, len(source_normalized) - width + 1):
            end_index = start_index + width
            if source_normalized[start_index:end_index] != normalized_rule:
                continue
            start = source_tokens[start_index].start
            end = source_tokens[end_index - 1].end
            evidence.append(
                TaskDMorphologyEvidence(
                    domain=rule.domain,
                    phrase=rule.phrase,
                    label=rule.label,
                    start=start,
                    end=end,
                    text=project.project_scope_text[start:end],
                    normalized_source=source_normalized[start_index:end_index],
                    normalized_rule=normalized_rule,
                )
            )

    unique: dict[tuple[str, int, int, str], TaskDMorphologyEvidence] = {}
    for item in evidence:
        unique[(item.domain.value, item.start, item.end, item.phrase)] = item
    return tuple(
        sorted(
            unique.values(),
            key=lambda item: (item.start, item.end, item.domain.value, item.phrase.casefold()),
        )
    )
