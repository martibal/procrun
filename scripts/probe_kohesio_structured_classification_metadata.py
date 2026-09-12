#!/usr/bin/env python3
"""Metadata-only qualification probe for Kohesio/EU Knowledge Graph classification properties.

This probe is deliberately restricted to Wikibase property metadata. It MUST NOT request item/project
entities, project rows, beneficiary values, free text, or SPARQL result rows. Its only purpose is to
establish whether an explicit structured property exists for intervention/category classification
before any row-level qualification can be considered.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request

ENDPOINT = "https://linkedopendata.eu/w/api.php"
USER_AGENT = "ProcRun/phase-r-kohesio-metadata-only-v1"
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


def request_property_search(term: str) -> list[dict[str, str | None]]:
    params = {
        "action": "wbsearchentities",
        "search": term,
        "language": "en",
        "type": "property",
        "limit": "10",
        "format": "json",
    }
    url = ENDPOINT + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)

    rows: list[dict[str, str | None]] = []
    for item in payload.get("search", []):
        entity_id = str(item.get("id", ""))
        if not entity_id.startswith("P"):
            raise RuntimeError(f"non-property entity returned by property-only search: {entity_id}")
        rows.append(
            {
                "id": entity_id,
                "label": item.get("label"),
                "description": item.get("description"),
            }
        )
    return rows


def main() -> int:
    searches = {term: request_property_search(term) for term in SEARCH_TERMS}
    unique: dict[str, dict[str, str | None]] = {}
    for rows in searches.values():
        for row in rows:
            unique[str(row["id"])] = row

    report = {
        "probe_contract": "kohesio-structured-classification-property-metadata-only-v1",
        "endpoint": ENDPOINT,
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
