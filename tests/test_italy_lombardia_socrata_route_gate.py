DOC = "docs/ITALY_LOMBARDIA_SOCRATA_FINDINGS.md"


def _read_doc() -> str:
    with open(DOC, encoding="utf-8") as handle:
        return handle.read()


def test_lombardia_socrata_projection_passes_but_scope_fails() -> None:
    text = _read_doc()

    assert "server-side output projection: **PASS at platform-contract level**" in text
    assert "broad record data safety: **FAIL**" in text
    assert "project-text zero-PII guarantee: **FAIL / NOT ESTABLISHED**" in text
    assert "coverage: **PARTIAL / Lombardia only**" in text


def test_lombardia_project_rows_remain_prohibited() -> None:
    text = _read_doc()

    assert "project-row smoke test: **PROHIBITED pending scope-safety proof**" in text
    assert (
        "production eligibility: **REJECTED under the current zero-PII and scope "
        "requirements**"
    ) in text
    assert "no project row was requested" in text.lower()
