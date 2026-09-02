from pathlib import Path


SCRIPT = Path("scripts/probe_eukg_property_metadata.ps1")


def test_eukg_probe_is_property_metadata_only() -> None:
    text = SCRIPT.read_text(encoding="utf-8")

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
    text = SCRIPT.read_text(encoding="utf-8")
    marker = "$KnownPropertyIds = @("
    start = text.index(marker)
    end = text.index(")\n\n$knownResponse", start)
    block = text[start:end]

    assert '"Q' not in block
    assert '"P20"' in block
    assert '"P836"' in block
