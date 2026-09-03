"""One-shot, data-first TED capability inventory for ProcRun product discovery.

This is the final live foundation test. It executes real TED searches (syntax checking is not used
as a data request), proves a minimal field-bounded transport, resolves a working Portugal/date
query inside the same run, verifies the complete retained projection, inventories the last 12
months, and evaluates independent product hypotheses. Only approved non-person fields are
requested. No raw responses, titles, descriptions, buyer values or notice payloads are logged or
persisted.
"""

from __future__ import annotations

from collections import Counter, defaultdict
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

MINIMAL_FIELDS = ("publication-number",)
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

# Alternative documented/observed spellings are resolved within this one run. These are transport
# alternatives, not product-threshold changes.
COUNTRY_QUERIES = (
    "buyer-country = PRT",
    "buyer-country=PRT",
    "CY = PRT",
)
DATE_QUERIES = (
    f"publication-date >= {AUDIT_START}",
    f"publication-date = (>={AUDIT_START})",
    f"PD >= {AUDIT_START}",
    f"PD = (>={AUDIT_START})",
)


class QualificationError(RuntimeError):
    """Raised when the live source violates the capability-inventory contract."""


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
        out: list[str] = []
        for item in value:
            out.extend(_flatten(item))
        return out
    return [str(value)]


def _first(value: Any) -> str | None:
    values = _flatten(value)
    return values[0] if values else None


def _has_text(value: Any) -> bool:
    return any(bool(item.strip()) for item in _flatten(value))


