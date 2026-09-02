SCRIPT = "scripts/probe_opencoesione_api_options_metadata.ps1"


def _script_text() -> str:
    with open(SCRIPT, encoding="utf-8") as handle:
        return handle.read()


def _executable_text() -> str:
    return "\n".join(
        line for line in _script_text().splitlines() if not line.lstrip().startswith("#")
    ).lower()


def test_probe_is_frozen_to_project_collection_options_only() -> None:
    text = _script_text()
    executable = _executable_text()

    assert '$ApiUri = "https://opencoesione.gov.it/api/progetti.json"' in text
    assert '$AllowedHost = "opencoesione.gov.it"' in text
    assert '$uri.AbsolutePath -ne "/api/progetti.json"' in text
    assert '[System.Net.Http.HttpMethod]::new("OPTIONS")' in text
    assert "AllowAutoRedirect = $false" in text

    assert "invoke-webrequest" not in executable
    assert "invoke-restmethod" not in executable
    assert ".getasync(" not in executable
    assert 'httpmethod]::new("get")' not in executable
    assert "/api/progetti/" not in executable


def test_probe_bounds_metadata_response_before_json_shape_inspection() -> None:
    text = _script_text()

    assert "$MaxBodyBytes = 128KB" in text
    assert "ResponseHeadersRead" in text
    assert "$declaredLength -gt $MaxBodyBytes" in text
    assert "$total -gt $MaxBodyBytes" in text
    assert "$MaxShapePaths = 500" in text
    assert "$Depth -gt 8" in text
    assert "$pathCount -ge $MaxShapePaths" in text
    assert "ConvertFrom-Json" in text


def test_probe_emits_only_metadata_shape_not_response_values() -> None:
    text = _script_text()

    assert 'probe_contract = "opencoesione-api-options-metadata-v1"' in text
    assert 'method = "OPTIONS"' in text
    assert "project_list_get_called = $false" in text
    assert "project_detail_called = $false" in text
    assert "response_body_logged = $false" in text
    assert "metadata_shape_paths = $shapePaths" in text
    assert "projection_candidate_paths = $projectionPaths" in text
    assert "filter_candidate_paths = $filterPaths" in text
    assert "identity_candidate_paths = $identityPaths" in text

    for forbidden_output in (
        "response_body =",
        "body_text = $bodytext",
        "metadata_values =",
        "project_rows =",
        "results = $metadata",
    ):
        assert forbidden_output not in text.lower()


def test_probe_fails_closed_on_redirect_content_type_and_shape_drift() -> None:
    text = _script_text()

    assert "$statusCode -ge 300 -and $statusCode -lt 400" in text
    assert "redirects are disabled" in text
    assert "unexpected content type" in text
    assert "metadata body was not valid JSON" in text
    assert "metadata shape exceeded the bounded path limit" in text


def test_probe_searches_metadata_paths_for_projection_and_identity_markers() -> None:
    text = _script_text()

    for marker in (
        "fields?",
        "select",
        "projection",
        "include",
        "exclude",
        "serializer",
        "soggett",
        "beneficiar",
        "codice_fiscale",
        "fornitor",
        "aggiudicat",
        "supplier",
    ):
        assert marker in text
