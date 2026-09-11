import { PublicPage } from "@/components/public-site";

export default function PrivacyPage() {
  return <PublicPage>
    <section className="page-hero narrow-copy">
      <p className="small">Privacy</p>
      <h1 className="public-h1">Privacy notice.</h1>
      <p className="lede-large">Effective 11 September 2026. This notice describes the data boundary of the current ProcRun build. Paid customer-account and billing integrations are not yet activated and therefore are not represented here as if they were already processing data.</p>
    </section>
    <section className="public-section legal-copy">
      <h2>Intelligence plane</h2><p>ProcRun&apos;s intelligence pipeline is designed not to collect, store, receive or process natural-person data. Only approved, field-bounded source data may enter the intelligence plane. Customer-facing intelligence is exposed through a versioned customer-safe read model rather than raw source responses.</p>
      <h2>Information excluded from the customer intelligence surface</h2><p>Raw source payloads, beneficiary identity fields, buyer/contact identity, contact-person details, model prompts and unvalidated candidate text are outside the browser and export contract. ProcRun does not use a download-then-filter workflow as a privacy control for the intelligence plane.</p>
      <h2>Current website state</h2><p>This build does not accept payment and does not claim that a not-yet-selected authentication, billing, invoicing, analytics or support processor is already active. The processor register, legal merchant identity, retention periods and customer-contact route will be published when those services are selected and before the corresponding processing is enabled.</p>
      <h2>Separation of planes</h2><p>Future account, authentication, subscription, billing, invoicing and support data belong to a separate customer control plane. Activating that plane must not widen the source-data contract or introduce personal data into the intelligence pipeline.</p>
      <h2>Changes to this notice</h2><p>This notice will be updated before any new customer-data processor or paid control-plane service is activated. Changes to customer-account processing do not alter the evidence and privacy constraints of the intelligence plane.</p>
    </section>
  </PublicPage>;
}
