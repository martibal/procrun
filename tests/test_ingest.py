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


def _ted_record(publication_date: str, *, award_date: str | None = None) -> dict[str, object]:
    record: dict[str, object] = {
        "notice_id": "notice-date",
        "publication_date": publication_date,
        "title": "Rail works",
        "source_url": "https://example.invalid/notice/notice-date",
    }
    if award_date is not None:
        record["award_date"] = award_date
    return record


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


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2026-08-20", date(2026, 8, 20)),
        ("2021-11-24+01:00", date(2021, 11, 24)),
        ("2021-11-25-05:00", date(2021, 11, 25)),
        ("2023-12-18Z", date(2023, 12, 18)),
    ],
)
def test_normalize_ted_date_variants_preserve_published_calendar_date(
    raw: str, expected: date
) -> None:
    evidence = normalize_ted_record(
        _ted_record(raw),
        evidence_id="ev-date",
        component_id="component-rail",
    )
    assert evidence.publication_date == expected


def test_normalize_ted_date_only_value_with_offset_preserves_calendar_date() -> None:
    evidence = normalize_ted_record(
        _ted_record("2021-11-24+01:00", award_date="2021-11-25-05:00"),
        evidence_id="ev-offset",
        component_id="component-rail",
    )
    assert evidence.publication_date == date(2021, 11, 24)
    assert evidence.award_date == date(2021, 11, 25)


@pytest.mark.parametrize(
    "raw",
    [
        "24/11/2021+01:00",
        "2021-11-24T00:00:00Z",
        "2021-11-24 UTC",
        "2021-11-24+0100",
        "2021-11-24Zextra",
    ],
)
def test_normalize_ted_rejects_non_date_formats(raw: str) -> None:
    with pytest.raises(ValueError, match="invalid TED date value"):
        normalize_ted_record(
            _ted_record(raw),
            evidence_id="ev-bad-date",
            component_id="component-rail",
        )
