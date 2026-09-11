import { PublicPage } from "@/components/public-site";

export default function MethodologyPage() {
  return <PublicPage>
    <section className="page-hero narrow-copy">
      <p className="small">Methodology</p>
      <h1 className="public-h1">Evidence first. Interpretation second. Coverage always explicit.</h1>
      <p className="lede-large">ProcRun keeps three things separate: exact project-source wording, accepted procurement evidence, and the state derived from the frozen production rules. A customer should always be able to tell which layer they are looking at.</p>
    </section>

    <section className="public-section method-grid">
      <article><h2>Project evidence is verbatim</h2><p>Production components must be anchored to exact wording from an approved project field. ProcRun does not rewrite, summarize or invent wording and then present that rewrite as evidence. If the only admissible evidence is the project title, the interface labels it as <strong>Project title</strong>.</p></article>
      <article><h2>OPEN is bounded</h2><p><strong>No procurement match satisfying ProcRun&apos;s frozen exact-evidence rules was found in TED as of DATE.</strong> This does not establish absence outside TED or under different wording, classification or procurement routes. Incomplete retrieval cannot produce OPEN.</p></article>
      <article><h2>States preserve uncertainty</h2><p>CLOSED requires accepted exact procurement evidence. OPEN requires the complete accepted TED search scope with no qualifying match. UNRESOLVED is used whenever ambiguity or insufficient evidence prevents a safe conclusion.</p></article>
      <article><h2>Source and customer boundary</h2><p>The funded-project source is restricted to the approved OpenCoesione 2021–2027 publication family and admitted fields. Browser, API and export surfaces may consume only the versioned customer-safe read model.</p></article>
    </section>

    <section className="public-section">
      <h2 className="display-h2">Production proof</h2>
      <div className="proof-strip">
        <div><strong>4,305</strong><span>logical funded projects</span></div>
        <div><strong>177,160</strong><span>TED notices in the complete accepted Italy universe</span></div>
        <div><strong>717</strong><span>TED result pages processed</span></div>
      </div>
      <p className="small" style={{marginTop:20}}>Customer output was identical across three independent builds, the candidate index was reused, and the sealed research holdout was not touched.</p>
    </section>

    <section className="public-section">
      <h2 className="display-h2">Separate research gate</h2>
      <p className="lede-large">The production product does not claim that an inferential classifier has passed an independent human-gold benchmark. Any future move beyond the current evidence-bounded semantics remains a separate quality gate and cannot silently widen production claims.</p>
    </section>
  </PublicPage>;
}
