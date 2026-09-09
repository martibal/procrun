from __future__ import annotations

from scripts.probe_a21a_lombardia_socrata_projection import (
    FORBIDDEN_FIELDS,
    SAFE_FIELDS,
    projected_row_url,
    validate_metadata,
    validate_projected_rows,
)


def _metadata() -> dict[str, object]:
    columns: list[dict[str, str]] = []
    for field in SAFE_FIELDS:
        description = "Descrizione del progetto" if field == "descrizione_operazione" else field
        columns.append({"fieldName": field, "description": description})
    columns.extend(
        [
            {
                "fieldName": "nome_del_beneficiario",
                "description": "Nome dell'impresa o della persona fisica a cui è concesso il contributo",
            },
            {"fieldName": "codice_del_beneficiario", "description": "Codice del beneficiario"},
        ]
    )
    return {"columns": columns}


def test_metadata_gate_requires_description_and_identity_boundary() -> None:
    report = validate_metadata(_metadata())
    assert report["metadata_gate_pass"] is True
    assert report["description_contract_ok"] is True
    assert report["beneficiary_identity_confirmed"] is True


def test_metadata_gate_fails_if_safe_field_disappears() -> None:
    metadata = _metadata()
    metadata["columns"] = [
        column
        for column in metadata["columns"]  # type: ignore[union-attr]
        if column["fieldName"] != "descrizione_operazione"
    ]
    report = validate_metadata(metadata)
    assert report["metadata_gate_pass"] is False
    assert "descrizione_operazione" in report["missing_safe_fields"]


def test_projection_url_requests_only_safe_fields() -> None:
    url = projected_row_url()
    assert "%24select=" in url
    for field in SAFE_FIELDS:
        assert field in url
    for field in FORBIDDEN_FIELDS:
        assert field not in url


def test_projected_row_rejects_any_unexpected_field() -> None:
    row = {field: "x" for field in SAFE_FIELDS}
    row["descrizione_operazione"] = "Intervento di riqualificazione energetica."
    assert validate_projected_rows([row])["projection_gate_pass"] is True

    row["nome_del_beneficiario"] = "must never be received"
    report = validate_projected_rows([row])
    assert report["projection_gate_pass"] is False
    assert report["forbidden_fields_returned"] == ["nome_del_beneficiario"]
