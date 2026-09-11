"""Phase R Task C: corpus-derived Italian phrase evidence.

These rules are deliberately isolated from the production component taxonomy while Phase R is
being measured. A Task C phrase counts only when an already-approved structured classification
suggests the same ProcRun domain. It therefore cannot manufacture OPEN/CLOSED evidence by itself.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final, Sequence

from procrun.component_engine import ComponentDomain, StructuredComponentSuggestion
from procrun.domain import FundingProject

TASK_C_RULE_VERSION: Final = "phase-r-corpus-phrases-v1"


@dataclass(frozen=True)
class TaskCPhraseRule:
    domain: ComponentDomain
    phrase: str
    label: str


@dataclass(frozen=True)
class TaskCPhraseEvidence:
    domain: ComponentDomain
    phrase: str
    label: str
    start: int
    end: int
    text: str
    rule_version: str = TASK_C_RULE_VERSION


# Frozen from the isolated Task A corpus report. Generic tokens such as "energetico",
# "riqualificazione", "efficientamento", "ristrutturazione" and "lavori" are intentionally
# excluded because they are not sufficiently specific on their own.
TASK_C_RULES: Final[tuple[TaskCPhraseRule, ...]] = (
    TaskCPhraseRule(
        ComponentDomain.ENERGY_EFFICIENCY,
        "efficientamento energetico",
        "Energy-efficiency upgrade",
    ),
    TaskCPhraseRule(
        ComponentDomain.ENERGY_EFFICIENCY,
        "riqualificazione energetica",
        "Energy-efficiency upgrade",
    ),
)


def _pattern(phrase: str) -> re.Pattern[str]:
    return re.compile(rf"(?<!\w){re.escape(phrase)}(?!\w)", flags=re.IGNORECASE)


def task_c_phrase_evidence(
    project: FundingProject,
    structured: Sequence[StructuredComponentSuggestion],
) -> tuple[TaskCPhraseEvidence, ...]:
    """Return exact Task C spans supported by a compatible structured classification."""

    allowed_domains = {item.domain for item in structured}
    evidence: list[TaskCPhraseEvidence] = []
    for rule in TASK_C_RULES:
        if rule.domain not in allowed_domains:
            continue
        for match in _pattern(rule.phrase).finditer(project.project_scope_text):
            evidence.append(
                TaskCPhraseEvidence(
                    domain=rule.domain,
                    phrase=rule.phrase,
                    label=rule.label,
                    start=match.start(),
                    end=match.end(),
                    text=project.project_scope_text[match.start() : match.end()],
                )
            )
    return tuple(
        sorted(
            evidence,
            key=lambda item: (item.start, item.end, item.domain.value, item.phrase.casefold()),
        )
    )
