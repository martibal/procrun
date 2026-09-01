"""Portugal 2030 source contract.

Phase A deliberately starts with a canonical, PII-free projection contract. The live collector
must prove that its chosen source surface can return these fields without first downloading a
broader record containing prohibited fields.
"""

from datetime import date, datetime
from typing import Any

from procrun.domain import FundingProject, TemporalProvenance
from procrun.privacy import validate_projected_record

PORTUGAL2030_ALLOWED_FIELDS = frozenset(
    {
        "operation_code",
        "first_seen_at",
        "project_title",
        "project_start",
        "project_end",
        "approved_funding_eur",
        "executed_funding_eur",
        "project_scope_text",
        "fund",
        "programme",
        "objective",
        "theme",
        "region",
        "municipality",
        "nuts_code",
        "source_url",
    }
)


def _parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return date.fromisoformat(str(value))


def _parse_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def normalize_project_record(
    record: dict[str, Any],
    *,
    temporal_provenance: TemporalProvenance = TemporalProvenance.UNRESOLVED,
) -> FundingProject:
    safe = validate_projected_record(record, PORTUGAL2030_ALLOWED_FIELDS)
    return FundingProject(
        operation_code=str(safe["operation_code"]),
        first_seen_at=_parse_datetime(safe.get("first_seen_at")),
        temporal_provenance=temporal_provenance,
        project_title=(
            None if safe.get("project_title") in (None, "") else str(safe["project_title"])
        ),
        project_start=_parse_date(safe.get("project_start")),
        project_end=_parse_date(safe.get("project_end")),
        approved_funding_eur=safe.get("approved_funding_eur"),
        executed_funding_eur=safe.get("executed_funding_eur"),
        project_scope_text=str(safe["project_scope_text"]),
        fund=None if safe.get("fund") in (None, "") else str(safe["fund"]),
        programme=(None if safe.get("programme") in (None, "") else str(safe["programme"])),
        objective=(None if safe.get("objective") in (None, "") else str(safe["objective"])),
        theme=None if safe.get("theme") in (None, "") else str(safe["theme"]),
        region=None if safe.get("region") in (None, "") else str(safe["region"]),
        municipality=(
            None if safe.get("municipality") in (None, "") else str(safe["municipality"])
        ),
        nuts_code=(None if safe.get("nuts_code") in (None, "") else str(safe["nuts_code"])),
        source_url=str(safe["source_url"]),
    )
