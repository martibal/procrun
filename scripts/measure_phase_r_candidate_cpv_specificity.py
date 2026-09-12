#!/usr/bin/env python3
"""Measure Phase R candidate CPV specificity using count-only TED Search API queries.

The diagnostic requests only ``publication-number`` and records aggregate ``totalNoticeCount``
values. It does not persist notice rows, titles, descriptions, buyers, contacts, locations, values,
links, or other row-level data.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Final

import httpx

from procrun.collectors.ted import TED_SEARCH_URL, TED_SOURCE_ID
from procrun.source_contracts import require_live_source

START_DATE: Final = date(2021, 1, 1)
CUTOFF_DATE: Final = date(2026, 9, 12)
REPORT_PATH: Final = Path("artifacts/phase-r-candidate-cpv-specificity.json")
FIELD_PROJECTION: Final = ("publication-number",)


@dataclass(frozen=True)
class CountQuery:
    key: str
    query: str


def _date_clause() -> str:
    return (
        f"buyer-country = ITA AND publication-date >= {START_DATE.isoformat()} "
        f"AND publication-date <= {CUTOFF_DATE.isoformat()}"
    )


def _queries() -> tuple[CountQuery, ...]:
    base = _date_clause()
    return (
        CountQuery("italy_total", base),
        CountQuery("digital_302", f"{base} AND classification-cpv = 302*"),
        CountQuery("digital_48", f"{base} AND classification-cpv = 48*"),
        CountQuery("digital_72", f"{base} AND classification-cpv = 72*"),
        CountQuery(
            "digital_union",
            f"{base} AND (classification-cpv = 302* OR classification-cpv = 48* "
            "OR classification-cpv = 72*)",
        ),
        CountQuery("waste_42914", f"{base} AND classification-cpv = 42914*"),
        CountQuery("waste_452221", f"{base} AND classification-cpv = 452221*"),
        CountQuery("waste_9051", f"{base} AND classification-cpv = 9051*"),
        CountQuery(
            "waste_union",
            f"{base} AND (classification-cpv = 42914* OR classification-cpv = 452221* "
            "OR classification-cpv = 9051*)",
        ),
    )


def _count(http: httpx.Client, item: CountQuery) -> int:
    payload = {
        "query": item.query,
        "fields": list(FIELD_PROJECTION),
        "limit": 1,
        "scope": "ALL",
        "checkQuerySyntax": False,
        "paginationMode": "ITERATION",
    }
    response = http.post(TED_SEARCH_URL, json=payload)
    if response.status_code >= 400:
        error_text = response.text.replace("\n", " ")[:500]
        raise RuntimeError(
            f"TED {item.key} count query failed: HTTP {response.status_code}: {error_text}"
        )
    body = response.json()
    if not isinstance(body, dict):
        raise RuntimeError(f"TED {item.key} response is not an object")
    unexpected_envelope = set(body) - {
        "notices",
        "totalNoticeCount",
        "iterationNextToken",
        "timedOut",
    }
    if unexpected_envelope:
        raise RuntimeError(
            f"TED {item.key} returned unexpected envelope fields: {sorted(unexpected_envelope)}"
        )
    if body.get("timedOut") is not False:
        raise RuntimeError(f"TED {item.key} query timed out")
    total = body.get("totalNoticeCount")
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        raise RuntimeError(f"TED {item.key} totalNoticeCount is invalid")
    notices = body.get("notices")
    if not isinstance(notices, list):
        raise RuntimeError(f"TED {item.key} notices is not a list")
    for notice in notices:
        if not isinstance(notice, dict):
            raise RuntimeError(f"TED {item.key} notice is not an object")
        unexpected_fields = set(notice) - set(FIELD_PROJECTION)
        if unexpected_fields:
            raise RuntimeError(
                f"TED {item.key} returned non-projected fields: {sorted(unexpected_fields)}"
            )
    return total


def main() -> int:
    contract = require_live_source(TED_SOURCE_ID)
    if not contract.server_side_projection:
        raise RuntimeError("TED source contract no longer guarantees server-side projection")

    counts: dict[str, int] = {}
    with httpx.Client(
        timeout=30.0,
        headers={"Accept": "application/json", "User-Agent": "ProcRun/phase-r-cpv-specificity-v1"},
    ) as http:
        for item in _queries():
            counts[item.key] = _count(http, item)

    italy_total = counts["italy_total"]
    if italy_total <= 0:
        raise RuntimeError("TED Italy total must be positive")

    report = {
        "schema_version": "phase-r-candidate-cpv-specificity-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window": {
            "buyer_country": "ITA",
            "start_date": START_DATE.isoformat(),
            "cutoff_date": CUTOFF_DATE.isoformat(),
        },
        "counts": counts,
        "shares_of_italy_pct": {
            key: round(value / italy_total * 100, 4)
            for key, value in counts.items()
            if key != "italy_total"
        },
        "boundary": {
            "server_side_projection_required": True,
            "requested_fields": list(FIELD_PROJECTION),
            "rows_persisted": False,
            "titles_requested": False,
            "descriptions_requested": False,
            "buyers_requested": False,
            "contacts_requested": False,
            "locations_requested": False,
            "values_requested": False,
            "production_mapping_changed": False,
            "open_closed_semantics_changed": False,
        },
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
