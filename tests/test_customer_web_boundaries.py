from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_customer_project_projection_excludes_municipality() -> None:
    projection = (REPO_ROOT / "web/lib/production-projects.ts").read_text(encoding="utf-8")
    project_list = (REPO_ROOT / "web/app/app/page.tsx").read_text(encoding="utf-8")
    project_detail = (REPO_ROOT / "web/app/app/projects/[id]/page.tsx").read_text(encoding="utf-8")

    assert "municipality" not in projection
    assert "municipality" not in project_list
    assert "municipality" not in project_detail


def test_customer_category_baselines_fail_closed_below_twenty() -> None:
    source = (REPO_ROOT / "web/lib/category-baselines.ts").read_text(encoding="utf-8")

    assert "MIN_CATEGORY_BASELINE_N = 20" in source
    assert "HAVING count(*) >= ${MIN_CATEGORY_BASELINE_N}" in source
    assert "durations.length < MIN_CATEGORY_BASELINE_N" in source


def test_market_copy_discloses_minimum_baseline_sample() -> None:
    page = (REPO_ROOT / "web/app/app/market/page.tsx").read_text(encoding="utf-8")

    assert "at least 20 completed comparable lifecycles" in page
    assert "n ≥ 20" in page


def test_authenticated_app_routes_are_guarded_by_fail_closed_account_boundary() -> None:
    auth = (REPO_ROOT / "web/lib/auth.ts").read_text(encoding="utf-8")
    layout = (REPO_ROOT / "web/app/app/layout.tsx").read_text(encoding="utf-8")

    assert 'import "server-only"' in auth
    assert 'process.env.NODE_ENV === "production"' in auth
    assert "if (!isProduction)" in auth
    assert "PROCRUN_DEV_ACCOUNT_ID" in auth
    assert 'redirect("/login")' in auth
    assert "return { accountId, source: \"session\" }" in auth
    assert 'import { requireAccount } from "@/lib/auth"' in layout
    assert "await requireAccount();" in layout
    assert "PROCRUN_DEV_ACCOUNT_ID" not in layout


def test_development_account_cannot_be_used_as_production_fallback() -> None:
    auth = (REPO_ROOT / "web/lib/auth.ts").read_text(encoding="utf-8")

    production_guard = auth.index('const isProduction = process.env.NODE_ENV === "production"')
    dev_guard = auth.index("if (!isProduction)")
    dev_account = auth.index("PROCRUN_DEV_ACCOUNT_ID")
    session_lookup = auth.index("resolveSessionAccountId")

    assert production_guard < dev_guard < dev_account
    assert dev_account < auth.index('redirect("/login")')
    assert session_lookup < auth.index('redirect("/login")')
