"""Single self-diagnosing live qualification of TED as a ProcRun production foundation.

The run first proves working TED query semantics with aggregate-only control probes, then executes
one complete Portugal 12-month qualification using only the frozen non-person field projection.
No raw response bodies, titles, descriptions, buyer values or person fields are logged or persisted.
Frozen product thresholds are not changed based on observed results.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import httpx

from procrun.source_contracts import require_live_source

TED_URL = "https://api.ted.europa.eu/v3/notices/search"
SOURCE_ID = "ted_search_api"
AUDIT_START = "20250903"
PAGE_SIZE = 250
MAX_PAGES = 200

SAFE_FIELDS = (
    "publication-number",
    "publication-date",
    "notice-type",
    "procedure-identifier",
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
ALLOWED_NOTICE_KEYS = frozenset(SAFE_FIELDS) | {"links"}
ALLOWED_ENVELOPE_KEYS = frozenset(
    {"notices", "totalNoticeCount", "iterationNextToken", "timedOut"}
)

EARLY_TYPES = frozenset({"pin-buyer", "pin-only", "pin-rtl", "pin-tran", "pmc"})
LATER_TYPES = frozenset(
    {
        "pin-cfc-standard",
        "pin-cfc-social",
        "cn-standard",
        "cn-social",
        "cn-desg",
        "can-standard",
        "can-social",
        "can-desg",
        "can-tran",
        "compl",
    }
)
INFRA_CPV_PREFIXES = ("31", "34", "42", "44", "45", "90")

# Candidate spellings are resolved inside this single run. This is transport diagnosis only;
# the product gates below remain frozen and are never weakened to manufacture PASS.
COUNTRY_QUERIES = (
    "buyer-country = PRT",
    "buyer-country = (PRT)",
)
DATE_QUERIES = (
    f"publication-date = (>={AUDIT_START})",
    f"publication-date >= {AUDIT_START}",
)


class QualificationError(RuntimeError):
    """Raised when the live source violates the qualification contract."""


@dataclass(frozen=True)
class SliceResult:
    records: tuple[Mapping[str, Any], ...]
    pages: int


def _flatten(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, Mapping):
        out: list[str] = []
        for item in value.values():
            out.extend(_flatten(item))
        return out
    if isinstance(value, Sequence) and not isinstance(value, bytes | bytearray):
        out = []
        for item in value:
            out.extend(_flatten(item))
        return out
    return [str(value)]


def _first(value: Any) -> str | None:
    values = _flatten(value)
    return values[0] if values else None


def _has_text(value: Any) -> bool:
    return any(bool(item.strip()) for item in _flatten(value))


def _validate_notice(notice: Any) -> Mapping[str, Any]:
    if not isinstance(notice, Mapping):
        raise QualificationError("TED returned a non-object notice")
    extra = set(notice) - ALLOWED_NOTICE_KEYS
    if extra:
        raise QualificationError(
            "TED returned fields outside the pre-receipt allowlist: " + ", ".join(sorted(extra))
        )
    return notice


def _post_page(
    client: httpx.Client,
    query: str,
    *,
    limit: int,
    token: str | None = None,
) -> Mapping[str, Any]:
    payload: dict[str, Any] = {
        "query": query,
        "fields": list(SAFE_FIELDS),
        "limit": limit,
        "scope": "ALL",
        "checkQuerySyntax": True,
        "paginationMode": "ITERATION",
    }
    if token is not None:
        payload["iterationNextToken"] = token

    response = client.post(TED_URL, json=payload)
    response.raise_for_status()
    if "application/json" not in response.headers.get("content-type", "").lower():
        raise QualificationError("TED returned a non-JSON response")
    body = response.json()
    if not isinstance(body, Mapping):
        raise QualificationError("TED returned a non-object envelope")
    extra = set(body) - ALLOWED_ENVELOPE_KEYS
    if extra:
        raise QualificationError(
            "TED returned unexpected envelope fields: " + ", ".join(sorted(extra))
        )
    if body.get("timedOut") is not False:
        raise QualificationError("TED query timed out")
    notices = body.get("notices")
    if not isinstance(notices, list):
        raise QualificationError("TED notices is not an array")
    for notice in notices:
        _validate_notice(notice)
    return body


def _probe_query(client: httpx.Client, query: str) -> bool:
    """Return only whether a query yields at least one projected notice."""
    try:
        body = _post_page(client, query, limit=1)
    except (httpx.HTTPError, QualificationError):
        return False
    notices = body.get("notices")
    return isinstance(notices, list) and bool(notices)


def _resolve_query(client: httpx.Client) -> str:
    country_results = [(_query, _probe_query(client, _query)) for _query in COUNTRY_QUERIES]
    date_results = [(_query, _probe_query(client, _query)) for _query in DATE_QUERIES]

    print(
        "TED_QUERY_DIAGNOSTIC country_control="
        + ("PASS" if any(ok for _, ok in country_results) else "FAIL")
    )
    print(
        "TED_QUERY_DIAGNOSTIC date_control="
        + ("PASS" if any(ok for _, ok in date_results) else "FAIL")
    )

    for country_query, country_ok in country_results:
        if not country_ok:
            continue
        for date_query, date_ok in date_results:
            if not date_ok:
                continue
            combined = f"{country_query} AND {date_query}"
            if _probe_query(client, combined):
                print("TED_QUERY_DIAGNOSTIC combined_control=PASS")
                return combined

    print("TED_QUERY_DIAGNOSTIC combined_control=FAIL")
    raise QualificationError(
        "TED query semantics could not be resolved to a non-empty Portugal 12-month result"
    )


def _fetch_slice(client: httpx.Client, query: str) -> SliceResult:
    token: str | None = None
    records: list[Mapping[str, Any]] = []
    seen_publication_numbers: set[str] = set()

    for page in range(1, MAX_PAGES + 1):
        body = _post_page(client, query, limit=PAGE_SIZE, token=token)
        notices = body["notices"]

        if not notices:
            return SliceResult(tuple(records), page)

        for item in notices:
            notice = _validate_notice(item)
            publication_number = _first(notice.get("publication-number"))
            if publication_number:
                if publication_number in seen_publication_numbers:
                    raise QualificationError("TED returned duplicate publication-number")
                seen_publication_numbers.add(publication_number)
            records.append(notice)

        next_token = body.get("iterationNextToken")
        if not isinstance(next_token, str) or not next_token:
            raise QualificationError("TED iteration token missing before completion")
        token = next_token

    raise QualificationError("TED qualification exceeded MAX_PAGES")


def _is_infra(record: Mapping[str, Any]) -> bool:
    codes = _flatten(record.get("classification-cpv"))
    return any(code.startswith(INFRA_CPV_PREFIXES) for code in codes)


def _pct(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else 100.0 * numerator / denominator


def main() -> int:
    contract = require_live_source(SOURCE_ID)
    if not contract.server_side_projection:
        raise QualificationError("TED source contract lost server-side projection")

    with httpx.Client(timeout=45.0, headers={"Accept": "application/json"}) as client:
        base_query = _resolve_query(client)
        portugal = _fetch_slice(client, base_query)

    records = portugal.records
    infra = tuple(record for record in records if _is_infra(record))
    early = tuple(
        record for record in infra if _first(record.get("notice-type")) in EARLY_TYPES
    )
    later = tuple(
        record for record in infra if _first(record.get("notice-type")) in LATER_TYPES
    )

    rich_scope = sum(
        1
        for record in early
        if _has_text(record.get("notice-title")) and _has_text(record.get("description-proc"))
    )
    procedure_ids = sum(1 for record in early if _has_text(record.get("procedure-identifier")))
    eu_funded = sum(
        1
        for record in infra
        if _has_text(record.get("eu-funds-identifier"))
        or _has_text(record.get("eu-funds-financing-id-lot"))
    )

    phases_by_procedure: dict[str, set[str]] = defaultdict(set)
    for record in infra:
        procedure_id = _first(record.get("procedure-identifier"))
        notice_type = _first(record.get("notice-type"))
        if procedure_id and notice_type:
            phases_by_procedure[procedure_id].add(notice_type)
    linked_lifecycles = sum(
        1
        for types in phases_by_procedure.values()
        if types.intersection(EARLY_TYPES) and types.intersection(LATER_TYPES)
    )

    metrics = {
        "portugal_notices_12m": len(records),
        "infra_notices_12m": len(infra),
        "early_infra_notices_12m": len(early),
        "later_infra_notices_12m": len(later),
        "early_rich_scope_pct": round(_pct(rich_scope, len(early)), 1),
        "early_procedure_id_pct": round(_pct(procedure_ids, len(early)), 1),
        "infra_eu_funding_marker_pct": round(_pct(eu_funded, len(infra)), 1),
        "linked_early_to_later_procedures": linked_lifecycles,
        "pages_fetched": portugal.pages,
    }
    for name, value in metrics.items():
        print(f"TED_QUALIFICATION {name}={value}")

    gates = {
        "national_volume": len(records) >= 200,
        "infrastructure_volume": len(infra) >= 50,
        "early_signal_volume": len(early) >= 5,
        "scope_richness": _pct(rich_scope, len(early)) >= 70.0,
        "procedure_linkability": _pct(procedure_ids, len(early)) >= 70.0,
        "observed_lifecycle_link": linked_lifecycles >= 1,
    }
    for name, passed in gates.items():
        print(f"TED_GATE {name}={'PASS' if passed else 'FAIL'}")

    if not all(gates.values()):
        failed = ", ".join(name for name, passed in gates.items() if not passed)
        print("PRODUCTION_FOUNDATION=FAIL")
        raise QualificationError(f"TED production foundation failed: {failed}")

    print("PRODUCTION_FOUNDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
