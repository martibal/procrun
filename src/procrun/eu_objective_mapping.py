"""Frozen Phase R mapping from approved EU structured classifications to ProcRun domains.

This module contains only structured, publisher-supplied classification signals already present in
FundingProject.objective / FundingProject.theme. It never reads free text and never upgrades a
structured-only suggestion to OPEN/CLOSED evidence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final


MAPPING_VERSION: Final = "eu-structured-mapping-v1"


@dataclass(frozen=True)
class StructuredMapping:
    source: str
    key: str
    domain: str
    label: str


# Regulation (EU) 2021/1058, Article 3 specific objectives. Only objectives that map
# unambiguously to one existing ProcRun domain are admitted here. Broader objectives such as
# climate/disaster resilience and connected transport are intentionally not mapped by objective
# alone because they span multiple ProcRun domains.
SPECIFIC_OBJECTIVE_MAP: Final[dict[str, StructuredMapping]] = {
    "RSO2.1": StructuredMapping(
        source="specific_objective",
        key="RSO2.1",
        domain="energy_efficiency",
        label="Energy efficiency",
    ),
    "RSO2.5": StructuredMapping(
        source="specific_objective",
        key="RSO2.5",
        domain="water_wastewater",
        label="Water and wastewater",
    ),
}


# Regulation (EU) 2021/1060, Annex I intervention fields. These codes are sufficiently narrow
# to map to an existing ProcRun domain without using project free text.
INTERVENTION_FIELD_MAP: Final[dict[str, StructuredMapping]] = {
    **{
        code: StructuredMapping("intervention_category", code, "energy_efficiency", "Energy efficiency")
        for code in ("038", "039", "040", "041", "042", "043", "044", "045")
    },
    "059": StructuredMapping(
        "intervention_category", "059", "resilience_fire", "Fire-risk resilience"
    ),
    **{
        code: StructuredMapping("intervention_category", code, "water_wastewater", "Water and wastewater")
        for code in ("062", "063", "064", "065", "066")
    },
    **{
        code: StructuredMapping("intervention_category", code, "rail_transport", "Rail transport")
        for code in (
            "096",
            "097",
            "098",
            "099",
            "100",
            "101",
            "102",
            "103",
            "104",
            "105",
            "106",
            "107",
        )
    },
    **{
        code: StructuredMapping("intervention_category", code, "ports_coastal", "Ports and coastal")
        for code in ("110", "111", "112", "113", "114", "115")
    },
}

_OBJECTIVE_RE = re.compile(r"\b(RSO\d+(?:\.\d+)+)\b", re.IGNORECASE)
_INTERVENTION_RE = re.compile(r"(?<!\d)(\d{3})(?!\d)")


def _objective_key(value: str | None) -> str | None:
    if not value:
        return None
    match = _OBJECTIVE_RE.search(value)
    return match.group(1).upper() if match else None


def _intervention_key(value: str | None) -> str | None:
    if not value:
        return None
    for match in _INTERVENTION_RE.finditer(value):
        code = match.group(1)
        if code in INTERVENTION_FIELD_MAP:
            return code
    return None


def mappings_for(*, specific_objective: str | None, intervention_category: str | None) -> tuple[StructuredMapping, ...]:
    """Return deterministic structured mappings, deduplicated by source/key/domain."""

    found: list[StructuredMapping] = []
    objective_key = _objective_key(specific_objective)
    if objective_key and objective_key in SPECIFIC_OBJECTIVE_MAP:
        found.append(SPECIFIC_OBJECTIVE_MAP[objective_key])
    intervention_key = _intervention_key(intervention_category)
    if intervention_key and intervention_key in INTERVENTION_FIELD_MAP:
        found.append(INTERVENTION_FIELD_MAP[intervention_key])
    unique: dict[tuple[str, str, str], StructuredMapping] = {}
    for item in found:
        unique[(item.source, item.key, item.domain)] = item
    return tuple(sorted(unique.values(), key=lambda item: (item.domain, item.source, item.key)))
