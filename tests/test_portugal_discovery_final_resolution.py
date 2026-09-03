DOC = "docs/PORTUGAL_DISCOVERY_FINAL_RESOLUTION.md"


def _text() -> str:
    with open(DOC, encoding="utf-8") as handle:
        return handle.read()


def test_portugal_discovery_is_closed_by_default() -> None:
    text = _text()
    assert "Portugal 2030 funded-project discovery remains NOT PRODUCTION-APPROVED" in text
    assert "CLOSED BY DEFAULT" in text
    assert "production eligibility: **REJECTED**" in text


def test_pre_receipt_privacy_boundary_is_not_weakened() -> None:
    text = _text()
    assert "ProcRun must not weaken the zero-PII boundary" in text
    assert "download-then-filter: **PROHIBITED**" in text
    assert "rich-scope field-bounded transport: **FAIL / NOT ESTABLISHED**" in text


def test_reopen_requires_complete_safe_transport_contract() -> None:
    text = _text()
    assert "machine-testable completeness boundary" in text
    assert "sufficiently rich project-specific scope" in text
    assert "commercial reuse and automated-access terms for the exact route" in text
    assert "defensible `first_seen_at` provenance" in text


def test_final_pass_did_not_fetch_project_bodies() -> None:
    text = _text()
    assert "No new project-detail body or beneficiary record was fetched" in text
    assert "No workbook body or operation row was fetched" in text
    assert "No Excel body was fetched" in text
