#!/usr/bin/env python3
"""Freeze the first prospective OpenBDAP MOP cohort without identity-bearing data."""
from __future__ import annotations

import hashlib
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
MAX_PAGES: Final = 25
MAX_RESPONSE_BYTES: Final = 4_000_000
OBSERVED_DATE: Final = date(2026, 8, 31)
END_12M: Final = date(2027, 8, 31)
VALID_FLOOR: Final = "2000-01-01"
VALID_CEILING: Final = "2100-12-31"
SENTINEL: Final = "9999-12-31"
EXPECTED_FILTERED_ROWS: Final = 35852
EXPECTED_UNIQUE_CUPS: Final = 34988
EXPECTED_CONFLICTING_DATE_CUPS: Final = 339
EXPECTED_COHORT_CUPS: Final = 1356
OUT_DIR = Path("artifacts/openbdap-mop-prospective-2026-08-31")
COHORT_PATH = OUT_DIR / "cohort.jsonl"
MANIFEST_PATH = OUT_DIR / "manifest.json"


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


def _canonical_json_line(cup: str, planned: date) -> str:
    return json.dumps(
        {"cup": cup, "planned_execution_start": planned.isoformat()},
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def main() -> int:
    parsed = urlparse(BASE_URL)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise RuntimeError("OpenBDAP endpoint left the frozen origin")

    headers = {
        "User-Agent": "ProcRun-OpenBDAP-MOP-Prospective-Freeze/1.0",
        "Accept": "application/json",
    }
    timeout = httpx.Timeout(30.0, connect=15.0)
    earliest_by_cup: dict[str, date] = {}
    latest_by_cup: dict[str, date] = {}
    rows_received = 0
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
                raise RuntimeError("OpenBDAP prospective freeze request redirected")
            response.raise_for_status()
            if len(response.content) > MAX_RESPONSE_BYTES:
                raise RuntimeError("OpenBDAP prospective freeze page exceeded safety bound")
            rows = _extract_rows(response.json())
            if len(rows) > PAGE_SIZE:
                raise RuntimeError("OpenBDAP returned more rows than requested")
            if not rows:
                break

            for row in rows:
                unexpected = _data_keys(row) - SAFE_FIELDS
                if unexpected:
                    raise RuntimeError(
                        "OpenBDAP prospective projection escaped allowlist: "
                        + ", ".join(sorted(unexpected))
                    )
                cup_value = row.get(CUP)
                if not isinstance(cup_value, str) or not cup_value.strip():
                    raise RuntimeError("OpenBDAP prospective row has no CUP")
                cup = cup_value.strip().upper()
                planned = _parse_date(row.get(PLANNED_EXECUTION_START))
                rows_received += 1
                if cup in earliest_by_cup:
                    earliest_by_cup[cup] = min(earliest_by_cup[cup], planned)
                    latest_by_cup[cup] = max(latest_by_cup[cup], planned)
                else:
                    earliest_by_cup[cup] = planned
                    latest_by_cup[cup] = planned

            if len(rows) < PAGE_SIZE:
                break
        else:
            raise RuntimeError("OpenBDAP prospective freeze hit frozen page ceiling")

    conflicting = sum(
        1 for cup, earliest in earliest_by_cup.items() if latest_by_cup[cup] != earliest
    )
    cohort = sorted(
        (cup, planned)
        for cup, planned in earliest_by_cup.items()
        if OBSERVED_DATE <= planned <= END_12M
    )

    if rows_received != EXPECTED_FILTERED_ROWS:
        raise RuntimeError("OpenBDAP filtered row count drift before prospective freeze")
    if len(earliest_by_cup) != EXPECTED_UNIQUE_CUPS:
        raise RuntimeError("OpenBDAP unique CUP count drift before prospective freeze")
    if conflicting != EXPECTED_CONFLICTING_DATE_CUPS:
        raise RuntimeError("OpenBDAP conflicting-date CUP count drift before prospective freeze")
    if len(cohort) != EXPECTED_COHORT_CUPS:
        raise RuntimeError("OpenBDAP 12m cohort count drift before prospective freeze")

    lines = [_canonical_json_line(cup, planned) for cup, planned in cohort]
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    cohort_sha256 = hashlib.sha256(payload).hexdigest()

    protocol = {
        "canonical_planned_start_rule": "earliest valid planned execution start per CUP",
        "cohort_end": END_12M.isoformat(),
        "cohort_start": OBSERVED_DATE.isoformat(),
        "deduplication_key": "CUP",
        "eligibility": "status A + no actual execution start + valid planned execution start",
        "outcome_definition": (
            "future TED-observed procurement materialization; "
            "absence is not proof of no procurement"
        ),
        "projection_fields": [CUP, PLANNED_EXECUTION_START],
        "source_observed_date": OBSERVED_DATE.isoformat(),
    }
    protocol_bytes = json.dumps(
        protocol, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    protocol_sha256 = hashlib.sha256(protocol_bytes).hexdigest()

    manifest = {
        "cohort_count": len(cohort),
        "cohort_file": COHORT_PATH.name,
        "cohort_sha256": cohort_sha256,
        "conflicting_date_cups_in_parent_population": conflicting,
        "free_text_received": False,
        "identity_fields_received": False,
        "measurement_contract": "openbdap-mop-prospective-freeze-v1",
        "protocol": protocol,
        "protocol_sha256": protocol_sha256,
        "raw_rows_persisted": False,
        "request_count": request_count,
        "resource_id": RESOURCE_ID,
        "source_filtered_rows": rows_received,
        "source_unique_cups": len(earliest_by_cup),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    COHORT_PATH.write_bytes(payload)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
