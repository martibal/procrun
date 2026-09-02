SCRIPT = "scripts/probe_eukg_property_metadata.ps1"


def _script_text() -> str:
    with open(SCRIPT, encoding="utf-8") as handle:
        return handle.read()


def test_eukg_probe_is_property_metadata_only() -> None:
    text = _script_text()

    assert 'action = "wbgetentities"' in text
    assert 'action = "wbsearchentities"' in text
    assert 'type = "property"' in text
    assert 'props = "labels|descriptions"' in text
    assert '"P841"' in text  # metadata about the forbidden property is safe to inspect

    forbidden = (
        "api/projects",
        "PACS-FC-",
        'type = "item"',
        "SELECT ",
        "DESCRIBE ",
        "CONSTRUCT ",
        "?project",
    )
    for token in forbidden:
        assert token not in text


def test_eukg_probe_uses_only_property_ids_for_direct_entity_lookup() -> None:
    text = _script_text()
    marker = "$KnownPropertyIds = @("
    start = text.index(marker)
    end = text.index(")\n\n$knownResponse", start)
    block = text[start:end]

    assert '"Q' not in block
    assert '"P20"' in block
    assert '"P836"' in block
