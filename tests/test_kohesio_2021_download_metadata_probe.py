SCRIPT = "scripts/probe_kohesio_2021_download_metadata.ps1"


def _script_text() -> str:
    with open(SCRIPT, encoding="utf-8") as handle:
        return handle.read()


def test_probe_targets_only_official_2021_2027_index_page() -> None:
    text = _script_text()

    assert (
        '$IndexUri = "https://kohesio.ec.europa.eu/en/data/projects-2021-2027/latest"'
        in text
    )
    assert text.count("Invoke-WebRequest") == 1
    assert "Invoke-RestMethod" not in text
    assert '-Uri $IndexUri' in text


def test_probe_never_fetches_distribution_bodies() -> None:
    text = _script_text()

    forbidden = (
        "Invoke-WebRequest -Uri $resolved",
        "Invoke-WebRequest -Uri $candidate",
        "Invoke-RestMethod -Uri $resolved",
        "Invoke-RestMethod -Uri $candidate",
        "Start-BitsTransfer",
        "WebClient",
        "DownloadFile",
        "Out-File",
        "Set-Content",
        "Add-Content",
    )
    for token in forbidden:
        assert token not in text

    assert 'distribution_bodies_fetched = $false' in text


def test_probe_outputs_only_catalog_link_metadata_and_hash() -> None:
    text = _script_text()

    assert 'host = $resolved.Host' in text
    assert 'path_and_query = $resolved.PathAndQuery' in text
    assert 'anchor_text = $text' in text
    assert "response_sha256 = Get-Sha256Hex" in text
    assert "response_length_bytes = $htmlBytes.Length" in text
    assert 'probe_contract = "kohesio-2021-download-metadata-v1"' in text

    assert "raw_html" not in text.lower()
    assert "response_body" not in text.lower()


def test_probe_does_not_embed_project_or_beneficiary_fields() -> None:
    text = _script_text().lower()

    forbidden = (
        "operation_unique_identifier",
        "beneficiary_name",
        "beneficiary_unique_identifier",
        "social_media_links",
        "operation_summary_programme_language",
        "p841",
        "select *",
        "describe ",
        "construct ",
    )
    for token in forbidden:
        assert token not in text
