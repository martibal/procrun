DOC = "docs/ITALY_REGIONAL_SCREENING.md"


def _read_doc() -> str:
    with open(DOC, encoding="utf-8") as handle:
        return handle.read()


def test_no_screened_region_is_row_test_eligible() -> None:
    text = _read_doc()

    assert "**No screened regional route qualifies for a project-row smoke test.**" in text
    assert "Emilia-Romagna" in text
    assert "Piemonte" in text
    assert "Toscana" in text
    assert "Veneto" in text
    assert "Sicilia" in text
    assert "**REJECTED / NO ROW TEST**" in text
    assert "**REJECTED AS DUPLICATE ROUTE**" in text
    assert "**REJECTED — RIGHTS FAIL**" in text


def test_zero_pii_boundary_remains_pre_receipt() -> None:
    text = _read_doc()

    assert "before receipt" in text
    assert "receiving a bulk file and discarding" in text
    assert "No production registry change is made by this note." in text


def test_screening_closes_default_region_by_region_search() -> None:
    text = _read_doc()

    assert "**Do not continue region-by-region by default.**" in text
    assert "currently unsupported for funded-project discovery" in text
    assert "field-bounded transport" in text
    assert "pre-publication safety guarantee" in text
