#!/usr/bin/env python3
"""Metadata-only qualification probe for Regione Lombardia Socrata dataset q78n-g3m9.

This probe MUST NOT request row endpoints. It reads only public view metadata so ProcRun can establish
whether the dataset exposes the frozen safe classification fields and explicitly forbidden beneficiary
fields before any server-side projection control request is considered.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

DATASET_ID = "q78n-g3m9"
METADATA_URL = f"https://www.dati.lombardia.it/api/views/{DATASET_ID}"
SAFE_FIELDS = {
    "cup",
    "priorita",
    "obiettivo_specifico",
    "azione",
    "codice_bando",
    "codice_operazione",
}
FORBIDDEN_FIELDS = {
    "nome_del_beneficiario",
    "codice_del_beneficiario",
}
HEADERS = {
    "User-Agent": "ProcRun/phase-r-lombardia-socrata-metadata-only-v1",
    "Accept": "application/json",
}


def main() -> int:
    request = urllib.request.Request(METADATA_URL, headers=HEADERS)
    status: int | None = None
    error_name: str | None = None
    payload: dict[str, object] | None = None

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
            loaded = json.load(response)
            if not isinstance(loaded, dict):
                raise RuntimeError("unexpected non-object Socrata metadata payload")
            payload = loaded
    except (urllib.error.HTTPError, urllib.error.URLError) as error:
        status = error.code if isinstance(error, urllib.error.HTTPError) else None
        error_name = type(error).__name__

    field_names: set[str] = set()
    columns: list[dict[str, str | None]] = []
    if payload is not None:
        raw_columns = payload.get("columns", [])
        if not isinstance(raw_columns, list):
            raise RuntimeError("Socrata metadata columns is not a list")
        for column in raw_columns:
            if not isinstance(column, dict):
                raise RuntimeError("unexpected non-object Socrata column metadata")
            field_name = column.get("fieldName")
            if isinstance(field_name, str):
                field_names.add(field_name)
                columns.append(
                    {
                        "field_name": field_name,
                        "name": column.get("name") if isinstance(column.get("name"), str) else None,
                        "data_type": column.get("dataTypeName")
                        if isinstance(column.get("dataTypeName"), str)
                        else None,
                    }
                )

    safe_present = sorted(SAFE_FIELDS & field_names)
    safe_missing = sorted(SAFE_FIELDS - field_names)
    forbidden_present = sorted(FORBIDDEN_FIELDS & field_names)
    metadata_access_ok = payload is not None and status == 200
    stage1_pass = (
        metadata_access_ok
        and not safe_missing
        and FORBIDDEN_FIELDS.issubset(field_names)
    )

    report = {
        "probe_contract": "lombardia-socrata-metadata-only-v1",
        "dataset_id": DATASET_ID,
        "metadata_url": METADATA_URL,
        "http_status": status,
        "error": error_name,
        "metadata_access_ok": metadata_access_ok,
        "stage1_result": "PASS_METADATA" if stage1_pass else "BLOCKED_METADATA_GATE",
        "safe_fields_required": sorted(SAFE_FIELDS),
        "safe_fields_present": safe_present,
        "safe_fields_missing": safe_missing,
        "forbidden_fields_required": sorted(FORBIDDEN_FIELDS),
        "forbidden_fields_present": forbidden_present,
        "columns": columns,
        "boundary": {
            "view_metadata_only": True,
            "row_endpoint_requested": False,
            "project_rows_requested": False,
            "beneficiary_values_requested": False,
            "exports_requested": False,
            "odata_rows_requested": False,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
