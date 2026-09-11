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
        <h1 className="page-title">Evidence first. Interpretation second. Coverage always explicit.</h1>
        <p className="page-intro">ProcRun keeps three things separate: exact project-source wording, accepted procurement evidence, and the state derived from the frozen production rules. A customer should always be able to tell which layer they are looking at.</p>

        <section className="content-section">
          <h2>Project evidence is verbatim</h2>
          <p>Production components must be anchored to exact wording from an approved project field. ProcRun does not rewrite, summarize or invent wording and then present that rewrite as evidence. If the only admissible evidence is the project title, the interface labels it as <strong>Project title</strong>.</p>
        </section>

        <section className="content-section">
          <h2>OPEN is a bounded search conclusion</h2>
          <div className="definition"><strong>No procurement match satisfying ProcRun&apos;s frozen exact-evidence rules was found in TED as of DATE.</strong><br /><br />This does not establish absence outside TED or under different wording, classification or procurement routes. Incomplete retrieval cannot produce OPEN.</div>
        </section>

        <section className="content-section">
          <h2>States preserve uncertainty</h2>
          <p><strong>CLOSED</strong> requires accepted exact procurement evidence. <strong>OPEN</strong> requires the complete accepted TED search scope with no qualifying match. <strong>UNRESOLVED</strong> is used whenever ambiguity or insufficient evidence prevents a safe conclusion. For UNRESOLVED rows, the interface surfaces the exact source wording that the interpretation rests on.</p>
        </section>

        <section className="content-section">
          <h2>Production proof</h2>
          <p>The accepted infrastructure closure used 4,305 logical funded projects and 177,160 TED notices across 717 pages. TED retrieval was complete, the customer output was identical across three independent builds, the candidate index was reused, and the sealed research holdout was not touched.</p>
        </section>

        <section className="content-section">
          <h2>Source and customer boundary</h2>
          <p>The funded-project source is restricted to the approved OpenCoesione 2021–2027 publication family and admitted fields. TED is the procurement evidence and negative-search boundary for the launch product. Browser, API and export surfaces may consume only the versioned customer-safe read model.</p>
        </section>

        <section className="content-section">
          <h2>Separate research gate</h2>
          <p>The production product does not claim that an inferential classifier has passed an independent human-gold benchmark. Any future move beyond the current evidence-bounded semantics remains a separate quality gate and cannot silently widen production claims.</p>
        </section>
      </main>
    </div>
  );
}
