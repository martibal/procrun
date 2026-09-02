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


def test_probe_fails_closed_on_unknown_response_variables() -> None:
    text = _script_text()

    assert "Assert-AllowedVariables" in text
    assert "SPARQL response declared unexpected variable" in text
    assert "SPARQL response returned unexpected variable" in text
    assert '"operation_identifier"' in text
    assert '"summary"' in text
    assert '"last_update"' in text


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
