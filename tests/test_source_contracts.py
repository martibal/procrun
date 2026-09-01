import pytest

from procrun.source_contracts import (
    SOURCE_CONTRACTS,
    SourceNotApprovedError,
    SourceStatus,
    require_live_source,
)


def test_ted_is_live_approved_with_projection() -> None:
    contract = require_live_source("ted_search_api")
    assert contract.status is SourceStatus.APPROVED
    assert contract.server_side_projection is True


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
        require_live_source(source_id)


def test_pt2030_bulk_and_detail_are_hard_blocked() -> None:
    assert SOURCE_CONTRACTS["pt2030_project_detail"].status is SourceStatus.BLOCKED
    assert SOURCE_CONTRACTS["pt2030_operations_bulk"].status is SourceStatus.BLOCKED


def test_unknown_source_fails_closed() -> None:
    with pytest.raises(SourceNotApprovedError):
        require_live_source("unregistered-source")
