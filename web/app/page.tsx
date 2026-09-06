import Link from "next/link";
import { PublicPage } from "@/components/public-site";
import styles from "./landing.module.css";

export default function HomePage() {
  return <PublicPage>
    <section className={styles.hero}>
      <div className="eyebrow">Procurement intelligence for infrastructure suppliers</div>
      <h1>Find funded projects that may still have procurement left.</h1>
      <p className={styles.intro}>ProcRun takes public funded-project records, identifies the equipment and services described in the project scope, and checks TED for procurement evidence. You get a project list that shows what appears already procured, what has no matching TED procurement at the cutoff, and what cannot be decided safely.</p>
      <p className={styles.use}>Use it to decide which funded projects are worth investigating first, without reading project documents and procurement notices one by one.</p>
      <div className="actions">
        <Link className="button large" href="/app">Open the demo</Link>
        <Link className={`text-link strong ${styles.secondaryLink}`} href="/methodology">See exactly how it is calculated →</Link>
      </div>
    </section>

    <section className={`${styles.section} ${styles.twoCol}`}>
      <div>
        <h2>What you get</h2>
        <p>Each project is broken down into purchasable components supported by the published project description. ProcRun then checks those components against TED procurement evidence.</p>
      </div>
      <div className={styles.lines}>
        <div><strong>Project</strong><span>Title, programme, region, dates, approved funding and source.</span></div>
        <div><strong>Components</strong><span>The equipment or services that can be supported directly by the project scope.</span></div>
        <div><strong>Procurement evidence</strong><span>Matched TED notices with publication date, notice identity and the exact evidence used.</span></div>
        <div><strong>Current state</strong><span>OPEN, CLOSED, PARTIAL or UNRESOLVED, with the cutoff date and explanation.</span></div>
      </div>
    </section>

    <section className={styles.section}>
      <h2>How to read the result</h2>
      <div className={styles.statusList}>
        <div><strong>OPEN</strong><p>No relevant procurement was found in TED as of the stated date. This is TED-scoped; it does not mean procurement cannot exist in national or below-threshold channels.</p></div>
        <div><strong>CLOSED</strong><p>Accepted procurement evidence was found for the component.</p></div>
        <div><strong>PARTIAL</strong><p>A project contains a mix of component states, so some procurement may remain while other parts have evidence of procurement.</p></div>
        <div><strong>UNRESOLVED</strong><p>The available evidence is too ambiguous or incomplete to classify safely.</p></div>
      </div>
    </section>

    <section className={`${styles.section} ${styles.twoCol}`}>
      <div>
        <h2>Where the data comes from</h2>
        <p>Funded-project scope currently comes from the approved OpenCoesione 2021–2027 EU-cohesion operation-list publication family. Procurement evidence comes from Tenders Electronic Daily (TED).</p>
      </div>
      <div>
        <h2>What ProcRun does not claim</h2>
        <p>ProcRun does not claim complete national procurement coverage, a complete bill of materials, every future purchase, win probability or buyer/contact intelligence. Where the evidence is insufficient, the product shows that explicitly.</p>
        <p style={{marginTop:16}}><Link className="text-link strong" href="/methodology">Read methodology and coverage →</Link></p>
      </div>
    </section>

    <section className={`${styles.section} ${styles.bottom}`}>
      <div>
        <h2>ProcRun Portugal</h2>
        <p className={styles.price}>€149 <span>/ month</span></p>
        <p>One professional package with the procurement runway workspace, evidence detail, supplier profile, saved opportunities, market context and customer-safe CSV export.</p>
      </div>
      <div className={styles.bottomAction}>
        <Link className="button large" href="/pricing">See pricing</Link>
        <Link className="text-link strong" href="/faq">Read the FAQ →</Link>
      </div>
    </section>
  </PublicPage>;
}
