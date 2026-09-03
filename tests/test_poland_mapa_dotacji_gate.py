from pathlib import Path

DOC = Path("docs/POLAND_MAPA_DOTACJI_FINDINGS.md")


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_current_coverage_is_not_established() -> None:
    text = _text()

    assert "authoritative current 2021-2027 coverage: **FAIL / NOT ESTABLISHED**" in text
    assert "national 2021-2027 completeness: **FAIL / NOT ESTABLISHED**" in text
    assert "production eligibility: **REJECTED for Poland 2021-2027 discovery**" in text


def test_no_project_probe_is_authorised() -> None:
    text = _text()

    assert "project-row/API smoke test: **PROHIBITED**" in text
    assert "No Mapa Dotacji project record" in text
    assert "pre-receipt exclusion of prohibited person fields" in text


def test_route_moves_on_without_internal_probing() -> None:
    text = _text()

    assert "Move to a genuinely different Poland source family" in text
    assert "rather than probing Mapa Dotacji internals" in text
