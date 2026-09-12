#!/usr/bin/env python3
"""Qualify OpenBDAP MOP OData pre-receipt field projection.

Safety contract:
- the exact MOP Totale UUID is frozen from OpenBDAP download metadata;
- MdData metadata is fetched first;
- DataRows is never called unless a small set of safe project fields can be
  identified from metadata;
- the single-row DataRows request uses server-side $select and $top=1;
- the run fails if the response contains any field outside the selected set.

No bulk resource body is downloaded and no unrestricted project row is ever
requested.
"""
from __future__ import annotations

import json
import re
from collections.abc import Iterable
from typing import Any
from urllib.parse import urlparse

import httpx

ALLOWED_HOST = "bdap-opendata.rgs.mef.gov.it"
RESOURCE_KEY = "bda1676b-62ab-44b7-8f9a-ca93b8534488@rgs"
ODATA_ENTITY = (
    "https://bdap-opendata.rgs.mef.gov.it/ODataProxy/"
    f"MdData('{RESOURCE_KEY}')"
)
ODATA_ROWS = f"{ODATA_ENTITY}/DataRows"
MAX_METADATA_BYTES = 4_000_000
MAX_ROW_BYTES = 200_000

# Only structured, non-identity, non-free-text concepts are eligible. The probe
# deliberately does not select project owner, fiscal code, title or description.
SAFE_CONCEPT_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("cup", (r"^cup$", r"codice.*cup", r"cup.*codice")),
    ("nature", (r"natura",)),
    ("typology", (r"tipologia",)),
    ("sector", (r"^settore$", r"settore.*cup")),
    ("subsector", (r"sottosettore",)),
    ("category", (r"categoria",)),
    ("status", (r"stato.*progetto", r"stato.*opera", r"stato.*cup")),
    ("planned_start", (r"data.*inizio.*prev", r"inizio.*prev")),
    ("actual_start", (r"data.*inizio.*eff", r"inizio.*eff")),
    ("planned_end", (r"data.*fine.*prev", r"fine.*prev")),
    ("actual_end", (r"data.*fine.*eff", r"fine.*eff")),
)

FORBIDDEN_TERMS = (
    "codice fiscale",
    "codice_fiscale",
    "cf titolare",
    "titolare",
    "responsabile",
    "rup",
    "beneficiario",
    "aggiudicatario",
    "fornitore",
    "nome",
    "cognome",
    "denominazione",
    "descrizione",
    "titolo",
)

NAME_KEYS = {
    "name",
    "field",
    "fieldname",
    "column",
    "columnname",
    "property",
    "propertyname",
    "key",
    "code",
    "codice",
}
LABEL_KEYS = {
    "label",
    "title",
    "description",
    "descrizione",
    "displayname",
    "caption",
    "nome",
}


def _normalise(value: str) -> str:
    value = value.casefold().replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", value).strip()


