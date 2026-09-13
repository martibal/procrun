"""Commercial release validation contract for Readiness Dossier bandi.

A bando is sellable only when every automated customer-facing claim is inside the
publicly verifiable contract and an immutable validation record binds the exact
source package and benchmark snapshot used by production.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

VALIDATION_SCHEMA_VERSION = "readiness-validation-v1"


class ClaimCategory(StrEnum):
    MACHINE_VERIFIABLE_FACT = "MACHINE_VERIFIABLE_FACT"
    EXPLICIT_SCOPED_FACT = "EXPLICIT_SCOPED_FACT"
    PROFESSIONAL_VERIFICATION_REQUIRED = "PROFESSIONAL_VERIFICATION_REQUIRED"


class ValidationStatus(StrEnum):
    RELEASED = "RELEASED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class ValidationCase:
    case_id: str
    requirement_id: str
    claim_category: ClaimCategory
    source_document_id: str
    source_citation: str
    expected_result: str
    actual_result: str
    independent_reconstruction_method: str
    reconstruction_blind_to_first_extraction: bool
    passed: bool

    def __post_init__(self) -> None:
        for value, label in (
            (self.case_id, "case_id"),
            (self.requirement_id, "requirement_id"),
            (self.source_document_id, "source_document_id"),
            (self.source_citation, "source_citation"),
            (self.independent_reconstruction_method, "independent_reconstruction_method"),
        ):
            if not value.strip():
                raise ValueError(f"{label} is required")
        if self.claim_category is not ClaimCategory.PROFESSIONAL_VERIFICATION_REQUIRED:
            if not self.reconstruction_blind_to_first_extraction:
                raise ValueError(
                    "automated claims require a reconstruction performed without seeing "
                    "the first extraction"
                )
            if not self.passed or self.expected_result != self.actual_result:
                raise ValueError("automated validation case did not pass exactly")


@dataclass(frozen=True)
class ReadinessValidationRelease:
    validation_id: str
    bando_code: str
    source_package_id: str
    source_package_sha256: str
    benchmark_snapshot_id: str
    benchmark_snapshot_sha256: str
    validated_at: datetime
    founder_validation_only: bool
    external_validation_required: bool
    ambiguity_rule_attested: bool
    source_universe_complete_attested: bool
    benchmark_cohort_attested: bool
    dossier_semantics_attested: bool
    adversarial_suite_passed: bool
    cases: tuple[ValidationCase, ...]

    def __post_init__(self) -> None:
        if self.validated_at.tzinfo is None:
            raise ValueError("validated_at must be timezone-aware")
        for digest, label in (
            (self.source_package_sha256, "source_package_sha256"),
            (self.benchmark_snapshot_sha256, "benchmark_snapshot_sha256"),
        ):
            if len(digest) != 64:
                raise ValueError(f"{label} must contain 64 hex characters")
            int(digest, 16)
        if self.external_validation_required:
            raise ValueError("commercial release must not depend on validation outside the project")
        if not self.founder_validation_only:
            raise ValueError(
                "validation must explicitly acknowledge that source interpretation is "
                "founder/project work only"
            )
        mandatory = (
            self.ambiguity_rule_attested,
            self.source_universe_complete_attested,
            self.benchmark_cohort_attested,
            self.dossier_semantics_attested,
            self.adversarial_suite_passed,
        )
        if not all(mandatory):
            raise ValueError("all commercial release validation attestations must pass")
        if not self.cases:
            raise ValueError("commercial release requires validation cases")
        ids = {case.case_id for case in self.cases}
        if len(ids) != len(self.cases):
            raise ValueError("duplicate validation case ids")

    @property
    def status(self) -> ValidationStatus:
        return ValidationStatus.RELEASED


def validation_manifest(release: ReadinessValidationRelease) -> dict[str, object]:
    return {
        "schema_version": VALIDATION_SCHEMA_VERSION,
        "validation_id": release.validation_id,
        "status": release.status.value,
        "bando_code": release.bando_code,
        "source_package_id": release.source_package_id,
        "source_package_sha256": release.source_package_sha256,
        "benchmark_snapshot_id": release.benchmark_snapshot_id,
        "benchmark_snapshot_sha256": release.benchmark_snapshot_sha256,
        "validated_at": release.validated_at.astimezone(UTC).isoformat(),
        "founder_validation_only": release.founder_validation_only,
        "external_validation_required": release.external_validation_required,
        "ambiguity_rule_attested": release.ambiguity_rule_attested,
        "source_universe_complete_attested": release.source_universe_complete_attested,
        "benchmark_cohort_attested": release.benchmark_cohort_attested,
        "dossier_semantics_attested": release.dossier_semantics_attested,
        "adversarial_suite_passed": release.adversarial_suite_passed,
        "cases": [
            {
                "case_id": case.case_id,
                "requirement_id": case.requirement_id,
                "claim_category": case.claim_category.value,
                "source_document_id": case.source_document_id,
                "source_citation": case.source_citation,
                "expected_result": case.expected_result,
                "actual_result": case.actual_result,
                "independent_reconstruction_method": case.independent_reconstruction_method,
                "reconstruction_blind_to_first_extraction": (
                    case.reconstruction_blind_to_first_extraction
                ),
                "passed": case.passed,
            }
            for case in release.cases
        ],
    }


def validation_sha256(release: ReadinessValidationRelease) -> str:
    canonical = json.dumps(
        validation_manifest(release), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
