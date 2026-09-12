"""Diagnostic-only Phase R candidate component/CPV design.

This module is intentionally isolated from the production ComponentDomain enum and matching
pipeline. It records only public-definition-qualified candidate domains and conservative CPV
families for later validation against procurement evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class CandidateComponentRule:
    candidate_domain: str
    category: str
    label: str
    cpv_prefixes: tuple[str, ...]


CANDIDATE_COMPONENT_RULE_VERSION: Final = "phase-r-candidate-components-v1"

CANDIDATE_COMPONENT_RULES: Final[tuple[CandidateComponentRule, ...]] = (
    CandidateComponentRule(
        "digital_transformation",
        "computer_hardware",
        "Computer hardware and equipment",
        ("302",),
    ),
    CandidateComponentRule(
        "digital_transformation",
        "software_information_systems",
        "Software packages and information systems",
        ("48",),
    ),
    CandidateComponentRule(
        "digital_transformation",
        "it_software_data_network_services",
        "IT, software, data and network services",
        ("72",),
    ),
    CandidateComponentRule(
        "waste_circular_economy",
        "refuse_recycling_services",
        "Refuse recycling services",
        ("90514",),
    ),
)


def candidate_rules_for(domain: str) -> tuple[CandidateComponentRule, ...]:
    return tuple(rule for rule in CANDIDATE_COMPONENT_RULES if rule.candidate_domain == domain)


def candidate_cpv_match(domain: str, cpv_code: str) -> bool:
    normalized = "".join(character for character in cpv_code if character.isdigit())[:8]
    if not normalized:
        return False
    return any(
        normalized.startswith(prefix)
        for rule in candidate_rules_for(domain)
        for prefix in rule.cpv_prefixes
    )
