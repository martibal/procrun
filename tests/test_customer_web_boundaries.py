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


def test_clerk_is_the_production_control_plane_without_user_profile_leakage() -> None:
    auth = (REPO_ROOT / "web/lib/auth.ts").read_text(encoding="utf-8")
    proxy = (REPO_ROOT / "web/proxy.ts").read_text(encoding="utf-8")
    package = (REPO_ROOT / "web/package.json").read_text(encoding="utf-8")

    assert '@clerk/nextjs/server' in auth
    assert "await auth()" in auth
    assert "orgId" in auth and "userId" in auth
    assert "currentUser" not in auth
    assert "email" not in auth.casefold()
    assert "clerkMiddleware" in proxy
    assert '"@clerk/nextjs":"7.9.1"' in package


def test_account_activity_is_explicitly_scoped_to_authenticated_account() -> None:
    activity = (REPO_ROOT / "web/lib/since-last-visit.ts").read_text(encoding="utf-8")
    page = (REPO_ROOT / "web/app/app/page.tsx").read_text(encoding="utf-8")

    assert "PROCRUN_DEV_ACCOUNT_ID" not in activity
    assert "loadSinceLastVisitSummary(\n  accountId: string," in activity
    assert "WHERE account_id = $1" in activity
    assert 'import { requireAccount } from "@/lib/auth"' in page
    assert "const { accountId } = await requireAccount();" in page
    assert "loadSinceLastVisitSummary(accountId)" in page


def test_login_and_registration_fail_closed_when_clerk_is_unconfigured() -> None:
    login = (REPO_ROOT / "web/app/login/page.tsx").read_text(encoding="utf-8")
    signup = (REPO_ROOT / "web/app/signup/page.tsx").read_text(encoding="utf-8")
    root_layout = (REPO_ROOT / "web/app/layout.tsx").read_text(encoding="utf-8")

    assert "<SignIn" in login
    assert "Sign in is not configured." in login
    assert "<SignUp" in signup
    assert "Registration is not configured." in signup
    assert "ClerkProvider" in root_layout
    assert "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" in root_layout
