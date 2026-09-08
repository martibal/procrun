from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_account_deletion_requires_explicit_confirmation_and_authenticated_principal() -> None:
    actions = (REPO_ROOT / "web/app/app/account/actions.ts").read_text(encoding="utf-8")
    deletion = (REPO_ROOT / "web/lib/account-deletion.ts").read_text(encoding="utf-8")

    assert 'confirmation !== "DELETE"' in actions
    assert "await requireAccount()" in actions
    assert "await auth()" in actions
    assert "validateDeletionPrincipal(principal)" in deletion
    assert 'principal.orgRole !== "org:admin"' in deletion
    assert "expectedAccountId !== principal.accountId" in deletion


def test_account_deletion_verifies_all_account_scoped_workflow_rows_are_gone() -> None:
    deletion = (REPO_ROOT / "web/lib/account-deletion.ts").read_text(encoding="utf-8")

    assert "DELETE FROM procrun.accounts WHERE account_id = $1" in deletion
    assert "FROM procrun.component_matches WHERE account_id = $1" in deletion
    assert "FROM procrun.saved_opportunities WHERE account_id = $1" in deletion
    assert "FROM procrun.supplier_profiles WHERE account_id = $1" in deletion
    assert "ProcRun account-data deletion could not be verified" in deletion


def test_billing_identity_is_purged_before_workspace_and_clerk_identity() -> None:
    deletion = (REPO_ROOT / "web/lib/account-deletion.ts").read_text(encoding="utf-8")
    billing = (REPO_ROOT / "web/lib/billing.ts").read_text(encoding="utf-8")

    billing_pos = deletion.index("await purgeBillingIdentity(principal.accountId)")
    workspace_pos = deletion.index("await purgeIntelligenceAccount(principal.accountId)")
    clerk_pos = deletion.index("await purgeClerkPrincipal(principal)")
    assert billing_pos < workspace_pos < clerk_pos
    assert 'method: "DELETE"' in billing
    assert 'stripeDelete(`/subscriptions/${' in billing
    assert 'stripeDelete(`/customers/${' in billing
    assert "DELETE FROM procrun_control.billing_accounts WHERE account_id = $1" in billing
    assert "Billing-account deletion could not be verified" in billing


def test_provider_identity_deletion_matches_account_scope() -> None:
    deletion = (REPO_ROOT / "web/lib/account-deletion.ts").read_text(encoding="utf-8")

    assert "client.organizations.deleteOrganization(principal.orgId)" in deletion
    assert "client.users.deleteUser(principal.userId)" in deletion
    assert "clerkClient" in deletion


def test_privacy_copy_discloses_selected_processors_and_deletion_boundary() -> None:
    privacy = (REPO_ROOT / "web/app/privacy/page.tsx").read_text(encoding="utf-8")

    assert "Clerk" in privacy
    assert "Stripe" in privacy
    assert "Delete account" in privacy
    assert "legal retention" in privacy
