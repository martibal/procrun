"""Frozen production source approval and compliance registry.

A source is live-usable only when status, rights, automated access and pre-receipt
data safety are all APPROVED. Conditional sources are deliberately callable only
through metadata/research paths outside the intelligence collector.
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
    """Raised when the legal/access review for an approved source is stale."""


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


_REVIEWED_ON = date(2026, 9, 3)
_REVIEW_DUE_ON = date(2026, 11, 30)

SOURCE_CONTRACTS = {
    "ted_search_api": SourceContract(
        source_id="ted_search_api",
        status=SourceStatus.APPROVED,
        retrieval_route="POST /v3/notices/search with explicit fields projection",
        reason=(
            "TED supports reuse/value-added services and the Search API provides the "
            "server-side field boundary required by ProcRun."
        ),
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
            "Source: Tenders Electronic Daily (TED), Publications Office of the European "
            "Union. ProcRun transforms/classifies source data; derived analysis is not an "
            "official EU publication or endorsement."
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
    "prr_projects_dados_gov": SourceContract(
        source_id="prr_projects_dados_gov",
        status=SourceStatus.CONDITIONAL,
        retrieval_route=(
            "Estrutura de Missao Recuperar Portugal — PRR Projects distribution/API via "
            "dados.gov.pt; exact production machine route not yet frozen"
        ),
        reason=(
            "Published-evidence qualification is closed without approval. The PRR Projects dataset "
            "shows 'Licença não especificada', uses a broad machine distribution, and lacks a "
            "source-specific pre-publication guarantee that retained project text and structured "
            "fields cannot emit natural-person identifiers. Publisher confirmation is required."
        ),
        rights_status=SourceStatus.CONDITIONAL,
        access_status=SourceStatus.APPROVED,
        data_safety_status=SourceStatus.CONDITIONAL,
        commercial_reuse_allowed=None,
        automated_access_allowed=True,
        license_basis=(
            "dados.gov.pt general terms are supportive, but the PRR Projects dataset-specific "
            "metadata says licence unspecified; source-specific confirmation is required."
        ),
        legal_basis_urls=(
            "https://dados.gov.pt/pt/termos-de-utilizacao",
            "https://dados.gov.pt/pt/datasets/dataset-estrutura-de-missao-prr-projetos-2/",
            "https://recuperarportugal.gov.pt/monitorizacao-relatorios-de-monitorizacao/",
            "https://recuperarportugal.gov.pt/wp-content/uploads/2024/04/"
            "EMRP-Politica-de-Protecao-de-Dados_publicacao-20230717.pdf",
        ),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=True,
        attribution_text=(
            "Source: Estrutura de Missao Recuperar Portugal via dados.gov.pt. ProcRun "
            "transforms project scope into derived component intelligence."
        ),
        obligations=(
            "Do not call this source from a live intelligence collector while CONDITIONAL.",
            "Do not use download-then-filter as a privacy mechanism.",
            "Before approval freeze exact route, schema and retained field allowlist.",
            "Obtain source-specific commercial reuse confirmation for the Projects resource.",
            "Obtain authoritative source-specific pre-publication safety coverage for every "
            "retained structured and free-text field.",
        ),
    ),
    "pt2030_project_search": SourceContract(
        source_id="pt2030_project_search",
        status=SourceStatus.CONDITIONAL,
        retrieval_route="Mais Transparencia Portugal 2030 project-only search surface",
        reason="Human discovery route; exact transport rights/field boundary are not frozen.",
        rights_status=SourceStatus.CONDITIONAL,
        access_status=SourceStatus.CONDITIONAL,
        data_safety_status=SourceStatus.CONDITIONAL,
        commercial_reuse_allowed=None,
        automated_access_allowed=None,
        license_basis="Mais Transparencia site terms; no source-specific approval frozen.",
        legal_basis_urls=("https://transparencia.gov.pt/pt/termos-e-condicoes/",),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=False,
        attribution_text=None,
        obligations=("Do not scrape portal HTML for production ingestion.",),
    ),
    "pt2030_project_detail": SourceContract(
        source_id="pt2030_project_detail",
        status=SourceStatus.BLOCKED,
        retrieval_route="Mais Transparencia full project detail page",
        reason="The page includes beneficiary content in the same response.",
        rights_status=SourceStatus.CONDITIONAL,
        access_status=SourceStatus.CONDITIONAL,
        data_safety_status=SourceStatus.BLOCKED,
        commercial_reuse_allowed=None,
        automated_access_allowed=None,
        license_basis="Route not approved for intelligence ingestion.",
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
        reason=(
            "Broad response includes beneficiary/tax surface; download-then-filter is "
            "prohibited."
        ),
        rights_status=SourceStatus.CONDITIONAL,
        access_status=SourceStatus.APPROVED,
        data_safety_status=SourceStatus.BLOCKED,
        commercial_reuse_allowed=None,
        automated_access_allowed=True,
        license_basis="dados.gov.pt default terms do not cure the unsafe broad transport.",
        legal_basis_urls=("https://dados.gov.pt/pt/termos-de-utilizacao",),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=False,
        attribution_text=None,
        obligations=("Do not download the broad workbook into the intelligence environment.",),
    ),
    "portal_base": SourceContract(
        source_id="portal_base",
        status=SourceStatus.BLOCKED,
        retrieval_route="Portal BASE / IMPIC APIBase2",
        reason=(
            "The documented API response cannot exclude prohibited identity-bearing fields before "
            "receipt and exposes no server-side output projection. IMPIC also documents that BASE "
            "announcement data can be delayed and less complete than Diário da República."
        ),
        rights_status=SourceStatus.CONDITIONAL,
        access_status=SourceStatus.CONDITIONAL,
        data_safety_status=SourceStatus.BLOCKED,
        commercial_reuse_allowed=None,
        automated_access_allowed=True,
        license_basis="API use requires IMPIC authorization; exact production reuse terms pending.",
        legal_basis_urls=(
            "https://www.base.gov.pt/APIBase2",
            "https://www.base.gov.pt/Base4/pt/documentacao/"
            "formas-de-obter-dados-sobre-os-contratos-publicos/",
        ),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=False,
        attribution_text=None,
        obligations=(
            "Do not activate while prohibited fields cannot be excluded pre-receipt.",
            "Obtain a bounded announcement response or source-specific no-person guarantee.",
            "Obtain exact historical/completeness semantics needed for the OPEN boundary.",
        ),
    ),
    "base_announcements_bulk": SourceContract(
        source_id="base_announcements_bulk",
        status=SourceStatus.BLOCKED,
        retrieval_route=(
            "dados.gov.pt IMPIC dataset: Contratos Públicos - Portal Base - Anúncios de 2012 a 2026"
        ),
        reason=(
            "The separate nationwide announcement dataset has historical coverage and a public-domain "
            "licence, but delivery is a broad annual JSON/XLSX resource without documented server-side "
            "field projection or a source-specific no-natural-person guarantee for all received text."
        ),
        rights_status=SourceStatus.APPROVED,
        access_status=SourceStatus.APPROVED,
        data_safety_status=SourceStatus.BLOCKED,
        commercial_reuse_allowed=True,
        automated_access_allowed=True,
        license_basis="Dataset-specific dados.gov.pt licence: Outra (Domínio Público).",
        legal_basis_urls=(
            "https://dados.gov.pt/pt/datasets/"
            "contratos-publicos-portal-base-impic-anuncios-de-2012-a-2026/",
            "https://www.base.gov.pt/Base4/pt/documentacao/"
            "formas-de-obter-dados-sobre-os-contratos-publicos/",
        ),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=True,
        attribution_text="Source: Portal BASE / IMPIC via dados.gov.pt.",
        obligations=(
            "Never download the annual bulk announcement file into the intelligence plane.",
            "Do not treat public-domain licensing as a privacy-safety guarantee.",
        ),
    ),
    "dre_part_l_rss": SourceContract(
        source_id="dre_part_l_rss",
        status=SourceStatus.CONDITIONAL,
        retrieval_route="Diário da República Série II, Parte L official RSS/index feed",
        reason=(
            "The official feed is a narrower update surface than full announcements, but no official "
            "item-schema/no-natural-person guarantee or historical-completeness contract has been "
            "found. Part L also covers procedures requiring journal publication, not every possible "
            "Portuguese procurement path."
        ),
        rights_status=SourceStatus.CONDITIONAL,
        access_status=SourceStatus.APPROVED,
        data_safety_status=SourceStatus.CONDITIONAL,
        commercial_reuse_allowed=None,
        automated_access_allowed=True,
        license_basis="DRE legal/service terms reviewed; commercial feed reuse not yet frozen.",
        legal_basis_urls=(
            "https://diariodarepublica.pt/dr/geral/rss",
            "https://diariodarepublica.pt/dr/detalhe/despacho-normativo/13-2009-1142925",
            "https://diariodarepublica.pt/dr/geral/avisos-legais",
        ),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=False,
        attribution_text=None,
        obligations=(
            "Do not use RSS absence as national procurement absence.",
            "Do not follow RSS links into full notices in the intelligence plane.",
            "Require official item schema, reuse terms and historical completeness before approval.",
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
            gates = (
                contract.rights_status,
                contract.access_status,
                contract.data_safety_status,
            )
            if any(gate is not SourceStatus.APPROVED for gate in gates):
                raise ValueError(
                    f"approved source has a non-approved compliance gate: {contract.source_id}"
                )
            if contract.commercial_reuse_allowed is not True:
                raise ValueError(f"approved source lacks reuse approval: {contract.source_id}")
            if contract.automated_access_allowed is not True:
                raise ValueError(f"approved source lacks access approval: {contract.source_id}")


_validate_registry()


def require_live_source(source_id: str, *, as_of: date | None = None) -> SourceContract:
    """Return a fully approved, currently reviewed source or fail before retrieval."""
    try:
        contract = SOURCE_CONTRACTS[source_id]
    except KeyError as exc:
        raise SourceNotApprovedError(f"unknown source contract: {source_id}") from exc
    if contract.status is not SourceStatus.APPROVED:
        raise SourceNotApprovedError(
            f"source {source_id} is {contract.status}; live retrieval is prohibited"
        )
    gates = {
        "rights": contract.rights_status,
        "access": contract.access_status,
        "data_safety": contract.data_safety_status,
    }
    failed = [name for name, status in gates.items() if status is not SourceStatus.APPROVED]
    if failed:
        raise SourceNotApprovedError(
            f"source {source_id} has non-approved gates: {', '.join(failed)}"
        )
    if contract.commercial_reuse_allowed is not True:
        raise SourceNotApprovedError(f"source {source_id} lacks approved commercial reuse rights")
    if contract.automated_access_allowed is not True:
        raise SourceNotApprovedError(f"source {source_id} lacks approved automated access")
    effective_date = as_of or date.today()
    if effective_date > contract.terms_review_due_on:
        raise SourceComplianceExpiredError(
            f"source {source_id} compliance review expired on "
            f"{contract.terms_review_due_on.isoformat()}"
        )
    return contract


def public_attributions(source_ids: Iterable[str]) -> tuple[str, ...]:
    """Return de-duplicated attribution statements for sources used in an output."""
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
                    f"source {source_id} requires attribution but has no statement"
                )
            if contract.attribution_text not in seen:
                statements.append(contract.attribution_text)
                seen.add(contract.attribution_text)
    return tuple(statements)
