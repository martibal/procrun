#!/usr/bin/env python3
"""Fail-closed OData projection probe for OpenBDAP MOP Totale.

The probe first calls the exact MOP Totale OData resource with ``$top=0`` so
no project row is received. It then requests one row with ``$select`` limited
to the public CUP identifier only. Any additional data property fails the run.

This is a transport-safety diagnostic only. It does not approve OpenBDAP MOP
for production use and it never requests the unrestricted dataset.
"""
from __future__ import annotations

import json
from typing import Any, Final
from urllib.parse import urlparse

import httpx

RESOURCE_ID: Final = "bda1676b-62ab-44b7-8f9a-ca93b8534488@rgs"
BASE_URL: Final = (
    "https://bdap-opendata.rgs.mef.gov.it/"
    f"ODataProxy/MdData('{RESOURCE_ID}')/DataRows"
)
ALLOWED_HOST: Final = "bdap-opendata.rgs.mef.gov.it"
# The same MOP schema uses this generated OData property for CUP in the
# published regional example. The probe verifies whether MOP Totale exposes it.
CUP_PROPERTY: Final = "Cccodice_cup_1267962549"
MAX_RESPONSE_BYTES: Final = 250_000


def _request(client: httpx.Client, params: dict[str, str]) -> httpx.Response:
    response = client.get(BASE_URL, params=params)
    if response.is_redirect:
        raise RuntimeError("OpenBDAP OData request redirected")
    if len(response.content) > MAX_RESPONSE_BYTES:
        raise RuntimeError("OpenBDAP OData response exceeded safety bound")
    return response


def _extract_rows(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        raise RuntimeError("OpenBDAP OData JSON root is not an object")
    data = payload.get("d")
    if isinstance(data, dict):
        results = data.get("results")
        if isinstance(results, list):
            if not all(isinstance(row, dict) for row in results):
                raise RuntimeError("OpenBDAP OData returned a non-object row")
            return results
    value = payload.get("value")
    if isinstance(value, list):
        if not all(isinstance(row, dict) for row in value):
            raise RuntimeError("OpenBDAP OData returned a non-object row")
        return value
    raise RuntimeError("OpenBDAP OData response has no recognized row collection")


def _data_keys(row: dict[str, Any]) -> set[str]:
    # OData protocol metadata is not source-row content.
    return {key for key in row if key not in {"__metadata", "@odata.id", "@odata.etag"}}


def main() -> int:
    parsed = urlparse(BASE_URL)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise RuntimeError("OpenBDAP OData endpoint left the frozen origin")

    headers = {
        "User-Agent": "ProcRun-OpenBDAP-MOP-OData-Safety-Probe/1.0",
        "Accept": "application/json",
    }
    report: dict[str, Any] = {
        "probe_contract": "openbdap-mop-odata-projection-v1",
        "resource_id": RESOURCE_ID,
        "unrestricted_rows_requested": False,
        "sensitive_fields_requested": False,
        "top_zero_gate": None,
        "cup_projection_gate": None,
        "candidate_status": "BLOCKED",
    }

    with httpx.Client(timeout=60.0, follow_redirects=False, headers=headers) as client:
        zero = _request(client, {"$top": "0"})
        zero.raise_for_status()
        zero_rows = _extract_rows(zero.json())
        if zero_rows:
            raise RuntimeError("$top=0 unexpectedly returned project rows")
        report["top_zero_gate"] = {
            "status_code": zero.status_code,
            "rows_received": 0,
            "passed": True,
        }

        projected = _request(
            client,
            {
                "$select": CUP_PROPERTY,
                "$top": "1",
            },
        )
        if projected.status_code >= 400:
            report["cup_projection_gate"] = {
                "status_code": projected.status_code,
                "passed": False,
                "reason": "published regional CUP property is not accepted on MOP Totale",
            }
            print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
            return 0

        rows = _extract_rows(projected.json())
        if len(rows) != 1:
            raise RuntimeError(f"expected exactly one projected row, got {len(rows)}")
        keys = _data_keys(rows[0])
        allowed = {CUP_PROPERTY, "row_id"}
        unexpected = keys - allowed
        if unexpected:
            raise RuntimeError(
                "OData $select projection escaped allowlist: " + ", ".join(sorted(unexpected))
            )
        if CUP_PROPERTY not in keys:
            raise RuntimeError("OData projection returned no CUP property")

        report["cup_projection_gate"] = {
            "status_code": projected.status_code,
            "rows_received": 1,
            "returned_data_keys": sorted(keys),
            "passed": True,
        }
        report["candidate_status"] = "PROJECTION_CONFIRMED_FOR_CUP"

    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
