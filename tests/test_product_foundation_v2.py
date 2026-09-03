from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_readme_defers_web_readiness_to_a20() -> None:
    readme = _read("README.md")
    assert "docs/PRODUCT_FOUNDATION_FINAL.md" in readme
    assert "gate **A20**" in readme
    assert "funded project -> source-evidenced purchasable components" in readme
    assert "TED-only v2 pivot is retired" in readme
    assert "DO NOT START THE WEB BUILD YET" in readme


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


def test_final_product_restores_runway_without_rewriting_v2_history() -> None:
    spec = _read("docs/PRODUCT_FOUNDATION_FINAL.md")
    assert "Project-before-procurement unit of analysis" in spec
    assert "Phase 0B and Phase 0C remain FAIL" in spec
    assert "remaining procurement runway" in spec
    assert "TED-only demand feed" in spec


def test_zero_unsupported_inference_contract_is_bounded() -> None:
    spec = _read("docs/PRODUCT_FOUNDATION_FINAL.md")
    gates = _read("docs/BUILD_GATES.md")
    assert "No invented demand" in spec
    assert "100% source-verified" in spec
    assert "must not be used as a blanket claim" in spec
    assert "`OPEN` is not a source fact" in gates
    assert "UNRESOLVED" in gates


def test_absolute_intelligence_privacy_boundary_is_preserved() -> None:
    readme = _read("README.md")
    gates = _read("docs/BUILD_GATES.md")
    source_status = _read("docs/SOURCE_STATUS.md")
    assert "zero-natural-person" in readme
    assert "No natural-person data may be collected, stored or processed" in gates
    assert "Do not receive a broad response containing prohibited fields" in source_status
    assert "download-then-filter" in source_status


def test_zero_contact_validation_rule_is_locked() -> None:
    readme = _read("README.md")
    gates = _read("docs/BUILD_GATES.md")
    a1 = _read("docs/A1_PRR_SOURCE_CLARIFICATION.md")
    approval = _read("docs/PRR_PROJECTS_A1_APPROVAL_REQUEST.md")
    assert "no authority, source-owner or public-body contact" in gates
    assert "no paid consultant, auditor or legal opinion" in gates
    assert "Silence is never permission" in gates
    assert "No email, call, interview, survey" in a1
    assert "HUMAN-DEPENDENT APPROVAL PATH RETIRED" in approval
    assert "Only already-public, independently inspectable evidence" in readme


def test_prr_candidate_remains_fail_closed_until_public_safety_proof() -> None:
    source_status = _read("docs/SOURCE_STATUS.md")
    contracts = _read("src/procrun/source_contracts.py")
    a1 = _read("docs/A1_PRR_SOURCE_CLARIFICATION.md")
    assert "PRR Projects on dados.gov.pt | CONDITIONAL" in source_status
    assert '"prr_projects_dados_gov"' in contracts
    assert "data_safety_status=SourceStatus.CONDITIONAL" in contracts
    assert "live retrieval is prohibited" in contracts
    assert "new public authoritative evidence" in a1


def test_a20_is_single_authoritative_web_build_gate() -> None:
    gates = _read("docs/BUILD_GATES.md")
    spec = _read("docs/PRODUCT_FOUNDATION_FINAL.md")
    assert "A20 is the only authoritative `GO` source" in gates
    assert "A20 WEB BUILD: BLOCKED" in gates
    assert "A20 LIVE FUNDED-PROJECT INGEST: BLOCKED BY A1" in gates
    assert "A20 LIVE PORTUGAL OPEN CLASSIFICATION: BLOCKED BY NATIONAL SOURCE COVERAGE" in gates
    assert "A20 PAID PRODUCTION: BLOCKED" in gates
    assert "Only `BUILD_GATES.md` A20 can declare build readiness" in spec


def test_preweb_blockers_are_source_contracts_not_internal_pipeline() -> None:
    gates = _read("docs/BUILD_GATES.md")
    status = _read("docs/PREWEB_SHOWSTOPPER_STATUS.md")
    assert "one funded-project source passes A1 entirely from public evidence" in gates
    assert "one complete-enough Portuguese national procurement source" in gates
    assert "WEB BUILD BLOCKED — TWO PUBLIC-EVIDENCE SOURCE GATES REMAIN" in status
    assert "live end-to-end acceptance" in status


def test_customer_routes_follow_runway_product() -> None:
    spec = _read("docs/PRODUCT_FOUNDATION_FINAL.md")
    for route in (
        "/app",
        "/app/projects/[id]",
        "/app/components/[id]",
        "/app/market",
        "/app/profile",
        "/app/saved",
        "/app/account",
        "/methodology",
        "/pricing",
    ):
        assert route in spec
    assert "ProcRun Portugal — €149/month" in spec
