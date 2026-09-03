DOC = "docs/ITALY_DISCOVERY_ROUTE.md"


def _doc_text() -> str:
    with open(DOC, encoding="utf-8") as handle:
        return handle.read()


def test_openbdap_mop_is_rejected_under_zero_pii_scope_boundary() -> None:
    text = _doc_text()

    assert "project-row smoke test: **PROHIBITED**" in text
    assert "server-side field projection: **UNPROVEN**" in text
    assert "scope pre-receipt zero-PII guarantee: **FAIL / NOT ESTABLISHED**" in text
    assert (
        "production eligibility: **REJECTED under the current zero-PII and scope requirements**"
        in text
    )


def test_openbdap_mop_cannot_be_rescued_by_projection_alone() -> None:
    text = _doc_text()

    assert "That is an input instruction, not a source-side guarantee." in text
    assert "structured taxonomy as scope replacement: **INSUFFICIENT" in text
    assert "Proving `$select` alone would not make the route eligible." in text
    assert "rather than issue an OpenBDAP/MOP project-row request" in text
