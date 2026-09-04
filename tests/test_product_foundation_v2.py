from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase0_failures_are_preserved() -> None:
    b = _read("docs/PHASE0B_TED_DEMAND_RESULT.md")
    c = _read("docs/PHASE0C_CPV_NORMALIZATION_RESULT.md")
    assert "Result: FAIL" in b
    assert "Result: **FAIL**" in c


def test_zero_contact_and_zero_pii_are_locked() -> None:
    readme = _read("README.md")
    gates = _read("docs/BUILD_GATES.md")
    national = _read("docs/NATIONAL_PROCUREMENT_SOURCE_GATE.md")
    assert "without interviews, surveys, outreach" in readme
    assert "zero-contact" in gates
    assert "Silence is never permission" in national
    assert "download then filter" in readme
    assert "No natural-person data may be collected, stored or processed" in gates


def test_no_contact_drafts_remain_in_active_source_gate() -> None:
    national = _read("docs/NATIONAL_PROCUREMENT_SOURCE_GATE.md")
    for forbidden in (
        "Ready-to-send",
        "Exmos.",
        "IMPIC Helpdesk",
        "@diariodarepublica",
        "@recuperarportugal",
    ):
        assert forbidden not in national


def test_ted_scoped_open_is_canonical() -> None:
    spec = _read("docs/PRODUCT_FOUNDATION_FINAL.md")
    gates = _read("docs/BUILD_GATES.md")
    national = _read("docs/NATIONAL_PROCUREMENT_SOURCE_GATE.md")
    phrase = "No relevant procurement found in TED as of DATE."
    assert phrase in spec
    assert phrase in gates
    assert phrase in national
    assert "This is not a guarantee that no procurement exists outside TED" in spec
    assert "A20 LIVE PORTUGAL OPEN CLASSIFICATION: APPROVED (TED-SCOPED)" in gates


def test_source_categories_and_prr_final_status() -> None:
    status = _read("docs/SOURCE_STATUS.md")
    assert "Category A — eligible for no-contact qualification" in status
    assert "Category B — permanently ineligible" in status
    assert "PRR Projects on dados.gov.pt | B | PERMANENTLY BLOCKED" in status
    assert "OpenCoesione" in status
    assert "Category A candidate" in status
    assert "Poland" in status
    assert "Category B / rejected" in status


def test_funded_project_live_ingest_stays_fail_closed() -> None:
    gates = _read("docs/BUILD_GATES.md")
    contracts = _read("src/procrun/source_contracts.py")
    assert "A20 LIVE FUNDED-PROJECT INGEST: BLOCKED BY A1" in gates
    assert '"prr_projects_dados_gov"' in contracts
    assert "live retrieval is prohibited" in contracts


def test_build_is_go() -> None:
    readme = _read("README.md")
    gates = _read("docs/BUILD_GATES.md")
    assert "START THE WEB BUILD" in readme
    assert "A20 WEB BUILD: GO" in gates


def test_customer_routes_follow_product() -> None:
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
