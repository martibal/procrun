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

        <article className={styles.record} aria-label="Example ProcRun opportunity">
          <div className={styles.recordTop}>
            <div>
              <h2>{example.projectTitle}</h2>
              <p className={styles.recordMeta}>{example.geography} <span>/</span> €{(example.valueEur ?? 0).toLocaleString("en-GB")} <span>/</span> Cutoff {example.cutoffDate}</p>
            </div>
            <span className={styles.relevance}><i aria-hidden="true" />High relevance</span>
          </div>
          <p className={styles.demand}><strong>Demand identified:</strong> {example.component}</p>
          <details className={styles.evidence}>
            <summary>Show evidence</summary>
            <blockquote>“{example.projectEvidence}”</blockquote>
            <p>Project scope evidence from the approved OpenCoesione 2021–2027 operation-list route for PR FESR Lombardia.</p>
            <p><strong>Procurement state:</strong> {example.state}. {example.openWording}</p>
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
