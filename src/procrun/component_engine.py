"""ProcRun component engine: phrase evidence plus Phase R structured classification signals.

The free-text phrase matcher remains isolated in component_engine_phrase. Structured signals are
publisher-supplied classifications already admitted on FundingProject.objective/theme and are never
promoted to OPEN/CLOSED evidence by this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from procrun.component_engine_phrase import (
    COMPONENT_RULE_VERSION,
    RULES,
    ComponentDomain,
    ComponentRule,
    EvidenceSpan,
    ExtractedComponent,
    ExtractionResult,
    cpv_matches_prefixes,
    extract_components,
    rules_for,
)
from procrun.domain import FundingProject
from procrun.eu_objective_mapping import MAPPING_VERSION, mappings_for

STRUCTURED_RULE_VERSION: Final = "component-structured-v1"


class StructuredSignalSource(StrEnum):
    SPECIFIC_OBJECTIVE = "specific_objective"
    INTERVENTION_CATEGORY = "intervention_category"


@dataclass(frozen=True)
class StructuredComponentSuggestion:
    """A category suggestion from structured source metadata, never full text evidence."""

    domain: ComponentDomain
    label: str
    source: StructuredSignalSource
    mapping_key: str
    source_value: str
    rule_version: str = STRUCTURED_RULE_VERSION
    mapping_version: str = MAPPING_VERSION


def structured_component_suggestions(
    project: FundingProject,
    domains: tuple[ComponentDomain, ...] | list[ComponentDomain],
) -> tuple[StructuredComponentSuggestion, ...]:
    """Return deterministic structured-only category suggestions for an admitted project.

    This function is deliberately separate from ``extract_components``. A return value here does
    not create a PurchaseComponent and cannot be consumed by OPEN/CLOSED matching without a later
    explicit confidence/evidence gate.
    """

    allowed = frozenset(domains)
    if not allowed:
        raise ValueError("at least one component domain is required")

    raw = mappings_for(
        specific_objective=project.objective,
        intervention_category=project.theme,
    )
    suggestions: list[StructuredComponentSuggestion] = []
    for mapping in raw:
        domain = ComponentDomain(mapping.domain)
        if domain not in allowed:
            continue
        if mapping.source == StructuredSignalSource.SPECIFIC_OBJECTIVE.value:
            source = StructuredSignalSource.SPECIFIC_OBJECTIVE
            source_value = project.objective or ""
        elif mapping.source == StructuredSignalSource.INTERVENTION_CATEGORY.value:
            source = StructuredSignalSource.INTERVENTION_CATEGORY
            source_value = project.theme or ""
        else:  # pragma: no cover - mapping module is frozen and validated by tests
            raise RuntimeError(f"unknown structured mapping source: {mapping.source}")
        suggestions.append(
            StructuredComponentSuggestion(
                domain=domain,
                label=mapping.label,
                source=source,
                mapping_key=mapping.key,
                source_value=source_value,
            )
        )

    unique: dict[tuple[str, str, str], StructuredComponentSuggestion] = {}
    for item in suggestions:
        unique[(item.domain.value, item.source.value, item.mapping_key)] = item
    return tuple(
        sorted(
            unique.values(),
            key=lambda item: (item.domain.value, item.source.value, item.mapping_key),
        )
    )


__all__ = [
    "COMPONENT_RULE_VERSION",
    "RULES",
    "ComponentDomain",
    "ComponentRule",
    "EvidenceSpan",
    "ExtractedComponent",
    "ExtractionResult",
    "cpv_matches_prefixes",
    "extract_components",
    "rules_for",
    "STRUCTURED_RULE_VERSION",
    "StructuredSignalSource",
    "StructuredComponentSuggestion",
    "structured_component_suggestions",
]
