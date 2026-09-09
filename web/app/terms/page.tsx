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
        <h1 className="page-title">Terms of service — pre-launch draft.</h1>
        <p className="page-intro">ProcRun is not yet accepting paid subscriptions from this build. These terms establish the product and coverage boundaries that the final checkout terms must preserve; merchant identity, billing mechanics and effective date must be finalized before paid launch.</p>

        <section className="content-section">
          <h2>Service scope</h2>
          <p>ProcRun provides supplier-side infrastructure procurement runway based on approved funded-project scope and accepted procurement evidence. It is an information product, not a tender portal, bid-writing service, legal opinion or guarantee of commercial outcome.</p>
        </section>

        <section className="content-section">
          <h2>Coverage limitation</h2>
          <div className="definition"><strong>OPEN means: no relevant procurement found in TED as of the stated date.</strong><br /><br />It does not establish that no procurement exists outside TED, including national or below-threshold procedures.</div>
        </section>

        <section className="content-section">
          <h2>No guaranteed completeness or outcome</h2>
          <p>ProcRun does not guarantee complete national procurement coverage, a complete bill of materials, discovery of every future purchase, win probability, award outcome or supplier suitability. UNRESOLVED states are intentionally retained where evidence is insufficient or ambiguous.</p>
        </section>

        <section className="content-section">
          <h2>Source attribution</h2>
          <p>ProcRun uses independently published public sources under their applicable reuse terms. ProcRun is not endorsed by TED, the European Union, OpenCoesione or any source publisher.</p>
        </section>
      </main>
    </div>
  );
}
