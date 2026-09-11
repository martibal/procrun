import Link from "next/link";

export default function TermsPage() {
  return (
    <div className="public-shell">
      <header className="public-nav">
        <Link href="/" className="brand">ProcRun</Link>
        <nav className="nav"><Link href="/product">Product</Link><Link href="/methodology">Methodology</Link><Link href="/pricing">Pricing</Link><Link href="/login" className="nav-cta">Sign in</Link></nav>
      </header>
      <main className="page-shell narrow">
        <div className="eyebrow">Terms</div>
        <h1 className="page-title">Terms of use.</h1>
        <p className="page-intro">Effective 11 September 2026. These terms govern use of the ProcRun website and the currently available product surfaces. Paid checkout is disabled; merchant, billing, tax and invoicing terms will be added before any paid subscription can be formed.</p>

        <section className="content-section">
          <h2>Service scope</h2>
          <p>ProcRun provides supplier-side procurement intelligence based on approved funded-project wording and accepted procurement evidence. It is an information product, not a tender portal, bid-writing service, legal opinion, procurement authority or guarantee of commercial outcome.</p>
        </section>

        <section className="content-section">
          <h2>Evidence and interpretation</h2>
          <p>Source wording is presented as source evidence and is kept separate from ProcRun interpretation. ProcRun states are derived under frozen production rules and must be read together with their stated source scope, date and provenance.</p>
        </section>

        <section className="content-section">
          <h2>Coverage limitation</h2>
          <div className="definition"><strong>OPEN means that no procurement match satisfying ProcRun&apos;s frozen exact-evidence rules was found in TED as of the stated date.</strong><br /><br />It does not establish absence outside TED or under different wording, classification or procurement routes.</div>
        </section>

        <section className="content-section">
          <h2>No guaranteed completeness or outcome</h2>
          <p>ProcRun does not guarantee a complete bill of materials, discovery of every future purchase, supplier suitability, win probability, award outcome or complete procurement coverage outside the stated product boundary. UNRESOLVED states are intentionally retained when the evidence does not support a safe conclusion.</p>
        </section>

        <section className="content-section">
          <h2>Source attribution and availability</h2>
          <p>ProcRun uses independently published public sources under their applicable reuse terms. ProcRun is not endorsed by TED, the European Union, OpenCoesione or any source publisher. Source availability and upstream publication practices may change; ProcRun fails closed rather than silently widening an evidence claim.</p>
        </section>

        <section className="content-section">
          <h2>Paid service status</h2>
          <p>No paid subscription can currently be purchased through this build. Pricing shown on the site is informational until checkout is enabled. The legal merchant identity, billing terms, tax treatment and invoicing mechanics belong to the separate payment-integration gate and must be published before checkout activation.</p>
        </section>
      </main>
    </div>
  );
}
