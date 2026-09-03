SCRIPT = "scripts/probe_opencoesione_beneficiary_metadata.ps1"


def _script_text() -> str:
    with open(SCRIPT, encoding="utf-8") as handle:
        return handle.read()


def _executable_text() -> str:
    return "\n".join(
        line for line in _script_text().splitlines() if not line.lstrip().startswith("#")
    ).lower()


def test_probe_fetches_only_exact_beneficiary_metadata_xls() -> None:
    text = _script_text()
    executable = _executable_text()

    assert (
        '$MetadataUri = "https://opencoesione.gov.it/media/opendata/'
        'metadati_beneficiari.xls"'
    ) in text
    assert '$AllowedHost = "opencoesione.gov.it"' in text
    assert executable.count("invoke-webrequest") == 1
    assert "-Uri $MetadataUri" in text
    assert "invoke-restmethod" not in executable

    for forbidden in (
        ".csv",
        "/api/",
        "progetti_esteso",
        "soggetti.csv",
        "beneficiari_operazioni",
    ):
        assert forbidden not in executable


def test_probe_disables_redirects_and_bounds_payload() -> None:
    text = _script_text()

    assert "$MaxMetadataBytes = 512KB" in text
    assert "-MaximumRedirection 0" in text
    assert "$fileInfo.Length -gt $MaxMetadataBytes" in text
    assert '$uri.Scheme -ne "https" -or $uri.Host -ne $AllowedHost' in text
    assert "application/vnd\\.ms-excel|application/octet-stream" in text


def test_probe_requires_legacy_xls_ole_signature() -> None:
    text = _script_text()

    assert "0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1" in text
    assert "not a legacy XLS/OLE payload" in text
    assert "$read -ne 8" in text


def test_probe_only_saves_metadata_to_gitignored_download_area() -> None:
    text = _script_text()

    assert '"data\\downloads\\research"' in text
    assert '"opencoesione_beneficiary_metadata.xls"' in text
    assert "Copy-Item -LiteralPath $TempPath -Destination $OutputPath -Force" in text
    assert "metadata_only = $true" in text
    assert "beneficiary_operation_csv_called = $false" in text
    assert "project_api_called = $false" in text
    assert "project_data_called = $false" in text
    assert "redirect_following_allowed = $false" in text


def test_probe_always_removes_temporary_download() -> None:
    text = _script_text()

    assert "finally {" in text
    assert "Test-Path -LiteralPath $TempPath" in text
    assert "Remove-Item -LiteralPath $TempPath -Force" in text
