import Link from "next/link";
import { PublicPage } from "@/components/public-site";

export default function ProductPage() {
  return <PublicPage>
    <section className="page-hero narrow-copy">
      <p className="small">Product</p>
      <h1 className="public-h1">Funded-project evidence, procurement evidence and interpretation — kept separate.</h1>
      <p className="lede-large">ProcRun is a supplier-side procurement intelligence product for already-funded infrastructure projects. It shows the exact project wording used as evidence, the procurement evidence found in TED, and the bounded state ProcRun derives from those two layers.</p>
    </section>

    <section className="public-section">
      <h2 className="display-h2">The production chain</h2>
      <div className="feature-stack">
        <div className="feature-row"><span className="step">01</span><div><h3>Start with approved project wording</h3><p>Only approved funded-project publications and admitted fields enter the intelligence pipeline.</p></div></div>
        <div className="feature-row"><span className="step">02</span><div><h3>Anchor supported components</h3><p>A purchasable component exists only when frozen rules anchor it to exact source wording.</p></div></div>
        <div className="feature-row"><span className="step">03</span><div><h3>Search the accepted TED universe</h3><p>Procurement evidence is checked against the complete accepted search scope for the stated cutoff.</p></div></div>
        <div className="feature-row"><span className="step">04</span><div><h3>Return a bounded state</h3><p>OPEN, CLOSED or UNRESOLVED is shown without converting ambiguity into a lead.</p></div></div>
      </div>
    </section>

    <section className="public-section">
      <h2 className="display-h2">What the three states mean</h2>
      <div className="state-grid">
        <article className="state-panel"><h3>OPEN</h3><p>No procurement match satisfying ProcRun&apos;s frozen exact-evidence rules was found in TED as of the stated date.</p></article>
        <article className="state-panel"><h3>CLOSED</h3><p>Accepted exact TED evidence closes the component under the frozen rules.</p></article>
        <article className="state-panel"><h3>UNRESOLVED</h3><p>The evidence does not support a safe OPEN or CLOSED conclusion. The exact source wording remains visible.</p></article>
      </div>
    </section>

    <section className="public-section split-section">
      <div><h2 className="display-h2">What ProcRun does not infer</h2></div>
      <div className="coverage-list"><div><p>No win probability, buyer-person intelligence, complete bill of materials, guaranteed discovery of every future purchase, or claim of procurement coverage outside the stated source boundary.</p></div></div>
    </section>

    <section className="public-section cta-band">
      <div><h2 className="display-h2">Inspect the rules before the result.</h2><p className="small">The browser and export surfaces consume only the versioned customer-safe read model.</p></div>
      <div className="actions"><Link className="button" href="/methodology">Read methodology</Link><Link className="button secondary" href="/pricing">View pricing</Link></div>
    </section>
  </PublicPage>;
}
