import { requireAccount } from "@/lib/auth";
import {
  billingConfigured,
  hasPaidAccess,
  loadBillingAccount,
  merchantGateOpen,
} from "@/lib/billing";
import { openBillingPortalAction, startCheckoutAction } from "./actions";

export const dynamic = "force-dynamic";

export default async function AccountPage() {
  const { accountId } = await requireAccount();
  const billing = await loadBillingAccount(accountId);
  const configured = billingConfigured();
  const paid = hasPaidAccess(billing);
  const status = billing?.subscriptionStatus ?? "not subscribed";

  return <>
    <p className="small">Account</p>
    <h1 className="h1">Workspace and billing.</h1>
    <p className="lede">Control-plane account and billing data remain separate from ProcRun&apos;s intelligence plane.</p>

    <div className="coverage-list section">
      <div><strong>Plan</strong><p>ProcRun Lombardia, €149/month launch package.</p></div>
      <div><strong>Subscription</strong><p>{status}{paid ? " — paid access active" : ""}</p></div>
      <div><strong>Merchant gate</strong><p>{merchantGateOpen() ? "Enabled" : "Closed"}</p></div>
      <div><strong>Control-plane boundary</strong><p>Stripe billing data and billing identifiers are kept outside the intelligence database. ProcRun stores only opaque account, customer and subscription identifiers plus subscription state in the separate control database.</p></div>
    </div>

    {!configured ? (
      <div className="notice scope">
        <strong>Checkout remains fail-closed.</strong> The merchant gate and all required Stripe/control-plane configuration must be enabled before ProcRun can create a checkout or billing-portal session.
      </div>
    ) : (
      <div className="actions">
        {!paid ? <form action={startCheckoutAction}><button className="button" type="submit">Subscribe for €149/month</button></form> : null}
        {billing?.stripeCustomerId ? <form action={openBillingPortalAction}><button className="button secondary" type="submit">Manage subscription</button></form> : null}
      </div>
    )}
  </>;
}
