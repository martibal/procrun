"""Portugal 2030 source contract.

Phase A deliberately starts with a canonical, PII-free projection contract. The live collector
must prove that its chosen source surface can return these fields without first downloading a
broader record containing prohibited fields.
"""

from datetime import date, datetime
from typing import Any

from procrun.domain import FundingProject
from procrun.privacy import validate_projected_record

PORTUGAL2030_ALLOWED_FIELDS = frozenset(
    {
        "operation_code",
        "first_seen_at",
        "project_start",
        "project_end",
        "approved_funding_eur",
        "executed_funding_eur",
        "project_scope_text",
        "source_url",
    }
)


def _parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return date.fromisoformat(str(value))


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def normalize_project_record(record: dict[str, Any]) -> FundingProject:
    safe = validate_projected_record(record, PORTUGAL2030_ALLOWED_FIELDS)
    return FundingProject(
        operation_code=str(safe["operation_code"]),
        first_seen_at=_parse_datetime(safe["first_seen_at"]),
        project_start=_parse_date(safe.get("project_start")),
        project_end=_parse_date(safe.get("project_end")),
        approved_funding_eur=safe.get("approved_funding_eur"),
        executed_funding_eur=safe.get("executed_funding_eur"),
        project_scope_text=str(safe["project_scope_text"]),
        source_url=str(safe["source_url"]),
    )
