import Link from "next/link";

const proof = [
  ["4,631", "funded projects in the accepted production run"],
  ["176,540", "TED notices retrieved across the complete accepted Italy universe"],
  ["37", "projects resolved usefully from the production runway run"],
] as const;

export default function HomePage() {
  return (
    <div className="public-shell">
      <header className="public-nav">
        <Link href="/" className="brand">ProcRun</Link>
        <nav className="nav" aria-label="Primary navigation">
          <Link href="/product">Product</Link>
          <Link href="/methodology">Methodology</Link>
          <Link href="/pricing">Pricing</Link>
          <Link href="/login" className="nav-cta">Sign in</Link>
        </nav>
      </header>

      <main>
        <section className="hero hero-grid">
          <div>
            <div className="eyebrow">Infrastructure procurement runway</div>
            <h1>Find funded projects where procurement may still be open.</h1>
            <p className="lede">
              ProcRun starts with approved funded-project scope, maps purchasable components,
              checks source-evidenced procurement activity in TED, and shows the remaining runway
              without inventing demand.
            </p>
            <div className="actions">
              <Link className="button" href="/product">See how it works</Link>
              <Link className="button secondary" href="/methodology">Read the evidence rules</Link>
            </div>
          </div>
          <aside className="hero-panel" aria-label="ProcRun trust contract">
            <div className="eyebrow">The trust contract</div>
            <h2>Positive matches keep their evidence. Absence stays bounded.</h2>
            <p>
              In the MVP, <strong>OPEN</strong> means exactly: no relevant procurement found in TED
              as of the stated date. It is not a claim that no procurement exists outside TED,
              including national or below-threshold procedures.
            </p>
          </aside>
        </section>

        <section className="proof-strip" aria-label="Production acceptance evidence">
          {proof.map(([value, label]) => (
            <div key={value} className="proof-item">
              <strong>{value}</strong>
              <span>{label}</span>
            </div>
          ))}
        </section>

        <section className="public-section">
          <div className="section-heading">
            <div className="eyebrow">What ProcRun does</div>
            <h2>One evidence chain from funded scope to supplier runway.</h2>
          </div>
          <div className="step-grid">
            <article className="step-card"><span>01</span><h3>Start with funded scope</h3><p>Use only approved funded-project publications and admitted project fields.</p></article>
            <article className="step-card"><span>02</span><h3>Extract purchasable components</h3><p>Components must be supported by exact project-scope evidence. Unsupported demand is discarded.</p></article>
            <article className="step-card"><span>03</span><h3>Check procurement evidence</h3><p>Accepted TED evidence can close a component. Ambiguous or incomplete retrieval stays unresolved.</p></article>
            <article className="step-card"><span>04</span><h3>Show remaining runway</h3><p>Customer-safe project states surface what is closed, unresolved, partial, or still open in the TED-scoped MVP.</p></article>
          </div>
        </section>

        <section className="public-section split-section">
          <div>
            <div className="eyebrow">Built for suppliers</div>
            <h2>Not another tender portal.</h2>
          </div>
          <div className="body-copy">
            <p>ProcRun is designed to answer a different question: which already-funded projects still have evidence-supported procurement runway?</p>
            <p>It does not score your chance of winning, create buyer-person intelligence, or claim complete national procurement coverage.</p>
          </div>
        </section>

        <section className="scope-banner">
          <div><div className="eyebrow">MVP coverage</div><h2>TED-scoped by design.</h2></div>
          <p>Every OPEN conclusion preserves the same limitation: no relevant procurement found in TED as of the observation date. Broader absence is never inferred.</p>
        </section>
      </main>

      <footer className="public-footer">
        <div><strong>ProcRun</strong><span>Evidence-first infrastructure procurement runway.</span></div>
        <nav><Link href="/terms">Terms</Link><Link href="/privacy">Privacy</Link><Link href="/methodology">Methodology</Link></nav>
      </footer>
    </div>
  );
}
