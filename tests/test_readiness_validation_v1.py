from datetime import UTC, datetime

import pytest

from procrun.readiness_validation import (
    ClaimCategory,
    ReadinessValidationRelease,
    ValidationCase,
    validation_manifest,
    validation_sha256,
)


def _case() -> ValidationCase:
    return ValidationCase(
        case_id="minimum-eur-boundary",
        requirement_id="min-eur",
        claim_category=ClaimCategory.EXPLICIT_SCOPED_FACT,
        source_document_id="bando",
        source_citation="Art. 4",
        expected_result="BELOW_PUBLISHED_MINIMUM",
        actual_result="BELOW_PUBLISHED_MINIMUM",
        independent_reconstruction_method=(
            "Blind structured keyword/search reconstruction from frozen source"
        ),
        reconstruction_blind_to_first_extraction=True,
        passed=True,
    )


def _release() -> ReadinessValidationRelease:
    return ReadinessValidationRelease(
        validation_id="validation-1",
        bando_code="BANDO-X",
        source_package_id="pkg-1",
        source_package_sha256="a" * 64,
        benchmark_snapshot_id="snapshot-1",
        benchmark_snapshot_sha256="b" * 64,
        validated_at=datetime(2026, 9, 13, tzinfo=UTC),
        founder_validation_only=True,
        external_validation_required=False,
        ambiguity_rule_attested=True,
        source_universe_complete_attested=True,
        benchmark_cohort_attested=True,
        dossier_semantics_attested=True,
        adversarial_suite_passed=True,
        cases=(_case(),),
    )


def test_release_is_hash_bound_and_explicitly_founder_validated() -> None:
    release = _release()
    manifest = validation_manifest(release)
    assert manifest["status"] == "RELEASED"
    assert manifest["founder_validation_only"] is True
    assert manifest["external_validation_required"] is False
    assert len(validation_sha256(release)) == 64


def test_automated_claim_requires_blind_independent_reconstruction() -> None:
    with pytest.raises(ValueError, match="without seeing the first extraction"):
        ValidationCase(
            case_id="bad",
            requirement_id="min-eur",
            claim_category=ClaimCategory.MACHINE_VERIFIABLE_FACT,
            source_document_id="bando",
            source_citation="Art. 4",
            expected_result="X",
            actual_result="X",
            independent_reconstruction_method="Read the same extraction again",
            reconstruction_blind_to_first_extraction=False,
            passed=True,
        )


def test_automated_claim_mismatch_blocks_release_case() -> None:
    with pytest.raises(ValueError, match="did not pass exactly"):
        ValidationCase(
            case_id="bad-result",
            requirement_id="min-eur",
            claim_category=ClaimCategory.EXPLICIT_SCOPED_FACT,
            source_document_id="bando",
            source_citation="Art. 4",
            expected_result="BELOW",
            actual_result="WITHIN",
            independent_reconstruction_method="Blind structured reconstruction",
            reconstruction_blind_to_first_extraction=True,
            passed=False,
        )


def test_external_validation_dependency_is_forbidden() -> None:
    values = _release().__dict__ | {"external_validation_required": True}
    with pytest.raises(ValueError, match="outside the project"):
        ReadinessValidationRelease(**values)


def test_missing_release_attestation_blocks_release() -> None:
    values = _release().__dict__ | {"ambiguity_rule_attested": False}
    with pytest.raises(ValueError, match="attestations must pass"):
        ReadinessValidationRelease(**values)
