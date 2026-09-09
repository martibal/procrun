"""A21a source-candidate decisions for remote zero-PII project evidence input.

These decisions are deliberately separate from production source contracts. A candidate remains
non-ingestible until every required safety property is proven from public evidence and automated
checks. In particular, download-then-filter is never an acceptable privacy boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CandidateStatus(StrEnum):
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


CANDIDATES: dict[str, A21aSourceCandidate] = {
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
