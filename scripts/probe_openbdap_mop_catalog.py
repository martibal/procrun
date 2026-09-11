#!/usr/bin/env python3
"""Discover the exact OpenBDAP MOP Totale resource using metadata only.

The probe calls only CKAN-compatible catalogue endpoints. It never requests a
resource body or OData DataRows.
"""
from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlparse

import httpx

CATALOG_BASE = "https://bdap-opendata.rgs.mef.gov.it/SpodCkanApi/api/3/action"
PACKAGE_LIST = f"{CATALOG_BASE}/package_list"
PACKAGE_SHOW = f"{CATALOG_BASE}/package_show"
ALLOWED_HOST = "bdap-opendata.rgs.mef.gov.it"
EXACT_TITLE = "Progetti Opere Pubbliche MOP - Totale"
MAX_RESPONSE_BYTES = 4_000_000
MAX_CANDIDATES = 100


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
    resources = package.get("resources") or []
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


def _ckan_get(client: httpx.Client, url: str, params: dict[str, str] | None = None) -> Any:
    response = client.get(url, params=params)
    if response.is_redirect:
        raise RuntimeError("OpenBDAP catalogue request redirected")
    response.raise_for_status()
    if len(response.content) > MAX_RESPONSE_BYTES:
        raise RuntimeError("OpenBDAP catalogue response exceeded safety bound")
    payload = response.json()
    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise RuntimeError("OpenBDAP catalogue returned an invalid CKAN response")
    return payload.get("result")


def main() -> int:
    for endpoint in (PACKAGE_LIST, PACKAGE_SHOW):
        parsed = urlparse(endpoint)
        if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
            raise RuntimeError("OpenBDAP catalogue endpoint left the frozen origin")

    headers = {
        "User-Agent": "ProcRun-OpenBDAP-MOP-Catalog-Probe/2.0",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=60.0, follow_redirects=False, headers=headers) as client:
        package_ids = _ckan_get(client, PACKAGE_LIST)
        if not isinstance(package_ids, list) or not all(
            isinstance(item, str) for item in package_ids
        ):
            raise RuntimeError("OpenBDAP package_list returned an invalid ID list")
        candidates = [
            package_id
            for package_id in package_ids
            if "mop" in package_id.casefold()
            and ("prg" in package_id.casefold() or "opere" in package_id.casefold())
        ]
        if not candidates or len(candidates) > MAX_CANDIDATES:
            raise RuntimeError(
                f"unexpected MOP candidate count from package_list: {len(candidates)}"
            )

        exact: list[dict[str, Any]] = []
        candidate_titles: list[dict[str, object]] = []
        for package_id in candidates:
            package = _ckan_get(client, PACKAGE_SHOW, {"id": package_id})
            if not isinstance(package, dict):
                raise RuntimeError(f"package_show returned invalid metadata for {package_id}")
            candidate_titles.append({"id": package_id, "title": package.get("title")})
            if package.get("title") == EXACT_TITLE:
                exact.append(package)

    if len(exact) != 1:
        raise RuntimeError(
            "expected one exact MOP Totale package; "
            f"found={len(exact)}, candidates={candidate_titles!r}"
        )

    report = {
        "probe_contract": "openbdap-mop-catalog-metadata-v2",
        "metadata_only": True,
        "resource_body_called": False,
        "odata_datarows_called": False,
        "catalog_package_count": len(package_ids),
        "mop_candidate_count": len(candidates),
        "exact_match": _package_metadata(exact[0]),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
