#!/usr/bin/env python3
"""Discover the exact OpenBDAP MOP Totale resource using metadata only.

The probe calls the OpenBDAP CKAN-compatible catalogue. It never requests a
resource body or OData DataRows.
"""
from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlparse

import httpx

CATALOG_ACTION = "https://bdap-opendata.rgs.mef.gov.it/SpodCkanApi/api/3/action/package_search"
ALLOWED_HOST = "bdap-opendata.rgs.mef.gov.it"
EXACT_TITLE = "Progetti Opere Pubbliche MOP - Totale"
MAX_RESPONSE_BYTES = 4_000_000
MAX_RESULTS = 20


def _url_shape(value: object) -> dict[str, str] | None:
    if not isinstance(value, str) or not value:
        return None
    parsed = urlparse(value)
    return {
        "scheme": parsed.scheme,
        "host": parsed.hostname or "",
        "path": parsed.path,
    }


def _resource_metadata(resource: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "id",
        "name",
        "description",
        "format",
        "mimetype",
        "mimetype_inner",
        "resource_type",
        "url_type",
        "size",
        "created",
        "last_modified",
        "metadata_modified",
        "hash",
    }
    result = {key: resource.get(key) for key in sorted(allowed) if key in resource}
    result["url_shape"] = _url_shape(resource.get("url"))
    result["metadata_keys"] = sorted(resource)
    return result


def _package_metadata(package: dict[str, Any]) -> dict[str, Any]:
    resources = package.get("resources")
    if resources is None:
        resources = []
    if not isinstance(resources, list):
        raise RuntimeError("OpenBDAP package resources are not a list")
    return {
        "id": package.get("id"),
        "name": package.get("name"),
        "title": package.get("title"),
        "license_id": package.get("license_id"),
        "license_title": package.get("license_title"),
        "metadata_modified": package.get("metadata_modified"),
        "metadata_keys": sorted(package),
        "resources": [
            _resource_metadata(resource)
            for resource in resources
            if isinstance(resource, dict)
        ],
    }


def main() -> int:
    parsed = urlparse(CATALOG_ACTION)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise RuntimeError("OpenBDAP catalogue endpoint left the frozen origin")

    params = {"q": f'title:"{EXACT_TITLE}"', "rows": str(MAX_RESULTS)}
    headers = {
        "User-Agent": "ProcRun-OpenBDAP-MOP-Catalog-Probe/1.0",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=60.0, follow_redirects=False, headers=headers) as client:
        response = client.get(CATALOG_ACTION, params=params)
        if response.is_redirect:
            raise RuntimeError("OpenBDAP catalogue request redirected")
        response.raise_for_status()
        if len(response.content) > MAX_RESPONSE_BYTES:
            raise RuntimeError("OpenBDAP catalogue response exceeded safety bound")
        payload = response.json()

    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise RuntimeError("OpenBDAP catalogue returned an invalid CKAN response")
    result = payload.get("result")
    if not isinstance(result, dict):
        raise RuntimeError("OpenBDAP catalogue response has no result object")
    packages = result.get("results")
    if not isinstance(packages, list):
        raise RuntimeError("OpenBDAP catalogue response has no package result list")

    exact = [
        package
        for package in packages
        if isinstance(package, dict) and package.get("title") == EXACT_TITLE
    ]
    if len(exact) != 1:
        raise RuntimeError(f"expected one exact MOP Totale package, found {len(exact)}")

    report = {
        "probe_contract": "openbdap-mop-catalog-metadata-v1",
        "metadata_only": True,
        "resource_body_called": False,
        "odata_datarows_called": False,
        "query_result_count": result.get("count"),
        "exact_match": _package_metadata(exact[0]),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
