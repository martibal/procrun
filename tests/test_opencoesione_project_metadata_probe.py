SCRIPT = "scripts/probe_opencoesione_project_metadata.ps1"


def _script_text() -> str:
    with open(SCRIPT, encoding="utf-8") as handle:
        return handle.read()


def _executable_text() -> str:
    return "\n".join(
        line for line in _script_text().splitlines() if not line.lstrip().startswith("#")
    ).lower()


def test_probe_fetches_only_frozen_metadata_workbook() -> None:
    text = _script_text()
    executable = _executable_text()

    assert (
        '$MetadataUri = "https://opencoesione.gov.it/media/opendata/'
        'metadati_database_OC.xlsx"'
    ) in text
    assert '$AllowedHost = "opencoesione.gov.it"' in text
    assert "Invoke-WebRequest" in text
    assert "-Uri $MetadataUri" in text
    assert executable.count("invoke-webrequest") == 1
    assert "invoke-restmethod" not in executable

    for forbidden in (
        "/api/",
        "progetti_esteso",
        "soggetti.csv",
        "progetti.csv",
        "beneficiari_operazioni",
    ):
        assert forbidden not in executable


def test_probe_enforces_small_metadata_payload_and_safe_xlsx_parsing() -> None:
    text = _script_text()

    assert "$MaxWorkbookBytes = 2MB" in text
    assert "$fileInfo.Length -gt $MaxWorkbookBytes" in text
    assert "$prefix[0] -ne 0x50 -or $prefix[1] -ne 0x4B" in text
    assert "$archive.Entries.Count -gt 500" in text
    assert '"xl/workbook.xml"' in text
    assert '"xl/_rels/workbook.xml.rels"' in text
    assert '"xl/sharedStrings.xml"' in text
    assert "XmlResolver = $null" in text
    assert 'if ($text -match "(?i)<!DOCTYPE")' in text
    assert '$normalized.Contains("..")' in text


def test_probe_is_bounded_to_project_metadata_rows() -> None:
    text = _script_text()

    assert "$MaxProjectRows = 300" in text
    assert "$MaxCellChars = 1500" in text
    assert 'Where-Object { $_.name -match "(?i)progett" }' in text
    assert "$projectSheets.Count -eq 0" in text
    assert "$totalProjectRows -ge $MaxProjectRows" in text
    assert "$value.Length -gt $MaxCellChars" in text
    assert "suspicious_term_hits = $suspiciousHits" in text
    assert "scope_term_hits = $scopeHits" in text


def test_probe_declares_no_project_or_subject_data_was_called() -> None:
    text = _script_text()

    assert 'probe_contract = "opencoesione-project-metadata-v1"' in text
    assert "metadata_only = $true" in text
    assert "project_data_called = $false" in text
    assert "subject_data_called = $false" in text
    assert "api_project_record_called = $false" in text


def test_probe_always_removes_temporary_workbook() -> None:
    text = _script_text()

    assert "finally {" in text
    assert "$archive.Dispose()" in text
    assert "Test-Path -LiteralPath $tempPath" in text
    assert "Remove-Item -LiteralPath $tempPath -Force" in text
