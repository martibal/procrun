from __future__ import annotations

import copy

import pytest

from scripts.validate_a21a_sanitized_source_pool import validate


def _document() -> dict:
    return {
        "schema_version": "a21a-sanitized-source-pool-v1",
        "pii_review_status": "ZERO_PII_CONFIRMED",
        "engine_output_present": False,
        "sanitization_provenance": {
            "raw_archive_present": False,
            "download_then_filter_used": False,
            "source_only_projection_confirmed": True,
            "projection_boundary": "upstream_before_receipt",
            "transport_kind": "field_selective_endpoint",
            "projection_evidence_url": "https://example.invalid/projection-contract",
        },
        "cases": [
            {
                "operation_code": "A21A-001",
                "project_title": "Riqualificazione energetica edificio pubblico",
                "project_scope_text": "Intervento di efficientamento energetico dell'edificio.",
                "region": "Lombardia",
                "municipality": None,
                "nuts_code": "ITC4",
                "source_url": "https://example.invalid/project/A21A-001",
                "language": "it",
            }
        ],
    }


def test_valid_sanitized_pool_passes() -> None:
    report = validate(_document())
    assert report["ingress_pass"] is True
    assert report["case_count"] == 1
    assert report["zero_pii_confirmed"] is True
    assert report["projection_boundary"] == "upstream_before_receipt"
    assert report["transport_kind"] == "field_selective_endpoint"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("pii_review_status", "UNKNOWN"),
        ("engine_output_present", True),
    ],
)
def test_hard_gate_rejects_unqualified_top_level_state(field: str, value: object) -> None:
    document = _document()
    document[field] = value
    with pytest.raises(ValueError):
        validate(document)


def test_rejects_raw_archive_or_download_then_filter() -> None:
    for key in ("raw_archive_present", "download_then_filter_used"):
        document = _document()
        document["sanitization_provenance"][key] = True
        with pytest.raises(ValueError):
            validate(document)


def test_rejects_local_or_unproven_projection_boundary() -> None:
    for boundary in (None, "local_after_receipt", "unknown"):
        document = _document()
        document["sanitization_provenance"]["projection_boundary"] = boundary
        with pytest.raises(ValueError):
            validate(document)


def test_rejects_bulk_archive_transport_even_with_safe_flags() -> None:
    document = _document()
    document["sanitization_provenance"]["transport_kind"] = "bulk_archive"
    with pytest.raises(ValueError):
        validate(document)


def test_accepts_prebuilt_sanitized_resource_transport() -> None:
    document = _document()
    document["sanitization_provenance"]["transport_kind"] = "prebuilt_sanitized_resource"
    report = validate(document)
    assert report["transport_kind"] == "prebuilt_sanitized_resource"


def test_requires_https_projection_evidence() -> None:
    for url in (None, "http://example.invalid/contract"):
        document = _document()
        document["sanitization_provenance"]["projection_evidence_url"] = url
        with pytest.raises(ValueError):
            validate(document)


def test_rejects_beneficiary_and_contact_fields_recursively() -> None:
    for key in ("beneficiary_name", "CodiceFiscaleBeneficiario", "contact_email"):
        document = _document()
        document["cases"][0][key] = "forbidden"
        with pytest.raises(ValueError):
            validate(document)


def test_rejects_engine_output_field_even_if_flag_false() -> None:
    document = _document()
    document["cases"][0]["extractor_output"] = []
    with pytest.raises(ValueError):
        validate(document)


def test_rejects_duplicate_operation_codes() -> None:
    document = _document()
    duplicate = copy.deepcopy(document["cases"][0])
    document["cases"].append(duplicate)
    with pytest.raises(ValueError):
        validate(document)


def test_rejects_non_https_source_url() -> None:
    document = _document()
    document["cases"][0]["source_url"] = "http://example.invalid/project/A21A-001"
    with pytest.raises(ValueError):
        validate(document)
