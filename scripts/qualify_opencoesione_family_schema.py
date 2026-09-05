"""Guard the public OpenCoesione beneficiary metadata without retrieving data rows."""

from __future__ import annotations

import sys
import urllib.request

import xlrd

from procrun.collectors.opencoesione import EXPECTED_HEADERS

PUBLICATION_PAGE = "https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/"
METADATA_URL = "https://opencoesione.gov.it/media/opendata/metadati_beneficiari.xls"
EXPECTED_DOCUMENTED_MISMATCH = (
    "CostoTotale_TotalCost",
    "Ciclo_Period",
    "ObiettivoSpecifico_SpecificObjective",
    "DataInizioOperazione_OperationStartDate",
    "DataFineOperazione_OperationEndDate",
    "Paese_Country",
)


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
    missing = tuple(header for header in EXPECTED_HEADERS if header not in cells)
    print(f"metadata_url={METADATA_URL}")
    print(f"metadata_bytes={len(payload)}")
    print(f"frozen_transport_fields={len(EXPECTED_HEADERS)}")
    print("missing_exact_transport_headers=" + repr(missing))
    if missing != EXPECTED_DOCUMENTED_MISMATCH:
        print("guard=FAIL")
        print("reason=public metadata changed relative to documented fail-closed mismatch")
        return 1
    for required in (
        "DataInizioProgetto_OperationStartDate",
        "DataFineProgetto_OperationEndDate",
        "StatoMembro_Country",
    ):
        if required not in cells:
            print("guard=FAIL")
            print(f"reason=expected metadata-side name disappeared: {required}")
            return 1
    print("guard=PASS")
    print("qualification=NOT_ACTIVATED")
    print("reason=official metadata remains non-identical to frozen 20-column runtime contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
