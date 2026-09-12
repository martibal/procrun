#!/usr/bin/env python3
"""Inspect only the official metadata workbook for national FESR 2021-2027 projects.

No project dataset or project row is requested. The probe establishes whether the exact extended
project transport documents structured investment-nature/type fields and whether identity-bearing
subject fields are part of that transport schema.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import urllib.request
import zipfile
from xml.etree import ElementTree as ET

METADATA_URL = (
    "https://opencoesione.gov.it/media/opendata/"
    "metadati_progetti_tracciato_esteso.xlsx"
)
PUBLICATION_PAGE = (
    "https://opencoesione.gov.it/it/opendata/dataset/"
    "progetti_esteso_fesr_2021-2027/"
)
MAX_BYTES = 512_000
MAX_ENTRIES = 250
MAX_CELL_CHARS = 2_000

IDENTITY_TERMS = (
    "beneficiar",
    "soggett",
    "codice fiscale",
    "codice_fiscale",
    "partita iva",
    "partita_iva",
    "persona fisica",
    "cognome",
    "email",
    "telefono",
    "fornitore",
    "aggiudicatario",
)
CLASSIFICATION_TERMS = (
    "natura",
    "tipo_operazione",
    "tipologia",
    "cup",
    "tema",
    "settore",
    "categoria",
    "intervento",
)


def _download() -> bytes:
    request = urllib.request.Request(
        METADATA_URL,
        headers={
            "User-Agent": "ProcRun-public-schema-qualification/2.0",
            "Referer": PUBLICATION_PAGE,
            "Accept": (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,"
                "application/octet-stream;q=0.9"
            ),
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
        final_url = response.geturl()
        if final_url != METADATA_URL:
            raise RuntimeError(f"unexpected metadata redirect: {final_url}")
        payload = response.read(MAX_BYTES + 1)
    if not payload or len(payload) > MAX_BYTES:
        raise RuntimeError("metadata workbook empty or exceeds safety bound")
    if not payload.startswith(b"PK"):
        raise RuntimeError("metadata workbook is not an XLSX ZIP payload")
    return payload


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        raw = archive.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    root = ET.fromstring(raw)  # noqa: S314 - bounded trusted workbook metadata
    result: list[str] = []
    for item in root.iter():
        if _local_name(item.tag) != "si":
            continue
        text = "".join(
            node.text or "" for node in item.iter() if _local_name(node.tag) == "t"
        )
        result.append(text)
    return result


def _cell_value(cell: ET.Element, shared: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        text = "".join(
            node.text or "" for node in cell.iter() if _local_name(node.tag) == "t"
        )
    else:
        value_node = next(
            (node for node in cell if _local_name(node.tag) == "v"), None
        )
        if value_node is None or value_node.text is None:
            return ""
        raw = value_node.text
        if cell_type == "s":
            index = int(raw)
            if index < 0 or index >= len(shared):
                raise RuntimeError("shared-string index out of range")
            text = shared[index]
        else:
            text = raw
    normalized = re.sub(r"\s+", " ", text).strip()
    return normalized[:MAX_CELL_CHARS]


def _rows(archive: zipfile.ZipFile, shared: list[str]) -> list[str]:
    rows: list[str] = []
    worksheet_names = sorted(
        name
        for name in archive.namelist()
        if name.startswith("xl/worksheets/") and name.endswith(".xml")
    )
    for name in worksheet_names:
        root = ET.fromstring(archive.read(name))  # noqa: S314 - bounded metadata
        for row in root.iter():
            if _local_name(row.tag) != "row":
                continue
            cells = [
                _cell_value(cell, shared)
                for cell in row
                if _local_name(cell.tag) == "c"
            ]
            cells = [cell for cell in cells if cell]
            if cells:
                rows.append(" | ".join(cells))
    return rows


def main() -> int:
    payload = _download()
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        if len(archive.infolist()) > MAX_ENTRIES:
            raise RuntimeError("metadata workbook exceeds ZIP-entry safety bound")
        shared = _shared_strings(archive)
        rows = _rows(archive, shared)

    lower_rows = [(row, row.casefold()) for row in rows]
    identity_hits = [
        row for row, lower in lower_rows if any(term in lower for term in IDENTITY_TERMS)
    ]
    classification_hits = [
        row
        for row, lower in lower_rows
        if any(term in lower for term in CLASSIFICATION_TERMS)
    ]

    result = {
        "probe_contract": "opencoesione-fesr-extended-metadata-v1",
        "metadata_url": METADATA_URL,
        "metadata_only": True,
        "project_rows_called": False,
        "response_bytes": len(payload),
        "response_sha256": hashlib.sha256(payload).hexdigest(),
        "metadata_row_count": len(rows),
        "identity_term_hit_count": len(identity_hits),
        "identity_term_hits": identity_hits,
        "classification_hit_count": len(classification_hits),
        "classification_hits": classification_hits,
        "all_metadata_rows": rows,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
