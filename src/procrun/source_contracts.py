"""Frozen production source approval and compliance registry.

A source is production-usable only when four conditions are simultaneously true:
the overall route is approved, commercial reuse rights are approved, automated
access is approved, and the received field surface is data-safe. Approved source
reviews also expire on a fixed date so changed terms cannot be ignored indefinitely.
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


_REVIEWED_ON = date(2026, 9, 1)
_REVIEW_DUE_ON = date(2026, 11, 30)

SOURCE_CONTRACTS = {
    "ted_search_api": SourceContract(
        source_id="ted_search_api",
        status=SourceStatus.APPROVED,
        retrieval_route="POST /v3/notices/search with explicit fields projection",
        reason=(
            "TED explicitly supports analysis/reuse and commercial value-added services; "
            "the Search API supports the field-bounded transport required by ProcRun."
        ),
        rights_status=SourceStatus.APPROVED,
        access_status=SourceStatus.APPROVED,
        data_safety_status=SourceStatus.APPROVED,
        commercial_reuse_allowed=True,
        automated_access_allowed=True,
        license_basis=(
            "TED legal notice / Commission Decision 2011/833/EU reuse policy; procurement "
            "notices are freely reusable for commercial or non-commercial purposes unless "
            "otherwise noted."
        ),
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
            "Union. Procurement Runway transforms and classifies the source data; the "
            "derived analysis is not an official EU publication or endorsement."
        ),
        obligations=(
            "Acknowledge TED/EU as source on customer-facing source/methodology surfaces.",
            "Identify that Procurement Runway transforms/classifies the source data.",
            "Do not imply EU endorsement and do not distort the source meaning.",
            "Use the public Search API rather than automated scraping of TED CMS pages.",
            "Stay below TED fair-use limits; ProcRun policy caps itself below the published "
            "700 HTTP requests/minute ceiling.",
            "Do not reuse identifiable-person or third-party material outside the frozen "
            "field projection.",
        ),
        server_side_projection=True,
        max_requests_per_minute=600,
    ),
    "pt2030_project_search": SourceContract(
        source_id="pt2030_project_search",
        status=SourceStatus.CONDITIONAL,
        retrieval_route="Mais Transparencia Portugal 2030 project-only search surface",
        reason=(
            "The public portal is useful for human discovery, but its site terms do not "
            "provide the same explicit open-data reuse grant as dados.gov.pt, and the exact "
            "transport-level field surface/first-seen provenance is not proven."
        ),
        rights_status=SourceStatus.CONDITIONAL,
        access_status=SourceStatus.CONDITIONAL,
        data_safety_status=SourceStatus.CONDITIONAL,
        commercial_reuse_allowed=None,
        automated_access_allowed=None,
        license_basis="Mais Transparencia site terms; no source-specific reuse approval frozen.",
        legal_basis_urls=(
            "https://transparencia.gov.pt/pt/termos-e-condicoes/",
            "https://transparencia.gov.pt/pt/",
        ),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=False,
        attribution_text=None,
        obligations=(
            "Do not build production ingestion by scraping the portal HTML.",
            "Prefer a separately approved underlying open-data/API route.",
        ),
    ),
    "pt2030_project_detail": SourceContract(
        source_id="pt2030_project_detail",
        status=SourceStatus.BLOCKED,
        retrieval_route="Mais Transparencia Portugal 2030 full project detail page",
        reason="The page includes beneficiary content in the same response.",
        rights_status=SourceStatus.CONDITIONAL,
        access_status=SourceStatus.CONDITIONAL,
        data_safety_status=SourceStatus.BLOCKED,
        commercial_reuse_allowed=None,
        automated_access_allowed=None,
        license_basis="Mais Transparencia site terms; route not approved for reuse/ingestion.",
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
        retrieval_route="AD&C / dados.gov.pt PT2030 approved-operations bulk workbook",
        reason=(
            "The workbook has a broad field surface including beneficiary/tax data, and "
            "download-then-filter is prohibited. The dataset page also reports its licence "
            "as unspecified, so source-specific rights remain conditional despite the "
            "dados.gov.pt default CC BY 4.0 rule for State datasets."
        ),
        rights_status=SourceStatus.CONDITIONAL,
        access_status=SourceStatus.APPROVED,
        data_safety_status=SourceStatus.BLOCKED,
        commercial_reuse_allowed=None,
        automated_access_allowed=True,
        license_basis=(
            "dados.gov.pt terms state CC BY 4.0 by default for State datasets unless "
            "otherwise specified; this PT2030 dataset currently displays 'licence not "
            "specified', so ProcRun requires an explicit source-specific clarification "
            "before relying on it commercially."
        ),
        legal_basis_urls=(
            "https://dados.gov.pt/pt/termos-de-utilizacao",
            "https://dados.gov.pt/fr/datasets/"
            "datasets-pt2030-03-lista-de-operacoes-pt2030/",
        ),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=True,
        attribution_text=(
            "Source: Agência para o Desenvolvimento e Coesão, I.P. via dados.gov.pt. "
            "Any production attribution must also state the finally confirmed dataset "
            "licence and identify Procurement Runway modifications."
        ),
        obligations=(
            "Do not download the broad workbook into the intelligence environment.",
            "Obtain/freeze explicit source-specific licence clarification before reuse.",
            "If later approved under CC BY 4.0, provide attribution and change disclosure.",
        ),
    ),
    "portal_base": SourceContract(
        source_id="portal_base",
        status=SourceStatus.BLOCKED,
        retrieval_route="Portal BASE / IMPIC APIBase2 contract and announcement endpoints",
        reason=(
            "Public BASE data is legally extractable, but API access requires registration "
            "and prior IMPIC authorization. The documented API response cannot be projected "
            "to exclude supplier/adjudicatario identifiers before receipt."
        ),
        rights_status=SourceStatus.CONDITIONAL,
        access_status=SourceStatus.CONDITIONAL,
        data_safety_status=SourceStatus.BLOCKED,
        commercial_reuse_allowed=None,
        automated_access_allowed=True,
        license_basis=(
            "Portaria 318-B/2023 Article 6 permits automated extraction of public BASE data; "
            "large-volume API access is conditional on registration and prior IMPIC "
            "authorization. Commercial product reuse terms must be confirmed as part of "
            "that authorization before any future activation."
        ),
        legal_basis_urls=(
            "https://www.base.gov.pt/Base4/pt/o-portal/base/",
            "https://www.base.gov.pt/APIBase2",
            "https://www.base.gov.pt/Base4/pt/noticias/2025/"
            "api-para-consulta-de-dados-do-portal-base/",
        ),
        terms_reviewed_on=_REVIEWED_ON,
        terms_review_due_on=_REVIEW_DUE_ON,
        attribution_required=False,
        attribution_text=None,
        obligations=(
            "Do not call APIBase2 without registration and prior IMPIC authorization.",
            "Do not activate any BASE route that receives prohibited supplier/person fields.",
            "Freeze any future IMPIC authorization terms before changing this route.",
        ),
        server_side_projection=False,
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
            required_gates = (
                contract.rights_status,
                contract.access_status,
                contract.data_safety_status,
            )
            if any(gate is not SourceStatus.APPROVED for gate in required_gates):
                raise ValueError(
                    f"approved source has a non-approved compliance gate: {contract.source_id}"
                )
            if contract.commercial_reuse_allowed is not True:
                raise ValueError(
                    f"approved source lacks commercial reuse approval: {contract.source_id}"
                )
            if contract.automated_access_allowed is not True:
                raise ValueError(
                    f"approved source lacks automated-access approval: {contract.source_id}"
                )


_validate_registry()


def require_live_source(
    source_id: str,
    *,
    as_of: date | None = None,
) -> SourceContract:
    """Return a fully approved, currently reviewed source contract or fail before retrieval."""

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
    not_approved = [name for name, status in gates.items() if status is not SourceStatus.APPROVED]
    if not_approved:
        raise SourceNotApprovedError(
            f"source {source_id} has non-approved gates: {', '.join(not_approved)}"
        )
    if contract.commercial_reuse_allowed is not True:
        raise SourceNotApprovedError(
            f"source {source_id} lacks approved commercial reuse rights"
        )
    if contract.automated_access_allowed is not True:
        raise SourceNotApprovedError(
            f"source {source_id} lacks approved automated-access rights"
        )

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
