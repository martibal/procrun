"""Metadata-only qualification probe for Regione Lombardia Socrata.

The dataset supports server-side field projection, but the free-text project description
field does not currently have a public pre-receipt zero-PII guarantee. Under the frozen
A21a ingress contract ProcRun therefore must not request any project row from this source.
This module may inspect public dataset metadata only and always fails closed for row ingest.
"""

from __future__ import annotations

import json
import sys
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

DATASET_ID = "q78n-g3m9"
APPROVED_HOST = "www.dati.lombardia.it"
METADATA_URL = f"https://{APPROVED_HOST}/api/views/{DATASET_ID}"
USER_AGENT = "ProcRun-A21a-Lombardia-Socrata-Metadata/2.0"

SAFE_METADATA_FIELDS = (
    "operazione_finanziata",
    "cup",
    "codice_operazione",
    "descrizione_operazione",
)

FORBIDDEN_ROW_FIELDS = (
    "nome_del_beneficiario",
    "codice_del_beneficiario",
)

BLOCK_REASON = (
    "Regione Lombardia Socrata row ingest is blocked: descrizione_operazione has no "
    "dataset-specific public pre-receipt zero-PII guarantee. Metadata inspection is allowed; "
    "project-row receipt is prohibited."
)


def _fetch_json(url: str, *, max_bytes: int = 2_000_000) -> Any:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != APPROVED_HOST:
        raise RuntimeError(f"refused non-approved Socrata origin: {url}")
    if url != METADATA_URL:
        raise RuntimeError("Socrata probe is metadata-only; row/resource URLs are prohibited")
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
        raise RuntimeError("Socrata metadata response exceeds safety bound")
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
    missing_project_fields = sorted(set(SAFE_METADATA_FIELDS) - set(fields))
    missing_identity_fields = sorted(set(FORBIDDEN_ROW_FIELDS) - set(fields))

    description_meta = fields.get("descrizione_operazione", {})
    description_text = str(description_meta.get("description", "")).casefold()
    description_field_confirmed = "descrizione del progetto" in description_text

    beneficiary_meta = fields.get("nome_del_beneficiario", {})
    beneficiary_description = str(beneficiary_meta.get("description", "")).casefold()
    natural_person_identity_risk_confirmed = "persona fisica" in beneficiary_description

    metadata_complete = (
        not missing_project_fields
        and not missing_identity_fields
        and description_field_confirmed
        and natural_person_identity_risk_confirmed
    )
    return {
        "metadata_complete": metadata_complete,
        "missing_project_fields": missing_project_fields,
        "missing_identity_fields": missing_identity_fields,
        "description_field_confirmed": description_field_confirmed,
        "natural_person_identity_risk_confirmed": natural_person_identity_risk_confirmed,
        "documented_column_count": len(fields),
        "row_ingest_allowed": False,
        "block_reason": BLOCK_REASON,
    }


def projected_row_url() -> str:
    """Fail closed so callers cannot construct a row-bearing URL from this probe."""

    raise RuntimeError(BLOCK_REASON)


def validate_projected_rows(rows: Any) -> dict[str, Any]:
    """Reject any row-bearing payload; receiving it is already outside the contract."""

    del rows
    return {
        "projection_gate_pass": False,
        "row_ingest_allowed": False,
        "candidate_status": "BLOCKED_FREE_TEXT_ZERO_PII_CONTRACT",
        "block_reason": BLOCK_REASON,
    }


def probe() -> dict[str, Any]:
    metadata = _fetch_json(METADATA_URL)
    if not isinstance(metadata, dict):
        raise RuntimeError("unexpected Socrata metadata response shape")
    metadata_report = validate_metadata(metadata)
    return {
        "probe_version": "a21a-lombardia-socrata-metadata-v2",
        "dataset_id": DATASET_ID,
        "metadata_requested": True,
        "projected_row_requested": False,
        "full_row_requested": False,
        "candidate_status": "BLOCKED_FREE_TEXT_ZERO_PII_CONTRACT",
        **metadata_report,
    }


def main() -> int:
    report = probe()
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 1


if __name__ == "__main__":
    sys.exit(main())
