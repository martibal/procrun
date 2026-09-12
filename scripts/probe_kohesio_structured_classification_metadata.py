#!/usr/bin/env python3
"""Metadata-only qualification probe for Kohesio/EU Knowledge Graph classification properties.

This probe is deliberately restricted to Wikibase property metadata. It MUST NOT request item/project
entities, project rows, beneficiary values, free text, or SPARQL result rows. Its only purpose is to
establish whether an explicit structured property exists for intervention/category classification
before any row-level qualification can be considered.
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


def request_json(params: dict[str, str]) -> tuple[dict[str, object], str]:
    encoded = urllib.parse.urlencode(params)
    get_request = urllib.request.Request(ENDPOINT + "?" + encoded, headers=HEADERS)
    try:
        with urllib.request.urlopen(get_request, timeout=30) as response:
            return json.load(response), "GET"
    except urllib.error.HTTPError as error:
        if error.code not in {403, 405, 429}:
            raise

    # The public endpoint has previously rejected query-string GETs from hosted runners while
    # accepting the exact same read-only Wikibase action as form-encoded POST. The parameter set is
    # unchanged and remains property-metadata-only.
    post_request = urllib.request.Request(
        ENDPOINT,
        data=encoded.encode("utf-8"),
        headers={**HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(post_request, timeout=30) as response:
        return json.load(response), "POST"


def request_property_search(term: str) -> tuple[list[dict[str, str | None]], str]:
    payload, transport = request_json(
        {
            "action": "wbsearchentities",
            "search": term,
            "language": "en",
            "type": "property",
            "limit": "10",
            "format": "json",
        }
    )

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
    return rows, transport


def main() -> int:
    searches: dict[str, list[dict[str, str | None]]] = {}
    transports: set[str] = set()
    for term in SEARCH_TERMS:
        rows, transport = request_property_search(term)
        searches[term] = rows
        transports.add(transport)

    unique: dict[str, dict[str, str | None]] = {}
    for rows in searches.values():
        for row in rows:
            unique[str(row["id"])] = row

    report = {
        "probe_contract": "kohesio-structured-classification-property-metadata-only-v1",
        "endpoint": ENDPOINT,
        "transports_used": sorted(transports),
        "boundary": {
            "property_metadata_only": True,
            "item_entities_requested": False,
            "project_rows_requested": False,
            "beneficiary_data_requested": False,
            "free_text_requested": False,
            "sparql_rows_requested": False,
        },
        "search_terms": list(SEARCH_TERMS),
        "searches": searches,
        "unique_property_candidates": [unique[key] for key in sorted(unique)],
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
