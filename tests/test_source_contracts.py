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
    contract = require_live_source("ted_search_api", as_of=date(2026, 9, 1))
    assert contract.status is SourceStatus.APPROVED
    assert contract.rights_status is SourceStatus.APPROVED
    assert contract.access_status is SourceStatus.APPROVED
    assert contract.data_safety_status is SourceStatus.APPROVED
    assert contract.commercial_reuse_allowed is True
    assert contract.automated_access_allowed is True
    assert contract.server_side_projection is True
    assert contract.max_requests_per_minute == 600


def test_ted_approved_review_is_current_in_ci() -> None:
    require_live_source("ted_search_api")


def test_ted_review_expires_fail_closed() -> None:
    with pytest.raises(SourceComplianceExpiredError):
        require_live_source("ted_search_api", as_of=date(2026, 12, 1))


@pytest.mark.parametrize(
    "source_id",
    [
        "pt2030_project_search",
        "pt2030_project_detail",
        "pt2030_operations_bulk",
        "portal_base",
    ],
)
def test_nonapproved_sources_fail_before_retrieval(source_id: str) -> None:
    with pytest.raises(SourceNotApprovedError):
        require_live_source(source_id, as_of=date(2026, 9, 1))


def test_known_broad_response_routes_are_hard_blocked() -> None:
    assert SOURCE_CONTRACTS["pt2030_project_detail"].status is SourceStatus.BLOCKED
    assert SOURCE_CONTRACTS["pt2030_operations_bulk"].status is SourceStatus.BLOCKED
    assert SOURCE_CONTRACTS["portal_base"].status is SourceStatus.BLOCKED
    assert SOURCE_CONTRACTS["portal_base"].server_side_projection is False


def test_pt2030_project_search_remains_conditional() -> None:
    contract = SOURCE_CONTRACTS["pt2030_project_search"]
    assert contract.status is SourceStatus.CONDITIONAL
    assert contract.rights_status is SourceStatus.CONDITIONAL
    assert contract.data_safety_status is SourceStatus.CONDITIONAL


def test_pt2030_bulk_does_not_inherit_unconditional_rights_from_portal_default() -> None:
    contract = SOURCE_CONTRACTS["pt2030_operations_bulk"]
    assert contract.rights_status is SourceStatus.CONDITIONAL
    assert contract.commercial_reuse_allowed is None
    assert contract.data_safety_status is SourceStatus.BLOCKED


def test_base_access_and_rights_stay_conditional_even_though_public_extraction_exists() -> None:
    contract = SOURCE_CONTRACTS["portal_base"]
    assert contract.rights_status is SourceStatus.CONDITIONAL
    assert contract.access_status is SourceStatus.CONDITIONAL
    assert contract.data_safety_status is SourceStatus.BLOCKED


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


def test_unknown_source_fails_closed() -> None:
    with pytest.raises(SourceNotApprovedError):
        require_live_source("unregistered-source", as_of=date(2026, 9, 1))
