from pathlib import Path

DOC = Path("docs/POLAND_CUPT_PROJECT_PAGES_FINDINGS.md")


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_cupt_project_page_route_is_rejected() -> None:
    text = _text()
    assert "production eligibility: **REJECTED**" in text
    assert "broad HTML data safety: **FAIL**" in text
    assert "download/render-then-filter: **PROHIBITED**" in text
    assert "further project-page or project-row smoke tests: **PROHIBITED**" in text


def test_cupt_route_requires_pre_receipt_projection() -> None:
    text = _text()
    assert "pre-receipt field projection: **NOT DOCUMENTED**" in text
    assert "natural-person identity fields" in text
    assert "pre-publication zero-PII guarantee" in text


def test_safety_incident_is_not_persisted() -> None:
    text = _text()
    assert "Safety incident note" in text
    assert "No such names or row content are reproduced or persisted in ProcRun." in text
