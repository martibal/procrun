"""Field-projected TED Search API collector.

The production collector intentionally uses a strict subset of the field projection that was
qualified live. Fields that were not part of that frozen qualification are not requested merely
because TED can return them.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from procrun.source_contracts import require_live_source

TED_SEARCH_URL = "https://api.ted.europa.eu/v3/notices/search"
TED_SOURCE_ID = "ted_search_api"
TED_DEFAULT_PAGE_SIZE = 100
TED_MAX_PAGE_SIZE = 250
TED_FIELD_CELL_LIMIT = 10_000

# Frozen production subset of scripts/qualify_ted_foundation.py SAFE_FIELDS.
# Deliberately excluded until separately qualified for the intelligence plane:
# buyer-name, place-of-performance-city-proc, result-value-notice and
# result-value-cur-notice.
TED_PROJECTED_FIELDS = (
    "publication-number",
    "publication-date",
    "notice-title",
    "description-proc",
    "classification-cpv",
    "contract-nature",
    "procedure-type",
    "estimated-value-proc",
    "estimated-value-cur-proc",
    "place-of-performance-subdiv-proc",
    "eu-funds-financing-id-lot",
    "eu-funds-identifier",
)
TED_RESPONSE_FIELDS = frozenset(
    {"notices", "totalNoticeCount", "iterationNextToken", "timedOut"}
)
TED_NOTICE_FIELDS = frozenset(TED_PROJECTED_FIELDS) | {"links"}
_LANGUAGE_PREFERENCE = ("eng", "por", "pt")


class TedContractError(ValueError):
    """Raised when TED returns data outside the frozen transport contract."""


class TedTransportError(RuntimeError):
    """Raised for HTTP or JSON failures without exposing a response body."""


@dataclass(frozen=True)
class TedCollectionResult:
    records: tuple[dict[str, Any], ...]
    total_notice_count: int | None
    pages_fetched: int
    complete: bool
    stop_reason: str


def _flatten_text(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, Mapping):
        for language in _LANGUAGE_PREFERENCE:
            if language in value:
                preferred = _flatten_text(value[language])
                if preferred:
                    return preferred
        result: list[str] = []
        for key in sorted(value, key=str):
            result.extend(_flatten_text(value[key]))
        return result
    if isinstance(value, Sequence) and not isinstance(value, bytes | bytearray):
        result = []
        for item in value:
            result.extend(_flatten_text(item))
        return result
    return [str(value)]


def _text(value: Any, *, join: bool = False) -> str | None:
    values = list(dict.fromkeys(_flatten_text(value)))
    if not values:
        return None
    return " | ".join(values) if join else values[0]


def _codes(value: Any) -> list[str]:
    return list(dict.fromkeys(_flatten_text(value)))


def _eur_integer_amount(value: Any, currency: Any) -> int | None:
    if value in (None, ""):
        return None
    if _text(currency) != "EUR":
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    if not number.is_finite() or number < 0 or number != number.to_integral_value():
        return None
    return int(number)


def _project_reference(notice: Mapping[str, Any]) -> str | None:
    for field in ("eu-funds-identifier", "eu-funds-financing-id-lot"):
        value = _text(notice.get(field))
        if value is not None:
            return value
    return None


def _validate_notice_shape(notice: Any) -> Mapping[str, Any]:
    if not isinstance(notice, Mapping):
        raise TedContractError("TED notice must be a JSON object")
    unexpected = set(notice) - TED_NOTICE_FIELDS
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise TedContractError(f"TED notice returned non-projected fields: {names}")
    return notice


def canonicalize_ted_notice(notice: Mapping[str, Any]) -> dict[str, Any]:
    """Convert one field-projected TED notice into the canonical ingest field shape."""

    safe = _validate_notice_shape(notice)
    publication_number = _text(safe.get("publication-number"))
    publication_date = _text(safe.get("publication-date"))
    title = _text(safe.get("notice-title"))
    if publication_number is None:
        raise TedContractError("TED notice lacks publication-number")
    if publication_date is None:
        raise TedContractError("TED notice lacks publication-date")
    if title is None:
        raise TedContractError("TED notice lacks notice-title")

    return {
        "notice_id": publication_number,
        "publication_date": publication_date,
        "award_date": None,
        "contract_date": None,
        "title": title,
        "scope_description": _text(safe.get("description-proc"), join=True),
        "cpv_codes": _codes(safe.get("classification-cpv")),
        "contract_nature": _text(safe.get("contract-nature"), join=True),
        "procedure_type": _text(safe.get("procedure-type"), join=True),
        "procedure_value_eur": None,
        "estimated_value_eur": _eur_integer_amount(
            safe.get("estimated-value-proc"), safe.get("estimated-value-cur-proc")
        ),
        "base_value_eur": None,
        "awarded_value_eur": None,
        "place_of_performance": None,
        "nuts_code": _text(safe.get("place-of-performance-subdiv-proc"), join=True),
        "municipality": None,
        "project_reference": _project_reference(safe),
        "source_url": f"https://ted.europa.eu/en/notice/-/detail/{publication_number}",
    }


def _validate_page_size(page_size: int) -> None:
    if not 1 <= page_size <= TED_MAX_PAGE_SIZE:
        raise ValueError(f"page_size must be between 1 and {TED_MAX_PAGE_SIZE}")
    effective_fields = set(TED_PROJECTED_FIELDS) | {"links"}
    if len(effective_fields) * page_size > TED_FIELD_CELL_LIMIT:
        raise ValueError("TED field projection exceeds the per-page field-cell limit")


def _parse_envelope(response: httpx.Response) -> Mapping[str, Any]:
    content_type = response.headers.get("content-type", "")
    if "application/json" not in content_type.lower():
        raise TedTransportError("TED search returned a non-JSON content type")
    try:
        body = response.json()
    except ValueError as exc:
        raise TedTransportError("TED search returned invalid JSON") from exc
    if not isinstance(body, Mapping):
        raise TedContractError("TED search response must be a JSON object")
    unexpected = set(body) - TED_RESPONSE_FIELDS
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise TedContractError(f"TED response returned unexpected fields: {names}")
    if "notices" not in body or "timedOut" not in body:
        raise TedContractError("TED response lacks required envelope fields")
    if not isinstance(body["notices"], list):
        raise TedContractError("TED notices must be a JSON array")
    return body


def collect_ted_notices(
    query: str,
    *,
    client: httpx.Client | None = None,
    page_size: int = TED_DEFAULT_PAGE_SIZE,
    max_pages: int = 100,
    scope: str = "ALL",
) -> TedCollectionResult:
    """Collect a bounded, point-in-time TED result set using ITERATION pagination."""

    contract = require_live_source(TED_SOURCE_ID)
    if not contract.server_side_projection:
        raise TedContractError("TED source contract no longer guarantees server-side projection")
    if not query.strip():
        raise ValueError("query must not be empty")
    _validate_page_size(page_size)
    if max_pages < 1:
        raise ValueError("max_pages must be at least 1")
    if scope not in {"ALL", "ACTIVE", "LATEST"}:
        raise ValueError("unsupported TED scope")

    owns_client = client is None
    http = client or httpx.Client(timeout=30.0, headers={"Accept": "application/json"})
    records: list[dict[str, Any]] = []
    seen_publications: set[str] = set()
    token: str | None = None
    first_total: int | None = None

    try:
        for page_number in range(1, max_pages + 1):
            payload: dict[str, Any] = {
                "query": query,
                "fields": list(TED_PROJECTED_FIELDS),
                "limit": page_size,
                "scope": scope,
                "checkQuerySyntax": False,
                "paginationMode": "ITERATION",
            }
            if token is not None:
                payload["iterationNextToken"] = token

            try:
                response = http.post(TED_SEARCH_URL, json=payload)
                response.raise_for_status()
            except httpx.HTTPError as exc:
                raise TedTransportError("TED search HTTP request failed") from exc

            body = _parse_envelope(response)
            if body["timedOut"] is not False:
                return TedCollectionResult(
                    records=tuple(records),
                    total_notice_count=first_total,
                    pages_fetched=page_number,
                    complete=False,
                    stop_reason="timed_out",
                )

            total = body.get("totalNoticeCount")
            if first_total is None and total is not None:
                if not isinstance(total, int) or isinstance(total, bool) or total < 0:
                    raise TedContractError("TED totalNoticeCount must be a non-negative integer")
                first_total = total

            notices = body["notices"]
            if not notices:
                complete = first_total is None or len(records) == first_total
                return TedCollectionResult(
                    records=tuple(records),
                    total_notice_count=first_total,
                    pages_fetched=page_number,
                    complete=complete,
                    stop_reason="complete" if complete else "count_mismatch",
                )

            page_records = [canonicalize_ted_notice(notice) for notice in notices]
            for record in page_records:
                notice_id = str(record["notice_id"])
                if notice_id in seen_publications:
                    raise TedContractError(f"duplicate TED publication-number: {notice_id}")
                seen_publications.add(notice_id)
            records.extend(page_records)

            output_token = body.get("iterationNextToken")
            if not isinstance(output_token, str) or not output_token:
                return TedCollectionResult(
                    records=tuple(records),
                    total_notice_count=first_total,
                    pages_fetched=page_number,
                    complete=False,
                    stop_reason="missing_iteration_token",
                )
            token = output_token

        return TedCollectionResult(
            records=tuple(records),
            total_notice_count=first_total,
            pages_fetched=max_pages,
            complete=False,
            stop_reason="max_pages",
        )
    finally:
        if owns_client:
            http.close()
