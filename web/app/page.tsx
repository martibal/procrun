import Link from "next/link";
import { PublicPage } from "@/components/public-site";

export default function HomePage() {
  return <PublicPage>
    <section className="hero hero-wide">
      <div className="eyebrow">Infrastructure procurement intelligence for suppliers</div>
      <h1>See which funded projects may still have procurement runway.</h1>
      <p className="lede lede-large">ProcRun starts with approved funded-project scope, identifies source-evidenced purchasable components, checks procurement evidence in TED, and shows what the evidence supports — including where the answer remains unresolved.</p>
      <div className="actions">
        <Link className="button large" href="/product">See how ProcRun works</Link>
        <Link className="button secondary large" href="/app">Open demo workspace</Link>
      </div>
      <p className="micro hero-note">The current workspace is a development/demo surface. Paid checkout and production authentication are not enabled yet.</p>
    </section>

    <section className="proof-strip" aria-label="Product principles">
      <div><strong>Source-evidenced</strong><span>Positive procurement matches retain supporting evidence.</span></div>
      <div><strong>Bounded absence</strong><span>OPEN is explicitly limited to the complete TED search scope.</span></div>
      <div><strong>Safe abstention</strong><span>Ambiguous or incomplete evidence stays UNRESOLVED.</span></div>
    </section>

    <section className="public-section split-section">
      <div>
        <div className="eyebrow">What you get</div>
        <h2 className="display-h2">A project-level view of what appears bought, still open, or genuinely uncertain.</h2>
      </div>
      <div className="feature-stack">
        <div className="feature-row"><span className="step">01</span><div><h3>Funded project scope</h3><p>Start from approved public project records rather than invented demand or generic tender keywords.</p></div></div>
        <div className="feature-row"><span className="step">02</span><div><h3>Purchasable components</h3><p>ProcRun derives only components supported by exact project-scope evidence and fixed extraction rules.</p></div></div>
        <div className="feature-row"><span className="step">03</span><div><h3>Procurement evidence</h3><p>Accepted TED evidence is matched conservatively to each component, with evidence and cutoff retained.</p></div></div>
        <div className="feature-row"><span className="step">04</span><div><h3>Remaining runway</h3><p>Each component and project is classified as OPEN, CLOSED, PARTIAL or UNRESOLVED under explicit rules.</p></div></div>
      </div>
    </section>

    <section className="public-section">
      <div className="section-heading-row">
        <div><div className="eyebrow">Read the state correctly</div><h2 className="display-h2 compact-heading">Three component outcomes, one important boundary.</h2></div>
        <Link className="text-link strong" href="/methodology">Full methodology →</Link>
      </div>
      <div className="state-grid">
        <article className="state-panel"><span className="pill">OPEN · TED-scoped</span><h3>No relevant procurement found in TED as of the stated cutoff.</h3><p>This does not establish that no procurement exists outside TED, including national or below-threshold procedures.</p></article>
        <article className="state-panel"><span className="pill closed">CLOSED</span><h3>Accepted procurement evidence exists for the specific component.</h3><p>The supporting publication, evidence span, date and matching rationale remain inspectable.</p></article>
        <article className="state-panel"><span className="pill unresolved">UNRESOLVED</span><h3>The evidence is not strong enough for a safe decision.</h3><p>Incomplete retrieval, ambiguity or insufficient corroboration cannot be converted into an opportunity claim.</p></article>
      </div>
    </section>

    <section className="public-section split-section coverage-section">
      <div>
        <div className="eyebrow">Coverage today</div>
        <h2 className="display-h2">Know exactly which public sources sit behind the result.</h2>
        <p className="lede">ProcRun does not imply broader coverage than its approved source contracts support.</p>
      </div>
      <div className="coverage-list">
        <div><strong>Funded-project source</strong><p>OpenCoesione, exact 2021–2027 EU-cohesion operation-list publication family. The current live funded-project route is PR FESR Lombardia.</p></div>
        <div><strong>Procurement evidence</strong><p>Tenders Electronic Daily (TED), used for field-bounded procurement evidence and the MVP negative-search boundary.</p></div>
        <div><strong>What is outside the claim</strong><p>ProcRun does not claim complete national procurement coverage, every future purchase, a complete bill of materials, win probability or buyer-person intelligence.</p></div>
      </div>
    </section>

    <section className="public-section cta-band">
      <div><div className="eyebrow">Launch package</div><h2 className="display-h2 compact-heading">Professional procurement evidence, €149 per month.</h2><p className="lede">One launch package. No permanent free tier is planned.</p></div>
      <div className="actions"><Link className="button large" href="/pricing">See pricing details</Link><Link className="button secondary large" href="/faq">Read FAQ</Link></div>
    </section>
  </PublicPage>;
}
