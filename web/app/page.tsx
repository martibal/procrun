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

        <article className={styles.record} aria-label="Current ProcRun opportunity">
          <div className={styles.recordTop}>
            <div>
              <p className={styles.guideText}>Current opportunity</p>
              <h2>{example.projectTitle}</h2>
            </div>
            <span className={styles.status}>{example.state}</span>
          </div>

          <dl className={styles.facts}>
            <div><dt>Region</dt><dd>{example.geography}</dd></div>
            <div><dt>Approved funding</dt><dd>€{(example.valueEur ?? 0).toLocaleString("en-GB")}</dd></div>
            <div><dt>Programme</dt><dd>{example.programme}</dd></div>
            <div><dt>Project start</dt><dd>{example.projectStart}</dd></div>
            <div><dt>Operation code</dt><dd>{example.projectId}</dd></div>
            <div><dt>Procurement checked through</dt><dd>{example.cutoffDate}</dd></div>
          </dl>

          <div className={styles.resultStep}>
            <p className={styles.guideText}>Identified purchasing need</p>
            <p className={styles.resultValue}>{example.component}</p>
            <p className={styles.projectContext}>The published project scope states that LED lighting is to be replaced for playing fields and walkways.</p>
          </div>

          <div className={styles.resultStep}>
            <p className={styles.guideText}>Procurement status</p>
            <p className={styles.resultValue}>{example.openWording}</p>
            <p className={styles.coverageNote}>{example.coverageNote}</p>
          </div>

          <details className={styles.evidence}>
            <summary>View full project evidence</summary>
            <div className={styles.evidenceBody}>
              <h3>Published project text</h3>
              <blockquote>“{example.projectEvidence}”</blockquote>

              <h3>Why lighting is identified</h3>
              <p>The source text explicitly refers to replacement of LED lighting for playing fields and walkways. The customer-safe production record classifies this as <code>energy_efficiency:lighting</code>.</p>

              <h3>What was checked in procurement data</h3>
              <p>{example.openWording}</p>
              <p>{example.coverageNote}</p>

              <h3>Source</h3>
              <p>{example.programme}</p>
              <p>OpenCoesione 2021–2027 beneficiary publication used by the approved Lombardia production route.</p>
              {example.sourceUrl ? <a className={styles.textLink} href={example.sourceUrl}>Open source publication</a> : null}

              <h3>Production record</h3>
              <p>Read model: <code>{example.sourceVersion}</code></p>
              <p>Operation code: <code>{example.projectId}</code></p>
              <p>Cutoff date: <code>{example.cutoffDate}</code></p>
            </div>
          </details>
        </article>

        <div className={styles.actions}>
          <Link className={styles.primaryButton} href="/app">Open demo</Link>
          <Link className={styles.secondaryButton} href="/pricing">View pricing</Link>
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
