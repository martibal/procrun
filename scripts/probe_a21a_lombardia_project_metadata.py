"""Probe only public OpenCoesione metadata for the A21a Lombardia project source candidate.

This script deliberately does NOT download project rows. It opens the public dataset catalogue
page, resolves only the published record-layout workbook, and inspects that workbook's schema
text. The purpose is to decide whether a project-only 2021-2027 route is safe enough to consider
for a later zero-PII source contract.
"""

from __future__ import annotations

import io
import json
import re
import sys
import zipfile
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree

CATALOG_URL = (
    "https://opencoesione.gov.it/it/opendata/dataset/"
    "progetti_esteso_lom_2021-2027/"
)
APPROVED_HOST = "opencoesione.gov.it"
USER_AGENT = "ProcRun-A21a-Metadata-Probe/1.0"

# Metadata field-name fragments that would make a project-only source candidate unsafe for
# ingestion without a stronger server-side projection boundary.
FORBIDDEN_METADATA_FRAGMENTS = (
    "beneficiari",
    "beneficiario",
    "codice_fiscale",
    "codicefiscale",
    "partita_iva",
    "partitaiva",
    "email",
    "telefono",
    "telephone",
    "phone",
    "indirizzo",
    "address",
    "contatto",
    "contact",
    "nome_persona",
    "cognome",
)

REQUIRED_PROJECT_CONCEPTS = (
    "titolo",
    "sintesi",
    "codice locale",
)


class _AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._href: str | None = None
        self._text: list[str] = []
        self.anchors: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        self._href = dict(attrs).get("href")
        self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href is not None:
            self.anchors.append((self._href, " ".join(self._text).strip()))
            self._href = None
            self._text = []


def _fetch(url: str) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != APPROVED_HOST:
        raise RuntimeError(f"metadata probe refused non-approved origin: {url}")
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response:  # noqa: S310 - frozen HTTPS origin above
        final = urlparse(response.geturl())
        if final.scheme != "https" or final.hostname != APPROVED_HOST:
            raise RuntimeError(f"metadata probe redirected outside approved origin: {response.geturl()}")
        return response.read()


def _record_layout_url(page: bytes) -> str:
    parser = _AnchorParser()
    parser.feed(page.decode("utf-8", errors="strict"))
    candidates = [
        urljoin(CATALOG_URL, href)
        for href, text in parser.anchors
        if "tracciato record" in text.lower()
    ]
    if len(candidates) != 1:
        raise RuntimeError(f"expected exactly one record-layout link; found {len(candidates)}")
    url = candidates[0]
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != APPROVED_HOST:
        raise RuntimeError(f"record-layout link leaves approved origin: {url}")
    return url


def _xlsx_text(blob: bytes) -> list[str]:
    if not blob.startswith(b"PK"):
        raise RuntimeError("record-layout resource is not an XLSX/ZIP container")

    strings: list[str] = []
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            for si in root.findall("{*}si"):
                text = "".join(node.text or "" for node in si.iter() if node.tag.endswith("}t"))
                if text.strip():
                    strings.append(text.strip())

        # Some workbooks store strings inline instead of in sharedStrings.xml.
        for name in sorted(n for n in archive.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n)):
            root = ElementTree.fromstring(archive.read(name))
            for cell in root.findall(".//{*}c"):
                if cell.attrib.get("t") != "inlineStr":
                    continue
                text = "".join(node.text or "" for node in cell.iter() if node.tag.endswith("}t"))
                if text.strip():
                    strings.append(text.strip())

    # Preserve first occurrence so the report remains deterministic and readable.
    return list(dict.fromkeys(strings))


def _normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def probe() -> dict[str, object]:
    page = _fetch(CATALOG_URL)
    layout_url = _record_layout_url(page)
    layout = _fetch(layout_url)
    texts = _xlsx_text(layout)
    normalized = [_normalized(value) for value in texts]

    forbidden_hits = sorted(
        {
            raw
            for raw, norm in zip(texts, normalized, strict=True)
            if any(fragment in norm for fragment in FORBIDDEN_METADATA_FRAGMENTS)
        }
    )
    required_hits = {
        concept: any(_normalized(concept) in norm for norm in normalized)
        for concept in REQUIRED_PROJECT_CONCEPTS
    }

    return {
        "probe_version": "a21a-lombardia-project-metadata-v1",
        "catalog_url": CATALOG_URL,
        "record_layout_url": layout_url,
        "project_rows_downloaded": False,
        "metadata_text_count": len(texts),
        "forbidden_metadata_hits": forbidden_hits,
        "required_project_concepts": required_hits,
        "candidate_status": (
            "METADATA_GATE_PASS"
            if not forbidden_hits and all(required_hits.values())
            else "METADATA_GATE_FAIL"
        ),
        "note": (
            "PASS permits only the next source-safety review step. It does not approve project-row ingest."
        ),
    }


def main() -> int:
    report = probe()
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["candidate_status"] == "METADATA_GATE_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
