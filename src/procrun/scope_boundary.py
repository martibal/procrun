"""Deterministic guards for component scopes that cannot safely be treated as one bought unit."""

from __future__ import annotations

import re

from procrun.component_engine import ExtractedComponent
from procrun.domain import FundingProject

_RAIL_CROSSING_CATEGORY = "rail_transport:crossings"
_PK_IDENTIFIER = re.compile(r"\b(?:PK|PN)\s*\d{1,3}\+\d{3}\b", flags=re.IGNORECASE)
_CROSSING_QUANTITY = re.compile(
    r"\b(?P<count>\d{1,3})\s+passagens?\s+de\s+n[ií]vel\b",
    flags=re.IGNORECASE,
)


def component_scope_boundary_resolved(
    project: FundingProject,
    extracted: ExtractedComponent,
) -> bool:
    """Return False when source scope proves a grouped component but not individual buy units.

    A grouped rail-crossing scope is the critical historical false-OPEN/false-CLOSED case. If the
    source describes multiple crossings in one extracted category, one procurement notice cannot be
    assumed to cover every crossing merely because it matches the category/project. The component is
    withheld until the scope is decomposed or a source proves whole-group coverage.
    """

    if extracted.component.category != _RAIL_CROSSING_CATEGORY:
        return True

    text = project.project_scope_text
    identifiers = {match.group(0).casefold() for match in _PK_IDENTIFIER.finditer(text)}
    if len(identifiers) > 1:
        return False

    quantities = [int(match.group("count")) for match in _CROSSING_QUANTITY.finditer(text)]
    return not any(count > 1 for count in quantities)
