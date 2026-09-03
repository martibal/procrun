from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_readme_records_current_no_build_decision() -> None:
    readme = _read("README.md")
    assert "NOT READY FOR WEBSITE BUILD" in readme
    assert "Phase 0B" in readme
    assert "Phase 0C" in readme
    assert "TED notice -> normalized purchasable requirements" in readme


def test_phase0b_failure_is_preserved() -> None:
    prereg = _read("docs/PHASE0B_TED_DEMAND_PREREG.md")
    result = _read("docs/PHASE0B_TED_DEMAND_RESULT.md")
    assert "description_only_value_pct >= 10.0" in prereg
    assert "description-only value: 2.7%" in result
    assert "Result: FAIL" in result
    assert "not changed after observation" in result


def test_phase0c_failure_is_preserved() -> None:
    prereg = _read("docs/PHASE0C_CPV_NORMALIZATION_PREREG.md")
    result = _read("docs/PHASE0C_CPV_NORMALIZATION_RESULT.md")
    assert "at least 15 distinct normalized categories" in prereg
    assert "distinct categories: 13" in result
    assert "Result: **FAIL**" in result
    assert "No threshold was lowered" in result


def test_v2_source_capability_is_not_relabelled_as_product_validation() -> None:
    readme = _read("README.md")
    assert "Active infrastructure notice feed | SUPPORTED" in readme
    assert "Early procurement runway from TED | NOT SUPPORTED" in readme
    assert "These results establish source capability. They do not by themselves validate a paid supplier product." in readme


def test_absolute_intelligence_privacy_boundary_is_preserved() -> None:
    readme = _read("README.md")
    gates = _read("docs/BUILD_GATES.md")
    source_status = _read("docs/SOURCE_STATUS.md")

    assert "No natural-person data may be collected, stored or processed" in readme
    assert "pre-receipt" in readme.lower()
    assert "No natural-person data may be collected, stored or processed" in gates
    assert "Do not receive a broad response containing prohibited fields" in source_status


def test_original_runway_evidence_is_not_claimed_for_v2() -> None:
    readme = _read("README.md")
    assert "The old evidence remains valid for what it actually tested" in readme
    assert "it does not validate the TED-based v2 pivot" in readme
