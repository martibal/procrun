DOC = "docs/POLAND_DANE_GOV_API_FINDINGS.md"


def _text() -> str:
    with open(DOC, encoding="utf-8") as handle:
        return handle.read()


def test_row_api_is_not_treated_as_field_projection() -> None:
    text = _text()

    assert "server-side output-field projection: **FAIL / NOT ESTABLISHED**" in text
    assert "A row API is not automatically a field-bounded API." in text


def test_project_rows_remain_prohibited() -> None:
    text = _text()

    assert "project-row smoke test: **PROHIBITED**" in text
    assert "No project row was requested" in text


def test_route_is_rejected_until_all_reopen_conditions_are_met() -> None:
    text = _text()

    assert "production eligibility: **REJECTED**" in text
    assert "Do not issue a funded-project row request unless all of the following" in text
    assert "project-description/scope fields" in text
