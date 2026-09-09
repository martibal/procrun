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
        <p className="page-intro">ProcRun Portugal is defined at €149/month. The product is in the authorized customer-web build phase; paid launch remains blocked until authentication, billing, privacy/control-plane and final access tests are complete.</p>

        <section className="content-section">
          <div className="card">
            <div className="eyebrow">ProcRun Portugal</div>
            <h2 style={{marginTop: 10}}>€149 / month</h2>
            <p className="small">TED-scoped runway feed, funded-project and component evidence, market context, supplier profile, saved opportunities and customer-safe export surfaces.</p>
            <div className="notice"><strong>Checkout is not yet enabled.</strong> ProcRun is not accepting payment from this build until the web-phase launch controls are green.</div>
          </div>
        </section>

        <section className="content-section">
          <h2>Coverage remains explicit at every price point</h2>
          <p>OPEN means no relevant procurement found in TED as of the stated date. Subscription packaging never expands that conclusion into a claim about national or below-threshold procurement outside TED.</p>
        </section>
      </main>
    </div>
  );
}
