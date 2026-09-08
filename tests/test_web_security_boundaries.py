from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_security_headers_are_applied_by_proxy() -> None:
    proxy = (REPO_ROOT / "web/proxy.ts").read_text(encoding="utf-8")
    headers = (REPO_ROOT / "web/lib/security-headers.ts").read_text(encoding="utf-8")

    assert 'import { applySecurityHeaders } from "@/lib/security-headers"' in proxy
    assert "await clerkProxy(request, event)" in proxy
    assert "applySecurityHeaders(response, request.nextUrl.pathname)" in proxy
    assert '"X-Content-Type-Options", "nosniff"' in headers
    assert '"X-Frame-Options", "DENY"' in headers
    assert '"Referrer-Policy", "strict-origin-when-cross-origin"' in headers
    assert '"Permissions-Policy"' in headers
    assert '"Strict-Transport-Security"' in headers
    assert 'process.env.NODE_ENV === "production"' in headers


def test_authenticated_workspace_is_explicitly_non_cacheable_and_non_indexable() -> None:
    headers = (REPO_ROOT / "web/lib/security-headers.ts").read_text(encoding="utf-8")

    assert 'pathname === "/app" || pathname.startsWith("/app/")' in headers
    assert '"Cache-Control", "private, no-store, max-age=0"' in headers
    assert '"X-Robots-Tag", "noindex, nofollow, noarchive"' in headers
    assert 'response.headers.append("Vary", "Cookie")' in headers


def test_account_scoped_customer_queries_do_not_accept_foreign_account_ids() -> None:
    supplier = (REPO_ROOT / "web/lib/supplier-profile.ts").read_text(encoding="utf-8")
    saved = (REPO_ROOT / "web/lib/saved-opportunities.ts").read_text(encoding="utf-8")
    activity = (REPO_ROOT / "web/lib/since-last-visit.ts").read_text(encoding="utf-8")
    export_route = (REPO_ROOT / "web/app/app/export/route.ts").read_text(encoding="utf-8")

    assert supplier.count("WHERE account_id = $1") >= 2
    assert "WHERE account_id = $1 AND component_id = $2" in saved
    assert "WHERE s.account_id = $1" in saved
    assert "WHERE account_id = $1" in activity
    assert "const { accountId } = await requireAccount();" in export_route
    assert "loadSavedOpportunities(accountId)" in export_route
    assert "loadSupplierProfile(accountId)" in export_route

    for source in (supplier, saved, activity, export_route):
        assert "PROCRUN_DEV_ACCOUNT_ID" not in source


def test_deletion_target_is_bound_to_authenticated_clerk_principal() -> None:
    deletion = (REPO_ROOT / "web/lib/account-deletion.ts").read_text(encoding="utf-8")

    assert "expectedAccountId !== principal.accountId" in deletion
    assert 'principal.orgRole !== "org:admin"' in deletion
    assert 'DELETE FROM procrun.accounts WHERE account_id = $1' in deletion
    assert "purgeBillingIdentity(principal.accountId)" in deletion
    assert "purgeClerkPrincipal(principal)" in deletion


def test_remote_security_smoke_test_exists_and_is_fail_closed() -> None:
    smoke = (REPO_ROOT / "scripts/web_security_e2e.py").read_text(encoding="utf-8")

    assert "PROCRUN_E2E_BASE_URL" in smoke
    assert '"/app"' in smoke
    assert '"/api/stripe/webhook"' in smoke
    assert "X-Content-Type-Options" in smoke
    assert "X-Frame-Options" in smoke
    assert "unsigned Stripe webhook was accepted" in smoke
