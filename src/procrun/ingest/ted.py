"""TED Search API projection contract.

The live client must request only these fields via TED's server-side field projection. A broader
notice response is not an acceptable input to the intelligence pipeline.
"""

from datetime import date, datetime
from typing import Any

from procrun.domain import ProcurementEvidence
from procrun.privacy import validate_projected_record

TED_ALLOWED_FIELDS = frozenset(
    {
        "notice_id",
        "publication_date",
        "title",
        "cpv_codes",
        "procedure_value_eur",
        "project_reference",
        "source_url",
    }
)


def normalize_ted_record(
    record: dict[str, Any], *, evidence_id: str, component_id: str
) -> ProcurementEvidence:
    safe = validate_projected_record(record, TED_ALLOWED_FIELDS)
    publication = safe["publication_date"]
    if isinstance(publication, datetime):
        publication_date = publication.date()
    elif isinstance(publication, date):
        publication_date = publication
    else:
        publication_date = date.fromisoformat(str(publication))

    raw_cpv = safe.get("cpv_codes") or ()
    cpv_codes = (
        (raw_cpv,)
        if isinstance(raw_cpv, str)
        else tuple(str(code) for code in raw_cpv)
    )

    return ProcurementEvidence(
        evidence_id=evidence_id,
        component_id=component_id,
        notice_id=str(safe["notice_id"]),
        publication_date=publication_date,
        title=str(safe["title"]),
        cpv_codes=cpv_codes,
        procedure_value_eur=safe.get("procedure_value_eur"),
        project_reference=(
            None
            if safe.get("project_reference") in (None, "")
            else str(safe["project_reference"])
        ),
        source_url=str(safe["source_url"]),
    )
