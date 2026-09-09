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
        <h1 className="page-title">From funded project scope to remaining procurement runway.</h1>
        <p className="page-intro">ProcRun is a supplier-side infrastructure procurement product. It combines approved funded-project scope with source-evidenced TED procurement activity and preserves uncertainty instead of converting it into a lead.</p>

        <section className="content-section">
          <h2>The decision chain</h2>
          <ul>
            <li>Start with an approved funded project.</li>
            <li>Extract purchasable components only when the project scope supports them.</li>
            <li>Search accepted TED procurement evidence against those components.</li>
            <li>Classify each component as OPEN, CLOSED or UNRESOLVED.</li>
            <li>Aggregate the component evidence into a customer-safe project runway state.</li>
          </ul>
        </section>

        <section className="content-section">
          <h2>What OPEN means</h2>
          <div className="definition"><strong>Coverage: TED.</strong> No relevant procurement was found in TED as of the stated date. This does not establish that no procurement exists outside TED, including purely national or below-threshold procedures.</div>
        </section>

        <section className="content-section">
          <h2>What ProcRun refuses to infer</h2>
          <p>ProcRun does not provide win probability, buyer-person intelligence, a complete bill of materials, guaranteed discovery of every future purchase, or a claim of complete national procurement coverage. Ambiguous or incomplete evidence remains unresolved.</p>
        </section>

        <section className="content-section">
          <h2>Customer data boundary</h2>
          <p>The browser-facing intelligence contract is the versioned <code>customer-runway-v1</code> read model. Raw source payloads, beneficiary identity fields, buyer/contact identity, model prompts and unvalidated candidate text are outside the customer surface.</p>
          <div className="actions"><Link className="button" href="/methodology">Read methodology</Link><Link className="button secondary" href="/pricing">View pricing</Link></div>
        </section>
      </main>
    </div>
  );
}
