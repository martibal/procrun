"""Field-projected TED Search API collector.

The production collector intentionally uses a strict subset of the field projection that was
qualified live. Fields that were not part of that frozen qualification are not requested merely
because TED can return them.
"""

import time
from collections.abc import Mapping, Sequence
from contextlib import suppress
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
TED_MAX_THROTTLE_RETRIES = 5
TED_THROTTLE_BACKOFF_SECONDS = 2.0

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
    "eu-funds-identifier",
    "links",
)

TED_RESPONSE_FIELDS = frozenset(
    {
        "notices",
        "totalNoticeCount",
        "iterationNextToken",
        "timedOut",
    }
)


class TedError(RuntimeError):
    """Base TED collector failure."""


class TedContractError(TedError):
    """TED response no longer matches the frozen production contract."""


class TedTransportError(TedError):
    """TED transport failed before a complete response could be validated."""


@dataclass(frozen=True)
class TedCollectionResult:
    records: tuple[dict[str, Any], ...]
    total_notice_count: int | None
    pages_fetched: int
    complete: bool
    stop_reason: str


def _validate_page_size(page_size: int) -> None:
    if page_size < 1 or page_size > TED_MAX_PAGE_SIZE:
        raise ValueError(f"page_size must be between 1 and {TED_MAX_PAGE_SIZE}")
    if page_size * len(TED_PROJECTED_FIELDS) > TED_FIELD_CELL_LIMIT:
        raise ValueError("page_size exceeds TED projected-field cell limit")


def _first_text(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if isinstance(value, Mapping):
        for language in ("eng", "por", "ita"):
            candidate = value.get(language)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
        for candidate in value.values():
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for item in value:
            candidate = _first_text(item)
            if candidate:
                return candidate
    return None


def _first_scalar(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for item in value:
            if isinstance(item, str) and item.strip():
                return item.strip()
    return None


def _string_tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return tuple(str(item).strip() for item in value if str(item).strip())
    return ()


def _whole_eur(value: Any, currency: Any) -> int | None:
    if value in (None, "") or str(currency).upper() != "EUR":
        return None
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    if not amount.is_finite() or amount < 0 or amount != amount.to_integral_value():
        return None
    return int(amount)


def _source_url(value: Any, notice_id: str) -> str:
    if isinstance(value, Mapping):
        for key in ("html", "xml", "pdf"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.startswith("https://"):
                return candidate
    return f"https://ted.europa.eu/en/notice/-/detail/{notice_id}"


def canonicalize_ted_notice(notice: Mapping[str, Any]) -> dict[str, Any]:
    unexpected = set(notice) - set(TED_PROJECTED_FIELDS)
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise TedContractError(f"TED notice returned non-projected fields: {names}")

    notice_id = _first_scalar(notice.get("publication-number"))
    publication_date = _first_scalar(notice.get("publication-date"))
    title = _first_text(notice.get("notice-title"))
    if not notice_id or not publication_date or not title:
        raise TedContractError("TED notice lacks required projected identity/date/title")

    estimated_value_eur = _whole_eur(
        notice.get("estimated-value-proc"), notice.get("estimated-value-cur-proc")
    )
    nuts_codes = _string_tuple(notice.get("place-of-performance-subdiv-proc"))
    references = _string_tuple(notice.get("eu-funds-identifier"))

    return {
        "notice_id": notice_id,
        "publication_date": publication_date,
        "award_date": None,
        "contract_date": None,
        "title": title,
        "scope_description": _first_text(notice.get("description-proc")),
        "cpv_codes": _string_tuple(notice.get("classification-cpv")),
        "contract_nature": _first_scalar(notice.get("contract-nature")),
        "procedure_type": _first_scalar(notice.get("procedure-type")),
        "procedure_value_eur": estimated_value_eur,
        "estimated_value_eur": estimated_value_eur,
        "base_value_eur": None,
        "awarded_value_eur": None,
        "place_of_performance": None,
        "nuts_code": nuts_codes[0] if nuts_codes else None,
        "municipality": None,
        "project_reference": references[0] if references else None,
        "source_url": _source_url(notice.get("links"), notice_id),
    }


def _parse_envelope(response: httpx.Response) -> dict[str, Any]:
    content_type = response.headers.get("content-type", "").lower()
    if "application/json" not in content_type:
        raise TedContractError("TED response is not JSON")
    try:
        body = response.json()
    except ValueError as exc:
        raise TedContractError("TED response body is invalid JSON") from exc
    if not isinstance(body, dict):
        raise TedContractError("TED response envelope must be an object")
    unexpected = set(body) - TED_RESPONSE_FIELDS
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise TedContractError(f"TED response returned unexpected fields: {names}")
    if "notices" not in body or "timedOut" not in body:
        raise TedContractError("TED response lacks required envelope fields")
    if not isinstance(body["notices"], list):
        raise TedContractError("TED notices must be a JSON array")
    return body


def _post_with_throttle_retry(
    http: httpx.Client,
    payload: dict[str, Any],
    *,
    sleep: Any = time.sleep,
) -> httpx.Response:
    """Retry only explicit TED throttling; all other transport failures remain immediate/fail-closed."""
    for retry in range(TED_MAX_THROTTLE_RETRIES + 1):
        try:
            response = http.post(TED_SEARCH_URL, json=payload)
        except httpx.HTTPError as exc:
            raise TedTransportError("TED search HTTP request failed") from exc
        if response.status_code != 429:
            try:
                response.raise_for_status()
            except httpx.HTTPError as exc:
                raise TedTransportError("TED search HTTP request failed") from exc
            return response
        if retry == TED_MAX_THROTTLE_RETRIES:
            raise TedTransportError("TED search remained throttled after bounded retries")
        retry_after = response.headers.get("retry-after")
        delay = TED_THROTTLE_BACKOFF_SECONDS * (2**retry)
        if retry_after is not None:
            with suppress(ValueError):
                delay = max(delay, float(retry_after))
        sleep(delay)
    raise AssertionError("unreachable")


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

            response = _post_with_throttle_retry(http, payload)

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

            for raw_notice in notices:
                if not isinstance(raw_notice, Mapping):
                    raise TedContractError("TED notice must be an object")
                canonical = canonicalize_ted_notice(raw_notice)
                publication_key = f"{canonical['notice_id']}|{canonical['publication_date']}"
                if publication_key in seen_publications:
                    continue
                seen_publications.add(publication_key)
                records.append(canonical)

            next_token = body.get("iterationNextToken")
            if not isinstance(next_token, str) or not next_token:
                complete = first_total is None or len(records) == first_total
                return TedCollectionResult(
                    records=tuple(records),
                    total_notice_count=first_total,
                    pages_fetched=page_number,
                    complete=complete,
                    stop_reason="complete" if complete else "missing_iteration_token",
                )
            token = next_token

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