def _check_endpoint(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise RuntimeError("OpenBDAP OData endpoint left the frozen origin")


def _safe_get(
    client: httpx.Client,
    url: str,
    *,
    params: dict[str, str] | None,
    max_bytes: int,
) -> Any:
    response = client.get(url, params=params)
    if response.is_redirect:
        raise RuntimeError(f"unexpected OpenBDAP redirect: {response.headers.get('location')}")
    response.raise_for_status()
    if len(response.content) > max_bytes:
        raise RuntimeError("OpenBDAP response exceeded safety bound")
    return response.json()


def _iter_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _iter_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_dicts(child)


def _candidate_fields(metadata: Any) -> list[tuple[str, str]]:
    """Extract (wire-name, human label) pairs conservatively from metadata."""
    candidates: list[tuple[str, str]] = []
    for obj in _iter_dicts(metadata):
        name_values = [
            value
            for key, value in obj.items()
            if key.casefold() in NAME_KEYS and isinstance(value, str) and value.strip()
        ]
        if not name_values:
            continue
        labels = [
            value
            for key, value in obj.items()
            if key.casefold() in LABEL_KEYS and isinstance(value, str) and value.strip()
        ]
        wire_name = name_values[0].strip()
        label = " | ".join(labels) if labels else wire_name
        candidates.append((wire_name, label))

    # Stable dedupe preserving first metadata occurrence.
    seen: set[str] = set()
    result: list[tuple[str, str]] = []
    for wire_name, label in candidates:
        if wire_name in seen:
            continue
        seen.add(wire_name)
        result.append((wire_name, label))
    return result


def _is_forbidden(wire_name: str, label: str) -> bool:
    combined = _normalise(f"{wire_name} {label}")
    return any(term in combined for term in FORBIDDEN_TERMS)


def _select_safe_fields(candidates: list[tuple[str, str]]) -> dict[str, str]:
    selected: dict[str, str] = {}
    for concept, patterns in SAFE_CONCEPT_PATTERNS:
        matches: list[str] = []
        for wire_name, label in candidates:
            if _is_forbidden(wire_name, label):
                continue
            haystack = _normalise(f"{wire_name} {label}")
            if any(re.search(pattern, haystack) for pattern in patterns):
                matches.append(wire_name)
        unique = sorted(set(matches))
        if len(unique) == 1:
            selected[concept] = unique[0]

    # Require enough structure to make the projection test meaningful and to
    # support the intended ProcRun use-case if the gate passes.
    required = {"cup", "sector", "category"}
    missing = sorted(required - set(selected))
    if missing:
        raise RuntimeError(
            "metadata did not identify an unambiguous safe field set; "
            f"missing={missing!r}, discovered_candidates={len(candidates)}"
        )
    return selected


def _row_objects(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    if isinstance(payload.get("value"), list):
        return [item for item in payload["value"] if isinstance(item, dict)]
    d_value = payload.get("d")
    if isinstance(d_value, dict) and isinstance(d_value.get("results"), list):
        return [item for item in d_value["results"] if isinstance(item, dict)]
    if isinstance(d_value, list):
        return [item for item in d_value if isinstance(item, dict)]
    return []


def _strip_odata_meta(keys: set[str]) -> set[str]:
    return {key for key in keys if not key.startswith("__") and not key.startswith("@odata.")}


def main() -> int:
    for endpoint in (ODATA_ENTITY, ODATA_ROWS):
        _check_endpoint(endpoint)

    headers = {
        "User-Agent": "ProcRun-OpenBDAP-MOP-Projection-Probe/1.0",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=60.0, follow_redirects=False, headers=headers) as client:
        metadata = _safe_get(
            client,
            ODATA_ENTITY,
            params=None,
            max_bytes=MAX_METADATA_BYTES,
        )
        candidates = _candidate_fields(metadata)
        selected_by_concept = _select_safe_fields(candidates)
        selected_fields = sorted(set(selected_by_concept.values()))

        row_payload = _safe_get(
            client,
            ODATA_ROWS,
            params={"$select": ",".join(selected_fields), "$top": "1"},
            max_bytes=MAX_ROW_BYTES,
        )

    rows = _row_objects(row_payload)
    if len(rows) != 1:
        raise RuntimeError(f"expected exactly one projected OData row, got {len(rows)}")

    returned_fields = _strip_odata_meta(set(rows[0]))
    expected_fields = set(selected_fields)
    unexpected = sorted(returned_fields - expected_fields)
    missing = sorted(expected_fields - returned_fields)
    if unexpected:
        raise RuntimeError(f"OData $select projection leaked unexpected fields: {unexpected!r}")
    if missing:
        raise RuntimeError(f"OData $select omitted selected fields: {missing!r}")

    # The report contains schema/projection facts only. It intentionally never
    # persists the row values fetched for the transport-contract test.
    report = {
        "probe_contract": "openbdap-mop-odata-projection-v1",
        "resource_key": RESOURCE_KEY,
        "bulk_resource_called": False,
        "metadata_called": True,
        "datarows_called": True,
        "datarows_top": 1,
        "selected_by_concept": selected_by_concept,
        "selected_fields": selected_fields,
        "returned_fields": sorted(returned_fields),
        "unexpected_fields": unexpected,
        "row_values_persisted": False,
        "projection_gate": "PASS",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
