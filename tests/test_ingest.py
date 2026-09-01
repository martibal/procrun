from datetime import date

from procrun.ingest.portugal2030 import normalize_project_record
from procrun.ingest.ted import normalize_ted_record


def test_normalize_project_record_from_safe_projection() -> None:
    project = normalize_project_record(
        {
            "operation_code": "PACS-FC-TEST",
            "first_seen_at": "2026-08-01T00:00:00+00:00",
            "project_start": "2026-01-01",
            "project_end": "2028-12-31",
            "approved_funding_eur": 1000000,
            "executed_funding_eur": 100000,
            "project_scope_text": "Construction of water infrastructure.",
            "source_url": "https://example.invalid/project/PACS-FC-TEST",
        }
    )
    assert project.operation_code == "PACS-FC-TEST"
    assert project.project_end == date(2028, 12, 31)
    assert project.approved_funding_eur == 1000000


def test_normalize_ted_record_from_safe_projection() -> None:
    evidence = normalize_ted_record(
        {
            "notice_id": "notice-1",
            "publication_date": "2026-08-20",
            "title": "Water infrastructure works",
            "cpv_codes": ["45200000"],
            "procedure_value_eur": 500000,
            "project_reference": "PACS-FC-TEST",
            "source_url": "https://example.invalid/notice/notice-1",
        },
        evidence_id="ev-1",
        component_id="component-water",
    )
    assert evidence.publication_date == date(2026, 8, 20)
    assert evidence.cpv_codes == ("45200000",)
    assert evidence.project_reference == "PACS-FC-TEST"
