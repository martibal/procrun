import zipfile
from io import BytesIO

import pytest

from procrun.collectors.opencoesione import (
    EXPECTED_HEADERS,
    OpenCoesioneRowError,
    OpenCoesioneSchemaError,
    parse_operation_list_zip,
)


def _valid_row() -> list[str]:
    return [
        "FESR",
        "OBJ",
        "OP-1",
        "CUP1",
        "LEGAL123",
        "Comune X",
        "Water upgrade",
        "New pumps and controls",
        "2026-01-01",
        "2027-12-31",
        "1000000",
        "800000",
        "0.6",
        "00100",
        "IT",
        "Water",
        "2026-08-31",
    ]


def _zip_csv(
    headers: tuple[str, ...] = EXPECTED_HEADERS,
    rows: list[list[str]] | None = None,
) -> bytes:
    rows = rows or [_valid_row()]
    text = ";".join(headers) + "\n" + "\n".join(";".join(row) for row in rows) + "\n"
    out = BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("beneficiari_2021-2027.csv", text.encode("utf-8"))
    return out.getvalue()


def test_known_valid_row_is_accepted() -> None:
    batch = parse_operation_list_zip(
        _zip_csv(), source_url="https://example.test/source.zip"
    )
    assert len(batch.operations) == 1
    operation = batch.operations[0]
    assert operation.operation_id == "OP-1"
    assert operation.operation_name == "Water upgrade"
    assert operation.operation_summary == "New pumps and controls"


def test_unexpected_field_fails_closed_before_admission() -> None:
    with pytest.raises(OpenCoesioneSchemaError):
        parse_operation_list_zip(
            _zip_csv(EXPECTED_HEADERS + ("Unexpected",)), source_url="x"
        )


def test_missing_field_fails_closed_before_admission() -> None:
    with pytest.raises(OpenCoesioneSchemaError):
        parse_operation_list_zip(_zip_csv(EXPECTED_HEADERS[:-1]), source_url="x")


def test_bad_row_rejects_entire_batch() -> None:
    good = _valid_row()
    bad = good.copy()
    bad[2] = ""
    with pytest.raises(OpenCoesioneRowError):
        parse_operation_list_zip(_zip_csv(rows=[good, bad]), source_url="x")
