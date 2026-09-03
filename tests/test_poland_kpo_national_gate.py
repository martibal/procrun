DOC = "docs/POLAND_KPO_NATIONAL_FINDINGS.md"


def _text() -> str:
    with open(DOC, encoding="utf-8") as handle:
        return handle.read()


def test_kpo_national_route_is_rejected() -> None:
    text = _text()
    assert "production eligibility: **REJECTED**" in text
    assert "Poland-wide project-level coverage surface: **FAIL / NOT ESTABLISHED**" in text
    completeness_gate = (
        "completeness boundary that can be tested automatically: "
        "**FAIL / NOT ESTABLISHED**"
    )
    assert completeness_gate in text


def test_privacy_and_transport_are_not_probed_after_coverage_failure() -> None:
    text = _text()
    assert "field-bounded pre-receipt transport: **NOT INVESTIGATED**" in text
    assert "rich-scope pre-publication zero-PII guarantee: **NOT INVESTIGATED**" in text
    assert "project/list row smoke test: **PROHIBITED**" in text


def test_no_kpo_project_body_was_received() -> None:
    text = _text()
    assert "No KPO project-list attachment" in text
    assert "project row or beneficiary record was fetched" in text
