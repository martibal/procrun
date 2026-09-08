import { requireAccount } from "@/lib/auth";
import {
  billingConfigured,
  hasPaidAccess,
  loadBillingAccount,
  merchantGateOpen,
} from "@/lib/billing";
import { deleteAccountAction, openBillingPortalAction, startCheckoutAction } from "./actions";

export const dynamic = "force-dynamic";

export default async function AccountPage() {
  const { accountId } = await requireAccount();
  const billing = await loadBillingAccount(accountId);
  const configured = billingConfigured();
  const paid = hasPaidAccess(billing);
  const status = billing?.subscriptionStatus ?? "not subscribed";
  const organizationWorkspace = accountId.startsWith("org:");

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

    <section className="section">
      <h2 className="h2">Delete account</h2>
      <p>
        This permanently removes the Supplier Profile, saved opportunities, match history and account
        activity for this ProcRun workspace. Any Stripe subscription is cancelled before local data is
        removed, and the linked Stripe customer is deleted. Deletion is verified before the Clerk
        identity or organization is removed.
      </p>
      {organizationWorkspace ? (
        <div className="notice scope">
          <strong>Organization workspace.</strong> Only an organization administrator can delete it.
          Deleting it removes the shared ProcRun organization, not only your membership.
        </div>
      ) : null}
      <form action={deleteAccountAction} className="formgrid">
        <label className="field" htmlFor="delete-confirmation">
          <strong>Type DELETE to confirm</strong>
          <input
            id="delete-confirmation"
            name="confirmation"
            type="text"
            autoComplete="off"
            pattern="DELETE"
            required
          />
        </label>
        <div className="actions">
          <button className="button" type="submit">Delete ProcRun account</button>
        </div>
      </form>
      <p className="micro">
        Payment processors may retain transaction records where required by law or their legal-retention
        obligations. ProcRun does not copy those retained payment records into the intelligence plane.
      </p>
    </section>
  </>;
}
