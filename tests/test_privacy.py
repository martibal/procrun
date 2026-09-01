from datetime import date

import pytest

from procrun.ingest.portugal2030 import (
    PORTUGAL2030_ALLOWED_FIELDS,
    normalize_project_record,
)
from procrun.ingest.ted import TED_ALLOWED_FIELDS, normalize_ted_record
from procrun.privacy import UnexpectedFieldError, validate_projected_record

PROHIBITED_FIELD_NAMES = {
    "name",
    "beneficiary_name",
    "supplier_name",
    "contact_name",
    "contact_person",
    "nif",
    "tax_id",
    "email",
    "phone",
    "address",
    "postal_address",
    "ip_address",
}


def test_source_allowlists_do_not_include_known_pii_fields() -> None:
    assert not (PORTUGAL2030_ALLOWED_FIELDS & PROHIBITED_FIELD_NAMES)
    assert not (TED_ALLOWED_FIELDS & PROHIBITED_FIELD_NAMES)


def test_unexpected_field_fails_closed() -> None:
    with pytest.raises(UnexpectedFieldError):
        validate_projected_record(
            {"operation_code": "PT2030-X", "nif": "prohibited"},
            frozenset({"operation_code"}),
        )


def test_portugal_record_rejects_beneficiary_name() -> None:
    record = {
        "operation_code": "PACS-FC-TEST",
        "first_seen_at": "2026-09-01T00:00:00+00:00",
        "project_start": "2026-01-01",
        "project_end": "2028-12-31",
        "approved_funding_eur": 1000000,
        "executed_funding_eur": 0,
        "project_scope_text": "Construction of water infrastructure.",
        "source_url": "https://example.invalid/project",
        "beneficiary_name": "must never enter the pipeline",
    }
    with pytest.raises(UnexpectedFieldError):
        normalize_project_record(record)


def test_ted_record_rejects_contact_field() -> None:
    record = {
        "notice_id": "notice-1",
        "publication_date": date(2026, 8, 1),
        "title": "Water infrastructure works",
        "cpv_codes": ["45200000"],
        "procedure_value_eur": 500000,
        "project_reference": "PACS-FC-TEST",
        "source_url": "https://example.invalid/notice",
        "contact_name": "must never enter the pipeline",
    }
    with pytest.raises(UnexpectedFieldError):
        normalize_ted_record(record, evidence_id="ev-1", component_id="comp-1")
