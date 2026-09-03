from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_readme_points_to_v2_foundation() -> None:
    readme = _read("README.md")
    assert "docs/PRODUCT_FOUNDATION_V2.md" in readme
    assert "READY FOR WEBSITE BUILD" in readme
    assert "TED notice -> procurement opportunity -> purchasable requirements" in readme


def test_v2_product_identity_is_locked() -> None:
    spec = _read("docs/PRODUCT_FOUNDATION_V2.md")
    assert "ProcRun turns public procurement notices into supplier-specific product demand." in spec
    assert "active infrastructure opportunity feed | SUPPORTED" in spec
    assert "early procurement runway | NOT SUPPORTED" in spec
    assert "comprehensive EU-funding subset | NOT SUPPORTED" in spec
    assert "ProcRun Portugal — €149/month" in spec


def test_v2_preserves_absolute_intelligence_privacy_boundary() -> None:
    spec = _read("docs/PRODUCT_FOUNDATION_V2.md")
    gates = _read("docs/BUILD_GATES.md")
    source_status = _read("docs/SOURCE_STATUS.md")

    assert "No natural-person data may be collected, stored or processed" in spec
    assert "pre-receipt" in spec.lower()
    assert "No natural-person data may be collected, stored or processed" in gates
    assert "Do not receive a broad response containing prohibited fields" in source_status


def test_funded_project_discovery_is_not_a_v2_dependency() -> None:
    spec = _read("docs/PRODUCT_FOUNDATION_V2.md")
    gates = _read("docs/BUILD_GATES.md")
    source_status = _read("docs/SOURCE_STATUS.md")

    assert "product no longer depends on a funded-project discovery source" in spec
    assert "CLOSED BY DEFAULT" in gates
    assert "CLOSED BY DEFAULT" in source_status


def test_v2_website_scope_is_complete() -> None:
    spec = _read("docs/PRODUCT_FOUNDATION_V2.md")
    required_routes = (
        "/app",
        "/app/opportunities/[id]",
        "/app/market",
        "/app/profile",
        "/app/saved",
        "/app/account",
        "/methodology",
        "/pricing",
    )
    for route in required_routes:
        assert route in spec

    for capability in (
        "supplier-profile onboarding",
        "opportunity feed",
        "opportunity detail",
        "market-intelligence dashboard",
        "saved opportunities",
        "customer-safe read model/API",
    ):
        assert capability in spec
