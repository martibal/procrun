#!/usr/bin/env python3
"""Qualify a zero-free-text TED route for prospective MOP linkage."""
from __future__ import annotations

import json
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final
from urllib.parse import urlparse

import httpx

from procrun.source_contracts import require_live_source

TED_URL: Final = "https://api.ted.europa.eu/v3/notices/search"
ALLOWED_HOST: Final = "api.ted.europa.eu"
SOURCE_ID: Final = "ted_search_api"
REPORT_PATH = Path("artifacts/ted-mop-safe-linkage-qualification.json")

SAFE_FIELDS: Final = (
    "publication-number",
    "publication-date",
    "notice-type",
    "classification-cpv",
    "estimated-value-proc",
    "estimated-value-cur-proc",
)
ALLOWED_ENVELOPE_KEYS: Final = frozenset(
    {"notices", "totalNoticeCount", "iterationNextToken", "timedOut"}
)
ALLOWED_NOTICE_KEYS: Final = frozenset(SAFE_FIELDS) | {"links"}
QUERY_TEMPLATES: Final = (
    'internal-identifier-proc = "{cup}"',
    "internal-identifier-proc = {cup}",
)
CONTROL_QUERY: Final = "publication-date >= 20260901"
SAMPLE_CUPS: Final = (
    "B11B21006090001",
    "B13D10000830006",
    "B14H17001380001",
    "B17E18000060006",
    "B17H21006070001",
    "B17H22000530001",
    "B17H23001580001",
    "B19J21004500005",
    "B19J21004510005",
    "B21F18000250001",
    "B23D21008000001",
    "B24B13000160001",
    "B24H21000060005",
    "B27H23001590001",
    "B29J21004770002",
    "B29J21004780002",
    "B29J21004790002",
    "B31B20004010001",
    "B31B20004020001",
    "B31B21007990001",
)
MAX_RETURNED_NOTICES_PER_CUP: Final = 10
MAX_TOTAL_MATCHES_PER_CUP: Final = 50
REQUEST_DELAY_SECONDS: Final = 0.12


class QualificationError(RuntimeError):
    """Raised when the frozen TED safe-linkage contract is violated."""


def _validate_links(value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, Mapping):
        raise QualificationError("TED links is not an object")
    for item in value.values():
        if isinstance(item, str) and not item.startswith("https://"):
            raise QualificationError("TED links contained a non-HTTPS URL")


def _validate_body(body: Any) -> Mapping[str, Any]:
    if not isinstance(body, Mapping):
        raise QualificationError("TED response envelope is not an object")
    unexpected = set(body) - ALLOWED_ENVELOPE_KEYS
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise QualificationError(f"TED envelope escaped allowlist: {names}")
    notices = body.get("notices")
    if not isinstance(notices, list):
        raise QualificationError("TED response has no notices array")
    if body.get("timedOut") is not False:
        raise QualificationError("TED query timed out")
    for notice in notices:
        if not isinstance(notice, Mapping):
            raise QualificationError("TED returned a non-object notice")
        extra = set(notice) - ALLOWED_NOTICE_KEYS
        if extra:
            names = ", ".join(sorted(extra))
            raise QualificationError(f"TED notice escaped allowlist: {names}")
        _validate_links(notice.get("links"))
    return body


def _search(
    client: httpx.Client,
    query: str,
    *,
    fields: tuple[str, ...],
    limit: int,
) -> Mapping[str, Any]:
    payload = {
        "query": query,
        "fields": list(fields),
        "limit": limit,
        "page": 1,
        "scope": "ALL",
        "checkQuerySyntax": False,
        "paginationMode": "PAGE_NUMBER",
    }
    response = client.post(TED_URL, json=payload)
    response.raise_for_status()
    content_type = response.headers.get("content-type", "").lower()
    if "application/json" not in content_type:
        raise QualificationError("TED response is not JSON")
    body = _validate_body(response.json())
    time.sleep(REQUEST_DELAY_SECONDS)
    return body


