"""Prove a zero-PII, source-only A21a projection on Regione Lombardia Socrata.

The probe first inspects public dataset metadata. Only after the metadata proves the exact
safe field contract does it request one row through an explicit server-side SELECT projection.
No beneficiary, contact, address, tax-id or other identity-bearing field is requested.
The row values themselves are never printed; only structural diagnostics are emitted.
"""

from __future__ import annotations

import json
import sys
from typing import Any
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

DATASET_ID = "q78n-g3m9"
APPROVED_HOST = "www.dati.lombardia.it"
METADATA_URL = f"https://{APPROVED_HOST}/api/views/{DATASET_ID}"
RESOURCE_URL = f"https://{APPROVED_HOST}/resource/{DATASET_ID}.json"
USER_AGENT = "ProcRun-A21a-Lombardia-Socrata-Projection/1.0"

SAFE_FIELDS = (
    "nome_del_fondo",
    "priorita",
    "obiettivo_specifico",
    "azione",
    "nome_del_bando",
    "codice_bando",
    "operazione_finanziata",
    "cup",
    "codice_operazione",
    "descrizione_operazione",
    "data_inizio_operazione",
    "data_fine_operazione",
)

FORBIDDEN_FIELDS = (
    "nome_del_beneficiario",
    "codice_del_beneficiario",
)


def _fetch_json(url: str, *, max_bytes: int = 2_000_000) -> Any:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != APPROVED_HOST:
        raise RuntimeError(f"refused non-approved Socrata origin: {url}")
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=60) as response:  # noqa: S310 - frozen HTTPS origin above
        final = urlparse(response.geturl())
        if final.scheme != "https" or final.hostname != APPROVED_HOST:
            raise RuntimeError(f"unexpected redirect outside approved origin: {response.geturl()}")
        payload = response.read(max_bytes + 1)
    if len(payload) > max_bytes:
        raise RuntimeError("Socrata response exceeds safety bound")
    return json.loads(payload.decode("utf-8"))


def _field_map(metadata: dict[str, Any]) -> dict[str, dict[str, Any]]:
    columns = metadata.get("columns")
    if not isinstance(columns, list):
        raise RuntimeError("Socrata metadata missing columns list")
    result: dict[str, dict[str, Any]] = {}
    for column in columns:
        if not isinstance(column, dict):
            raise RuntimeError("unexpected non-object column metadata")
        field_name = column.get("fieldName")
        if isinstance(field_name, str):
            result[field_name] = column
    return result


def validate_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    fields = _field_map(metadata)
    missing_safe = sorted(set(SAFE_FIELDS) - set(fields))
    missing_forbidden = sorted(set(FORBIDDEN_FIELDS) - set(fields))
    description_meta = fields.get("descrizione_operazione", {})
    description_text = str(description_meta.get("description", "")).casefold()
    description_contract_ok = "descrizione del progetto" in description_text

    beneficiary_meta = fields.get("nome_del_beneficiario", {})
    beneficiary_description = str(beneficiary_meta.get("description", "")).casefold()
    beneficiary_identity_confirmed = (
        "persona fisica" in beneficiary_description or "beneficiario" in beneficiary_description
    )

    passed = (
        not missing_safe
        and not missing_forbidden
        and description_contract_ok
        and beneficiary_identity_confirmed
    )
    return {
        "metadata_gate_pass": passed,
        "missing_safe_fields": missing_safe,
        "missing_forbidden_fields": missing_forbidden,
        "description_contract_ok": description_contract_ok,
        "beneficiary_identity_confirmed": beneficiary_identity_confirmed,
        "documented_column_count": len(fields),
    }


def projected_row_url() -> str:
    query = {
        "$select": ",".join(SAFE_FIELDS),
        "$where": "descrizione_operazione is not null",
        "$limit": "1",
    }
    return f"{RESOURCE_URL}?{urlencode(query)}"


def validate_projected_rows(rows: Any) -> dict[str, Any]:
    if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
        return {
            "projection_gate_pass": False,
            "row_count": len(rows) if isinstance(rows, list) else None,
            "unexpected_fields": ["INVALID_RESPONSE_SHAPE"],
            "description_present": False,
        }
    row = rows[0]
    unexpected_fields = sorted(set(row) - set(SAFE_FIELDS))
    forbidden_returned = sorted(set(row) & set(FORBIDDEN_FIELDS))
    description = row.get("descrizione_operazione")
    description_present = isinstance(description, str) and bool(description.strip())
    passed = not unexpected_fields and not forbidden_returned and description_present
    return {
        "projection_gate_pass": passed,
        "row_count": 1,
        "unexpected_fields": unexpected_fields,
        "forbidden_fields_returned": forbidden_returned,
        "description_present": description_present,
        "returned_field_names": sorted(row),
    }


def probe() -> dict[str, Any]:
    metadata = _fetch_json(METADATA_URL)
    if not isinstance(metadata, dict):
        raise RuntimeError("unexpected Socrata metadata response shape")
    metadata_report = validate_metadata(metadata)
    if not metadata_report["metadata_gate_pass"]:
        return {
            "probe_version": "a21a-lombardia-socrata-projection-v1",
            "dataset_id": DATASET_ID,
            "projected_row_requested": False,
            "candidate_status": "BLOCKED_METADATA_CONTRACT",
            **metadata_report,
        }

    rows = _fetch_json(projected_row_url(), max_bytes=200_000)
    projection_report = validate_projected_rows(rows)
    return {
        "probe_version": "a21a-lombardia-socrata-projection-v1",
        "dataset_id": DATASET_ID,
        "projected_row_requested": True,
        "full_row_requested": False,
        "candidate_status": (
            "PROJECTION_GATE_PASS"
            if projection_report["projection_gate_pass"]
            else "BLOCKED_PROJECTION_CONTRACT"
        ),
        **metadata_report,
        **projection_report,
    }


def main() -> int:
    report = probe()
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["candidate_status"] == "PROJECTION_GATE_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
