DOC = "docs/ITALY_DISCOVERY_ROUTE.md"


def _doc_text() -> str:
    with open(DOC, encoding="utf-8") as handle:
        return handle.read()


def test_openbdap_mop_rows_are_blocked_until_projection_and_scope_are_proven() -> None:
    text = _doc_text()

    assert "project-row smoke test: **PROHIBITED**" in text
    assert "server-side field projection: **UNPROVEN**" in text
    assert "scope sufficiency after safe projection: **UNPROVEN**" in text
    assert "production eligibility: **BLOCKED pending metadata-only OData and scope proof**" in text


def test_openbdap_mop_research_remains_metadata_only() -> None:
    text = _doc_text()

    assert "No `DataRows`, CSV, JSON or XML project body may be fetched" in text
    assert "metadata and transport-contract validation only" in text
