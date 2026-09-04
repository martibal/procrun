from datetime import date

import pytest

from procrun.domain import TemporalProvenance
from procrun.ingest.portugal2030 import normalize_project_record
from procrun.ingest.ted import normalize_ted_record


def test_normalize_project_record_from_safe_projection() -> None:
    project = normalize_project_record(
        {
            "operation_code": "PACS-FC-TEST",
            "first_seen_at": "2026-08-01T00:00:00+00:00",
            "project_title": "Water infrastructure upgrade",
            "project_start": "2026-01-01",
            "project_end": "2028-12-31",
            "approved_funding_eur": 1_000_000,
            "executed_funding_eur": 100_000,
            "project_scope_text": "Construction of water infrastructure.",
            "programme": "Portugal 2030",
            "region": "Norte",
            "source_url": "https://example.invalid/project/PACS-FC-TEST",
        },
        temporal_provenance=TemporalProvenance.RESOLVED,
    )
    assert project.operation_code == "PACS-FC-TEST"
    assert project.project_end == date(2028, 12, 31)
    assert project.approved_funding_eur == 1_000_000
    assert project.temporal_provenance is TemporalProvenance.RESOLVED


def test_missing_first_seen_never_uses_project_start_as_proxy() -> None:
    project = normalize_project_record(
        {
            "operation_code": "PACS-FC-TEST",
            "project_start": "2026-01-01",
            "project_scope_text": "Construction of water infrastructure.",
            "source_url": "https://example.invalid/project/PACS-FC-TEST",
        }
    )
    assert project.first_seen_at is None
    assert project.project_start == date(2026, 1, 1)
    assert project.temporal_provenance is TemporalProvenance.UNRESOLVED


def test_normalize_ted_record_from_safe_projection() -> None:
    evidence = normalize_ted_record(
        {
            "notice_id": "notice-1",
            "publication_date": "2026-08-20",
            "award_date": "2026-09-01",
            "title": "Water infrastructure works",
            "scope_description": "Civil works and pumps",
            "cpv_codes": ["45200000"],
            "procedure_value_eur": 500_000,
            "project_reference": "PACS-FC-TEST",
            "source_url": "https://example.invalid/notice/notice-1",
        },
        evidence_id="ev-1",
        component_id="component-water",
    )
    assert evidence.publication_date == date(2026, 8, 20)
    assert evidence.award_date == date(2026, 9, 1)
    assert evidence.cpv_codes == ("45200000",)
    assert evidence.contracting_authority_name is None
    assert evidence.project_reference == "PACS-FC-TEST"


def test_normalize_ted_date_only_value_with_offset_preserves_calendar_date() -> None:
    evidence = normalize_ted_record(
        {
            "notice_id": "notice-offset",
            "publication_date": "2021-11-24+01:00",
            "award_date": "2021-11-25-05:00",
            "title": "Rail works",
            "source_url": "https://example.invalid/notice/notice-offset",
        },
        evidence_id="ev-offset",
        component_id="component-rail",
    )
    assert evidence.publication_date == date(2021, 11, 24)
    assert evidence.award_date == date(2021, 11, 25)


def test_normalize_ted_rejects_non_date_offset_formats() -> None:
    with pytest.raises(ValueError):
        normalize_ted_record(
            {
                "notice_id": "notice-bad-date",
                "publication_date": "24/11/2021+01:00",
                "title": "Rail works",
                "source_url": "https://example.invalid/notice/notice-bad-date",
            },
            evidence_id="ev-bad-date",
            component_id="component-rail",
        )
