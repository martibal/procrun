import Link from "next/link";

const proof = [
  ["4,305", "logical funded projects in the accepted production proof"],
  ["177,160", "TED notices across the complete accepted Italy universe"],
  ["116", "projects with evidence-bounded OPEN runway at the proof cutoff"],
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
            <div className="eyebrow">Funded-project procurement evidence</div>
            <h1>See what a funded project says — and what ProcRun can safely conclude.</h1>
            <p className="lede">
              ProcRun starts with exact wording from approved funded-project publications, identifies only components supported by that wording, checks the complete accepted TED search universe, and keeps source evidence separate from ProcRun interpretation.
            </p>
            <div className="actions">
              <Link className="button" href="/product">See the product</Link>
              <Link className="button secondary" href="/methodology">Read the evidence rules</Link>
            </div>
          </div>
          <aside className="hero-panel" aria-label="ProcRun trust contract">
            <div className="eyebrow">Evidence boundary</div>
            <h2>Source wording is evidence. State is interpretation.</h2>
            <p>
              ProcRun never rewrites source wording into evidence. OPEN, CLOSED and UNRESOLVED are derived states with explicit rules and provenance. OPEN is bounded to TED and never means that procurement is absent everywhere.
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
            <div className="eyebrow">How the product works</div>
            <h2>Four steps, with the evidence visible at each one.</h2>
          </div>
          <div className="step-grid">
            <article className="step-card"><span>01</span><h3>Read approved project scope</h3><p>Only admitted project fields enter the intelligence pipeline. Exact source wording remains identifiable.</p></article>
            <article className="step-card"><span>02</span><h3>Identify supported components</h3><p>A component exists in production only when frozen rules can anchor it to exact project wording.</p></article>
            <article className="step-card"><span>03</span><h3>Check TED evidence</h3><p>Accepted procurement evidence may close a component. Plausible ambiguity blocks an OPEN conclusion.</p></article>
            <article className="step-card"><span>04</span><h3>Show the bounded state</h3><p>The workspace presents source wording and ProcRun interpretation separately: OPEN, CLOSED or UNRESOLVED.</p></article>
          </div>
        </section>

        <section className="public-section split-section">
          <div>
            <div className="eyebrow">Why it exists</div>
            <h2>Not another tender portal.</h2>
          </div>
          <div className="body-copy">
            <p>ProcRun is designed for suppliers who want to inspect already-funded projects before a conventional tender search answers the question.</p>
            <p>It does not manufacture leads, score win probability, infer buyer-person intelligence, or hide uncertainty behind a confidence label.</p>
          </div>
        </section>

        <section className="scope-banner">
          <div><div className="eyebrow">Launch coverage</div><h2>Italy source scope. TED procurement boundary.</h2></div>
          <p>The accepted production proof covers 4,305 logical funded projects and the complete accepted Italy TED universe at the cutoff. Every OPEN conclusion remains explicitly limited to the frozen TED search rules and date shown to the customer.</p>
        </section>
      </main>

      <footer className="public-footer">
        <div><strong>ProcRun</strong><span>Evidence-bounded funded-project procurement intelligence.</span></div>
        <nav><Link href="/terms">Terms</Link><Link href="/privacy">Privacy</Link><Link href="/methodology">Methodology</Link></nav>
      </footer>
    </div>
  );
}
