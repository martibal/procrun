from datetime import date

import pytest

from procrun.source_contracts import (
    SOURCE_CONTRACTS,
    SourceComplianceExpiredError,
    SourceNotApprovedError,
    SourceStatus,
    public_attributions,
    require_live_source,
)


def test_ted_is_live_approved_only_when_all_compliance_gates_are_green() -> None:
    contract = require_live_source("ted_search_api", as_of=date(2026, 9, 4))
    assert contract.status is SourceStatus.APPROVED
    assert contract.rights_status is SourceStatus.APPROVED
    assert contract.access_status is SourceStatus.APPROVED
    assert contract.data_safety_status is SourceStatus.APPROVED
    assert contract.commercial_reuse_allowed is True
    assert contract.automated_access_allowed is True
    assert contract.server_side_projection is True
    assert contract.max_requests_per_minute == 600


def test_opencoesione_exact_pilot_route_is_registered_and_approved() -> None:
    contract = require_live_source("opencoesione_2021_2027_operations", as_of=date(2026, 9, 4))
    assert contract.status is SourceStatus.APPROVED
    assert contract.rights_status is SourceStatus.APPROVED
    assert contract.access_status is SourceStatus.APPROVED
    assert contract.data_safety_status is SourceStatus.APPROVED
    assert contract.commercial_reuse_allowed is True
    assert contract.automated_access_allowed is True
    assert "beneficiari_PR_FESR_LOMBARDIA.zip" in contract.retrieval_route
    assert any("all-program ZIP" in item for item in contract.obligations)
    assert any("general OpenCoesione API" in item for item in contract.obligations)


def test_approved_reviews_are_current_in_ci() -> None:
    require_live_source("ted_search_api")
    require_live_source("opencoesione_2021_2027_operations")


def test_approved_review_expires_fail_closed() -> None:
    for source_id in ("ted_search_api", "opencoesione_2021_2027_operations"):
        with pytest.raises(SourceComplianceExpiredError):
            require_live_source(source_id, as_of=date(2026, 12, 1))


@pytest.mark.parametrize(
    "source_id",
    [
        "prr_projects_dados_gov",
        "pt2030_project_search",
        "pt2030_project_detail",
        "pt2030_operations_bulk",
        "portal_base",
        "base_announcements_bulk",
        "dre_part_l_rss",
    ],
)
def test_nonapproved_sources_fail_before_retrieval(source_id: str) -> None:
    with pytest.raises(SourceNotApprovedError):
        require_live_source(source_id, as_of=date(2026, 9, 4))


def test_prr_projects_are_permanently_blocked_not_waiting() -> None:
    contract = SOURCE_CONTRACTS["prr_projects_dados_gov"]
    assert contract.status is SourceStatus.BLOCKED
    assert contract.rights_status is SourceStatus.BLOCKED
    assert contract.access_status is SourceStatus.APPROVED
    assert contract.data_safety_status is SourceStatus.BLOCKED
    assert "Category B" in contract.reason
    assert "closed, not waiting" in contract.reason
    assert any("download-then-filter" in item for item in contract.obligations)


def test_known_broad_response_routes_are_hard_blocked() -> None:
    for source_id in (
        "pt2030_project_search",
        "pt2030_project_detail",
        "pt2030_operations_bulk",
        "portal_base",
        "base_announcements_bulk",
    ):
        assert SOURCE_CONTRACTS[source_id].status is SourceStatus.BLOCKED


def test_base_announcement_bulk_has_rights_but_fails_pre_receipt_safety() -> None:
    contract = SOURCE_CONTRACTS["base_announcements_bulk"]
    assert contract.rights_status is SourceStatus.APPROVED
    assert contract.access_status is SourceStatus.APPROVED
    assert contract.commercial_reuse_allowed is True
    assert contract.data_safety_status is SourceStatus.BLOCKED


def test_dre_rss_can_change_only_from_already_public_documentation() -> None:
    contract = SOURCE_CONTRACTS["dre_part_l_rss"]
    assert contract.status is SourceStatus.CONDITIONAL
    assert contract.access_status is SourceStatus.APPROVED
    assert contract.data_safety_status is SourceStatus.CONDITIONAL
    assert contract.commercial_reuse_allowed is None
    assert any("RSS absence" in item for item in contract.obligations)
    assert any("already-public documentation" in item for item in contract.obligations)


def test_approved_sources_have_frozen_legal_basis_and_attribution() -> None:
    for contract in SOURCE_CONTRACTS.values():
        if contract.status is not SourceStatus.APPROVED:
            continue
        assert contract.legal_basis_urls
        assert contract.terms_reviewed_on <= contract.terms_review_due_on
        assert contract.attribution_required
        assert contract.attribution_text


def test_public_attribution_is_deduplicated() -> None:
    statements = public_attributions(["ted_search_api", "ted_search_api"])
    assert len(statements) == 1
    assert "Tenders Electronic Daily" in statements[0]


def test_open_coesione_attribution_is_customer_safe() -> None:
    statements = public_attributions(["opencoesione_2021_2027_operations"])
    assert len(statements) == 1
    assert "OpenCoesione / MEF-RGS-IGRUE" in statements[0]


def test_unknown_source_fails_closed() -> None:
    with pytest.raises(SourceNotApprovedError):
        require_live_source("unregistered-source", as_of=date(2026, 9, 4))
