from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase0_failures_are_preserved() -> None:
    phase_b = _read("docs/PHASE0B_TED_DEMAND_RESULT.md")
    phase_c = _read("docs/PHASE0C_CPV_NORMALIZATION_RESULT.md")
    assert "Result: FAIL" in phase_b
    assert "Result: **FAIL**" in phase_c


def test_zero_contact_and_zero_pii_are_locked() -> None:
    readme = _read("README.md")
    gates = _read("docs/BUILD_GATES.md")
    national = _read("docs/NATIONAL_PROCUREMENT_SOURCE_GATE.md")
    assert "permanent\nbyggeforutsetning" in readme
    assert "No human contact, permission request or source-owner outreach is permitted" in gates
    assert "Silence is never permission" in national
    assert "download then filter" in readme
    assert "No personal data may be collected, received, stored or processed" in gates


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


def test_rule_bounded_open_is_canonical() -> None:
    gates = _read("docs/BUILD_GATES.md")
    semantics = _read("docs/EVIDENCE_BOUNDED_PRODUCTION_SEMANTICS.md")
    phrase = (
        "No procurement match satisfying ProcRun's frozen exact-evidence rules "
        "was found in TED as of DATE."
    )
    assert phrase in semantics
    assert "no match satisfying ProcRun's frozen exact-evidence rules" in gates
    assert "does not establish absence outside TED" in semantics
    assert "historical inferential classification target" in gates
    assert "NEVER CLAIMED AS PASSED" in gates


def test_source_categories_and_prr_final_status() -> None:
    status = _read("docs/SOURCE_STATUS.md")
    assert "Category A — eligible for no-contact qualification" in status
    assert "Category B — permanently ineligible" in status
    assert "PRR Projects on dados.gov.pt | B | PERMANENTLY BLOCKED" in status
    assert "OpenCoesione PR FESR Lombardia 2021-2027 operation-list ZIP/CSV" in status
    assert "Broader OpenCoesione API / Projects / Soggetti routes" in status
    assert "Poland" in status
    assert "| B | REJECTED" in status


def test_opencoesione_a1_and_live_delivery_are_accepted() -> None:
    gates = _read("docs/BUILD_GATES.md")
    qualification = _read("docs/OPENCOESIONE_A1_QUALIFICATION.md")
    contracts = _read("src/procrun/source_contracts.py")
    collector = _read("src/procrun/collectors/opencoesione.py")
    live_transport = _read("src/procrun/collectors/opencoesione_live.py")
    assert "## A1-A20" in gates
    assert "**PASS.**" in gates
    assert (
        "APPROVED SOURCE CONTRACT — EXACT 2021-2027 EU COHESION OPERATION-LIST ROUTE ONLY"
        in qualification
    )
    assert "general OpenCoesione API" in qualification
    assert '"opencoesione_2021_2027_operations"' in contracts
    assert "EXPECTED_HEADERS" in collector
    assert "to_funding_projects" in collector
    assert "OPENCOESIONE_PROGRAM_URL" in live_transport
    assert "parse_operation_list_zip" in live_transport
    assert "OPENCOESIONE_PUBLICATION_PAGE" in live_transport


def test_opencoesione_privacy_and_scope_contract_is_frozen() -> None:
    qualification = _read("docs/OPENCOESIONE_A1_QUALIFICATION.md")
    for required in (
        "TITOLO_PROGETTO",
        "SINTESI_PROG",
        "name, tax code, telephone number or email address",
        "only for legal persons",
        "data-provider instruction and publication rule, not a technical database constraint",
        "CC BY 4.0",
        "bimonthly",
        "all national and regional 2021-2027 programmes financed with EU funds",
        "fail-closed",
    ):
        assert required in qualification


def test_own_code_closure_precedes_cosmetic_and_third_party_phase() -> None:
    readme = _read("README.md")
    gates = _read("docs/BUILD_GATES.md")
    sequencing = _read("docs/DELIVERY_READINESS_GATE.md")
    assert "A1-A20" in gates
    assert "infrastructure-closure" in gates
    assert "COSMETIC WEB WORK + THIRD-PARTY INTEGRATIONS ONLY" in gates
    assert "WEB PRODUCT BUILD: GO" in readme
    assert "Web implementation is the final build phase" in sequencing
    assert "Stripe" in sequencing


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
