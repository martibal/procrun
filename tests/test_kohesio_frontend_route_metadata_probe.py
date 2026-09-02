SCRIPT = "scripts/probe_kohesio_frontend_route_metadata.ps1"


def _script_text() -> str:
    with open(SCRIPT, encoding="utf-8") as handle:
        return handle.read()


def test_probe_only_reads_html_and_same_origin_javascript() -> None:
    text = _script_text()

    assert 'https://kohesio.ec.europa.eu/en/data/projects-2021-2027/latest' in text
    assert '$AllowedHost = "kohesio.ec.europa.eu"' in text
    assert '$resolved.Scheme -ne "https" -or $resolved.Host -ne $AllowedHost' in text
    assert '$resolved.AbsolutePath -notmatch "(?i)\\.js$"' in text
    assert '$assetUris.Count -gt 24' in text
    assert '"Accept" = "application/javascript,text/javascript;q=0.9,*/*;q=0.1"' in text


def test_probe_never_calls_project_or_distribution_endpoints() -> None:
    text = _script_text()
    executable = "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    ).lower()

    assert "invoke-restmethod" not in executable
    assert 'project_api_called = $false' in text
    assert 'distribution_body_fetched = $false' in text
    assert 'probe_contract = "kohesio-frontend-route-metadata-v1"' in text

    forbidden_invocations = (
        '-uri "https://kohesio.ec.europa.eu/api/projects',
        '-uri "https://kohesio.ec.europa.eu/api/data/object',
        "invoke-webrequest -uri $endpoint",
        "sparql",
        ".csv",
        ".xlsx",
        ".rdf",
    )
    for token in forbidden_invocations:
        assert token not in executable


def test_probe_only_reports_code_metadata_not_asset_bodies() -> None:
    text = _script_text()

    assert "api_literals" in text
    assert "parameter_keywords_present" in text
    assert "length_bytes" in text
    assert "sha256" in text
    assert "content = $text" not in text.lower()
    assert "body = $text" not in text.lower()
    assert "write-alltext" not in text.lower()
    assert "set-content" not in text.lower()


def test_probe_scans_for_projection_and_filter_clues() -> None:
    text = _script_text()

    for keyword in (
        '"fields"',
        '"select"',
        '"projection"',
        '"countryCode"',
        '"programmingPeriod"',
        '"page"',
        '"size"',
    ):
        assert keyword in text
