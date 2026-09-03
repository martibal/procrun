DOC = "docs/ITALY_DISCOVERY_ROUTE.md"


def _doc_text() -> str:
    with open(DOC, encoding="utf-8") as handle:
        return handle.read()


def test_beneficiary_operation_csv_is_rejected_under_zero_pii_boundary() -> None:
    text = _doc_text()

    assert "Phase-3 record smoke test: **PROHIBITED**" in text
    assert "production eligibility: **REJECTED under the current zero-PII product requirement**" in text
    assert "source-side projection excluding `OperationSummary`: **NOT FOUND**" in text
    assert "A local filter, post-download scanner or sample inspection is not sufficient." in text


def test_italy_has_no_production_approved_funded_project_source() -> None:
    text = _doc_text()

    assert "No Italy funded-project source is production-approved yet." in text
    assert "**rejected under zero-PII boundary**" in text
