import Link from "next/link";
import { PublicPage } from "@/components/public-site";
import { opportunities } from "@/lib/read-model";
import styles from "./landing.module.css";

const example = opportunities[0];

export default function HomePage() {
  return <PublicPage>
    <div className={styles.page}>
      <section className={styles.hero}>
        <h1>Find what funded infrastructure projects still need to buy.</h1>
        <p className={styles.intro}>ProcRun helps suppliers find sales opportunities in public infrastructure projects in Lombardia. It shows what each project needs, what has already been procured, and what may still be left to buy — based on published EU funding data and procurement notices in TED.</p>

        <div className={styles.exampleIntro}>
          <h2>See how it works</h2>
          <p>This example shows how ProcRun turns a funded project into something a supplier can quickly assess. Start with the project, see the purchasing need ProcRun identified, then see whether matching procurement has been found.</p>
        </div>

        <article className={styles.record} aria-label="Example ProcRun result">
          <div className={styles.recordTop}>
            <div>
              <p className={styles.guideText}>The funded project</p>
              <h2>{example.projectTitle}</h2>
              <p className={styles.recordMeta}>{example.geography} <span>/</span> €{(example.valueEur ?? 0).toLocaleString("en-GB")} project value <span>/</span> Checked through {example.cutoffDate}</p>
              <p className={styles.explain}>This is a publicly funded infrastructure project included in the source data monitored by ProcRun.</p>
            </div>
          </div>

          <div className={styles.resultStep}>
            <p className={styles.guideText}>What the project needs</p>
            <p className={styles.resultValue}>{example.component}</p>
            <p className={styles.explain}>ProcRun reads the published project description and identifies equipment or services that the project says are part of the planned work.</p>
          </div>

          <div className={styles.resultStep}>
            <p className={styles.guideText}>What ProcRun found in procurement records</p>
            <p className={styles.resultValue}>No matching procurement found in TED as of {example.cutoffDate}.</p>
            <p className={styles.explain}>ProcRun checks TED, the EU publication service for public procurement notices, for evidence that this identified need has already been procured.</p>
          </div>

          <div className={styles.interpretation}>
            <p className={styles.guideText}>What this means for a supplier</p>
            <p>The identified need may still be worth investigating if your company supplies {example.component.toLowerCase()}. This is not a guarantee that the purchase is still available: ProcRun is showing that it found no relevant procurement in TED by the stated date.</p>
          </div>

          <details className={styles.evidence}>
            <summary>See the source evidence</summary>
            <div className={styles.evidenceBody}>
              <p className={styles.evidenceHeading}>Why ProcRun identified this need</p>
              <blockquote>“{example.projectEvidence}”</blockquote>
              <p>This text comes from the published project information used to identify the purchasing need above.</p>
              <p>Source: OpenCoesione 2021–2027 operation-list publication for PR FESR Lombardia.</p>
            </div>
          </details>
        </article>

        <div className={styles.actions}>
          <Link className={styles.primaryButton} href="/app">Open demo</Link>
          <Link className={styles.secondaryButton} href="/methodology">Read methodology</Link>
        </div>
      </section>

      <section className={styles.textSection}>
        <h2>What ProcRun gives you</h2>
        <p>For each funded project, ProcRun keeps the published project scope, the specific equipment or service identified in that scope, any accepted TED procurement evidence, the cutoff date and the resulting state.</p>
        <p>The useful distinction is simple: where procurement evidence exists, you can see it. Where no relevant TED procurement was found by the cutoff, that is shown as OPEN. Where the evidence is too weak or incomplete, the project stays UNRESOLVED.</p>
      </section>

      <section className={styles.definitionSection}>
        <h2>What OPEN means</h2>
        <p><strong>No relevant procurement found in TED as of the stated date.</strong></p>
        <p>That is a TED-scoped result. It does not mean the purchase cannot exist in a national or below-threshold channel.</p>
      </section>

      <section className={styles.textSection}>
        <h2>Current coverage</h2>
        <p>Funded-project scope currently comes from the approved OpenCoesione 2021–2027 EU-cohesion operation-list publication family, using the live PR FESR Lombardia route. Procurement evidence comes from Tenders Electronic Daily (TED).</p>
        <p>ProcRun does not claim complete national procurement coverage, every future purchase, a complete bill of materials, win probability or buyer/contact intelligence.</p>
        <Link className={styles.textLink} href="/methodology">Methodology and source limits</Link>
      </section>

      <section className={styles.priceSection}>
        <div>
          <h2>ProcRun Lombardia</h2>
          <p className={styles.price}>€149 <span>/ month</span></p>
          <p>Full opportunity feed, evidence detail, supplier profile, saved opportunities, market context and customer-safe CSV export.</p>
        </div>
        <Link className={styles.primaryButton} href="/pricing">View pricing</Link>
      </section>
    </div>
  </PublicPage>;
}
