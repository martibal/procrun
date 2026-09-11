import Link from "next/link";
import { PublicPage } from "@/components/public-site";
import styles from "./landing.module.css";

export default function HomePage() {
  return <PublicPage>
    <div className={styles.page}>
      <section className={styles.hero}>
        <h1>See what a funded project says — and what ProcRun can safely conclude.</h1>
        <p className={styles.intro}>ProcRun starts with exact wording from approved funded-project publications, identifies only components supported by that wording, checks the complete accepted TED search universe, and keeps source evidence separate from ProcRun interpretation.</p>
        <p className={styles.audience}>For suppliers evaluating already-funded infrastructure projects before a conventional tender search answers the question.</p>

        <article className={styles.record} aria-label="ProcRun evidence contract">
          <header className={styles.opportunityHeader}>
            <p className={styles.guideText}>What the customer sees</p>
            <h2>Project evidence and procurement state stay separate.</h2>
            <p className={styles.opportunityMeta}><span>Exact source wording</span><span>OPEN · CLOSED · UNRESOLVED</span></p>
            <p className={styles.originalTitle}>Every published row links back to the underlying project evidence and its bounded procurement assessment.</p>
          </header>

          <section className={styles.primaryFinding}>
            <p className={styles.guideText}>1 · Exact source wording</p>
            <p className={styles.resultValue}>The admitted project text is shown verbatim, with its source type and provenance.</p>
            <p className={styles.projectContext}>ProcRun does not rewrite project wording and present the rewrite as evidence.</p>
          </section>

          <section className={styles.procurementFinding}>
            <p className={styles.guideText}>2 · ProcRun interpretation</p>
            <p className={styles.procurementHeadline}>The derived state is shown separately from source text and accepted TED evidence.</p>
            <p className={styles.coverageNote}>OPEN is bounded to the complete accepted TED search universe. Ambiguity remains UNRESOLVED instead of being promoted to a stronger claim.</p>
          </section>

          <details className={styles.evidence}>
            <summary>View the evidence boundary</summary>
            <div className={styles.evidenceBody}>
              <h3>Project evidence</h3>
              <p>Only approved source fields enter the customer-safe read model, with exact text spans and source references preserved.</p>
              <h3>Procurement evidence</h3>
              <p>CLOSED requires accepted exact TED evidence. Plausible but insufficient matches block an OPEN conclusion.</p>
              <h3>Derived state</h3>
              <p>OPEN, CLOSED and UNRESOLVED are produced under frozen evidence rules. OPEN does not establish absence outside TED or under different wording, classification or procurement routes.</p>
              <h3>Reproducibility</h3>
              <p>The customer detail view exposes the read-model version, rule versions and deterministic content hash for the published project.</p>
            </div>
          </details>
        </article>

        <div className={styles.actions}>
          <Link className={styles.primaryButton} href="/app">Open customer view</Link>
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
