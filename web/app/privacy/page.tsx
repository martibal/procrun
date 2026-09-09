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
        <h1 className="page-title">Privacy — pre-launch control-plane notice.</h1>
        <p className="page-intro">ProcRun keeps the intelligence plane and the future customer account/billing control plane separate. Paid account processing is not enabled in this build; the final notice must be completed with the actual processors, retention rules, merchant identity and contact channel before launch.</p>

        <section className="content-section">
          <h2>Intelligence plane</h2>
          <p>ProcRun's intelligence pipeline is designed not to collect, store or process natural-person data. Customer-facing intelligence is exposed only through the versioned customer-safe read model. Raw source payloads, beneficiary identity fields and buyer/contact identity are outside the browser contract.</p>
        </section>

        <section className="content-section">
          <h2>Customer control plane</h2>
          <p>Authentication, subscription, billing, invoicing and support necessarily belong to a separate customer control plane. Those processors and exact data categories will be documented here before they are activated for paid users.</p>
        </section>

        <section className="content-section">
          <h2>Pre-launch status</h2>
          <p>This build does not yet accept paid subscriptions. No statement on this page should be read as implying that a not-yet-configured authentication, billing or analytics processor is already in use.</p>
        </section>
      </main>
    </div>
  );
}
