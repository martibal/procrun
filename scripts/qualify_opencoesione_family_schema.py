"""Qualify the public OpenCoesione beneficiary metadata without retrieving data rows."""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

import xlrd

from procrun.collectors.opencoesione import EXPECTED_HEADERS

PUBLICATION_PAGE = "https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/"
METADATA_URL = "https://opencoesione.gov.it/media/opendata/metadati_beneficiari.xls"


def _download_metadata() -> bytes:
    request = urllib.request.Request(
        METADATA_URL,
        headers={
            "User-Agent": "ProcRun-public-schema-qualification/1.0",
            "Referer": PUBLICATION_PAGE,
            "Accept": "application/vnd.ms-excel,application/octet-stream;q=0.9,*/*;q=0.1",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
        final_url = response.geturl()
        if final_url != METADATA_URL:
            raise RuntimeError(f"unexpected metadata redirect: {final_url}")
        payload = response.read(1_000_001)
    if len(payload) > 1_000_000:
        raise RuntimeError("metadata workbook exceeds 1 MB safety bound")
    if not payload:
        raise RuntimeError("metadata workbook is empty")
    return payload


def _normalise(value: object) -> str:
    return " ".join(str(value).strip().split())


def _ordered_string_cells(payload: bytes) -> list[str]:
    workbook = xlrd.open_workbook(file_contents=payload)
    values: list[str] = []
    for sheet in workbook.sheets():
        for row in range(sheet.nrows):
            for col in range(sheet.ncols):
                value = _normalise(sheet.cell_value(row, col))
                if value:
                    values.append(value)
    return values


def main() -> int:
    payload = _download_metadata()
    cells = _ordered_string_cells(payload)
    positions: list[int] = []
    missing: list[str] = []
    for header in EXPECTED_HEADERS:
        try:
            positions.append(cells.index(header))
        except ValueError:
            missing.append(header)
    print(f"metadata_url={METADATA_URL}")
    print(f"metadata_bytes={len(payload)}")
    print(f"frozen_transport_fields={len(EXPECTED_HEADERS)}")
    if missing:
        print("result=FAIL")
        print("missing_exact_transport_headers=" + repr(missing))
        print("workbook_strings=" + repr(cells))
        return 1
    if positions != sorted(positions) or len(set(positions)) != len(positions):
        print("result=FAIL")
        print("reason=frozen headers are not present in exact order")
        print("positions=" + repr(positions))
        return 1
    print("result=PASS")
    print("reason=all 20 frozen transport headers occur in exact order in official metadata workbook")
    return 0


if __name__ == "__main__":
    sys.exit(main())
