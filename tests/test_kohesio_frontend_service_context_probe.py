SCRIPT = "scripts/probe_kohesio_frontend_service_context.ps1"


def _script_text() -> str:
    with open(SCRIPT, encoding="utf-8") as handle:
        return handle.read()


def test_probe_only_reads_html_and_same_origin_javascript() -> None:
    text = _script_text()

    assert 'https://kohesio.ec.europa.eu/en/data/projects-2021-2027/latest' in text
    assert '$AllowedHost = "kohesio.ec.europa.eu"' in text
    assert "Resolve-SafeBaseUri" in text
    assert "Resolve-SafeAssetUri" in text
    assert '$resolved.Scheme -ne "https" -or $resolved.Host -ne $AllowedHost' in text
    assert '$resolved.AbsolutePath -notmatch "(?i)\\.js$"' in text
    assert "$assetUris.Count -gt 24" in text


def test_probe_never_calls_project_or_distribution_endpoints() -> None:
    text = _script_text()
    executable = "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    ).lower()

    assert "invoke-restmethod" not in executable
    assert 'project_api_called = $false' in text
    assert 'distribution_body_fetched = $false' in text
    assert 'probe_contract = "kohesio-frontend-service-context-v1"' in text

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


def test_probe_targets_actual_service_route_construction() -> None:
    text = _script_text()

    for token in (
        '"getProjectsFilters"',
        '"getProjects("',
        '"getProject("',
        '"getFilter("',
        '"getBeneficiariesFilters"',
        '"getBeneficiaries("',
        '"this.http.get("',
        '".http.get("',
        '"entityURL"',
        '"apiURL"',
        '"/projects"',
        '"projects?"',
        '"beneficiaryIdentifier"',
        '"uniqueIdentifier"',
    ):
        assert token in text


def test_service_context_output_is_strictly_bounded() -> None:
    text = _script_text()

    assert "ConvertTo-ServiceContextSnippet" in text
    assert "Get-TargetedServiceContexts" in text
    assert "$MaxContextCountAcrossAssets = 20" in text
    assert "-MaxPerToken 2" in text
    assert "-MaxTotal ([Math]::Min(16, $remaining))" in text
    assert "$snippet.Length -gt 3000" in text
    assert "service_context_count = $totalContextCount" in text
    assert "service_context_limit = $MaxContextCountAcrossAssets" in text
    assert "max_context_chars = 3000" in text
    assert "targeted_service_contexts" in text
    assert "write-alltext" not in text.lower()
    assert "set-content" not in text.lower()
    assert "content = $text" not in text.lower()
    assert "body = $text" not in text.lower()
