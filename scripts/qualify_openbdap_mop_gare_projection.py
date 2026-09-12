#!/usr/bin/env python3
"""Qualify OpenBDAP MOP_GAR CUP->CIG projection without identity/free-text receipt."""
from __future__ import annotations

import html
import json
import re
from collections.abc import Iterable
from typing import Any, Final
from urllib.parse import urlparse

import httpx

ALLOWED_HOST: Final = "bdap-opendata.rgs.mef.gov.it"
DOWNLOAD_PAGE: Final = (
    "https://bdap-opendata.rgs.mef.gov.it/opendata/"
    "spd_mop_gar_mon_reg00_01_9999?t=Scarica"
)
CONTROL_CUP: Final = "C11J05000030001"
MAX_PAGE_BYTES: Final = 2_000_000
MAX_METADATA_BYTES: Final = 4_000_000
MAX_ROW_BYTES: Final = 500_000

SAFE_PATTERNS: Final = {
    "cup": (r"codice.*cup", r"^cup$"),
    "cig": (r"codice.*cig", r"^cig$"),
    "publication_date": (r"data.*pubblicazione.*gara",),
}
FORBIDDEN_TERMS: Final = (
    "codice fiscale",
    "soggetto",
    "aggiudicatario",
    "partecipante",
    "invitato",
    "descrizione",
    "oggetto",
    "nome",
    "cognome",
    "rup",
    "responsabile",
    "email",
    "telefono",
)
NAME_KEYS: Final = {
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
LABEL_KEYS: Final = {
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


def _check_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise RuntimeError("OpenBDAP request left the frozen origin")


def _iter_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _iter_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_dicts(child)


def _candidate_fields(metadata: Any) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    for obj in _iter_dicts(metadata):
        names = [
            value
            for key, value in obj.items()
            if key.casefold() in NAME_KEYS and isinstance(value, str) and value.strip()
        ]
        if not names:
            continue
        labels = [
            value
            for key, value in obj.items()
            if key.casefold() in LABEL_KEYS and isinstance(value, str) and value.strip()
        ]
        wire = names[0].strip()
        label = " | ".join(labels) if labels else wire
        candidates.append((wire, label))

    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for wire, label in candidates:
        if wire not in seen:
            seen.add(wire)
            out.append((wire, label))
    return out


def _select_fields(candidates: list[tuple[str, str]]) -> dict[str, str]:
    selected: dict[str, str] = {}
    for concept, patterns in SAFE_PATTERNS.items():
        matches: list[str] = []
        for wire, label in candidates:
            combined = _normalise(f"{wire} {label}")
            if any(term in combined for term in FORBIDDEN_TERMS):
                continue
            if any(re.search(pattern, combined) for pattern in patterns):
                matches.append(wire)
        unique = sorted(set(matches))
        if len(unique) != 1:
            raise RuntimeError(
                f"OpenBDAP metadata did not identify exactly one safe {concept} field: {unique!r}"
            )
        selected[concept] = unique[0]
    return selected


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

    uuid_matches = sorted(
        set(
            re.findall(
                r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}@rgs",
                decoded,
                flags=re.IGNORECASE,
            )
        )
    )
    if len(uuid_matches) != 1:
        raise RuntimeError(
            "OpenBDAP download metadata did not expose one unambiguous OData resource key; "
            f"candidate_count={len(uuid_matches)}"
        )
    return uuid_matches[0]


def _rows(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    if isinstance(payload.get("value"), list):
        return [row for row in payload["value"] if isinstance(row, dict)]
    d_value = payload.get("d")
    if isinstance(d_value, dict) and isinstance(d_value.get("results"), list):
        return [row for row in d_value["results"] if isinstance(row, dict)]
    return []


def _data_keys(row: dict[str, Any]) -> set[str]:
    return {
        key
        for key in row
        if key != "row_id" and not key.startswith("__") and not key.startswith("@odata.")
    }


def main() -> int:
    _check_url(DOWNLOAD_PAGE)
    headers = {
        "User-Agent": "ProcRun-OpenBDAP-MOP-Gare-Projection/1.0",
        "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
    }
    request_count = 0

    with httpx.Client(timeout=60.0, follow_redirects=False, headers=headers) as client:
        page = client.get(DOWNLOAD_PAGE)
        request_count += 1
        if page.is_redirect:
            raise RuntimeError("OpenBDAP download metadata redirected")
        page.raise_for_status()
        if len(page.content) > MAX_PAGE_BYTES:
            raise RuntimeError("OpenBDAP download metadata exceeded safety bound")
        resource_key = _extract_resource_key(page.text)

        entity_url = (
            "https://bdap-opendata.rgs.mef.gov.it/ODataProxy/"
            f"MdData('{resource_key}')"
        )
        rows_url = f"{entity_url}/DataRows"
        _check_url(entity_url)
        _check_url(rows_url)

        metadata_response = client.get(entity_url)
        request_count += 1
        if metadata_response.is_redirect:
            raise RuntimeError("OpenBDAP MOP_GAR metadata redirected")
        metadata_response.raise_for_status()
        if len(metadata_response.content) > MAX_METADATA_BYTES:
            raise RuntimeError("OpenBDAP MOP_GAR metadata exceeded safety bound")
        metadata = metadata_response.json()
        selected = _select_fields(_candidate_fields(metadata))

        select_fields = [selected["cup"], selected["cig"], selected["publication_date"]]
        projection = client.get(
            rows_url,
            params={
                "$select": ",".join(select_fields),
                "$filter": f"{selected['cup']} eq '{CONTROL_CUP}'",
                "$top": "25",
                "$format": "json",
            },
        )
        request_count += 1
        if projection.is_redirect:
            raise RuntimeError("OpenBDAP MOP_GAR projected request redirected")
        projection.raise_for_status()
        if len(projection.content) > MAX_ROW_BYTES:
            raise RuntimeError("OpenBDAP MOP_GAR projected response exceeded safety bound")

    projected_rows = _rows(projection.json())
    if not projected_rows:
        raise RuntimeError("OpenBDAP MOP_GAR control CUP returned no projected rows")

    expected = set(select_fields)
    for row in projected_rows:
        unexpected = _data_keys(row) - expected
        if unexpected:
            raise RuntimeError(
                "OpenBDAP MOP_GAR projection leaked non-allowlisted fields: "
                + ", ".join(sorted(unexpected))
            )
        if row.get(selected["cup"]) != CONTROL_CUP:
            raise RuntimeError("OpenBDAP MOP_GAR server-side CUP filter was not enforced")

    report = {
        "decision": "PASS_SAFE_PROJECTED_CUP_CIG_ROUTE",
        "measurement_contract": "openbdap-mop-gare-safe-projection-v1",
        "dataset_slug": "spd_mop_gar_mon_reg00_01_9999",
        "resource_key": resource_key,
        "selected_by_concept": selected,
        "projection_fields": select_fields,
        "control_rows_received": len(projected_rows),
        "control_cup_filter_enforced": True,
        "identity_fields_received": False,
        "free_text_received": False,
        "raw_rows_persisted": False,
        "request_count": request_count,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