def _pct(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else 100.0 * numerator / denominator


def _validate_notice(notice: Any, requested_fields: Sequence[str]) -> Mapping[str, Any]:
    if not isinstance(notice, Mapping):
        raise QualificationError("TED returned a non-object notice")
    allowed = frozenset(requested_fields) | {"links"}
    extra = set(notice) - allowed
    if extra:
        raise QualificationError(
            "TED returned fields outside the pre-receipt allowlist: " + ", ".join(sorted(extra))
        )
    return notice


def _post_page(
    client: httpx.Client,
    query: str,
    *,
    fields: Sequence[str],
    limit: int,
    mode: str = "PAGE_NUMBER",
    page: int | None = 1,
    token: str | None = None,
) -> Mapping[str, Any]:
    payload: dict[str, Any] = {
        "query": query,
        "fields": list(fields),
        "limit": limit,
        "scope": "ALL",
        # Important: true is syntax-check mode and is not used for data retrieval.
        "checkQuerySyntax": False,
        "paginationMode": mode,
    }
    if mode == "PAGE_NUMBER":
        payload["page"] = page or 1
    elif token is not None:
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
    if body.get("timedOut") not in (False, None):
        raise QualificationError("TED query timed out")
    notices = body.get("notices")
    if not isinstance(notices, list):
        raise QualificationError("TED notices is not an array")
    for notice in notices:
        _validate_notice(notice, fields)
    return body


def _probe_query(client: httpx.Client, query: str) -> bool:
    """Execute a real first-page search using only publication-number."""
    body = _post_page(
        client,
        query,
        fields=MINIMAL_FIELDS,
        limit=1,
        mode="PAGE_NUMBER",
        page=1,
    )
    notices = body.get("notices")
    return isinstance(notices, list) and bool(notices)


def _first_working_query(client: httpx.Client, candidates: Sequence[str], label: str) -> str:
    failures: list[str] = []
    for query in candidates:
        try:
            if _probe_query(client, query):
                print(f"TED_QUERY_DIAGNOSTIC {label}=PASS")
                return query
            failures.append("EMPTY")
        except httpx.HTTPStatusError as exc:
            failures.append(f"HTTP_{exc.response.status_code}")
        except (httpx.HTTPError, QualificationError):
            failures.append("TRANSPORT_OR_SCHEMA")
    print(f"TED_QUERY_DIAGNOSTIC {label}=FAIL attempts={','.join(failures)}")
    raise QualificationError(f"TED {label} query could not be resolved")


def _verify_field(client: httpx.Client, query: str, field: str) -> bool:
    """Prove a retained field can be projected without receiving unrequested fields."""
    fields = tuple(dict.fromkeys(("publication-number", field)))
    try:
        _post_page(
            client,
            query,
            fields=fields,
            limit=1,
            mode="PAGE_NUMBER",
            page=1,
        )
    except (httpx.HTTPError, QualificationError):
        return False
    return True


def _fetch_slice(client: httpx.Client, query: str) -> SliceResult:
    token: str | None = None
    records: list[Mapping[str, Any]] = []
    seen_publication_numbers: set[str] = set()

    for page_number in range(1, MAX_PAGES + 1):
        body = _post_page(
            client,
            query,
            fields=SAFE_FIELDS,
            limit=PAGE_SIZE,
            mode="ITERATION",
            page=None,
            token=token,
        )
        notices = body["notices"]
        if not notices:
            return SliceResult(tuple(records), page_number)

        for item in notices:
            notice = _validate_notice(item, SAFE_FIELDS)
            publication_number = _first(notice.get("publication-number"))
            if publication_number:
                if publication_number in seen_publication_numbers:
                    raise QualificationError("TED returned duplicate publication-number")
                seen_publication_numbers.add(publication_number)
            records.append(notice)

        next_token = body.get("iterationNextToken")
        if not isinstance(next_token, str) or not next_token:
            # Some APIs terminate the final non-empty page without another cursor. Accept only a
            # short page as an unambiguous completion condition; a full page without a token is
            # fail-closed because records could otherwise be silently truncated.
            if len(notices) < PAGE_SIZE:
                return SliceResult(tuple(records), page_number)
            raise QualificationError("TED iteration token missing before completion")
        token = next_token

    raise QualificationError("TED capability inventory exceeded MAX_PAGES")


def _is_infra(record: Mapping[str, Any]) -> bool:
    codes = _flatten(record.get("classification-cpv"))
    return any(code.startswith(INFRA_CPV_PREFIXES) for code in codes)


def _population(records: Sequence[Mapping[str, Any]], field: str) -> float:
    return _pct(sum(1 for record in records if _has_text(record.get(field))), len(records))


def main() -> int:
    contract = require_live_source(SOURCE_ID)
    if not contract.server_side_projection:
        raise QualificationError("TED source contract lost server-side projection")

    with httpx.Client(
        timeout=60.0,
        headers={"Accept": "application/json", "User-Agent": "ProcRun-foundation-audit/1.0"},
    ) as client:
        # 1. Resolve a real, non-empty Portugal query using a minimal field projection. This proves
        # endpoint execution, query semantics and server-side field bounding together.
        country_query = _first_working_query(client, COUNTRY_QUERIES, "country_control")
        print("TED_TRANSPORT endpoint_execution=PASS")
        print("TED_TRANSPORT minimal_projection=PASS")

        # 2. Resolve date syntax independently, then prove the combined 12-month population.
        date_query = _first_working_query(client, DATE_QUERIES, "date_control")
        combined_query = f"{country_query} AND {date_query}"
        if not _probe_query(client, combined_query):
            raise QualificationError("TED Portugal/date combination returned no notices")
        print("TED_QUERY_DIAGNOSTIC combined_control=PASS")

        # 3. Verify the complete retained projection one field at a time against the same proven
        # population before bulk receipt.
        field_support = {
            field: _verify_field(client, combined_query, field) for field in SAFE_FIELDS
        }
        for field, supported in field_support.items():
            print(f"TED_FIELD_SUPPORT {field}={'PASS' if supported else 'FAIL'}")
        unsupported = [field for field, supported in field_support.items() if not supported]
        if unsupported:
            raise QualificationError(
                "TED safe projection contains unsupported fields: " + ", ".join(unsupported)
            )

        # 4. Inventory the actual current Portugal universe using only the proven safe projection.
        portugal = _fetch_slice(client, combined_query)

    records = portugal.records
    if not records:
        raise QualificationError("TED Portugal 12-month inventory unexpectedly empty")

    infra = tuple(record for record in records if _is_infra(record))
    early = tuple(record for record in infra if _first(record.get("notice-type")) in EARLY_TYPES)
    later = tuple(record for record in infra if _first(record.get("notice-type")) in LATER_TYPES)

    notice_type_counts = Counter(
        notice_type
        for record in records
        if (notice_type := _first(record.get("notice-type"))) is not None
    )

    rich_early = sum(
        1
        for record in early
        if _has_text(record.get("notice-title")) and _has_text(record.get("description-proc"))
    )
    rich_later = sum(
        1
        for record in later
        if _has_text(record.get("notice-title")) and _has_text(record.get("description-proc"))
    )
    early_with_procedure = sum(
        1 for record in early if _has_text(record.get("procedure-identifier"))
    )
    infra_with_funding = sum(
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

    metrics: dict[str, int | float] = {
        "portugal_notices_12m": len(records),
        "infra_notices_12m": len(infra),
        "early_infra_notices_12m": len(early),
        "later_infra_notices_12m": len(later),
        "early_rich_scope_pct": round(_pct(rich_early, len(early)), 1),
        "later_rich_scope_pct": round(_pct(rich_later, len(later)), 1),
        "early_procedure_id_pct": round(_pct(early_with_procedure, len(early)), 1),
        "infra_eu_funding_marker_pct": round(_pct(infra_with_funding, len(infra)), 1),
        "linked_early_to_later_procedures": linked_lifecycles,
        "distinct_notice_types": len(notice_type_counts),
        "pages_fetched": portugal.pages,
    }
    for name, value in metrics.items():
        print(f"TED_CAPABILITY {name}={value}")

    for notice_type, count in sorted(notice_type_counts.items()):
        print(f"TED_NOTICE_TYPE type={notice_type} count={count}")

    for field in SAFE_FIELDS:
        print(f"TED_FIELD_POPULATION field={field} pct={round(_population(records, field), 1)}")

    # These hypotheses are independent. A failed hypothesis does not invalidate the dataset.
    hypotheses = {
        "early_procurement_runway": (
            len(early) >= 5
            and _pct(rich_early, len(early)) >= 70.0
            and _pct(early_with_procedure, len(early)) >= 70.0
            and linked_lifecycles >= 1
        ),
        "active_infrastructure_feed": (
            len(later) >= 50 and _pct(rich_later, len(later)) >= 70.0
        ),
        "procurement_market_intelligence": len(infra) >= 200,
        "eu_funding_subset": len(infra) >= 50 and _pct(infra_with_funding, len(infra)) >= 10.0,
    }
    for name, viable in hypotheses.items():
        print(f"TED_PRODUCT_HYPOTHESIS {name}={'SUPPORTED' if viable else 'NOT_SUPPORTED'}")

    supported = [name for name, viable in hypotheses.items() if viable]
    if not supported:
        print("PRODUCT_FOUNDATION=NO_SUPPORTED_HYPOTHESIS")
        raise QualificationError(
            "TED inventory supports none of the predeclared product hypotheses"
        )

    # Prefer the earliest/highest-information product if the empirical evidence supports it; fall
    # back deterministically rather than bending thresholds after seeing results.
    priority = (
        "early_procurement_runway",
        "active_infrastructure_feed",
        "procurement_market_intelligence",
        "eu_funding_subset",
    )
    selected = next(name for name in priority if hypotheses[name])
    print(f"PRODUCT_FOUNDATION=PASS selected={selected}")
    print("TED_CAPABILITY_INVENTORY=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
