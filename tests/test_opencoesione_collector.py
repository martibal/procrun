import zipfile
from io import BytesIO

import pytest

from procrun.collectors.opencoesione import (
    EXPECTED_HEADERS,
    OpenCoesioneRowError,
    OpenCoesioneSchemaError,
    parse_operation_list_zip,
    to_funding_projects,
)
from procrun.collectors.opencoesione_live import (
    OPENCOESIONE_CANONICAL_ZIP_URL,
    _validate_zip_final_url,
)


def _valid_row() -> list[str]:
    return [
        "PRL",
        "PR FESR Lombardia 2021-2027",
        "OP-1",
        "CUP1",
        "Water upgrade",
        "New pumps and controls",
        "2026-08-31",
        "LEGAL123",
        "Comune X",
        "1000000",
        "800000",
        "FESR",
        "2021-2027",
        "Water",
        "OBJ",
        "2026-01-01",
        "2027-12-31",
        "0.6",
        "IT",
        "00100",
    ]


def _zip_csv(
    headers: tuple[str, ...] = EXPECTED_HEADERS,
    rows: list[list[str]] | None = None,
) -> bytes:
    rows = rows or [_valid_row()]
    text = f"{';'.join(headers)}\n" + "\n".join(";".join(row) for row in rows) + "\n"
    out = BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("beneficiari_2021-2027.csv", text.encode("utf-8"))
    return out.getvalue()


def test_known_valid_row_is_accepted() -> None:
    operation = parse_operation_list_zip(
        _zip_csv(), source_url="https://example.test/source.zip"
    ).operations[0]
    assert operation.operation_id == "OP-1"
    assert operation.cup == "CUP1"
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


def test_reordered_schema_fails_closed() -> None:
    reordered = list(EXPECTED_HEADERS)
    reordered[0], reordered[1] = reordered[1], reordered[0]
    with pytest.raises(OpenCoesioneSchemaError, match="order_changed=True"):
        parse_operation_list_zip(_zip_csv(tuple(reordered)), source_url="x")


def test_bad_row_rejects_entire_batch() -> None:
    good = _valid_row()
    bad = good.copy()
    bad[2] = ""
    with pytest.raises(OpenCoesioneRowError):
        parse_operation_list_zip(_zip_csv(rows=[good, bad]), source_url="x")


def test_missing_summary_uses_exact_title_as_source_evidenced_fallback() -> None:
    row = _valid_row()
    row[5] = ""
    operation = parse_operation_list_zip(
        _zip_csv(rows=[row]), source_url="https://example.test/source.zip"
    ).operations[0]
    assert operation.operation_name == "Water upgrade"
    assert operation.operation_summary == "Water upgrade"


def test_missing_title_uses_exact_summary_as_source_evidenced_fallback() -> None:
    row = _valid_row()
    row[4] = ""
    operation = parse_operation_list_zip(
        _zip_csv(rows=[row]), source_url="https://example.test/source.zip"
    ).operations[0]
    assert operation.operation_name == "New pumps and controls"
    assert operation.operation_summary == "New pumps and controls"


def test_missing_title_and_summary_still_rejects_entire_batch() -> None:
    row = _valid_row()
    row[4] = ""
    row[5] = ""
    with pytest.raises(OpenCoesioneRowError, match="both operation name and summary"):
        parse_operation_list_zip(_zip_csv(rows=[row]), source_url="x")


def test_canonical_mapping_uses_cup_for_ted_linkage_and_never_retains_identity() -> None:
    project = to_funding_projects(
        parse_operation_list_zip(
            _zip_csv(), source_url="https://example.test/source.zip"
        )
    )[0]
    assert project.operation_code == "CUP1"
    assert project.project_title == "Water upgrade"
    assert project.project_scope_text == "New pumps and controls"
    assert project.region == "Lombardia"
    assert project.nuts_code == "ITC4"
    serialized = project.model_dump_json()
    assert "LEGAL123" not in serialized
    assert "Comune X" not in serialized


def test_fractional_eligible_expenditure_maps_down_without_overstatement() -> None:
    row = _valid_row()
    row[10] = "42030.52"
    batch = parse_operation_list_zip(
        _zip_csv(rows=[row]), source_url="https://example.test/source.zip"
    )
    assert str(batch.operations[0].eligible_expenditure_eur) == "42030.52"
    assert to_funding_projects(batch)[0].approved_funding_eur == 42030


def test_canonical_mapping_falls_back_to_local_id_when_cup_is_absent() -> None:
    row = _valid_row()
    row[3] = ""
    project = to_funding_projects(
        parse_operation_list_zip(
            _zip_csv(rows=[row]), source_url="https://example.test/source.zip"
        )
    )[0]
    assert project.operation_code == "OP-1"


def test_exact_canonical_zip_redirect_is_allowed() -> None:
    _validate_zip_final_url(OPENCOESIONE_CANONICAL_ZIP_URL)


def test_unknown_zip_redirect_still_fails_closed() -> None:
    with pytest.raises(OpenCoesioneSchemaError, match="outside frozen route"):
        _validate_zip_final_url(
            "https://opencoesione.gov.it/media/open_data/beneficiari/2021-2027/other.zip"
        )
