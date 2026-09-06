import { PublicPage } from "@/components/public-site";

export default function MethodologyPage() {
  return <PublicPage>
    <section className="page-hero">
      <p className="small">Methodology & coverage</p>
      <h1 className="h1 public-h1">Evidence first. Coverage stated, not implied.</h1>
      <p className="lede lede-large">ProcRun separates source facts, component extraction, procurement evidence and derived state so a customer can see both what supports a conclusion and what the conclusion does not say.</p>
    </section>

    <section className="public-section">
      <div className="method-grid">
        <article><span className="step">01</span><h2>Approved project source</h2><p>Funded-project records enter the intelligence pipeline only from explicitly approved public publication routes. The current live funded-project route is PR FESR Lombardia 2021–2027.</p></article>
        <article><span className="step">02</span><h2>Deterministic components</h2><p>A component must be supported by an exact project-scope evidence span. Generic assumptions about what a project probably buys are not enough.</p></article>
        <article><span className="step">03</span><h2>TED evidence search</h2><p>Procurement evidence is retrieved from Tenders Electronic Daily under bounded field projection, pagination and schema checks. Incomplete retrieval fails closed.</p></article>
        <article><span className="step">04</span><h2>Conservative state</h2><p>Strong accepted evidence can support CLOSED. Absence inside the complete approved TED search scope can support OPEN. Ambiguity or insufficient evidence produces UNRESOLVED.</p></article>
      </div>
    </section>

    <section className="public-section">
      <p className="small">State definitions</p>
      <h2 className="display-h2 compact-heading">How to read a component state.</h2>
      <div className="state-grid">
        <article className="state-panel"><span className="pill">OPEN · TED-scoped</span><h3>No relevant procurement found in TED as of DATE.</h3><p>This is a bounded negative-search conclusion. It is not a guarantee that procurement does not exist outside TED, including purely national or below-threshold procedures.</p></article>
        <article className="state-panel"><span className="pill closed">CLOSED</span><h3>Accepted procurement evidence shows the specific component has entered procurement by the cutoff.</h3><p>The evidence object retains the publication identity, date, exact evidence, matching context and observation cutoff.</p></article>
        <article className="state-panel"><span className="pill unresolved">UNRESOLVED</span><h3>A safe conclusion cannot be supported.</h3><p>Review-band evidence, ambiguity, insufficient corroboration or incomplete retrieval must remain unresolved rather than being promoted into a lead.</p></article>
      </div>
    </section>

    <section className="public-section split-section">
      <div><p className="small">Project state</p><h2 className="display-h2">Project-level runway is an aggregate of component evidence.</h2></div>
      <div className="coverage-list">
        <div><strong>OPEN</strong><p>Open-derived project states inherit the same explicit TED coverage boundary.</p></div>
        <div><strong>PARTIAL</strong><p>Some components have accepted procurement evidence while others still meet the bounded OPEN definition.</p></div>
        <div><strong>CLOSED</strong><p>The relevant supported components have accepted procurement evidence under the matching rules.</p></div>
        <div><strong>UNRESOLVED</strong><p>Ambiguity or insufficient evidence prevents a safe project-level runway conclusion.</p></div>
      </div>
    </section>

    <section className="public-section split-section">
      <div><p className="small">Source attribution</p><h2 className="display-h2">The derived analysis is ProcRun's, not the source publisher's.</h2></div>
      <div className="source-cards">
        <article><h3>TED</h3><p>Source: Tenders Electronic Daily (TED), Publications Office of the European Union. ProcRun transforms and classifies the source data; the derived analysis is not an official EU publication or endorsement.</p></article>
        <article><h3>OpenCoesione</h3><p>Source: OpenCoesione, Lista beneficiari e operazioni 2021-2027 (PR FESR Lombardia), used under CC BY 4.0. ProcRun transforms and classifies the source data; the derived analysis is not an official OpenCoesione, Italian-government or EU publication or endorsement.</p></article>
      </div>
      <p className="small">Dekningen reflekterer det italienske overvåkingssystemets nåværende fyllingsgrad for 2021–2027-perioden og vil vokse i takt med at flere prosjekter registreres nasjonalt.</p>
    </section>

    <section className="public-section">
      <p className="small">Explicit limitations</p>
      <h2 className="display-h2 compact-heading">Claims ProcRun does not make.</h2>
      <div className="negative-grid">
        <div>Complete national procurement coverage</div><div>Complete Italian public-investment coverage</div><div>A complete bill of materials</div><div>Discovery of every future purchase</div><div>Win probability or GO/NO-GO scoring</div><div>Buyer-person or contact intelligence</div><div>100% accuracy</div><div>Government, source or EU endorsement</div>
      </div>
    </section>
  </PublicPage>;
}
