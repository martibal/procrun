from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_billing_control_plane_is_separate_and_fail_closed() -> None:
    control = (REPO_ROOT / "web/lib/control-db.ts").read_text(encoding="utf-8")
    billing = (REPO_ROOT / "web/lib/billing.ts").read_text(encoding="utf-8")

    assert "PROCRUN_CONTROL_DATABASE_URL" in control
    assert "PROCRUN_DATABASE_URL" not in control
    assert "PROCRUN_MERCHANT_GATE" in billing
    assert '=== "ENABLED"' in billing
    assert "STRIPE_SECRET_KEY" in billing
    assert "STRIPE_PRICE_LOMBARDIA_MONTHLY" in billing
    assert "STRIPE_WEBHOOK_SECRET" in billing
    assert "PROCRUN_CONTROL_DATABASE_URL" in billing
    assert "PROCRUN_DATABASE_URL" not in billing
    assert "email" not in control.casefold()
    assert "phone" not in control.casefold()


def test_checkout_and_portal_are_authenticated_and_account_scoped() -> None:
    actions = (REPO_ROOT / "web/app/app/account/actions.ts").read_text(encoding="utf-8")
    account = (REPO_ROOT / "web/app/app/account/page.tsx").read_text(encoding="utf-8")
    billing = (REPO_ROOT / "web/lib/billing.ts").read_text(encoding="utf-8")

    assert "const { accountId } = await requireAccount();" in actions
    assert "createCheckoutSession(accountId)" in actions
    assert "createBillingPortalSession(accountId)" in actions
    assert 'body.set("client_reference_id", accountId)' in billing
    assert 'body.set("metadata[procrun_account_id]", accountId)' in billing
    assert "loadBillingAccount(accountId)" in account
    assert "Subscribe for €149/month" in account
    assert "Manage subscription" in account


def test_stripe_webhook_requires_signature_and_persists_only_opaque_billing_state() -> None:
    route = (REPO_ROOT / "web/app/api/stripe/webhook/route.ts").read_text(encoding="utf-8")
    billing = (REPO_ROOT / "web/lib/billing.ts").read_text(encoding="utf-8")
    control = (REPO_ROOT / "web/lib/control-db.ts").read_text(encoding="utf-8")

    assert 'request.headers.get("stripe-signature")' in route
    assert "verifyStripeSignature(payload, signature)" in route
    assert "timingSafeEqual" in billing
    assert "createHmac" in billing
    assert "customer.subscription." in billing
    assert "checkout.session.completed" in billing
    assert "stripe_customer_id text UNIQUE" in control
    assert "stripe_subscription_id text UNIQUE" in control
    assert "subscription_status text" in control
    assert "billing_address" not in control
    assert "tax_id" not in control


def test_public_pricing_does_not_bypass_merchant_gate() -> None:
    pricing = (REPO_ROOT / "web/app/pricing/page.tsx").read_text(encoding="utf-8")

    assert "Checkout is merchant-gated." in pricing
    assert "Sign in to subscribe" in pricing
    assert "startCheckoutAction" not in pricing
