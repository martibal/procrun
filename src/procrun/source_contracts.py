"""Frozen production source approval and compliance registry.

A live source must be approved entirely from already-public evidence. No human-dependent
clarification path exists: if public evidence cannot close a source, the source is blocked.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class SourceStatus(StrEnum):
    APPROVED = "APPROVED"
    CONDITIONAL = "CONDITIONAL"
    BLOCKED = "BLOCKED"


class SourceNotApprovedError(RuntimeError):
    """Raised when code attempts to use a non-approved production source."""


class SourceComplianceExpiredError(SourceNotApprovedError):
    """Raised when the public-evidence review for an approved source is stale."""


@dataclass(frozen=True)
class SourceContract:
    source_id: str
    status: SourceStatus
    retrieval_route: str
    reason: str
    rights_status: SourceStatus
    access_status: SourceStatus
    data_safety_status: SourceStatus
    commercial_reuse_allowed: bool | None
    automated_access_allowed: bool | None
    license_basis: str
    legal_basis_urls: tuple[str, ...]
    terms_reviewed_on: date
    terms_review_due_on: date
    attribution_required: bool
    attribution_text: str | None
    obligations: tuple[str, ...]
    server_side_projection: bool = False
    max_requests_per_minute: int | None = None


_REVIEWED_ON = date(2026, 9, 4)
_REVIEW_DUE_ON = date(2026, 11, 30)

SOURCE_CONTRACTS = {
    "ted_search_api": SourceContract(
        source_id="ted_search_api",
        status=SourceStatus.APPROVED,
        retrieval_route="POST /v3/notices/search with explicit fields projection",
        reason="Public TED documentation provides the server-side field boundary required by ProcRun.",
        rights_status=SourceStatus.APPROVED,
        access_status=SourceStatus.APPROVED,
        data_safety_status=SourceStatus.APPROVED,
        commercial_reuse_allowed=True,
        automated_access_allowed=True,
        license_basis="TED legal notice / Commission Decision 2011/833/EU reuse policy.",
        legal_basis_urls=(
            "https://docs.ted.europa.eu/api/latest/search.html",
            "https://ted.europa.eu/en/legal-notice",
            "https://ted.europa.eu/en/news/fair-usage-policy-on-ted",
            "https://eur-lex.europa.eu/eli/dec/2011/833/oj",
        ),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=True,
        attribution_text=(
            "Source: Tenders Electronic Daily (TED), Publications Office of the European Union. "
            "ProcRun transforms/classifies source data; derived analysis is not an official EU "
            "publication or endorsement."
        ),
        obligations=(
            "Use only the frozen projected field allowlist.",
            "Acknowledge TED/EU and distinguish ProcRun transformations.",
            "Do not imply EU endorsement or distort source meaning.",
            "Use the Search API, not automated CMS scraping.",
        ),
        server_side_projection=True,
        max_requests_per_minute=600,
    ),
    "opencoesione_2021_2027_operations": SourceContract(
        source_id="opencoesione_2021_2027_operations",
        status=SourceStatus.APPROVED,
        retrieval_route=(
            "GET https://opencoesione.gov.it/it/opendata/beneficiari/2021-2027/"
            "beneficiari_PR_FESR_LOMBARDIA.zip; exact PR FESR Lombardia 2021-2027 "
            "operation-list ZIP/CSV live-transfer pilot"
        ),
        reason=(
            "The public 2021-2027 operation-list catalogue, CC BY 4.0 publication contract and RGS "
            "monitoring guidance approve the bounded per-program operation-list class. The current "
            "live pilot is narrowed to PR FESR Lombardia because the all-program ZIP returned HTTP "
            "403 from a clean CI runner."
        ),
        rights_status=SourceStatus.APPROVED,
        access_status=SourceStatus.APPROVED,
        data_safety_status=SourceStatus.APPROVED,
        commercial_reuse_allowed=True,
        automated_access_allowed=True,
        license_basis=(
            "OpenCoesione CC BY 4.0 licence and 2021-2027 per-program operation-list publication."
        ),
        legal_basis_urls=(
            "https://opencoesione.gov.it/en/licenza/",
            "https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/",
            "https://opencoesione.gov.it/media/uploads/linee-guida_comunicazione-e-opencoesione_v2_0.pdf",
            "https://opencoesione.gov.it/media/uploads/20241203_vademecum-monitoraggio-puc-rgs-vers10.pdf",
        ),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=True,
        attribution_text=(
            "Source: OpenCoesione / MEF-RGS-IGRUE, PR FESR Lombardia 2021-2027 operation list, "
            "CC BY 4.0. ProcRun-derived analysis is not an official OpenCoesione or Italian-"
            "government output."
        ),
        obligations=(
            "Use only the frozen PR FESR Lombardia per-program ZIP/CSV pilot route until other "
            "programme routes pass transfer acceptance.",
            "Validate the complete frozen header contract before admitting any row.",
            "Fail closed on missing, renamed, reordered or additional fields.",
            "Do not ingest the all-program ZIP while clean automated retrieval returns HTTP 403.",
            "Do not ingest the general OpenCoesione API, project-detail HTML or entity datasets.",
            "Do not retain beneficiary identity fields in the FundingProject analytical object.",
        ),
    ),
    "prr_projects_dados_gov": SourceContract(
        source_id="prr_projects_dados_gov",
        status=SourceStatus.BLOCKED,
        retrieval_route="Portugal PRR Projects distribution via dados.gov.pt",
        reason=(
            "Category B: human-authored project text lacks an already-public exact pre-publication "
            "safety contract for every required field. Under the permanent zero-contact rule this "
            "route is closed, not waiting."
        ),
        rights_status=SourceStatus.BLOCKED,
        access_status=SourceStatus.APPROVED,
        data_safety_status=SourceStatus.BLOCKED,
        commercial_reuse_allowed=None,
        automated_access_allowed=True,
        license_basis="Route permanently ineligible for the intelligence plane under current rules.",
        legal_basis_urls=(
            "https://dados.gov.pt/pt/termos-de-utilizacao",
            "https://dados.gov.pt/pt/datasets/dataset-estrutura-de-missao-prr-projetos-2/",
        ),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=False,
        attribution_text=None,
        obligations=(
            "Never retrieve this route into the intelligence plane.",
            "Never use download-then-filter as a privacy mechanism.",
            "If only human-dependent clarification could change the decision, reject the source.",
        ),
    ),
    "pt2030_project_search": SourceContract(
        source_id="pt2030_project_search",
        status=SourceStatus.BLOCKED,
        retrieval_route="Mais Transparencia Portugal 2030 project search/detail surface",
        reason=(
            "Category B human-authored project surface; permanently closed to intelligence ingest."
        ),
        rights_status=SourceStatus.BLOCKED,
        access_status=SourceStatus.BLOCKED,
        data_safety_status=SourceStatus.BLOCKED,
        commercial_reuse_allowed=None,
        automated_access_allowed=None,
        license_basis="No eligible production route under the permanent zero-contact/zero-PII rule.",
        legal_basis_urls=("https://transparencia.gov.pt/pt/termos-e-condicoes/",),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=False,
        attribution_text=None,
        obligations=("Never scrape or ingest this portal route for production intelligence.",),
    ),
    "pt2030_project_detail": SourceContract(
        source_id="pt2030_project_detail",
        status=SourceStatus.BLOCKED,
        retrieval_route="Mais Transparencia full project detail page",
        reason="Category B human-authored detail and beneficiary surface.",
        rights_status=SourceStatus.BLOCKED,
        access_status=SourceStatus.BLOCKED,
        data_safety_status=SourceStatus.BLOCKED,
        commercial_reuse_allowed=None,
        automated_access_allowed=None,
        license_basis="Route permanently ineligible for intelligence ingestion.",
        legal_basis_urls=("https://transparencia.gov.pt/pt/termos-e-condicoes/",),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=False,
        attribution_text=None,
        obligations=("Never ingest this route into the intelligence environment.",),
    ),
    "pt2030_operations_bulk": SourceContract(
        source_id="pt2030_operations_bulk",
        status=SourceStatus.BLOCKED,
        retrieval_route="PT2030 approved-operations bulk workbook",
        reason="Broad beneficiary/tax surface; download-then-filter is prohibited.",
        rights_status=SourceStatus.BLOCKED,
        access_status=SourceStatus.APPROVED,
        data_safety_status=SourceStatus.BLOCKED,
        commercial_reuse_allowed=None,
        automated_access_allowed=True,
        license_basis="Route permanently ineligible for intelligence ingestion.",
        legal_basis_urls=("https://dados.gov.pt/pt/termos-de-utilizacao",),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=False,
        attribution_text=None,
        obligations=("Never download the broad workbook into the intelligence environment.",),
    ),
    "portal_base": SourceContract(
        source_id="portal_base",
        status=SourceStatus.BLOCKED,
        retrieval_route="Portal BASE / IMPIC APIBase2",
        reason="Broad identity-bearing response with no approved pre-receipt projection.",
        rights_status=SourceStatus.BLOCKED,
        access_status=SourceStatus.BLOCKED,
        data_safety_status=SourceStatus.BLOCKED,
        commercial_reuse_allowed=None,
        automated_access_allowed=True,
        license_basis="Current route is Category B for ProcRun intelligence ingestion.",
        legal_basis_urls=("https://www.base.gov.pt/APIBase2",),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=False,
        attribution_text=None,
        obligations=("Do not activate the broad API route.",),
    ),
    "base_announcements_bulk": SourceContract(
        source_id="base_announcements_bulk",
        status=SourceStatus.BLOCKED,
        retrieval_route="dados.gov.pt Portal BASE announcements annual JSON/XLSX",
        reason=(
            "Rights are open but the broad transport lacks the required pre-receipt safety boundary."
        ),
        rights_status=SourceStatus.APPROVED,
        access_status=SourceStatus.APPROVED,
        data_safety_status=SourceStatus.BLOCKED,
        commercial_reuse_allowed=True,
        automated_access_allowed=True,
        license_basis="Dataset-specific dados.gov.pt public-domain licence.",
        legal_basis_urls=(
            "https://dados.gov.pt/pt/datasets/"
            "contratos-publicos-portal-base-impic-anuncios-de-2012-a-2026/",
        ),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=False,
        attribution_text=None,
        obligations=("Never download the annual bulk file into the intelligence plane.",),
    ),
    "dre_part_l_rss": SourceContract(
        source_id="dre_part_l_rss",
        status=SourceStatus.CONDITIONAL,
        retrieval_route="Diário da República Série II, Parte L public RSS/index",
        reason=(
            "Passive public-documentation candidate only. It remains disabled unless already-public "
            "documentation itself establishes an exact safe item contract."
        ),
        rights_status=SourceStatus.CONDITIONAL,
        access_status=SourceStatus.APPROVED,
        data_safety_status=SourceStatus.CONDITIONAL,
        commercial_reuse_allowed=None,
        automated_access_allowed=True,
        license_basis="Public RSS exists; exact production contract is not established.",
        legal_basis_urls=("https://diariodarepublica.pt/dr/geral/rss",),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=False,
        attribution_text=None,
        obligations=(
            "Do not use RSS absence as national procurement absence.",
            "Do not follow RSS links into full notices in the intelligence plane.",
            "Only already-public documentation may ever change this status.",
        ),
    ),
}


def _validate_registry() -> None:
    for contract in SOURCE_CONTRACTS.values():
        if contract.terms_reviewed_on > contract.terms_review_due_on:
            raise ValueError(f"invalid compliance review dates for {contract.source_id}")
        if not contract.legal_basis_urls:
            raise ValueError(f"missing legal basis URLs for {contract.source_id}")
        if contract.attribution_required and not contract.attribution_text:
            raise ValueError(f"missing attribution text for {contract.source_id}")
        if contract.status is SourceStatus.APPROVED:
            gates = (contract.rights_status, contract.access_status, contract.data_safety_status)
            if any(gate is not SourceStatus.APPROVED for gate in gates):
                raise ValueError(f"approved source has non-approved gate: {contract.source_id}")
            if contract.commercial_reuse_allowed is not True:
                raise ValueError(f"approved source lacks reuse approval: {contract.source_id}")
            if contract.automated_access_allowed is not True:
                raise ValueError(f"approved source lacks automated access: {contract.source_id}")


_validate_registry()


def require_live_source(source_id: str, *, as_of: date | None = None) -> SourceContract:
    try:
        contract = SOURCE_CONTRACTS[source_id]
    except KeyError as exc:
        raise SourceNotApprovedError(f"unknown source contract: {source_id}") from exc
    if contract.status is not SourceStatus.APPROVED:
        raise SourceNotApprovedError(
            f"source {source_id} is {contract.status}; live retrieval is prohibited"
        )
    if any(
        status is not SourceStatus.APPROVED
        for status in (contract.rights_status, contract.access_status, contract.data_safety_status)
    ):
        raise SourceNotApprovedError(f"source {source_id} has a non-approved compliance gate")
    if contract.commercial_reuse_allowed is not True or contract.automated_access_allowed is not True:
        raise SourceNotApprovedError(f"source {source_id} lacks approved reuse/access")
    effective_date = as_of or date.today()
    if effective_date > contract.terms_review_due_on:
        raise SourceComplianceExpiredError(
            f"source {source_id} compliance review expired on "
            f"{contract.terms_review_due_on.isoformat()}"
        )
    return contract


def public_attributions(source_ids: Iterable[str]) -> tuple[str, ...]:
    statements: list[str] = []
    seen: set[str] = set()
    for source_id in source_ids:
        try:
            contract = SOURCE_CONTRACTS[source_id]
        except KeyError as exc:
            raise SourceNotApprovedError(f"unknown source contract: {source_id}") from exc
        if contract.attribution_required:
            if contract.attribution_text is None:
                raise SourceNotApprovedError(
                    f"source {source_id} requires attribution but has none"
                )
            if contract.attribution_text not in seen:
                statements.append(contract.attribution_text)
                seen.add(contract.attribution_text)
    return tuple(statements)
