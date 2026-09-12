#!/usr/bin/env python3
"""Measure the current identity-free OpenBDAP MOP pre-execution runway.

This diagnostic does not read the broad MOP dataset. OpenBDAP performs the lifecycle
filter server-side. The client receives only CUP and planned execution start for
active projects with no actual execution start and a valid planned execution start.
No identity fields or free text are requested or persisted.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Final
from urllib.parse import urlparse

import httpx

RESOURCE_ID: Final = "bda1676b-62ab-44b7-8f9a-ca93b8534488@rgs"
BASE_URL: Final = (
    "https://bdap-opendata.rgs.mef.gov.it/"
    f"ODataProxy/MdData('{RESOURCE_ID}')/DataRows"
)
ALLOWED_HOST: Final = "bdap-opendata.rgs.mef.gov.it"
CUP: Final = "Cccodice_cup_1267962549"
STATUS_CODE: Final = "Cccodice_stato_1426672593"
PLANNED_EXECUTION_START: Final = "Ccinizio_esecuz2103627579"
ACTUAL_EXECUTION_START: Final = "Ccinizio_esecuzi167207395"
SAFE_FIELDS: Final = {CUP, PLANNED_EXECUTION_START, "row_id"}
PAGE_SIZE: Final = 2000
MAX_PAGES: Final = 250
MAX_RESPONSE_BYTES: Final = 4_000_000
OBSERVED_DATE: Final = date(2026, 8, 31)
END_12M: Final = date(2027, 8, 31)
END_24M: Final = date(2028, 8, 31)
VALID_FLOOR: Final = "2000-01-01"
VALID_CEILING: Final = "2100-12-31"
SENTINEL: Final = "9999-12-31"
FROZEN_NATIONAL_TOTAL_ROWS: Final = 561455
FROZEN_NATIONAL_ACTIVE_ROWS: Final = 343828
REPORT_PATH = Path("artifacts/openbdap-mop-runway.json")


def _extract_rows(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        raise RuntimeError("OpenBDAP JSON root is not an object")
    data = payload.get("d")
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise RuntimeError("OpenBDAP response has no d.results list")
    rows = data["results"]
    if not all(isinstance(row, dict) for row in rows):
        raise RuntimeError("OpenBDAP returned a non-object row")
    return rows


def _data_keys(row: dict[str, Any]) -> set[str]:
    metadata = {"__metadata", "@odata.id", "@odata.etag"}
    return {key for key in row if key not in metadata}


def _parse_date(value: object) -> date:
    if not isinstance(value, str):
        raise RuntimeError("OpenBDAP planned execution start is not text")
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise RuntimeError("OpenBDAP returned an invalid planned execution date") from exc


def _filter() -> str:
    missing_actual = (
        f"({ACTUAL_EXECUTION_START} eq '' or "
        f"{ACTUAL_EXECUTION_START} eq '{SENTINEL}')"
    )
    valid_planned = (
        f"({PLANNED_EXECUTION_START} ge '{VALID_FLOOR}' and "
        f"{PLANNED_EXECUTION_START} le '{VALID_CEILING}')"
    )
    return f"{STATUS_CODE} eq 'A' and {missing_actual} and {valid_planned}"


def main() -> int:
    parsed = urlparse(BASE_URL)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise RuntimeError("OpenBDAP endpoint left the frozen origin")

    headers = {
        "User-Agent": "ProcRun-OpenBDAP-MOP-Runway/1.0",
        "Accept": "application/json",
    }
    timeout = httpx.Timeout(30.0, connect=15.0)
    seen_cups: set[str] = set()
    valid_planned_rows = 0
    next_12m = 0
    next_24m = 0
    request_count = 0

    with httpx.Client(timeout=timeout, follow_redirects=False, headers=headers) as client:
        for page in range(MAX_PAGES):
            params = {
                "$select": f"{CUP},{PLANNED_EXECUTION_START}",
                "$filter": _filter(),
                "$skip": str(page * PAGE_SIZE),
                "$top": str(PAGE_SIZE),
                "$format": "json",
            }
            response = client.get(BASE_URL, params=params)
            request_count += 1
            if response.is_redirect:
                raise RuntimeError("OpenBDAP runway request redirected")
            response.raise_for_status()
            if len(response.content) > MAX_RESPONSE_BYTES:
                raise RuntimeError("OpenBDAP runway page exceeded safety bound")
            rows = _extract_rows(response.json())
            if len(rows) > PAGE_SIZE:
                raise RuntimeError("OpenBDAP returned more rows than requested")
            if not rows:
                break

            for row in rows:
                unexpected = _data_keys(row) - SAFE_FIELDS
                if unexpected:
                    raise RuntimeError(
                        "OpenBDAP runway projection escaped allowlist: "
                        + ", ".join(sorted(unexpected))
                    )
                cup = row.get(CUP)
                if not isinstance(cup, str) or not cup.strip():
                    raise RuntimeError("OpenBDAP runway row has no CUP")
                cup = cup.strip().upper()
                if cup in seen_cups:
                    raise RuntimeError("OpenBDAP runway pagination returned duplicate CUP")
                seen_cups.add(cup)

                planned = _parse_date(row.get(PLANNED_EXECUTION_START))
                valid_planned_rows += 1
                if OBSERVED_DATE <= planned <= END_24M:
                    next_24m += 1
                    if planned <= END_12M:
                        next_12m += 1

            if len(rows) < PAGE_SIZE:
                break
        else:
            raise RuntimeError("OpenBDAP runway scan hit frozen page ceiling")

    if not 0 <= next_12m <= next_24m <= valid_planned_rows:
        raise RuntimeError("OpenBDAP runway cohort counts are inconsistent")

    report = {
        "measurement_contract": "openbdap-mop-runway-v1",
        "resource_id": RESOURCE_ID,
        "observed_date": OBSERVED_DATE.isoformat(),
        "end_12m": END_12M.isoformat(),
        "end_24m": END_24M.isoformat(),
        "server_side_filter": "active + no actual execution start + valid planned execution start",
        "projection_fields": [CUP, PLANNED_EXECUTION_START],
        "identity_fields_received": False,
        "free_text_received": False,
        "raw_rows_persisted": False,
        "request_count": request_count,
        "page_size": PAGE_SIZE,
        "frozen_national_total_rows": FROZEN_NATIONAL_TOTAL_ROWS,
        "frozen_national_active_rows": FROZEN_NATIONAL_ACTIVE_ROWS,
        "no_actual_start_with_valid_planned_start": valid_planned_rows,
        "no_actual_start_planned_next_12m": next_12m,
        "no_actual_start_planned_next_24m": next_24m,
        "valid_planned_pct_of_active": round(
            valid_planned_rows * 100 / FROZEN_NATIONAL_ACTIVE_ROWS, 4
        ),
        "next_12m_pct_of_active": round(next_12m * 100 / FROZEN_NATIONAL_ACTIVE_ROWS, 4),
        "next_24m_pct_of_active": round(next_24m * 100 / FROZEN_NATIONAL_ACTIVE_ROWS, 4),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
