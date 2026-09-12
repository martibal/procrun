#!/usr/bin/env python3
"""Schema-only diagnostic for OpenBDAP MOP_GAR OData wire names.

This probe never calls DataRows. It resolves the current MOP_GAR resource key
from OpenBDAP's own download page, inspects only OData metadata surfaces, and
emits property names relevant to CUP, CIG and gara publication date.
"""
from __future__ import annotations

import html
import json
import re
from typing import Final
from urllib.parse import urlparse
from xml.etree import ElementTree

import httpx

ALLOWED_HOST: Final = "bdap-opendata.rgs.mef.gov.it"
DOWNLOAD_PAGE: Final = (
    "https://bdap-opendata.rgs.mef.gov.it/opendata/"
    "spd_mop_gar_mon_reg00_01_9999?t=Scarica"
)
METADATA_CANDIDATES: Final = (
    "https://bdap-opendata.rgs.mef.gov.it/ODataProxy/$metadata",
    "https://bdap-opendata.rgs.mef.gov.it/Proxy.svc/$metadata",
)
MAX_PAGE_BYTES: Final = 2_000_000
MAX_METADATA_BYTES: Final = 12_000_000
KEYWORDS: Final = ("cup", "cig", "pubblicaz", "gara")


def _check_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise RuntimeError("OpenBDAP schema request left the frozen origin")


def _normalise(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def _extract_resource_key(page_text: str) -> str:
    decoded = html.unescape(page_text)
    explicit_patterns = (
        r"MdData\(['\"]([^'\"]+@rgs)['\"]\)",
        r"MdData%28%27([^%]+@rgs)%27%29",
    )
    for pattern in explicit_patterns:
        matches = sorted(set(re.findall(pattern, decoded, flags=re.IGNORECASE)))
        if len(matches) == 1:
            return matches[0]

    matches = sorted(
        set(
            re.findall(
                r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}@rgs",
                decoded,
                flags=re.IGNORECASE,
            )
        )
    )
    if len(matches) != 1:
        raise RuntimeError(
            "OpenBDAP download metadata did not expose one resource key; "
            f"candidate_count={len(matches)}"
        )
    return matches[0]


def _property_names(payload: bytes) -> list[str]:
    root = ElementTree.fromstring(payload)
    names: set[str] = set()
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "Property":
            continue
        name = element.attrib.get("Name")
        if name:
            names.add(name)
    return sorted(names)


def main() -> int:
    _check_url(DOWNLOAD_PAGE)
    for candidate in METADATA_CANDIDATES:
        _check_url(candidate)

    headers = {
        "User-Agent": "ProcRun-OpenBDAP-MOP-Gare-Schema/1.0",
        "Accept": "application/xml,application/atom+xml,text/xml,text/html;q=0.8",
    }
    request_count = 0
    attempts: list[dict[str, object]] = []
    chosen_path: str | None = None
    properties: list[str] = []

    with httpx.Client(timeout=60.0, follow_redirects=False, headers=headers) as client:
        page = client.get(DOWNLOAD_PAGE)
        request_count += 1
        if page.is_redirect:
            raise RuntimeError("OpenBDAP MOP_GAR download metadata redirected")
        page.raise_for_status()
        if len(page.content) > MAX_PAGE_BYTES:
            raise RuntimeError("OpenBDAP MOP_GAR download metadata exceeded safety bound")
        resource_key = _extract_resource_key(page.text)

        for url in METADATA_CANDIDATES:
            response = client.get(url)
            request_count += 1
            parsed = urlparse(url)
            attempt = {
                "path": parsed.path,
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", ""),
                "response_bytes": len(response.content),
            }
            attempts.append(attempt)
            if response.is_redirect or response.status_code != 200:
                continue
            if len(response.content) > MAX_METADATA_BYTES:
                raise RuntimeError("OpenBDAP OData metadata exceeded safety bound")
            try:
                candidate_properties = _property_names(response.content)
            except ElementTree.ParseError:
                continue
            if candidate_properties:
                chosen_path = parsed.path
                properties = candidate_properties
                break

    relevant = [
        name
        for name in properties
        if any(keyword in _normalise(name) for keyword in KEYWORDS)
    ]
    report = {
        "decision": "SCHEMA_DIAGNOSTIC_COMPLETE" if chosen_path else "SCHEMA_NOT_FOUND",
        "measurement_contract": "openbdap-mop-gare-schema-v1",
        "dataset_slug": "spd_mop_gar_mon_reg00_01_9999",
        "resource_key": resource_key,
        "schema_only": True,
        "datarows_called": False,
        "identity_fields_received": False,
        "free_text_received": False,
        "raw_rows_persisted": False,
        "chosen_metadata_path": chosen_path,
        "property_count": len(properties),
        "relevant_property_names": relevant,
        "relevant_property_count": len(relevant),
        "metadata_attempts": attempts,
        "request_count": request_count,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
