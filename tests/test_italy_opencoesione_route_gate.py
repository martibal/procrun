DOC = "docs/ITALY_DISCOVERY_ROUTE.md"


def _doc_text() -> str:
    with open(DOC, encoding="utf-8") as handle:
        return handle.read()


def test_bounded_lombardia_route_is_qualified_without_general_reopening() -> None:
    text = _doc_text()

    assert "`SINTESI_PROG` pre-receipt natural-person rule: **PASS" in text
    assert "bounded `PR FESR LOMBARDIA` route: **QUALIFIED for A21a source-wording use**" in text
    assert "general OpenCoesione project/API/search surfaces: **NOT REOPENED" in text
    assert "production eligibility of the broad Candidate 3 family: **NOT GRANTED" in text
    assert "No raw source may be downloaded merely to test whether an unqualified route is safe." in text


def test_italy_has_no_blanket_production_approval() -> None:
    text = _doc_text()

    assert "No broad Italy funded-project source family is production-approved" in text
    assert "qualified for A21a source-wording use" in text
    assert "must not be generalized to unqualified OpenCoesione surfaces" in text
