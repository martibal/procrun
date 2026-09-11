import Link from "next/link";

export default function PricingPage() {
  return (
    <div className="public-shell">
      <header className="public-nav">
        <Link href="/" className="brand">ProcRun</Link>
        <nav className="nav"><Link href="/product">Product</Link><Link href="/methodology">Methodology</Link><Link href="/pricing">Pricing</Link><Link href="/login" className="nav-cta">Sign in</Link></nav>
      </header>
      <main className="page-shell narrow">
        <div className="eyebrow">Pricing</div>
        <h1 className="page-title">One professional launch package.</h1>
        <p className="page-intro">ProcRun is priced at €149/month for the launch product. Pricing is fixed; payment remains intentionally disabled until merchant, tax, invoicing, domain/TLS and final control-plane integrations are complete.</p>

        <section className="content-section">
          <div className="card">
            <div className="eyebrow">ProcRun</div>
            <h2 style={{marginTop: 10}}>€149 / month</h2>
            <p className="small">Evidence-bounded funded-project runway, exact project wording, component state, TED procurement evidence, supplier workspace, saved opportunities and customer-safe export surfaces.</p>
            <div className="notice"><strong>Checkout remains disabled.</strong> No payment is accepted from this build. Activation is a separate launch-integration step and does not change the evidence rules described on this site.</div>
          </div>
        </section>

        <section className="content-section">
          <h2>What the subscription does not change</h2>
          <p>OPEN remains a TED-bounded conclusion under the frozen exact-evidence rules. A paid subscription never expands that state into a claim that procurement is absent outside TED or under different wording, classification or procurement routes.</p>
        </section>
      </main>
    </div>
  );
}
