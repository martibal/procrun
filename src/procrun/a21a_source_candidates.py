"""A21a source-candidate decisions for remote zero-PII project evidence input.

These decisions are deliberately separate from production source contracts. A candidate remains
non-ingestible until every required safety property is proven from public evidence and automated
checks. Download-then-filter is never an acceptable privacy boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CandidateStatus(StrEnum):
    APPROVED = "APPROVED"
    BLOCKED = "BLOCKED"
    CONDITIONAL = "CONDITIONAL"


@dataclass(frozen=True)
class A21aSourceCandidate:
    source_id: str
    status: CandidateStatus
    route: str
    reason: str
    row_ingest_allowed: bool
    metadata_probe_allowed: bool
    requires_server_side_projection: bool
    forbidden_full_dataset_fields: tuple[str, ...] = ()
    richer_project_text_proven: bool = False


CANDIDATES: dict[str, A21aSourceCandidate] = {
    "opencoesione_2021_2027_operations": A21aSourceCandidate(
        source_id="opencoesione_2021_2027_operations",
        status=CandidateStatus.APPROVED,
        route=(
            "https://opencoesione.gov.it/it/opendata/beneficiari/2021-2027/"
            "beneficiari_PR_FESR_LOMBARDIA.zip"
        ),
        reason=(
            "The PR FESR Lombardia 2021-2027 operation list is already production-approved. "
            "RGS Vademecum Monitoraggio v1.0 explicitly states that both TITOLO_PROGETTO and "
            "SINTESI_PROG must not contain sensitive information attributable to natural persons, "
            "including name, tax code, telephone number or email address. This corrects the prior "
            "A21a review, which incorrectly treated the title rule as established while missing the "
            "same explicit rule for SINTESI_PROG. The summary provides up to 1,300 characters of "
            "project-specific scope and is therefore eligible as A21a source-evidence text. The live "
            "Lombardia universe currently has SINTESI_PROG identical to TITOLO_PROGETTO, so richer "
            "project text is not presently proven from this route."
        ),
        row_ingest_allowed=True,
        metadata_probe_allowed=True,
        requires_server_side_projection=False,
        richer_project_text_proven=False,
    ),
    "opencoesione_general_api": A21aSourceCandidate(
        source_id="opencoesione_general_api",
        status=CandidateStatus.BLOCKED,
        route="https://opencoesione.gov.it/api/progetti.json",
        reason=(
            "The published project-list serializer includes soggetto references and exposes no "
            "documented server-side field projection. It cannot satisfy the zero-PII boundary."
        ),
        row_ingest_allowed=False,
        metadata_probe_allowed=True,
        requires_server_side_projection=True,
        forbidden_full_dataset_fields=("soggetto",),
    ),
    "opencoesione_search_csv": A21aSourceCandidate(
        source_id="opencoesione_search_csv",
        status=CandidateStatus.BLOCKED,
        route="OpenCoesione project-search CSV export",
        reason=(
            "The project-search export includes SOGGETTI_PROGRAMMATORI and SOGGETTI_ATTUATORI. "
            "Receiving the export and filtering afterward is prohibited."
        ),
        row_ingest_allowed=False,
        metadata_probe_allowed=True,
        requires_server_side_projection=True,
        forbidden_full_dataset_fields=("SOGGETTI_PROGRAMMATORI", "SOGGETTI_ATTUATORI"),
    ),
    "openbdap_mop_lombardia_odata": A21aSourceCandidate(
        source_id="openbdap_mop_lombardia_odata",
        status=CandidateStatus.BLOCKED,
        route=(
            "https://bdap-opendata.rgs.mef.gov.it/opendata/"
            "spd_mop_prg_mon_reg03_01_9999"
        ),
        reason=(
            "The remote metadata-only A21a utility probe found structured MOP attributes such as "
            "CUP, status, nature, typology and sector, but no explicit project-title or project-"
            "description field class that can support verbatim A21a source evidence. Because the "
            "candidate fails the product-utility gate before row access, no OData projection or "
            "project-row probe is permitted or necessary."
        ),
        row_ingest_allowed=False,
        metadata_probe_allowed=True,
        requires_server_side_projection=True,
        forbidden_full_dataset_fields=("Codice Fiscale Titolare", "Descrizione Titolare"),
    ),
    "lombardia_pr_fesr_socrata": A21aSourceCandidate(
        source_id="lombardia_pr_fesr_socrata",
        status=CandidateStatus.BLOCKED,
        route="https://www.dati.lombardia.it/resource/q78n-g3m9.json",
        reason=(
            "The official dataset exposes DESCRIZIONE_OPERAZIONE as a project-description field and "
            "server-side projection is proven, so it is potentially richer than the title. However, "
            "the same dataset explicitly contains beneficiary names including natural persons, and no "
            "dataset-specific public rule guarantees that DESCRIZIONE_OPERAZIONE itself is free of "
            "natural-person data. ProcRun cannot receive free text first and inspect/filter it later. "
            "Therefore the source remains blocked by the absolute zero-PII pre-receipt boundary."
        ),
        row_ingest_allowed=False,
        metadata_probe_allowed=True,
        requires_server_side_projection=True,
        forbidden_full_dataset_fields=(
            "nome_del_beneficiario",
            "codice_del_beneficiario",
        ),
        richer_project_text_proven=False,
    ),
    "kohesio_eu_knowledge_graph": A21aSourceCandidate(
        source_id="kohesio_eu_knowledge_graph",
        status=CandidateStatus.BLOCKED,
        route="https://query.linkedopendata.eu/sparql",
        reason=(
            "Kohesio is an EC project-level aggregation and its public schema requires an operation "
            "summary; its validator also requires an individual person's beneficiary name to be "
            "anonymised. The SPARQL endpoint can technically project only project fields. However, "
            "the published anonymisation rule is attached to Beneficiary_Name, not to free-text "
            "Operation_Summary_Programme_Language. No public field-level contract was found that "
            "guarantees the operation summary cannot contain natural-person data. Under ProcRun's "
            "zero-PII pre-receipt rule, a projected free-text row still cannot be ingested merely so "
            "that ProcRun can inspect or filter it afterward."
        ),
        row_ingest_allowed=False,
        metadata_probe_allowed=True,
        requires_server_side_projection=True,
        forbidden_full_dataset_fields=(
            "Beneficiary_Name",
            "Beneficiary_Unique_Identifier",
            "Social_Media_Links",
        ),
        richer_project_text_proven=False,
    ),
    "beneficiary_article50_project_pages": A21aSourceCandidate(
        source_id="beneficiary_article50_project_pages",
        status=CandidateStatus.BLOCKED,
        route="Beneficiary public websites required/encouraged under Regulation (EU) 2021/1060",
        reason=(
            "Article 50 can make a short project description publicly available on beneficiary "
            "websites, but arbitrary beneficiary pages are unstructured documents that can contain "
            "names, contact details and other natural-person data. There is no server-side projection "
            "or source-wide content contract that would remove those fields before receipt. Public "
            "availability is therefore not sufficient for ProcRun's stricter zero-PII ingest rule."
        ),
        row_ingest_allowed=False,
        metadata_probe_allowed=True,
        requires_server_side_projection=True,
        richer_project_text_proven=False,
    ),
}


def require_metadata_probe(source_id: str) -> A21aSourceCandidate:
    candidate = CANDIDATES[source_id]
    if not candidate.metadata_probe_allowed:
        raise RuntimeError(f"metadata probing prohibited for {source_id}")
    return candidate


def require_row_ingest(source_id: str) -> A21aSourceCandidate:
    candidate = CANDIDATES[source_id]
    if not candidate.row_ingest_allowed:
        raise RuntimeError(f"row ingest not approved for A21a source candidate {source_id}")
    return candidate


def approved_richer_project_text_sources() -> tuple[A21aSourceCandidate, ...]:
    """Return sources safe for row ingest that are proven to add text beyond the project title."""

    return tuple(
        candidate
        for candidate in CANDIDATES.values()
        if candidate.status is CandidateStatus.APPROVED
        and candidate.row_ingest_allowed
        and candidate.richer_project_text_proven
    )
