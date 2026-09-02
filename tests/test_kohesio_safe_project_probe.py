import re

SCRIPT = "scripts/probe_kohesio_pt2030_project.ps1"


def _script_text() -> str:
    with open(SCRIPT, encoding="utf-8") as handle:
        return handle.read()


def _query_text() -> str:
    text = _script_text()
    start = text.index("$Query = @'")
    end = text.index("'@", start)
    return text[start:end]


def test_probe_is_exact_single_project_allowlist_query() -> None:
    text = _script_text()
    query = _query_text()

    assert '$TargetOperationCode = "PACS-FC-01781200"' in text
    assert '$Endpoint = "https://query.linkedopendata.eu/sparql"' in text
    assert 'FILTER(STR(?operation_identifier) = "PACS-FC-01781200")' in query
    assert "LIMIT 5" in query

    assert "SELECT *" not in query
    assert "DESCRIBE" not in query
    assert "CONSTRUCT" not in query
    assert "?predicate" not in query
    assert "?project ?p ?o" not in query
    assert "P841" not in query
    assert "beneficiary" not in query.lower()


def test_probe_uses_only_frozen_safe_properties() -> None:
    query = _query_text()
    expected = {
        "P1367",
        "P836",
        "P605685",
        "P1368",
        "P1584",
        "P20",
        "P33",
        "P474",
        "P835",
        "P192",
        "P1820",
    }

    used = set(re.findall(r"kohesio:(P[0-9]+)", query))
    assert used == expected


def test_probe_accepts_only_standard_sparql_tuple_formats() -> None:
    text = _script_text()

    assert "Invoke-WebRequest" in text
    assert "Invoke-RestMethod" not in text
    assert "application/sparql-results+xml" in text
    assert "application/sparql-results+json" in text
    assert "ConvertFrom-SparqlWebResponse" in text
    assert "unsupported SPARQL result content type" in text
    assert "response body was not logged" in text
    assert "response values were not logged" in text
    assert 'response_content_type = $script:SuccessfulContentType' in text


def test_probe_parses_xml_with_external_entities_disabled() -> None:
    text = _script_text()

    assert "ConvertFrom-SparqlXml" in text
    assert "$settings.DtdProcessing = [System.Xml.DtdProcessing]::Prohibit" in text
    assert "$settings.XmlResolver = $null" in text
    assert "$document.XmlResolver = $null" in text
    assert 'AddNamespace("sr", "http://www.w3.org/2005/sparql-results#")' in text
    assert 'SelectSingleNode("/sr:sparql/sr:head"' in text
    assert 'SelectSingleNode("/sr:sparql/sr:results"' in text
    assert "SPARQL XML binding without a variable name" in text
    assert "SPARQL XML binding without a value node" in text


def test_probe_reuses_same_query_for_get_and_post() -> None:
    text = _script_text()

    assert (
        '$response = ConvertFrom-SparqlWebResponse -WebResponse $webResponse -Method "GET"'
        in text
    )
    assert (
        '$response = ConvertFrom-SparqlWebResponse -WebResponse $webResponse -Method "POST"'
        in text
    )
    assert 'format = "application/sparql-results+xml"' in text
    assert "$postParameters = @{" in text
    assert "query = $Query" in text
    assert '-ContentType "application/x-www-form-urlencoded"' in text
    assert 'probe_contract = "kohesio-pt2030-safe-project-smoke-v4"' in text


def test_probe_fails_closed_on_unknown_response_variables() -> None:
    text = _script_text()

    assert "Assert-AllowedVariables" in text
    assert "SPARQL response declared unexpected variable" in text
    assert "SPARQL response returned unexpected variable" in text
    assert "SPARQL response is missing the required head/results envelope" in text
    assert '"operation_identifier"' in text
    assert '"summary"' in text
    assert '"last_update"' in text


def test_probe_tolerates_only_blank_header_metadata_not_blank_bindings() -> None:
    text = _script_text()

    assert "foreach ($declared in @($Response.head.vars))" in text
    assert "[string]::IsNullOrWhiteSpace($name)" in text
    assert "continue" in text
    assert "foreach ($property in $binding.PSObject.Properties)" in text
    assert (
        "[string]::IsNullOrWhiteSpace($name) -or -not $allowed.ContainsKey($name)"
        in text
    )


def test_probe_never_calls_broad_project_surfaces() -> None:
    text = _script_text().lower()

    forbidden = (
        "api/projects",
        "select *",
        "describe ",
        "construct ",
        "?project ?predicate ?value",
        "beneficiary_unique_identifier",
        "social_media_links",
    )
    for token in forbidden:
        assert token not in text
