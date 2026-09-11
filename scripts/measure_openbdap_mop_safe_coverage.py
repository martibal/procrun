#!/usr/bin/env python3
"""Measure national OpenBDAP MOP coverage using a frozen safe OData projection.

Only public project identifiers and non-identity project attributes are received:
CUP, CUP status, intervention sector and effective works cost. Raw rows are never
persisted; only aggregate counters are written to stdout.
"""
from __future__ import annotations

import json
from collections import Counter
from decimal import Decimal, InvalidOperation
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
STATUS_DESC: Final = "Ccdescrizione_s1176782119"
SECTOR: Final = "Ccsettore_inter1475973826"
COST_EFFECTIVE: Final = "Cccosto_lavori_e582037416"
SAFE_FIELDS: Final = (CUP, STATUS_CODE, STATUS_DESC, SECTOR, COST_EFFECTIVE)
ALLOWED_RETURNED_KEYS: Final = set(SAFE_FIELDS) | {"row_id"}
PAGE_SIZE: Final = 50_000
MAX_ROWS: Final = 700_000
MAX_RESPONSE_BYTES: Final = 40_000_000


def _extract_rows(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        raise RuntimeError("OpenBDAP OData JSON root is not an object")
    data = payload.get("d")
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise RuntimeError("OpenBDAP OData response has no d.results list")
    rows = data["results"]
    if not all(isinstance(row, dict) for row in rows):
        raise RuntimeError("OpenBDAP OData returned a non-object row")
    return rows


def _data_keys(row: dict[str, Any]) -> set[str]:
    return {key for key in row if key not in {"__metadata", "@odata.id", "@odata.etag"}}


def _norm(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    text = " ".join(value.split()).strip()
    return text or None


def _amount(value: object) -> Decimal | None:
    if value is None:
        return None
    text = str(value).strip().replace(" ", "")
    if not text:
        return None
    # OData values are normally dot-decimal; tolerate Italian thousands/decimal formatting.
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def main() -> int:
    parsed = urlparse(BASE_URL)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise RuntimeError("OpenBDAP endpoint left the frozen origin")

    status_codes: Counter[str] = Counter()
    status_labels: Counter[str] = Counter()
    sectors: Counter[str] = Counter()
    total_rows = 0
    unique_cups: set[str] = set()
    rows_with_sector = 0
    rows_with_cost = 0
    effective_cost_total = Decimal("0")
    pages = 0

    headers = {
        "User-Agent": "ProcRun-OpenBDAP-MOP-Safe-Coverage/1.0",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=120.0, follow_redirects=False, headers=headers) as client:
        skip = 0
        while skip < MAX_ROWS:
            response = client.get(
                BASE_URL,
                params={
                    "$select": ",".join(SAFE_FIELDS),
                    "$skip": str(skip),
                    "$top": str(PAGE_SIZE),
                    "$format": "json",
                },
            )
            if response.is_redirect:
                raise RuntimeError("OpenBDAP coverage request redirected")
            response.raise_for_status()
            if len(response.content) > MAX_RESPONSE_BYTES:
                raise RuntimeError("OpenBDAP coverage response exceeded safety bound")
            rows = _extract_rows(response.json())
            pages += 1

            for row in rows:
                keys = _data_keys(row)
                unexpected = keys - ALLOWED_RETURNED_KEYS
                if unexpected:
                    raise RuntimeError(
                        "safe projection escaped allowlist: " + ", ".join(sorted(unexpected))
                    )
                cup = _norm(row.get(CUP))
                if cup:
                    unique_cups.add(cup)
                status_code = _norm(row.get(STATUS_CODE))
                if status_code:
                    status_codes[status_code] += 1
                status_label = _norm(row.get(STATUS_DESC))
                if status_label:
                    status_labels[status_label] += 1
                sector = _norm(row.get(SECTOR))
                if sector:
                    rows_with_sector += 1
                    sectors[sector] += 1
                amount = _amount(row.get(COST_EFFECTIVE))
                if amount is not None:
                    rows_with_cost += 1
                    effective_cost_total += amount

            total_rows += len(rows)
            if len(rows) < PAGE_SIZE:
                break
            skip += PAGE_SIZE
        else:
            raise RuntimeError("MOP scan hit MAX_ROWS safety ceiling")

    report = {
        "measurement_contract": "openbdap-mop-safe-national-coverage-v1",
        "resource_id": RESOURCE_ID,
        "projection_fields": list(SAFE_FIELDS),
        "identity_fields_received": False,
        "raw_rows_persisted": False,
        "pages": pages,
        "rows": total_rows,
        "unique_cups": len(unique_cups),
        "rows_with_sector": rows_with_sector,
        "sector_coverage_pct": round(rows_with_sector * 100 / total_rows, 4) if total_rows else 0,
        "rows_with_effective_cost": rows_with_cost,
        "effective_cost_coverage_pct": round(rows_with_cost * 100 / total_rows, 4) if total_rows else 0,
        "effective_cost_total_eur": str(effective_cost_total),
        "status_codes": dict(status_codes.most_common()),
        "status_labels": dict(status_labels.most_common()),
        "top_sectors": dict(sectors.most_common(25)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
