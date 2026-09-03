DOC = "docs/ITALY_DISCOVERY_ROUTE.md"
PROBE = "scripts/probe_opencoesione_beneficiary_metadata.ps1"


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def test_beneficiary_operation_csv_remains_blocked_until_summary_is_precleared() -> None:
    doc = _read(DOC)

    assert "Phase-2 `OperationSummary` pre-receipt safety: **UNPROVEN**" in doc
    assert "overall data-safety gate: **BLOCKED**" in doc
    assert "Phase-3 CSV smoke test: **NOT AUTHORISED**" in doc
    assert "Download-then-filter is not" in doc
    assert "acceptable safety test" in doc


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
