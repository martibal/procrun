DOC = "docs/ITALY_DISCOVERY_ROUTE.md"
PROBE = "scripts/probe_opencoesione_beneficiary_metadata.ps1"


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def test_beneficiary_operation_csv_is_rejected_after_provenance_review() -> None:
    doc = _read(DOC)

    assert "Phase-3 record smoke test: **PROHIBITED**" in doc
    assert (
        "production eligibility: **REJECTED under the current zero-PII product requirement**"
        in doc
    )
    assert "source-side projection excluding `OperationSummary`: **NOT FOUND**" in doc
    assert "A local filter, post-download scanner or sample inspection is not sufficient." in doc


def test_metadata_probe_cannot_authorise_record_receipt() -> None:
    probe = _read(PROBE)
    executable = "\n".join(
        line for line in probe.splitlines() if not line.lstrip().startswith("#")
    ).lower()

    assert "beneficiary_operation_csv_called = $false" in probe
    assert "project_api_called = $false" in probe
    assert "project_data_called = $false" in probe
    assert "do not fetch an operations csv" in probe.lower()
    assert "documentation/provenance research only" in probe.lower()
    assert ".csv" not in executable
    assert "/api/" not in executable
