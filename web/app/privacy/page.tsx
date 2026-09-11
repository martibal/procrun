import Link from "next/link";

export default function PrivacyPage() {
  return (
    <div className="public-shell">
      <header className="public-nav">
        <Link href="/" className="brand">ProcRun</Link>
        <nav className="nav"><Link href="/product">Product</Link><Link href="/methodology">Methodology</Link><Link href="/pricing">Pricing</Link><Link href="/login" className="nav-cta">Sign in</Link></nav>
      </header>
      <main className="page-shell narrow">
        <div className="eyebrow">Privacy</div>
        <h1 className="page-title">Privacy notice.</h1>
        <p className="page-intro">Effective 11 September 2026. This notice describes the data boundary of the current ProcRun build. Paid customer-account and billing integrations are not yet activated and therefore are not represented here as if they were already processing data.</p>

        <section className="content-section">
          <h2>Intelligence plane</h2>
          <p>ProcRun&apos;s intelligence pipeline is designed not to collect, store, receive or process natural-person data. Only approved, field-bounded source data may enter the intelligence plane. Customer-facing intelligence is exposed through a versioned customer-safe read model rather than raw source responses.</p>
        </section>

        <section className="content-section">
          <h2>Information excluded from the customer intelligence surface</h2>
          <p>Raw source payloads, beneficiary identity fields, buyer/contact identity, contact-person details, model prompts and unvalidated candidate text are outside the browser and export contract. ProcRun does not use a download-then-filter workflow as a privacy control for the intelligence plane.</p>
        </section>

        <section className="content-section">
          <h2>Current website state</h2>
          <p>This build does not accept payment and does not claim that a not-yet-selected authentication, billing, invoicing, analytics or support processor is already active. The processor register, legal merchant identity, retention periods and customer-contact route will be published when those services are selected and before the corresponding processing is enabled.</p>
        </section>

        <section className="content-section">
          <h2>Separation of planes</h2>
          <p>Future account, authentication, subscription, billing, invoicing and support data belong to a separate customer control plane. Activating that plane must not widen the source-data contract or introduce personal data into the intelligence pipeline.</p>
        </section>

        <section className="content-section">
          <h2>Changes to this notice</h2>
          <p>This notice will be updated before any new customer-data processor or paid control-plane service is activated. Changes to customer-account processing do not alter the evidence and privacy constraints of the intelligence plane.</p>
        </section>
      </main>
    </div>
  );
}
