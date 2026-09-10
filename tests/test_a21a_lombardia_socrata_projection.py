from __future__ import annotations

import pytest

from scripts.probe_a21a_lombardia_socrata_projection import (
    FORBIDDEN_ROW_FIELDS,
    SAFE_METADATA_FIELDS,
    projected_row_url,
    validate_metadata,
    validate_projected_rows,
)


def _metadata() -> dict[str, object]:
    columns: list[dict[str, str]] = []
    for field in SAFE_METADATA_FIELDS:
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


def test_metadata_confirms_transport_candidate_but_keeps_row_ingest_blocked() -> None:
    report = validate_metadata(_metadata())
    assert report["metadata_complete"] is True
    assert report["description_field_confirmed"] is True
    assert report["natural_person_identity_risk_confirmed"] is True
    assert report["row_ingest_allowed"] is False


def test_metadata_is_incomplete_if_project_description_field_disappears() -> None:
    metadata = _metadata()
    metadata["columns"] = [
        column
        for column in metadata["columns"]  # type: ignore[union-attr]
        if column["fieldName"] != "descrizione_operazione"
    ]
    report = validate_metadata(metadata)
    assert report["metadata_complete"] is False
    assert "descrizione_operazione" in report["missing_project_fields"]
    assert report["row_ingest_allowed"] is False


def test_projected_row_url_is_permanently_fail_closed() -> None:
    with pytest.raises(RuntimeError, match="row ingest is blocked"):
        projected_row_url()


def test_any_row_payload_is_rejected_without_inspection() -> None:
    report = validate_projected_rows([{"descrizione_operazione": "must not be inspected"}])
    assert report["projection_gate_pass"] is False
    assert report["row_ingest_allowed"] is False
    assert report["candidate_status"] == "BLOCKED_FREE_TEXT_ZERO_PII_CONTRACT"


def test_identity_fields_remain_explicitly_classified_as_forbidden() -> None:
    assert "nome_del_beneficiario" in FORBIDDEN_ROW_FIELDS
    assert "codice_del_beneficiario" in FORBIDDEN_ROW_FIELDS
