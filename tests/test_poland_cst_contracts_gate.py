from pathlib import Path

DOC = Path("docs/POLAND_CST_CONTRACTS_FINDINGS.md")


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_poland_cst_contracts_route_is_rejected() -> None:
    text = _text()
    assert "production eligibility: **REJECTED**" in text
    assert "beneficiary address data" in text
    assert "download-then-filter: **PROHIBITED**" in text
    assert "report/file row smoke test: **PROHIBITED**" in text


def test_scope_failure_is_independent_of_projection() -> None:
    text = _text()
    assert "sufficiently rich project-specific scope: **FAIL" in text
    assert "not a substitute" in text
    assert "field-bounded transport" in text
    assert "pre-publication zero-PII guarantee" in text


def test_no_project_body_was_received() -> None:
    assert "No report body or project/agreement row was fetched." in _text()
