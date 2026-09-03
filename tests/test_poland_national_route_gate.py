from pathlib import Path


DOC = Path("docs/POLAND_NATIONAL_ROUTE_FINDINGS.md")


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_poland_bulk_route_is_rejected() -> None:
    text = _text()

    assert "broad distribution data safety: **FAIL**" in text
    assert "production eligibility: **REJECTED for the bulk route**" in text
    assert "project-row/file smoke test: **PROHIBITED**" in text


def test_download_then_filter_is_not_allowed() -> None:
    text = _text()

    assert "may not be downloaded and then reduced locally" in text
    assert "No XLSX or CSV body was fetched" in text


def test_dane_gov_pl_remains_metadata_only() -> None:
    text = _text()

    assert "dane.gov.pl` is **RESEARCH-ONLY / NOT PRODUCTION-APPROVED**" in text
    assert "Do not request a project data row" in text
    assert "server-side output-field projection" in text
