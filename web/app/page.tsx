import Link from "next/link";

export default function HomePage() {
  return <div className="public-shell">
    <div className="public-nav"><Link href="/" className="brand">ProcRun</Link><div className="nav"><Link href="/methodology">Methodology</Link><Link href="/pricing">Pricing</Link><Link href="/login">Sign in</Link></div></div>
    <section className="hero">
      <div className="eyebrow">Infrastructure procurement intelligence</div>
      <h1>See the evidence behind what may still be left to buy.</h1>
      <p className="lede">ProcRun separates project scope, procurement evidence and the conclusion that follows. In the MVP, every negative-search conclusion is explicitly limited to TED.</p>
      <div className="actions"><Link className="button" href="/app">Open fixture workspace</Link><Link className="button secondary" href="/methodology">Read methodology</Link></div>
    </section>
    <div className="notice scope"><strong>Current build:</strong> customer-safe fixture environment. No fixture is represented as live production data.</div>
    <section className="public-section grid">
      <div className="card flat"><div className="eyebrow">Evidence</div><h2 className="h2">Positive claims keep their source span.</h2><p className="small">Accepted components and procurement matches retain exact supporting evidence and version context.</p></div>
      <div className="card flat"><div className="eyebrow">Coverage</div><h2 className="h2">Absence is bounded.</h2><p className="small">OPEN means no relevant procurement found in TED as of the stated date — nothing broader.</p></div>
      <div className="card flat"><div className="eyebrow">Abstention</div><h2 className="h2">Ambiguity stays unresolved.</h2><p className="small">Incomplete retrieval or unsafe inference cannot be converted into a commercial lead.</p></div>
    </section>
  </div>;
}
