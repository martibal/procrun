from __future__ import annotations

from scripts.probe_a21a_openbdap_metadata import evaluate_metadata_text


def test_blocks_structured_only_metadata() -> None:
    report = evaluate_metadata_text(
        "Dati anagrafici: CUP, stato, natura, tipologia, settore, sottosettore e categoria."
    )
    assert report["candidate_status"] == "BLOCKED_INSUFFICIENT_EVIDENCE_TEXT"
    assert report["project_rows_requested"] is False
    assert report["odata_rows_requested"] is False


def test_allows_next_gate_only_when_project_wording_is_documented() -> None:
    report = evaluate_metadata_text(
        "Il dataset contiene CUP, stato e descrizione progetto per ciascuna opera."
    )
    assert report["candidate_status"] == "PROCEED_TO_PROJECTION_GATE"
    assert "descrizione progetto" in report["evidence_text_concept_hits"]


def test_generic_dataset_description_does_not_count_as_project_evidence() -> None:
    report = evaluate_metadata_text(
        "Descrizione: dati finanziari e procedurali delle opere pubbliche."
    )
    assert report["candidate_status"] == "BLOCKED_INSUFFICIENT_EVIDENCE_TEXT"
