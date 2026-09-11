#!/usr/bin/env python3
"""Metadata-only qualification probe for ANAC CIG datasets.

The probe calls CKAN package_show only. It never downloads a resource body.
"""
from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlparse

import httpx

CKAN_ACTION = "https://dati.anticorruzione.it/opendata/api/3/action/package_show"
PACKAGES = ("cig-2024", "cig-2025")
ALLOWED_HOST = "dati.anticorruzione.it"
MAX_RESPONSE_BYTES = 2_000_000

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
    "Content-Type": "application/json",
    "Referer": "https://dati.anticorruzione.it/opendata/dataset",
}


def _safe_url(value: object) -> dict[str, str] | None:
    if not isinstance(value, str) or not value:
        return None
    parsed = urlparse(value)
    return {
        "scheme": parsed.scheme,
        "host": parsed.hostname or "",
        "path": parsed.path,
    }


def _resource_summary(resource: dict[str, Any]) -> dict[str, Any]:
    # Metadata keys only. No resource URL is requested by this probe.
    allowed_metadata = {
        "id",
        "name",
        "description",
        "format",
        "mimetype",
        "mimetype_inner",
        "size",
        "created",
        "last_modified",
        "metadata_modified",
        "url_type",
        "resource_type",
        "schema",
        "fields",
        "hash",
    }
    summary = {key: resource.get(key) for key in sorted(allowed_metadata) if key in resource}
    summary["url_shape"] = _safe_url(resource.get("url"))
    summary["metadata_keys"] = sorted(resource)
    return summary


def _fetch_package(package_id: str) -> dict[str, Any]:
    with httpx.Client(timeout=45.0, follow_redirects=False, headers=BROWSER_HEADERS) as client:
        response = client.post(CKAN_ACTION, json={"id": package_id})
        if response.is_redirect:
            location = response.headers.get("location")
            raise RuntimeError(f"unexpected redirect for {package_id}: {location}")
        response.raise_for_status()
        if len(response.content) > MAX_RESPONSE_BYTES:
            raise RuntimeError(f"metadata response too large for {package_id}")
        payload = response.json()

    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise RuntimeError(f"invalid CKAN response for {package_id}")
    result = payload.get("result")
    if not isinstance(result, dict):
        raise RuntimeError(f"missing CKAN result for {package_id}")

    resources = result.get("resources")
    if not isinstance(resources, list):
        raise RuntimeError(f"missing resources for {package_id}")

    return {
        "id": result.get("id"),
        "name": result.get("name"),
        "title": result.get("title"),
        "notes": result.get("notes"),
        "license_id": result.get("license_id"),
        "license_title": result.get("license_title"),
        "metadata_modified": result.get("metadata_modified"),
        "package_metadata_keys": sorted(result),
        "resources": [
            _resource_summary(resource)
            for resource in resources
            if isinstance(resource, dict)
        ],
    }


def main() -> int:
    parsed = urlparse(CKAN_ACTION)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise RuntimeError("ANAC CKAN endpoint left the frozen origin")

    report = {
        "probe_contract": "anac-cig-package-metadata-v1",
        "metadata_only": True,
        "resource_body_called": False,
        "packages": [_fetch_package(package_id) for package_id in PACKAGES],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
