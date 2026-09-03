"""Live Phase 0B qualification for structured supplier demand inside TED notices.

No raw title/description/notice payload is logged or persisted. The script uses only the frozen safe
TED projection and the existing deterministic component taxonomy.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

import httpx

from procrun.component_engine import RULES
from procrun.source_contracts import require_live_source

TED_URL = "https://api.ted.europa.eu/v3/notices/search"
SOURCE_ID = "ted_search_api"
AUDIT_START = "20250903"
PAGE_SIZE = 250
MAX_PAGES = 8
TARGET_SAMPLE = 300
MIN_SAMPLE = 200

SAFE_FIELDS = (
    "publication-number",
    "publication-date",
    "notice-type",
    "notice-title",
    "description-proc",
    "classification-cpv",
)
ALLOWED_ENVELOPE_KEYS = frozenset(
    {"notices", "totalNoticeCount", "iterationNextToken", "timedOut"}
)
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
COUNTRY_QUERIES = ("buyer-country = PRT", "buyer-country=PRT", "CY = PRT")
DATE_QUERIES = (
    f"publication-date >= {AUDIT_START}",
    f"publication-date = (>={AUDIT_START})",
    f"PD >= {AUDIT_START}",
    f"PD = (>={AUDIT_START})",
)


class GateError(RuntimeError):
    pass


def _flatten(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
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


def _validate_notice(notice: Any) -> Mapping[str, Any]:
    if not isinstance(notice, Mapping):
        raise GateError("TED returned a non-object notice")
    allowed = frozenset(SAFE_FIELDS) | {"links"}
    extra = set(notice) - allowed
    if extra:
        raise GateError("TED returned fields outside allowlist: " + ", ".join(sorted(extra)))
    return notice


def _post(
    client: httpx.Client,
    query: str,
    *,
    fields: Sequence[str],
    limit: int,
    mode: str,
    page: int | None = None,
    token: str | None = None,
) -> Mapping[str, Any]:
    payload: dict[str, Any] = {
        "query": query,
        "fields": list(fields),
        "limit": limit,
        "scope": "ALL",
        "checkQuerySyntax": False,
        "paginationMode": mode,
    }
    if mode == "PAGE_NUMBER":
        payload["page"] = page or 1
    elif token:
        payload["iterationNextToken"] = token
    response = client.post(TED_URL, json=payload)
    response.raise_for_status()
    body = response.json()
    if not isinstance(body, Mapping):
        raise GateError("TED returned non-object envelope")
    extra = set(body) - ALLOWED_ENVELOPE_KEYS
    if extra:
        raise GateError("TED returned unexpected envelope fields: " + ", ".join(sorted(extra)))
    if body.get("timedOut") not in (False, None):
        raise GateError("TED query timed out")
    notices = body.get("notices")
    if not isinstance(notices, list):
        raise GateError("TED notices is not an array")
    for notice in notices:
        _validate_notice(notice)
    return body


def _probe(client: httpx.Client, query: str) -> bool:
    body = _post(
        client,
        query,
        fields=("publication-number",),
        limit=1,
        mode="PAGE_NUMBER",
        page=1,
    )
    return bool(body["notices"])


def _resolve(client: httpx.Client, candidates: Sequence[str], label: str) -> str:
    for candidate in candidates:
        try:
            if _probe(client, candidate):
                print(f"PHASE0B_QUERY {label}=PASS")
                return candidate
        except (httpx.HTTPError, GateError):
            continue
    raise GateError(f"could not resolve {label} query")


def _is_infra(notice: Mapping[str, Any]) -> bool:
    return any(
        code.startswith(INFRA_CPV_PREFIXES)
        for code in _flatten(notice.get("classification-cpv"))
    )


def _is_later(notice: Mapping[str, Any]) -> bool:
    return _first(notice.get("notice-type")) in LATER_TYPES


def _contains(text: str, phrase: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text, flags=re.IGNORECASE) is not None


def _matched_rules(title: str, description: str) -> tuple[tuple[Any, bool, bool], ...]:
    matches: list[tuple[Any, bool, bool]] = []
    for rule in RULES:
        in_title = any(_contains(title, phrase) for phrase in rule.phrases)
        in_description = any(_contains(description, phrase) for phrase in rule.phrases)
        if in_title or in_description:
            matches.append((rule, in_title, in_description))
    return tuple(matches)


def _pct(n: int, d: int) -> float:
    return 0.0 if d == 0 else round(100.0 * n / d, 1)


def main() -> int:
    contract = require_live_source(SOURCE_ID)
    if not contract.server_side_projection:
        raise GateError("TED source contract lost server-side projection")

    selected: list[Mapping[str, Any]] = []
    with httpx.Client(
        timeout=60.0,
        headers={"Accept": "application/json", "User-Agent": "ProcRun-phase0b/1.0"},
    ) as client:
        country = _resolve(client, COUNTRY_QUERIES, "country")
        date = _resolve(client, DATE_QUERIES, "date")
        query = f"{country} AND {date}"
        if not _probe(client, query):
            raise GateError("combined Portugal/date query is empty")

        token: str | None = None
        for _page in range(MAX_PAGES):
            body = _post(
                client,
                query,
                fields=SAFE_FIELDS,
                limit=PAGE_SIZE,
                mode="ITERATION",
                token=token,
            )
            notices = body["notices"]
            if not notices:
                break
            for raw in notices:
                notice = _validate_notice(raw)
                if _is_infra(notice) and _is_later(notice):
                    selected.append(notice)
                    if len(selected) >= TARGET_SAMPLE:
                        break
            if len(selected) >= TARGET_SAMPLE:
                break
            next_token = body.get("iterationNextToken")
            if not isinstance(next_token, str) or not next_token:
                break
            token = next_token

    sample = selected[:TARGET_SAMPLE]
    if len(sample) < MIN_SAMPLE:
        print(f"PHASE0B_METRIC sample_size={len(sample)}")
        print("PHASE0B_RESULT=FAIL reason=insufficient_sample")
        return 1

    any_requirement = 0
    multi_requirement = 0
    description_only_value = 0
    cpv_blind_value = 0
    categories: set[tuple[str, str]] = set()
    domains: set[str] = set()

    for notice in sample:
        title = " ".join(_flatten(notice.get("notice-title")))
        description = " ".join(_flatten(notice.get("description-proc")))
        cpvs = _flatten(notice.get("classification-cpv"))
        matches = _matched_rules(title, description)
        unique = {(str(rule.domain), rule.category) for rule, _it, _id in matches}
        if unique:
            any_requirement += 1
            categories.update(unique)
            domains.update(domain for domain, _category in unique)
        if len(unique) >= 2:
            multi_requirement += 1
        if any(in_description and not in_title for _rule, in_title, in_description in matches):
            description_only_value += 1
        blind = False
        for rule, _in_title, _in_description in matches:
            if not rule.cpv_prefixes:
                continue
            if not any(code.startswith(rule.cpv_prefixes) for code in cpvs):
                blind = True
                break
        if blind:
            cpv_blind_value += 1

    metrics: dict[str, int | float] = {
        "sample_size": len(sample),
        "any_requirement_pct": _pct(any_requirement, len(sample)),
        "multi_requirement_pct": _pct(multi_requirement, len(sample)),
        "description_only_value_pct": _pct(description_only_value, len(sample)),
        "cpv_blind_value_pct": _pct(cpv_blind_value, len(sample)),
        "distinct_categories": len(categories),
        "domains_represented": len(domains),
    }
    for name, value in metrics.items():
        print(f"PHASE0B_METRIC {name}={value}")

    gates = {
        "sample": len(sample) >= 200,
        "any_requirement": float(metrics["any_requirement_pct"]) >= 20.0,
        "description_only_value": float(metrics["description_only_value_pct"]) >= 10.0,
        "cpv_blind_value": float(metrics["cpv_blind_value_pct"]) >= 5.0,
        "category_breadth": int(metrics["distinct_categories"]) >= 8,
        "domain_breadth": int(metrics["domains_represented"]) >= 3,
    }
    for name, passed in gates.items():
        print(f"PHASE0B_GATE {name}={'PASS' if passed else 'FAIL'}")

    passed = all(gates.values())
    print(f"PHASE0B_RESULT={'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
