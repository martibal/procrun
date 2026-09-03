DOC = "docs/ITALY_REGIS_ROUTE_FINDINGS.md"


def _read_doc() -> str:
    with open(DOC, encoding="utf-8") as handle:
        return handle.read()


def test_regis_project_distribution_is_rejected() -> None:
    text = _read_doc()

    assert "broad project data safety: **FAIL**" in text
    assert "server-side field projection excluding prohibited fields: **NOT FOUND**" in text
    assert "title/summary pre-receipt zero-PII guarantee: **FAIL / NOT ESTABLISHED**" in text
    assert (
        "production eligibility: **REJECTED under the current zero-PII and scope requirements**"
        in text
    )


def test_regis_record_receipt_remains_prohibited() -> None:
    text = _read_doc()

    assert "download-then-filter mitigation: **PROHIBITED**" in text
    assert "project-row/file smoke test: **PROHIBITED**" in text
    assert "No `PNRR_Progetti` CSV, JSON or Excel body was retrieved" in text