def _total_count(body: Mapping[str, Any]) -> int:
    value = body.get("totalNoticeCount")
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise QualificationError("TED totalNoticeCount is not a non-negative integer")
    return value


def _resolve_query_template(client: httpx.Client) -> tuple[str, int]:
    first_cup = SAMPLE_CUPS[0]
    attempts = 0
    for template in QUERY_TEMPLATES:
        attempts += 1
        query = template.format(cup=first_cup)
        try:
            _search(client, query, fields=("publication-number",), limit=1)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 400:
                continue
            raise
        return template, attempts
    raise QualificationError("No frozen internal-identifier-proc query syntax was accepted")


def _verify_projection(client: httpx.Client) -> dict[str, bool]:
    support: dict[str, bool] = {}
    for field in SAFE_FIELDS:
        body = _search(
            client,
            CONTROL_QUERY,
            fields=("publication-number", field),
            limit=1,
        )
        support[field] = bool(body.get("notices"))
    return support


def main() -> int:
    parsed = urlparse(TED_URL)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise QualificationError("TED endpoint left the frozen origin")

    contract = require_live_source(SOURCE_ID)
    if not contract.server_side_projection:
        raise QualificationError("TED source contract lost server-side projection")

    headers = {
        "Accept": "application/json",
        "User-Agent": "ProcRun-TED-MOP-Safe-Linkage/1.0",
    }
    timeout = httpx.Timeout(30.0, connect=15.0)
    with httpx.Client(timeout=timeout, headers=headers) as client:
        query_template, syntax_attempts = _resolve_query_template(client)
        field_support = _verify_projection(client)
        unsupported = [name for name, supported in field_support.items() if not supported]
        if unsupported:
            raise QualificationError(
                "TED safe projection field support failed: " + ", ".join(unsupported)
            )

        sample_with_hits = 0
        total_matches = 0
        max_matches = 0
        returned_notice_objects = 0
        for cup in SAMPLE_CUPS:
            body = _search(
                client,
                query_template.format(cup=cup),
                fields=SAFE_FIELDS,
                limit=MAX_RETURNED_NOTICES_PER_CUP,
            )
            count = _total_count(body)
            if count > MAX_TOTAL_MATCHES_PER_CUP:
                raise QualificationError("TED CUP query returned implausibly broad result set")
            notices = body["notices"]
            returned_notice_objects += len(notices)
            total_matches += count
            max_matches = max(max_matches, count)
            if count > 0:
                sample_with_hits += 1

    route_evidenced = sample_with_hits > 0
    report = {
        "measurement_contract": "ted-mop-safe-linkage-qualification-v1",
        "source_id": SOURCE_ID,
        "endpoint": TED_URL,
        "query_field": "internal-identifier-proc",
        "query_template_selected": query_template,
        "query_syntax_attempts": syntax_attempts,
        "projection_fields": list(SAFE_FIELDS),
        "field_support": field_support,
        "sample_rule": "first 20 lexicographically sorted CUPs from frozen 12m cohort",
        "sample_size": len(SAMPLE_CUPS),
        "sample_cups_with_hits": sample_with_hits,
        "sample_total_notice_matches": total_matches,
        "sample_max_notice_matches_per_cup": max_matches,
        "returned_notice_objects": returned_notice_objects,
        "route_evidenced": route_evidenced,
        "identity_fields_received": False,
        "free_text_received": False,
        "internal_identifier_values_received": False,
        "raw_notices_persisted": False,
        "outcome_rows_persisted": False,
        "decision": "PASS" if route_evidenced else "BLOCKED_NO_STRUCTURED_CUP_EVIDENCE",
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True), flush=True)
    if not route_evidenced:
        raise QualificationError(
            "TED structured CUP linkage was not evidenced in the frozen qualification sample"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
