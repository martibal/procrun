import Link from "next/link";
import { PublicPage } from "@/components/public-site";

export default function PrivacyPage() {
  return <PublicPage>
    <section className="page-hero narrow-copy">
      <p className="small">Privacy</p>
      <h1 className="h1 public-h1">Privacy by separation.</h1>
      <p className="lede">ProcRun keeps the intelligence pipeline and the customer account/billing control plane separate. Natural-person data is excluded from the intelligence plane.</p>
    </section>

    <section className="public-section legal-copy">
      <h2>1. Intelligence data</h2>
      <p>The ProcRun intelligence pipeline is designed not to collect, store or process natural-person data. Browser/API intelligence output is limited to the frozen customer-safe read model.</p>

      <h2>2. Account and authentication data</h2>
      <p>Clerk is the selected authentication control plane. ProcRun uses only the authenticated user or organization identifier needed to scope a workspace. Personal profile data from Clerk is not copied into the intelligence pipeline or model context.</p>

      <h2>3. Payment processing</h2>
      <p>Stripe is the selected payment processor. Checkout can collect billing address and tax information directly in Stripe. ProcRun stores only opaque Stripe customer/subscription identifiers and subscription state in a separate control database; payment and billing PII is not copied into the intelligence database.</p>

      <h2>4. Account deletion</h2>
      <p>The authenticated Account page contains a Delete account control. ProcRun first cancels any linked Stripe subscription, removes the linked Stripe customer where available, deletes and verifies all account-scoped workflow records, and then deletes the corresponding Clerk user or organization identity. Payment processors may still retain transaction records where legal retention obligations apply.</p>

      <h2>5. Cookies and analytics</h2>
      <p>No advertising, session-replay or analytics SDK is enabled by default in the current web build. Any production cookies or telemetry that are genuinely necessary will be documented before launch.</p>

      <h2>6. Security and retention</h2>
      <p>Production account credentials, billing secrets and backend database credentials remain outside the public repository and outside intelligence output. ProcRun customer workflow data is retained while the workspace exists and is deleted through the verified account-deletion flow described above.</p>

      <h2>7. Source data</h2>
      <p>Public procurement and funded-project source data used by ProcRun is processed under the product&apos;s approved source contracts and customer-safe field boundary. Raw source payloads are not part of the browser contract.</p>

      <h2>8. Controller and contact information</h2>
      <p>Legal controller identity, registered address, privacy contact route and any additional required processor/subprocessor details remain a production launch gate and will be published before paid production launch.</p>

      <div className="notice scope"><strong>Launch gate:</strong> merchant-specific controller, VAT and invoicing details are still fail-closed. Clerk and Stripe are selected providers, but paid production launch remains blocked until the remaining legal and operational gates are completed.</div>
      <p><Link className="text-link strong" href="/terms">Read terms framework</Link></p>
    </section>
  </PublicPage>;
}
