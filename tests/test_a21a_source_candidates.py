from __future__ import annotations

import pytest

from procrun.a21a_source_candidates import (
    CANDIDATES,
    CandidateStatus,
    require_metadata_probe,
    require_row_ingest,
)


def test_opencoesione_operation_list_is_approved_for_a21a() -> None:
    candidate = require_row_ingest("opencoesione_2021_2027_operations")
    assert candidate.status is CandidateStatus.APPROVED
    assert candidate.row_ingest_allowed is True
    assert candidate.requires_server_side_projection is False
    assert "SINTESI_PROG" in candidate.reason
    assert "1,300" in candidate.reason
    assert "natural persons" in candidate.reason


def test_opencoesione_general_api_is_blocked() -> None:
    candidate = CANDIDATES["opencoesione_general_api"]
    assert candidate.status is CandidateStatus.BLOCKED
    assert candidate.row_ingest_allowed is False
    assert "soggetto" in candidate.forbidden_full_dataset_fields


def test_opencoesione_search_csv_is_blocked() -> None:
    candidate = CANDIDATES["opencoesione_search_csv"]
    assert candidate.status is CandidateStatus.BLOCKED
    assert candidate.row_ingest_allowed is False
    assert candidate.forbidden_full_dataset_fields == (
        "SOGGETTI_PROGRAMMATORI",
        "SOGGETTI_ATTUATORI",
    )


def test_openbdap_is_closed_after_metadata_utility_gate() -> None:
    candidate = require_metadata_probe("openbdap_mop_lombardia_odata")
    assert candidate.status is CandidateStatus.BLOCKED
    assert candidate.requires_server_side_projection is True
    assert candidate.row_ingest_allowed is False
    assert "project-title or project-description" in candidate.reason
    assert "Codice Fiscale Titolare" in candidate.forbidden_full_dataset_fields


def test_lombardia_socrata_is_closed_after_content_safety_review() -> None:
    candidate = require_metadata_probe("lombardia_pr_fesr_socrata")
    assert candidate.status is CandidateStatus.BLOCKED
    assert candidate.row_ingest_allowed is False
    assert candidate.requires_server_side_projection is True
    assert "public Open Data governance" in candidate.reason
    assert "absolute zero-PII" in candidate.reason
    assert candidate.forbidden_full_dataset_fields == (
        "nome_del_beneficiario",
        "codice_del_beneficiario",
    )


@pytest.mark.parametrize(
    "source_id",
    [
        "opencoesione_general_api",
        "opencoesione_search_csv",
        "openbdap_mop_lombardia_odata",
        "lombardia_pr_fesr_socrata",
    ],
)
def test_blocked_candidates_cannot_ingest_rows(source_id: str) -> None:
    with pytest.raises(RuntimeError, match="row ingest not approved"):
        require_row_ingest(source_id)
