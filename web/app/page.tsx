import Link from "next/link";
import { PublicPage } from "@/components/public-site";
import { opportunities } from "@/lib/read-model";
import styles from "./landing.module.css";

const example = opportunities[0];

export default function HomePage() {
  return <PublicPage>
    <div className={styles.page}>
      <section className={styles.hero}>
        <h1>See what a funded project says — and what ProcRun can safely conclude.</h1>
        <p className={styles.intro}>ProcRun starts with exact wording from approved funded-project publications, identifies only components supported by that wording, checks the complete accepted TED search universe, and keeps source evidence separate from ProcRun interpretation.</p>
        <p className={styles.audience}>For suppliers evaluating already-funded infrastructure projects before a conventional tender search answers the question.</p>

        <article className={styles.record} aria-label="ProcRun evidence example">
          <header className={styles.opportunityHeader}>
            <p className={styles.guideText}>Evidence example</p>
            <h2>{example.component}</h2>
            <p className={styles.opportunityMeta}><span>{example.geography}</span><span>{example.state}</span></p>
            <p className={styles.originalTitle}>Project: <span>{example.projectTitle}</span></p>
          </header>

          <section className={styles.primaryFinding}>
            <p className={styles.guideText}>Exact source wording · {example.projectEvidenceType}</p>
            <p className={styles.resultValue}>{example.projectEvidence}</p>
            <p className={styles.projectContext}>This wording is the source evidence. ProcRun does not rewrite it and present the rewrite as evidence.</p>
          </section>

          <section className={styles.procurementFinding}>
            <p className={styles.guideText}>ProcRun interpretation</p>
            <p className={styles.procurementHeadline}>{example.interpretation}</p>
            <p className={styles.coverageNote}>{example.openWording ?? example.procurementEvidence ?? "Evidence remains insufficient for a safe OPEN/CLOSED conclusion."}</p>
          </section>

          <details className={styles.evidence}>
            <summary>View the evidence boundary</summary>
            <div className={styles.evidenceBody}>
              <h3>Exact project text</h3>
              <blockquote>“{example.projectEvidence}”</blockquote>
              <h3>Derived state</h3>
              <p>{example.state}. Coverage: {example.coverage}. Cutoff: {example.cutoffDate}.</p>
              <h3>Production rule</h3>
              <p>OPEN, CLOSED and UNRESOLVED are derived under frozen evidence rules. OPEN is bounded to TED and does not establish absence outside TED or under different wording, classification or procurement routes.</p>
              <h3>Read model</h3>
              <p><code>{example.sourceVersion}</code></p>
            </div>
          </details>
        </article>

        <div className={styles.actions}>
          <Link className={styles.primaryButton} href="/app">Open demo</Link>
          <Link className={styles.secondaryButton} href="/methodology">Read methodology</Link>
        </div>
      </section>

      <section className="proof-strip" aria-label="Production acceptance evidence">
        <div><strong>4,305</strong><span>logical funded projects in the accepted production proof</span></div>
        <div><strong>177,160</strong><span>TED notices across the complete accepted Italy universe</span></div>
        <div><strong>717</strong><span>TED result pages processed in the accepted closure run</span></div>
      </section>

      <section className={styles.explainer}>
        <h2>Four steps, with the evidence visible at each one.</h2>
        <div className={styles.explainerRows}>
          <div><strong>Read approved project scope.</strong><p>Only admitted project fields enter the intelligence pipeline. Exact source wording remains identifiable.</p></div>
          <div><strong>Identify supported components.</strong><p>A component exists in production only when frozen rules can anchor it to exact project wording.</p></div>
          <div><strong>Check TED evidence.</strong><p>Accepted procurement evidence may close a component. Plausible ambiguity blocks an OPEN conclusion.</p></div>
          <div><strong>Show the bounded state.</strong><p>The workspace presents source wording and ProcRun interpretation separately: OPEN, CLOSED or UNRESOLVED.</p></div>
        </div>
      </section>

      <section className={styles.priceSection}>
        <div>
          <h2>ProcRun</h2>
          <p className={styles.price}>€149 <span>/ month</span></p>
          <p>Evidence-bounded funded-project runway, exact project wording, TED procurement evidence, supplier workspace, saved opportunities and customer-safe export surfaces. Checkout remains disabled until launch integrations are complete.</p>
        </div>
        <Link className={styles.primaryButton} href="/pricing">View pricing</Link>
      </section>
    </div>
  </PublicPage>;
}
