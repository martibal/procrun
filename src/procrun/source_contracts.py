"""Frozen production source-approval registry.

No live collector may run unless its retrieval route is explicitly APPROVED. This prevents
accidental use of public-but-PII-bearing bulk/detail sources while source audits are open.
"""

from dataclasses import dataclass
from enum import StrEnum


class SourceStatus(StrEnum):
    APPROVED = "APPROVED"
    CONDITIONAL = "CONDITIONAL"
    BLOCKED = "BLOCKED"


class SourceNotApprovedError(RuntimeError):
    """Raised when code attempts to use a non-approved production source."""


@dataclass(frozen=True)
class SourceContract:
    source_id: str
    status: SourceStatus
    retrieval_route: str
    reason: str
    server_side_projection: bool = False


SOURCE_CONTRACTS = {
    "ted_search_api": SourceContract(
        source_id="ted_search_api",
        status=SourceStatus.APPROVED,
        retrieval_route="POST /v3/notices/search with explicit fields projection",
        reason="TED supports server-side field projection; schema drift still fails closed.",
        server_side_projection=True,
    ),
    "pt2030_project_search": SourceContract(
        source_id="pt2030_project_search",
        status=SourceStatus.CONDITIONAL,
        retrieval_route="Mais Transparencia Portugal 2030 project-only search surface",
        reason=(
            "Useful discovery cards are visible, but transport-level zero-PII safety and the "
            "required scope/temporal field surface are not yet proven."
        ),
    ),
    "pt2030_project_detail": SourceContract(
        source_id="pt2030_project_detail",
        status=SourceStatus.BLOCKED,
        retrieval_route="Mais Transparencia Portugal 2030 full project detail page",
        reason="The page includes beneficiary content in the same response.",
    ),
    "pt2030_operations_bulk": SourceContract(
        source_id="pt2030_operations_bulk",
        status=SourceStatus.BLOCKED,
        retrieval_route="AD&C / dados.gov.pt PT2030 approved-operations bulk workbook",
        reason=(
            "Bulk operations data has a broader field surface including beneficiary/tax data; "
            "download-then-filter is prohibited."
        ),
    ),
    "portal_base": SourceContract(
        source_id="portal_base",
        status=SourceStatus.BLOCKED,
        retrieval_route="Portal BASE / IMPIC APIBase2 contract and announcement endpoints",
        reason=(
            "Official documentation states that the API returns the same fields as the broad "
            "dados.gov files and documents supplier/adjudicatario identifiers in responses. "
            "No server-side output field projection is documented, so prohibited fields cannot "
            "be excluded before receipt."
        ),
        server_side_projection=False,
    ),
}


def require_live_source(source_id: str) -> SourceContract:
    """Return an approved source contract or fail before any network retrieval."""

    try:
        contract = SOURCE_CONTRACTS[source_id]
    except KeyError as exc:
        raise SourceNotApprovedError(f"unknown source contract: {source_id}") from exc

    if contract.status is not SourceStatus.APPROVED:
        raise SourceNotApprovedError(
            f"source {source_id} is {contract.status}; live retrieval is prohibited"
        )
    return contract
