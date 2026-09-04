"""TED Search API projection contract.

The live client must request only the fields qualified and approved through TED's server-side field
projection. A broader notice response is not an acceptable input to the intelligence pipeline.
"""

import re
from datetime import date, datetime
from typing import Any

from procrun.domain import ProcurementEvidence
from procrun.privacy import validate_projected_record

TED_ALLOWED_FIELDS = frozenset(
    {
        "notice_id",
        "publication_date",
        "award_date",
        "contract_date",
        "title",
        "scope_description",
        "cpv_codes",
        "contract_nature",
        "procedure_type",
        "procedure_value_eur",
        "estimated_value_eur",
        "base_value_eur",
        "awarded_value_eur",
        "place_of_performance",
        "nuts_code",
        "municipality",
        "project_reference",
        "source_url",
    }
)

_DATE_WITH_OFFSET = re.compile(r"^(\d{4}-\d{2}-\d{2})[+-]\d{2}:\d{2}$")


def _parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = str(value)
    offset_match = _DATE_WITH_OFFSET.fullmatch(text)
    if offset_match is not None:
        # TED can serialize date-only fields with an offset suffix. The source field is still a
        # calendar date, so preserve that published calendar date rather than applying timezone
        # conversion that could move it across a day boundary.
        text = offset_match.group(1)
    return date.fromisoformat(text)


def _optional_text(value: Any) -> str | None:
    return None if value in (None, "") else str(value)


def normalize_ted_record(
    record: dict[str, Any], *, evidence_id: str, component_id: str
) -> ProcurementEvidence:
    safe = validate_projected_record(record, TED_ALLOWED_FIELDS)
    publication_date = _parse_date(safe["publication_date"])
    if publication_date is None:
        raise ValueError("publication_date is required")

    raw_cpv = safe.get("cpv_codes") or ()
    cpv_codes = (raw_cpv,) if isinstance(raw_cpv, str) else tuple(str(code) for code in raw_cpv)

    return ProcurementEvidence(
        evidence_id=evidence_id,
        component_id=component_id,
        notice_id=str(safe["notice_id"]),
        publication_date=publication_date,
        award_date=_parse_date(safe.get("award_date")),
        contract_date=_parse_date(safe.get("contract_date")),
        title=str(safe["title"]),
        scope_description=_optional_text(safe.get("scope_description")),
        cpv_codes=cpv_codes,
        contract_nature=_optional_text(safe.get("contract_nature")),
        procedure_type=_optional_text(safe.get("procedure_type")),
        procedure_value_eur=safe.get("procedure_value_eur"),
        estimated_value_eur=safe.get("estimated_value_eur"),
        base_value_eur=safe.get("base_value_eur"),
        awarded_value_eur=safe.get("awarded_value_eur"),
        place_of_performance=_optional_text(safe.get("place_of_performance")),
        nuts_code=_optional_text(safe.get("nuts_code")),
        municipality=_optional_text(safe.get("municipality")),
        contracting_authority_name=None,
        project_reference=_optional_text(safe.get("project_reference")),
        source_url=str(safe["source_url"]),
    )
