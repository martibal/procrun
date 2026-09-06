import Link from "next/link";
import { PublicPage } from "@/components/public-site";

export default function ProductPage() {
  return <PublicPage>
    <section className="page-hero">
      <div className="eyebrow">Product</div>
      <h1 className="h1 public-h1">From funded project to remaining procurement runway.</h1>
      <p className="lede lede-large">ProcRun is built for suppliers that need to understand where a funded infrastructure project appears to be in its procurement lifecycle — without turning weak signals into confident claims.</p>
    </section>

    <section className="public-section">
      <div className="process-grid">
        <article><span className="step">01</span><h2>Start with a funded project</h2><p>ProcRun admits projects only from approved public-source routes and preserves project identity, scope, dates, programme, region and funding fields allowed by the customer-safe contract.</p></article>
        <article><span className="step">02</span><h2>Identify evidenced components</h2><p>Purchasable components are derived from project scope only when an exact source span supports them. The component is not invented from generic sector assumptions.</p></article>
        <article><span className="step">03</span><h2>Check procurement evidence</h2><p>TED procurement evidence is searched and matched under fixed rules. Strong evidence can close a component; weaker evidence does not.</p></article>
        <article><span className="step">04</span><h2>Publish the runway state</h2><p>The resulting component and project states show what the evidence supports at a specific cutoff, together with coverage and rationale.</p></article>
      </div>
    </section>

    <section className="public-section split-section">
      <div><div className="eyebrow">Customer workspace</div><h2 className="display-h2">The information should be usable, not buried.</h2></div>
      <div className="coverage-list">
        <div><strong>Opportunity/runway feed</strong><p>Review projects and components by state and supplier relevance while keeping the evidence state separate from ranking.</p></div>
        <div><strong>Project detail</strong><p>Inspect funded scope, project metadata, component states, cutoff and the reasoning behind the aggregate project state.</p></div>
        <div><strong>Component evidence</strong><p>See the exact project-scope evidence and accepted procurement evidence behind each CLOSED decision, or the explicit TED coverage note behind OPEN.</p></div>
        <div><strong>Supplier profile</strong><p>Use deterministic profile inputs to improve relevance. Supplier relevance may change ordering; it cannot rewrite procurement evidence or state.</p></div>
        <div><strong>Saved opportunities</strong><p>Keep a working shortlist inside the customer control plane without changing the underlying intelligence record.</p></div>
        <div><strong>CSV export</strong><p>Export the customer-safe view for analysis or internal workflows without exposing raw source payloads or internal model data.</p></div>
      </div>
    </section>

    <section className="public-section">
      <div className="eyebrow">What ProcRun is not</div>
      <h2 className="display-h2 compact-heading">The product stays deliberately narrow.</h2>
      <div className="negative-grid">
        <div>Not a general tender portal</div><div>Not a bid writer</div><div>Not a CRM</div><div>Not a win-probability model</div><div>Not buyer-person intelligence</div><div>Not a guarantee of every future purchase</div>
      </div>
    </section>

    <section className="public-section cta-band">
      <div><div className="eyebrow">Inspect before you subscribe</div><h2 className="display-h2 compact-heading">Read the evidence rules and coverage boundary.</h2></div>
      <div className="actions"><Link className="button large" href="/methodology">Read methodology</Link><Link className="button secondary large" href="/app">Open demo workspace</Link></div>
    </section>
  </PublicPage>;
}
