from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_readme_records_final_build_decision() -> None:
    readme = _read("README.md")
    assert "READY FOR WEBSITE BUILD" in readme
    assert "docs/PRODUCT_FOUNDATION_FINAL.md" in readme
    assert "From tenders to infrastructure demand." in readme
    assert "Do not add another product-feasibility test" in readme


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
    assert "No threshold is lowered" in result


def test_final_product_does_not_relabel_failed_v2_as_pass() -> None:
    readme = _read("README.md")
    spec = _read("docs/PRODUCT_FOUNDATION_FINAL.md")
    assert "failed tests are preserved and are not relabelled as PASS" in readme
    assert "Failed Phase 0B and Phase 0C results remain valid" in spec
    assert "complete component decomposition" in spec
    assert "bounded enrichment" in spec


def test_validated_source_capabilities_are_preserved() -> None:
    readme = _read("README.md")
    assert "Active infrastructure notice feed | SUPPORTED" in readme
    assert "Procurement market-intelligence dataset | SUPPORTED" in readme
    assert "Early procurement runway from TED | NOT SUPPORTED" in readme
    assert "Comprehensive EU-funding subset | NOT SUPPORTED" in readme


def test_absolute_intelligence_privacy_boundary_is_preserved() -> None:
    readme = _read("README.md")
    gates = _read("docs/BUILD_GATES.md")
    source_status = _read("docs/SOURCE_STATUS.md")

    assert "No natural-person data may be collected, stored or processed" in readme
    assert "pre-receipt" in readme.lower()
    assert "No natural-person data may be collected, stored or processed" in gates
    assert "Do not receive a broad response containing prohibited fields" in source_status


def test_final_product_scope_is_locked() -> None:
    spec = _read("docs/PRODUCT_FOUNDATION_FINAL.md")
    gates = _read("docs/BUILD_GATES.md")

    for route in (
        "/app",
        "/app/opportunities/[id]",
        "/app/market",
        "/app/profile",
        "/app/saved",
        "/app/account",
        "/methodology",
        "/pricing",
    ):
        assert route in spec

    assert "ProcRun Portugal — €149/month" in spec
    assert "Do not create another product-feasibility test" in gates
    assert "A notice remains eligible for the feed even when no demand tag is present" in gates
