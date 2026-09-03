"""Disjoint confirmation of supplier-facing requirement normalization beyond TED CPV codes."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

import httpx

from procrun.component_engine import RULES
from procrun.source_contracts import require_live_source

TED_URL = "https://api.ted.europa.eu/v3/notices/search"
SOURCE_ID = "ted_search_api"
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
    "publication-date >= 20240903 AND publication-date <= 20250902",
    "PD >= 20240903 AND PD <= 20250902",
    "PD = (>=20240903 AND <=20250902)",
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


def _validate_notice(notice: Any, fields: Sequence[str]) -> Mapping[str, Any]:
    if not isinstance(notice, Mapping):
        raise GateError("TED returned non-object notice")
    allowed = frozenset(fields) | {"links"}
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
        raise GateError("unexpected TED envelope fields: " + ", ".join(sorted(extra)))
    if body.get("timedOut") not in (False, None):
        raise GateError("TED query timed out")
    notices = body.get("notices")
    if not isinstance(notices, list):
        raise GateError("TED notices is not array")
    for notice in notices:
        _validate_notice(notice, fields)
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
                print(f"PHASE0C_QUERY {label}=PASS")
                return candidate
        except (httpx.HTTPError, GateError):
            continue
    raise GateError(f"could not resolve {label} query")


def _contains(text: str, phrase: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text, flags=re.IGNORECASE) is not None


def _pct(n: int, d: int) -> float:
    return 0.0 if d == 0 else round(100.0 * n / d, 1)


def main() -> int:
    contract = require_live_source(SOURCE_ID)
    if not contract.server_side_projection:
        raise GateError("TED projection contract missing")

    sample: list[Mapping[str, Any]] = []
    with httpx.Client(
        timeout=60.0,
        headers={"Accept": "application/json", "User-Agent": "ProcRun-phase0c/1.0"},
    ) as client:
        country = _resolve(client, COUNTRY_QUERIES, "country")
        period = _resolve(client, DATE_QUERIES, "period")
        query = f"{country} AND {period}"
        if not _probe(client, query):
            raise GateError("combined historical Portugal query empty")

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
                notice = _validate_notice(raw, SAFE_FIELDS)
                cpvs = _flatten(notice.get("classification-cpv"))
                notice_type = _first(notice.get("notice-type"))
                if (
                    any(code.startswith(INFRA_CPV_PREFIXES) for code in cpvs)
                    and notice_type in LATER_TYPES
                ):
                    sample.append(notice)
                    if len(sample) >= TARGET_SAMPLE:
                        break
            if len(sample) >= TARGET_SAMPLE:
                break
            next_token = body.get("iterationNextToken")
            if not isinstance(next_token, str) or not next_token:
                break
            token = next_token

    sample = sample[:TARGET_SAMPLE]
    if len(sample) < MIN_SAMPLE:
        print(f"PHASE0C_METRIC sample_size={len(sample)}")
        print("PHASE0C_RESULT=FAIL reason=insufficient_sample")
        return 1

    any_requirement = 0
    multi_requirement = 0
    description_only = 0
    cpv_blind = 0
    categories: set[tuple[str, str]] = set()
    domains: set[str] = set()

    for notice in sample:
        title = " ".join(_flatten(notice.get("notice-title")))
        description = " ".join(_flatten(notice.get("description-proc")))
        cpvs = _flatten(notice.get("classification-cpv"))
        matches: list[tuple[Any, bool, bool]] = []
        for rule in RULES:
            in_title = any(_contains(title, phrase) for phrase in rule.phrases)
            in_description = any(_contains(description, phrase) for phrase in rule.phrases)
            if in_title or in_description:
                matches.append((rule, in_title, in_description))
        unique = {(str(rule.domain), rule.category) for rule, _it, _id in matches}
        if unique:
            any_requirement += 1
            categories.update(unique)
            domains.update(domain for domain, _category in unique)
        if len(unique) >= 2:
            multi_requirement += 1
        if any(in_description and not in_title for _rule, in_title, in_description in matches):
            description_only += 1
        if any(
            rule.cpv_prefixes
            and not any(code.startswith(rule.cpv_prefixes) for code in cpvs)
            for rule, _in_title, _in_description in matches
        ):
            cpv_blind += 1

    metrics: dict[str, int | float] = {
        "sample_size": len(sample),
        "any_requirement_pct": _pct(any_requirement, len(sample)),
        "multi_requirement_pct": _pct(multi_requirement, len(sample)),
        "description_only_value_pct": _pct(description_only, len(sample)),
        "cpv_blind_value_pct": _pct(cpv_blind, len(sample)),
        "distinct_categories": len(categories),
        "domains_represented": len(domains),
    }
    for name, value in metrics.items():
        print(f"PHASE0C_METRIC {name}={value}")

    gates = {
        "sample": len(sample) >= 200,
        "requirement_coverage": float(metrics["any_requirement_pct"]) >= 20.0,
        "cpv_blind_value": float(metrics["cpv_blind_value_pct"]) >= 12.0,
        "category_breadth": int(metrics["distinct_categories"]) >= 15,
        "domain_breadth": int(metrics["domains_represented"]) == 5,
    }
    for name, passed in gates.items():
        print(f"PHASE0C_GATE {name}={'PASS' if passed else 'FAIL'}")
    passed = all(gates.values())
    print(f"PHASE0C_RESULT={'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
