#!/usr/bin/env python3
"""Metadata-only qualification probe for Kohesio/EU Knowledge Graph classification properties.

The probe is restricted to Wikibase property metadata. Access failure is a qualification result, not
an invitation to broaden the request: no item/project entity, project row, beneficiary value, free
text or SPARQL row may be requested as fallback.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

ENDPOINT = "https://linkedopendata.eu/w/api.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/151 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://linkedopendata.eu/wiki/Main_Page",
}
SEARCH_TERMS = (
    "category of intervention",
    "intervention category",
    "intervention field",
    "field of intervention",
    "category intervention",
    "project category",
    "project sector",
    "project subsector",
)


def http_status(error: BaseException) -> int | None:
    return error.code if isinstance(error, urllib.error.HTTPError) else None


def request_json(params: dict[str, str]) -> tuple[dict[str, object] | None, dict[str, object]]:
    encoded = urllib.parse.urlencode(params)
    attempts: list[dict[str, object]] = []

    get_request = urllib.request.Request(ENDPOINT + "?" + encoded, headers=HEADERS)
    try:
        with urllib.request.urlopen(get_request, timeout=30) as response:
            return json.load(response), {"transport": "GET", "status": response.status}
    except (urllib.error.HTTPError, urllib.error.URLError) as error:
        attempts.append({"transport": "GET", "status": http_status(error), "error": type(error).__name__})

    post_request = urllib.request.Request(
        ENDPOINT,
        data=encoded.encode("utf-8"),
        headers={**HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(post_request, timeout=30) as response:
            return json.load(response), {"transport": "POST", "status": response.status}
    except (urllib.error.HTTPError, urllib.error.URLError) as error:
        attempts.append({"transport": "POST", "status": http_status(error), "error": type(error).__name__})
        return None, {"attempts": attempts}


def boundary() -> dict[str, bool]:
    return {
        "property_metadata_only": True,
        "item_entities_requested": False,
        "project_rows_requested": False,
        "beneficiary_data_requested": False,
        "free_text_requested": False,
        "sparql_rows_requested": False,
    }


def main() -> int:
    searches: dict[str, list[dict[str, str | None]]] = {}
    transports: set[str] = set()
    access_failures: list[dict[str, object]] = []

    for term in SEARCH_TERMS:
        payload, request_result = request_json(
            {
                "action": "wbsearchentities",
                "search": term,
                "language": "en",
                "type": "property",
                "limit": "10",
                "format": "json",
            }
        )
        if payload is None:
            access_failures.append({"term": term, **request_result})
            break

        transports.add(str(request_result["transport"]))
        rows: list[dict[str, str | None]] = []
        for item in payload.get("search", []):
            if not isinstance(item, dict):
                raise RuntimeError("unexpected non-object result from property-only search")
            entity_id = str(item.get("id", ""))
            if not entity_id.startswith("P"):
                raise RuntimeError(f"non-property entity returned by property-only search: {entity_id}")
            rows.append(
                {
                    "id": entity_id,
                    "label": item.get("label") if isinstance(item.get("label"), str) else None,
                    "description": item.get("description") if isinstance(item.get("description"), str) else None,
                }
            )
        searches[term] = rows

    unique: dict[str, dict[str, str | None]] = {}
    for rows in searches.values():
        for row in rows:
            unique[str(row["id"])] = row

    access_ok = not access_failures
    report = {
        "probe_contract": "kohesio-structured-classification-property-metadata-only-v1",
        "endpoint": ENDPOINT,
        "qualification_result": "METADATA_ACCESS_OK" if access_ok else "BLOCKED_AUTOMATED_METADATA_ACCESS",
        "access_ok": access_ok,
        "transports_used": sorted(transports),
        "access_failures": access_failures,
        "boundary": boundary(),
        "search_terms": list(SEARCH_TERMS),
        "searches": searches,
        "unique_property_candidates": [unique[key] for key in sorted(unique)],
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
