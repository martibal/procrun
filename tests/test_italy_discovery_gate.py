DOC = "docs/ITALY_DISCOVERY_ROUTE.md"
PROBE = "scripts/probe_opencoesione_beneficiary_metadata.ps1"


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def test_bounded_opencoesione_route_records_superseding_provenance() -> None:
    doc = _read(DOC)

    assert "Vademecum per il Monitoraggio" in doc
    assert "`TITOLO_PROGETTO` and `SINTESI_PROG`" in doc
    assert "previous blanket rejection" in doc
    assert "**superseded**" in doc
    assert "bounded `PR FESR LOMBARDIA` route: **QUALIFIED for A21a source-wording use**" in doc
    assert "general OpenCoesione project/API/search surfaces: **NOT REOPENED" in doc
    assert "No raw source may be downloaded merely to test whether an unqualified route is safe." in doc


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
