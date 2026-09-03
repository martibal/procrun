from pathlib import Path

DOC = Path("docs/POLAND_PORTAL_GALLERY_AND_CLOSURE_FINDINGS.md")


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_portal_gallery_route_is_rejected_at_coverage_and_timing_gate() -> None:
    text = _text()
    assert "production eligibility: **REJECTED**" in text
    assert "temporal suitability for ProcRun discovery: **FAIL**" in text
    assert "Poland-wide completeness boundary: **FAIL / NOT ESTABLISHED**" in text


def test_privacy_and_transport_are_not_probed_after_earlier_failure() -> None:
    text = _text()
    assert "field-bounded pre-receipt transport: **NOT INVESTIGATED**" in text
    assert "rich-scope pre-publication zero-PII guarantee: **NOT INVESTIGATED**" in text
    assert "project/list-row smoke test: **PROHIBITED**" in text


def test_poland_is_closed_by_default_with_strict_reopen_conditions() -> None:
    text = _text()
    assert "Poland source discovery is **CLOSED BY DEFAULT**" in text
    assert "authoritative field-bounded output before receipt" in text
    assert "explicit pre-publication zero-PII guarantee" in text
    assert "no Poland project-row or broad-file probing is permitted" in text
