import Link from "next/link";

export default function MethodologyPage() {
  return (
    <div className="public-shell">
      <header className="public-nav">
        <Link href="/" className="brand">ProcRun</Link>
        <nav className="nav"><Link href="/product">Product</Link><Link href="/methodology">Methodology</Link><Link href="/pricing">Pricing</Link><Link href="/login" className="nav-cta">Sign in</Link></nav>
      </header>
      <main className="page-shell narrow">
        <div className="eyebrow">Methodology</div>
        <h1 className="page-title">Evidence first. Coverage stated, never implied.</h1>
        <p className="page-intro">ProcRun separates source facts, component extraction, procurement evidence and derived state so customers can see what supports each conclusion.</p>

        <section className="content-section">
          <h2>OPEN is a bounded search conclusion</h2>
          <div className="definition"><strong>No relevant procurement found in TED as of DATE.</strong><br /><br />This is not a guarantee that no procurement exists outside TED, including purely national or below-threshold procedures. Incomplete TED retrieval cannot produce OPEN.</div>
        </section>

        <section className="content-section">
          <h2>States preserve uncertainty</h2>
          <p><strong>CLOSED</strong> requires accepted procurement evidence for the specific component. <strong>OPEN</strong> requires a complete accepted TED search scope with no relevant procurement found. <strong>UNRESOLVED</strong> is used when ambiguity, incomplete retrieval or insufficient evidence prevents a safe conclusion.</p>
        </section>

        <section className="content-section">
          <h2>Source and customer boundary</h2>
          <p>TED is approved for field-bounded procurement evidence, market context and the MVP negative-search boundary. The funded-project source is limited to the exact approved OpenCoesione 2021–2027 EU-cohesion operation-list publication family and accepted runtime routes.</p>
          <p>Browser, API and export surfaces may consume only the versioned customer-safe read model. Raw source responses, beneficiary identity, buyer/contact identity and unvalidated candidate text do not belong in the customer interface.</p>
        </section>

        <section className="content-section">
          <h2>Claims ProcRun does not make</h2>
          <p>No complete Portuguese procurement coverage. No complete Italian public-investment coverage. No complete bill of materials. No guaranteed discovery of every future purchase. No win probability. No buyer-person intelligence. No source or EU endorsement.</p>
        </section>
      </main>
    </div>
  );
}
