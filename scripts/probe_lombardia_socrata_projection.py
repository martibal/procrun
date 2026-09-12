#!/usr/bin/env python3
"""One-row server-side projection control for Regione Lombardia Socrata dataset q78n-g3m9.

This probe is authorized only after the metadata-only Stage 1 gate passed. It requests exactly one row
and only the frozen safe allowlist through Socrata $select. Any unexpected key is a hard failure.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request

DATASET_ID = "q78n-g3m9"
RESOURCE_URL = f"https://www.dati.lombardia.it/resource/{DATASET_ID}.json"
SAFE_FIELDS = (
    "cup",
    "priorita",
    "obiettivo_specifico",
    "azione",
    "codice_bando",
    "codice_operazione",
    "codice_tipologia_intervento",
    "descrizione_tipologia",
)
SAFE_FIELD_SET = set(SAFE_FIELDS)
HEADERS = {
    "User-Agent": "ProcRun/phase-r-lombardia-socrata-projection-v1",
    "Accept": "application/json",
}


def main() -> int:
    params = {
        "$select": ",".join(SAFE_FIELDS),
        "$limit": "1",
    }
    url = RESOURCE_URL + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers=HEADERS)

    with urllib.request.urlopen(request, timeout=30) as response:
        status = response.status
        payload = json.load(response)

    if not isinstance(payload, list):
        raise RuntimeError("unexpected non-list Socrata projection response")
    if len(payload) > 1:
        raise RuntimeError("projection control returned more than one row")

    response_keys: set[str] = set()
    row: dict[str, object] | None = None
    if payload:
        item = payload[0]
        if not isinstance(item, dict):
            raise RuntimeError("unexpected non-object Socrata projection row")
        row = item
        response_keys = set(item)

    unexpected = sorted(response_keys - SAFE_FIELD_SET)
    if unexpected:
        raise RuntimeError(f"unexpected fields received from Socrata projection: {unexpected}")

    required_observed = bool(row and "cup" in row and len(response_keys - {"cup"}) >= 1)
    stage2_pass = status == 200 and len(payload) <= 1 and not unexpected and required_observed

    report = {
        "probe_contract": "lombardia-socrata-projection-control-v1",
        "dataset_id": DATASET_ID,
        "http_status": status,
        "requested_select": list(SAFE_FIELDS),
        "requested_limit": 1,
        "rows_received": len(payload),
        "response_keys": sorted(response_keys),
        "unexpected_keys": unexpected,
        "stage2_result": "PASS_PROJECTION" if stage2_pass else "BLOCKED_PROJECTION_GATE",
        "row": row,
        "boundary": {
            "server_side_select_used": True,
            "select_star_used": False,
            "beneficiary_fields_requested": False,
            "project_narrative_requested": False,
            "address_fields_requested": False,
            "rows_requested_max": 1,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if stage2_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
