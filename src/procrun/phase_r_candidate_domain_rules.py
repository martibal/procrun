"""Diagnostic-only candidate domain rules for Phase R.

These rules are intentionally isolated from the production ComponentDomain enum and RULES tuple.
They support design-time coverage and specificity checks only. Importing this module cannot alter
production extraction, matching, OPEN/CLOSED classification, read models, or customer output.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Final

CANDIDATE_RULE_VERSION: Final = "phase-r-candidate-cpv-v1"


class CandidateDomain(StrEnum):
    DIGITAL_TRANSFORMATION = "digital_transformation"
    WASTE_CIRCULAR_ECONOMY = "waste_circular_economy"


@dataclass(frozen=True)
class CandidateComponentRule:
    domain: CandidateDomain
    category: str
    label: str
    cpv_prefixes: tuple[str, ...]


def cpv_matches_candidate_prefixes(cpv_code: str | None, prefixes: tuple[str, ...]) -> bool:
    """Return whether a normalized TED CPV code falls in an admitted candidate family."""

    if cpv_code is None:
        return False
    normalized = "".join(character for character in cpv_code if character.isdigit())
    if not normalized:
        return False
    return any(normalized.startswith(prefix) for prefix in prefixes)


CANDIDATE_COMPONENT_RULES: Final[tuple[CandidateComponentRule, ...]] = (
    CandidateComponentRule(
        domain=CandidateDomain.DIGITAL_TRANSFORMATION,
        category="computer_hardware",
        label="Computer equipment and hardware",
        cpv_prefixes=("302",),
    ),
    CandidateComponentRule(
        domain=CandidateDomain.DIGITAL_TRANSFORMATION,
        category="software_information_systems",
        label="Software packages and information systems",
        cpv_prefixes=("48",),
    ),
    CandidateComponentRule(
        domain=CandidateDomain.DIGITAL_TRANSFORMATION,
        category="it_services",
        label="IT and computer-related services",
        cpv_prefixes=("72",),
    ),
    CandidateComponentRule(
        domain=CandidateDomain.WASTE_CIRCULAR_ECONOMY,
        category="recycling_equipment",
        label="Recycling equipment",
        cpv_prefixes=("42914",),
    ),
    CandidateComponentRule(
        domain=CandidateDomain.WASTE_CIRCULAR_ECONOMY,
        category="waste_treatment_infrastructure",
        label="Waste-treatment plant construction",
        cpv_prefixes=("452221",),
    ),
    CandidateComponentRule(
        domain=CandidateDomain.WASTE_CIRCULAR_ECONOMY,
        category="waste_collection_treatment_recycling_services",
        label="Refuse collection, treatment and recycling services",
        cpv_prefixes=("9051",),
    ),
)


def candidate_rules_for(domain: CandidateDomain) -> tuple[CandidateComponentRule, ...]:
    return tuple(rule for rule in CANDIDATE_COMPONENT_RULES if rule.domain is domain)


__all__ = [
    "CANDIDATE_RULE_VERSION",
    "CandidateDomain",
    "CandidateComponentRule",
    "CANDIDATE_COMPONENT_RULES",
    "candidate_rules_for",
    "cpv_matches_candidate_prefixes",
]
