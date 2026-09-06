import Link from "next/link";
import { PublicPage } from "@/components/public-site";
import { opportunities } from "@/lib/read-model";
import styles from "./landing.module.css";

const example = opportunities[0];
const checkedThrough = "6 September 2026";

export default function HomePage() {
  return <PublicPage>
    <div className={styles.page}>
      <section className={styles.hero}>
        <h1>Find what funded infrastructure projects still need to buy.</h1>
        <p className={styles.intro}>ProcRun helps suppliers find sales opportunities in public infrastructure projects in Lombardia. It shows what each project needs, what has already been procured, and what may still be left to buy — based on published EU funding data and procurement notices in TED.</p>
        <p className={styles.audience}>For suppliers selling equipment, systems and services into public infrastructure projects.</p>

        <article className={styles.record} aria-label="Current ProcRun opportunity">
          <header className={styles.opportunityHeader}>
            <p className={styles.guideText}>Current opportunity</p>
            <h2>LED lighting replacement for playing fields and walkways</h2>
            <p className={styles.opportunityMeta}>{example.geography} <span>·</span> €{(example.valueEur ?? 0).toLocaleString("en-GB")} approved funding</p>
            <p className={styles.originalTitle}>Original project: <span>{example.projectTitle}</span></p>
          </header>

          <section className={styles.primaryFinding}>
            <p className={styles.guideText}>What may still need to be bought</p>
            <p className={styles.resultValue}>LED lighting for playing fields and walkways</p>
            <p className={styles.projectContext}>The published project scope explicitly states that LED lighting is to be replaced for playing fields and walkways.</p>
          </section>

          <section className={styles.procurementFinding}>
            <p className={styles.guideText}>Why this opportunity is showing now</p>
            <p className={styles.procurementHeadline}>The funded work identifies LED lighting, and ProcRun found no relevant procurement for it in TED through {checkedThrough}.</p>
            <p className={styles.coverageNote}>The procurement may still be ahead, or it may have taken place through a national or below-threshold procedure that does not appear in TED.</p>
          </section>

          <details className={styles.evidence}>
            <summary>View project and procurement evidence</summary>
            <div className={styles.evidenceBody}>
              <h3>Published project text</h3>
              <blockquote>“{example.projectEvidence}”</blockquote>

              <h3>Project details</h3>
              <dl className={styles.evidenceFacts}>
                <div><dt>Location</dt><dd>{example.geography}</dd></div>
                <div><dt>Programme</dt><dd>{example.programme}</dd></div>
                <div><dt>Project start</dt><dd>{example.projectStart}</dd></div>
                <div><dt>Operation code</dt><dd>{example.projectId}</dd></div>
                <div><dt>Approved funding</dt><dd>€{(example.valueEur ?? 0).toLocaleString("en-GB")}</dd></div>
              </dl>

              <h3>Why this purchasing need is shown</h3>
              <p>The source text explicitly refers to replacement of LED lighting for playing fields and walkways. The customer-safe production record classifies the identified component as <code>energy_efficiency:lighting</code>.</p>

              <h3>Procurement evidence</h3>
              <p>{example.openWording}</p>
              <p>{example.coverageNote}</p>

              <h3>Source</h3>
              <p>{example.programme}</p>
              <p>OpenCoesione 2021–2027 beneficiary publication used by the approved Lombardia production route.</p>
              {example.sourceUrl ? <a className={styles.textLink} href={example.sourceUrl}>Open source publication</a> : null}

              <h3>Production record</h3>
              <p>Read model: <code>{example.sourceVersion}</code></p>
              <p>Cutoff date: <code>{example.cutoffDate}</code></p>
            </div>
          </details>
        </article>

        <div className={styles.actions}>
          <Link className={styles.primaryButton} href="/demo">Open demo</Link>
          <Link className={styles.secondaryButton} href="/pricing">View pricing</Link>
        </div>
      </section>

      <section className={styles.explainer}>
        <h2>This is what ProcRun does across funded projects in Lombardia.</h2>
        <div className={styles.explainerRows}>
          <div><strong>Find the project.</strong><p>See funded projects and what they are expected to purchase.</p></div>
          <div><strong>Check the procurement.</strong><p>See whether ProcRun has found procurement evidence for those purchasing needs.</p></div>
          <div><strong>Focus your sales work.</strong><p>Filter the resulting opportunities to the products and services your company supplies.</p></div>
        </div>
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
