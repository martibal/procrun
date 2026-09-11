import Link from "next/link";

export default function ProductPage() {
  return (
    <div className="public-shell">
      <header className="public-nav">
        <Link href="/" className="brand">ProcRun</Link>
        <nav className="nav"><Link href="/product">Product</Link><Link href="/methodology">Methodology</Link><Link href="/pricing">Pricing</Link><Link href="/login" className="nav-cta">Sign in</Link></nav>
      </header>
      <main className="page-shell">
        <div className="eyebrow">Product</div>
        <h1 className="page-title">Funded-project evidence, procurement evidence and interpretation — kept separate.</h1>
        <p className="page-intro">ProcRun is a supplier-side procurement intelligence product for already-funded infrastructure projects. It shows the exact project wording used as evidence, the procurement evidence found in TED, and the bounded state ProcRun derives from those two layers.</p>

        <section className="content-section">
          <h2>The production chain</h2>
          <ul>
            <li>Start with an approved funded-project publication and admitted project fields.</li>
            <li>Create a purchasable component only when frozen rules anchor it to exact project wording.</li>
            <li>Search the complete accepted TED universe for procurement evidence relevant to that component.</li>
            <li>Return OPEN, CLOSED or UNRESOLVED without converting ambiguity into a lead.</li>
            <li>Expose source wording, provenance and ProcRun interpretation as separate customer fields.</li>
          </ul>
        </section>

        <section className="content-section">
          <h2>What the three states mean</h2>
          <div className="definition"><strong>OPEN</strong> — no procurement match satisfying ProcRun&apos;s frozen exact-evidence rules was found in TED as of the stated date.<br /><br /><strong>CLOSED</strong> — accepted exact TED evidence closes the component under the frozen rules.<br /><br /><strong>UNRESOLVED</strong> — the available evidence does not support a safe OPEN or CLOSED conclusion. The customer sees the exact project wording behind that unresolved state.</div>
        </section>

        <section className="content-section">
          <h2>What ProcRun does not infer</h2>
          <p>ProcRun does not provide win probability, buyer-person intelligence, a complete bill of materials, guaranteed discovery of every future purchase, or a claim of complete procurement coverage outside the stated source boundary.</p>
        </section>

        <section className="content-section">
          <h2>Customer data boundary</h2>
          <p>The browser and export surfaces consume only the versioned customer-safe read model. Raw source payloads, beneficiary identity fields, buyer/contact identity, model prompts and unvalidated candidate text remain outside the customer surface.</p>
          <div className="actions"><Link className="button" href="/methodology">Read methodology</Link><Link className="button secondary" href="/pricing">View pricing</Link></div>
        </section>
      </main>
    </div>
  );
}
