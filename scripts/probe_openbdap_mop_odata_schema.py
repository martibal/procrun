#!/usr/bin/env python3
"""Schema-only probe for OpenBDAP MOP OData.

No DataRows endpoint is called. The probe inspects OData service metadata only
and emits property names relevant to a future safe projection allowlist.
"""
from __future__ import annotations

import json
import re
from typing import Final
from urllib.parse import urlparse
from xml.etree import ElementTree

import httpx

ALLOWED_HOST: Final = "bdap-opendata.rgs.mef.gov.it"
MAX_RESPONSE_BYTES: Final = 12_000_000
RESOURCE_ID: Final = "bda1676b-62ab-44b7-8f9a-ca93b8534488@rgs"
CANDIDATES: Final = (
    "https://bdap-opendata.rgs.mef.gov.it/ODataProxy/$metadata",
    "https://bdap-opendata.rgs.mef.gov.it/Proxy.svc/$metadata",
)
KEYWORDS: Final = (
    "cup",
    "natura",
    "tipologia",
    "settore",
    "sottosettore",
    "categoria",
    "progettazione",
    "esecuzione",
    "conclusione",
    "funzionalita",
    "costo",
    "lavori",
)


def _normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def _metadata_properties(payload: bytes) -> list[str]:
    root = ElementTree.fromstring(payload)
    properties: set[str] = set()
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "Property":
            continue
        name = element.attrib.get("Name")
        if name:
            properties.add(name)
    return sorted(properties)


def main() -> int:
    headers = {
        "User-Agent": "ProcRun-OpenBDAP-MOP-OData-Schema-Probe/1.0",
        "Accept": "application/xml,application/atom+xml,text/xml",
    }
    attempts: list[dict[str, object]] = []
    chosen: str | None = None
    properties: list[str] = []

    with httpx.Client(timeout=60.0, follow_redirects=False, headers=headers) as client:
        for url in CANDIDATES:
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
                raise RuntimeError("metadata candidate left the frozen OpenBDAP origin")
            response = client.get(url)
            attempts.append({
                "path": parsed.path,
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", ""),
                "response_bytes": len(response.content),
            })
            if response.is_redirect or response.status_code != 200:
                continue
            if len(response.content) > MAX_RESPONSE_BYTES:
                raise RuntimeError("OData metadata response exceeded safety bound")
            try:
                candidate_properties = _metadata_properties(response.content)
            except ElementTree.ParseError:
                continue
            if candidate_properties:
                chosen = parsed.path
                properties = candidate_properties
                break

    relevant = [
        name
        for name in properties
        if any(keyword in _normalized(name) for keyword in KEYWORDS)
    ]
    report = {
        "probe_contract": "openbdap-mop-odata-schema-v1",
        "resource_id": RESOURCE_ID,
        "schema_only": True,
        "datarows_called": False,
        "attempts": attempts,
        "chosen_metadata_path": chosen,
        "property_count": len(properties),
        "relevant_property_names": relevant,
        "candidate_status": "SCHEMA_AVAILABLE" if chosen else "SCHEMA_NOT_FOUND",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
