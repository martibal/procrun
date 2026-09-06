import Link from "next/link";
import { PublicPage } from "@/components/public-site";

export default function TermsPage() {
  return <PublicPage>
    <section className="page-hero narrow-copy">
      <p className="small">Terms</p>
      <h1 className="h1 public-h1">Terms of service framework.</h1>
      <p className="lede">This page establishes the customer-facing terms structure for the web build. Final merchant identity, billing mechanics, cancellation language and effective date must be completed before paid checkout is enabled.</p>
    </section>

    <section className="public-section legal-copy">
      <h2>1. Service</h2>
      <p>ProcRun provides derived infrastructure procurement intelligence based on approved public data sources. The service may include project and component views, procurement evidence, supplier-relevance features, saved items, market context and customer-safe export.</p>

      <h2>2. Evidence and coverage</h2>
      <p>ProcRun does not guarantee that every procurement, future purchase or commercial opportunity will be identified. In the MVP, an OPEN state means only: <strong>No relevant procurement found in TED as of the stated date.</strong> It does not establish that no procurement exists outside TED, including purely national or below-threshold procedures.</p>

      <h2>3. Derived analysis</h2>
      <p>ProcRun transforms and classifies source data. The resulting analysis is not an official publication, approval or endorsement by TED, the Publications Office of the European Union, OpenCoesione, the Italian government or the European Union.</p>

      <h2>4. Customer responsibility</h2>
      <p>ProcRun is an information product. Customers remain responsible for commercial, procurement, legal and bidding decisions and for validating information appropriate to their own use case.</p>

      <h2>5. Subscription and billing</h2>
      <p>The current planned launch package is €149 per month. Final checkout will state taxes, invoice details, renewal, cancellation and payment terms before a customer is charged. No payment is accepted by the present development build.</p>

      <h2>6. Acceptable use</h2>
      <p>The service may not be used to misrepresent ProcRun analysis as an official source publication, to bypass access controls, or to attempt to obtain data outside the customer-safe product boundary.</p>

      <h2>7. Availability and change</h2>
      <p>Source availability, coverage and product features may change. ProcRun is designed to fail closed when source retrieval, evidence validation or publication integrity is not sufficient for a safe fresh result.</p>

      <h2>8. Merchant information</h2>
      <p>Legal business name, registered address, registration number, customer contact route and final governing-law/dispute information will be published here before paid launch.</p>

      <div className="notice scope"><strong>Launch gate:</strong> these terms are a product-development framework and are not yet the final paid-service contract.</div>
      <p><Link className="text-link strong" href="/privacy">Read privacy framework</Link></p>
    </section>
  </PublicPage>;
}
