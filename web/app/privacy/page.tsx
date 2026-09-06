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

      <h2>2. Account and billing data</h2>
      <p>When production authentication and billing are enabled, the customer control plane will necessarily process limited account, subscription and payment-related information required to provide the service. That data must remain separate from the intelligence ledger, source pipeline and model context.</p>

      <h2>3. Payment processing</h2>
      <p>Production payment processing is not yet active. Before paid launch, this page will identify the selected payment processor, the data handled for checkout/billing, and links to the relevant processor terms and privacy information.</p>

      <h2>4. Cookies and analytics</h2>
      <p>No advertising, session-replay or analytics SDK is enabled by default in the current web build. Any production cookies or telemetry that are genuinely necessary will be documented before launch.</p>

      <h2>5. Security and retention</h2>
      <p>Production account credentials, billing secrets and backend database credentials must remain outside the public repository and outside the intelligence output. Retention rules for customer-control-plane data will be published when the actual providers and authentication flow are finalized.</p>

      <h2>6. Source data</h2>
      <p>Public procurement and funded-project source data used by ProcRun is processed under the product's approved source contracts and customer-safe field boundary. Raw source payloads are not part of the browser contract.</p>

      <h2>7. Controller and contact information</h2>
      <p>Legal controller identity, registered address, privacy contact route and any required processor/subprocessor details will be published here before production account creation and paid checkout are enabled.</p>

      <div className="notice scope"><strong>Launch gate:</strong> this is the privacy framework for the customer web build. Processor-specific and merchant-specific details are intentionally not invented before those services are selected and activated.</div>
      <p><Link className="text-link strong" href="/terms">Read terms framework</Link></p>
    </section>
  </PublicPage>;
}
