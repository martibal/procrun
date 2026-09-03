DOC = "docs/ITALY_PUGLIA_ROUTE_FINDINGS.md"


def _read_doc() -> str:
    with open(DOC, encoding="utf-8") as handle:
        return handle.read()


def test_puglia_route_is_rejected_for_scope() -> None:
    text = _read_doc()

    assert "project-specific scope text: **FAIL / NOT PRESENT IN OFFICIAL METADATA**" in text
    assert "title-only replacement: **PROHIBITED**" in text
    assert "production eligibility: **REJECTED for insufficient project scope**" in text


def test_puglia_project_receipt_remains_prohibited() -> None:
    text = _read_doc()

    assert "project-row/file smoke test: **PROHIBITED**" in text
    assert "No CSV body, Data API project row or preview row was requested" in text
    assert "`beneficiario` field" in text
