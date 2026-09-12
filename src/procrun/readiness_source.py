"""Immutable source-package model for ProcRun Readiness Dossier v2."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum

SOURCE_PACKAGE_TTL_DAYS = 7
SOURCE_PACKAGE_SCHEMA_VERSION = "readiness-source-package-v2"


class SourcePackageState(StrEnum):
    FRESH = "FRESH"
    SOURCE_REFRESH_REQUIRED = "SOURCE_REFRESH_REQUIRED"
    INVALIDATED = "INVALIDATED"
    INCOMPLETE = "INCOMPLETE"


class SourceReuseMode(StrEnum):
    COMMERCIAL_REUSE_CONFIRMED = "COMMERCIAL_REUSE_CONFIRMED"
    FACT_EXTRACTION_ONLY = "FACT_EXTRACTION_ONLY"
    BLOCKED = "BLOCKED"


class RequirementKind(StrEnum):
    REFERENCE = "REFERENCE"
    MINIMUM_EUR = "MINIMUM_EUR"
    MAXIMUM_EUR = "MAXIMUM_EUR"
    MINIMUM_MONTHS = "MINIMUM_MONTHS"
    MAXIMUM_MONTHS = "MAXIMUM_MONTHS"
    ADVISOR_CONFIRMATION = "ADVISOR_CONFIRMATION"
    PROFESSIONAL_VERIFICATION = "PROFESSIONAL_VERIFICATION"


@dataclass(frozen=True)
class SourceDocument:
    document_id: str
    document_type: str
    title: str
    public_url: str
    sha256: str
    observed_at: datetime
    reuse_mode: SourceReuseMode
    reuse_basis_url: str
    reuse_basis_note: str

    def __post_init__(self) -> None:
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        if len(self.sha256) != 64:
            raise ValueError("document sha256 must be 64 hex characters")
        int(self.sha256, 16)
        if not self.reuse_basis_url.strip() or not self.reuse_basis_note.strip():
            raise ValueError("source reuse requires a public basis URL and note")


@dataclass(frozen=True)
class PublishedRequirement:
    requirement_id: str
    kind: RequirementKind
    label: str
    source_document_id: str
    source_citation: str
    source_text: str
    scope_note: str
    boundary_value: int | None = None

    def __post_init__(self) -> None:
        needs_boundary = self.kind in {
            RequirementKind.MINIMUM_EUR,
            RequirementKind.MAXIMUM_EUR,
            RequirementKind.MINIMUM_MONTHS,
            RequirementKind.MAXIMUM_MONTHS,
        }
        if needs_boundary != (self.boundary_value is not None):
            raise ValueError("mechanical requirements require exactly one integer boundary")
        if self.boundary_value is not None and self.boundary_value < 0:
            raise ValueError("boundary_value must be non-negative")


@dataclass(frozen=True)
class SourcePackage:
    source_package_id: str
    bando_code: str
    benchmark_cohort_id: str
    version: int
    verified_at: datetime
    documents: tuple[SourceDocument, ...]
    requirements: tuple[PublishedRequirement, ...]
    completeness_attested: bool

    def __post_init__(self) -> None:
        if self.verified_at.tzinfo is None:
            raise ValueError("verified_at must be timezone-aware")
        if self.version < 1:
            raise ValueError("version must be >= 1")
        if not self.benchmark_cohort_id.strip():
            raise ValueError("benchmark_cohort_id is required")
        document_ids = {item.document_id for item in self.documents}
        if len(document_ids) != len(self.documents):
            raise ValueError("duplicate source document ids")
        requirement_ids = {item.requirement_id for item in self.requirements}
        if len(requirement_ids) != len(self.requirements):
            raise ValueError("duplicate requirement ids")
        if any(item.source_document_id not in document_ids for item in self.requirements):
            raise ValueError("every requirement must reference a document in the package")

        documents_by_id = {item.document_id: item for item in self.documents}
        blocked = [
            item.document_id
            for item in self.documents
            if item.reuse_mode is SourceReuseMode.BLOCKED
        ]
        if blocked:
            raise ValueError(
                "blocked source documents cannot enter a production source package: "
                + ", ".join(sorted(blocked))
            )
        for requirement in self.requirements:
            document = documents_by_id[requirement.source_document_id]
            if (
                document.reuse_mode is SourceReuseMode.FACT_EXTRACTION_ONLY
                and requirement.source_text.strip()
            ):
                raise ValueError(
                    "FACT_EXTRACTION_ONLY documents cannot carry source_text into a paid package"
                )

    @property
    def refresh_due_at(self) -> datetime:
        return self.verified_at.astimezone(UTC) + timedelta(days=SOURCE_PACKAGE_TTL_DAYS)

    def state_at(self, as_of: datetime, *, invalidated_at: datetime | None = None) -> SourcePackageState:
        if as_of.tzinfo is None:
            raise ValueError("as_of must be timezone-aware")
        if not self.completeness_attested:
            return SourcePackageState.INCOMPLETE
        if invalidated_at is not None and invalidated_at <= as_of:
            return SourcePackageState.INVALIDATED
        if as_of.astimezone(UTC) > self.refresh_due_at:
            return SourcePackageState.SOURCE_REFRESH_REQUIRED
        return SourcePackageState.FRESH


def package_manifest(package: SourcePackage) -> dict[str, object]:
    return {
        "schema_version": SOURCE_PACKAGE_SCHEMA_VERSION,
        "source_package_id": package.source_package_id,
        "bando_code": package.bando_code,
        "benchmark_cohort_id": package.benchmark_cohort_id,
        "version": package.version,
        "verified_at": package.verified_at.astimezone(UTC).isoformat(),
        "refresh_due_at": package.refresh_due_at.isoformat(),
        "completeness_attested": package.completeness_attested,
        "documents": [
            {
                "document_id": item.document_id,
                "document_type": item.document_type,
                "title": item.title,
                "public_url": item.public_url,
                "sha256": item.sha256,
                "observed_at": item.observed_at.astimezone(UTC).isoformat(),
                "reuse_mode": item.reuse_mode.value,
                "reuse_basis_url": item.reuse_basis_url,
                "reuse_basis_note": item.reuse_basis_note,
            }
            for item in package.documents
        ],
        "requirements": [
            {
                "requirement_id": item.requirement_id,
                "kind": item.kind.value,
                "label": item.label,
                "source_document_id": item.source_document_id,
                "source_citation": item.source_citation,
                "source_text": item.source_text,
                "scope_note": item.scope_note,
                "boundary_value": item.boundary_value,
            }
            for item in package.requirements
        ],
    }


def package_sha256(package: SourcePackage) -> str:
    payload = json.dumps(
        package_manifest(package), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
