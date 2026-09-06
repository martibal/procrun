import Link from "next/link";
import { PublicPage } from "@/components/public-site";
import { opportunities } from "@/lib/read-model";
import styles from "./landing.module.css";

export default function HomePage() {
  return <PublicPage>
    <section className={styles.hero}>
      <p className={styles.kicker}>Procurement intelligence for infrastructure suppliers</p>
      <h1>See which funded projects still have no matching TED procurement for specific equipment and services.</h1>
      <p className={styles.intro}>ProcRun takes published funded-project scope, identifies the equipment and services described there, and checks those components against procurement notices in TED. The result is a project list with the component, the procurement state, the cutoff date and the evidence behind the decision.</p>
      <p className={styles.reason}>It is a faster way to decide which funded projects deserve attention before you spend time reading project documents and procurement notices manually.</p>
      <div className={styles.heroActions}>
        <Link className="button large" href="/app">Open the demo workspace</Link>
        <Link className={styles.plainLink} href="/methodology">Methodology and coverage</Link>
      </div>
    </section>

    <section className={styles.outputSection}>
      <div className={styles.outputHeading}>
        <div>
          <p className={styles.sectionLabel}>What the customer sees</p>
          <h2>A project list, not another document library.</h2>
        </div>
        <p>Each row ties a funded project to a specific purchasable component and shows whether relevant procurement evidence has been found in TED.</p>
      </div>

      <div className={styles.resultTable} role="table" aria-label="ProcRun demo results">
        <div className={styles.tableHead} role="row">
          <span>Project</span><span>Component</span><span>State</span><span>Cutoff</span>
        </div>
        {opportunities.map((item) => <div className={styles.tableRow} role="row" key={item.id}>
          <span><strong>{item.projectTitle}</strong><small>{item.geography}</small></span>
          <span>{item.component}</span>
          <span className={styles.state}>{item.state}{item.state === "OPEN" ? " · TED" : ""}</span>
          <span>{item.cutoffDate}</span>
        </div>)}
      </div>
      <p className={styles.fixtureNote}>Demo data shown above. Production views use the customer-safe ProcRun read model; raw source payloads are not exposed to the browser.</p>
    </section>

    <section className={styles.explanationSection}>
      <div className={styles.explanationIntro}>
        <p className={styles.sectionLabel}>How ProcRun gets there</p>
        <h2>Three checks between a funded project and the final state.</h2>
      </div>
      <ol className={styles.steps}>
        <li><span>1</span><div><strong>Read the funded-project scope.</strong><p>ProcRun uses the published project description and keeps the exact text that supports each extracted component.</p></div></li>
        <li><span>2</span><div><strong>Check that component against TED.</strong><p>Relevant procurement notices are matched conservatively. A weak or ambiguous match is not treated as proof.</p></div></li>
        <li><span>3</span><div><strong>Return the state with its evidence.</strong><p>OPEN means no relevant procurement was found in TED as of the cutoff. CLOSED means accepted procurement evidence exists. If the evidence is not good enough, the result is UNRESOLVED.</p></div></li>
      </ol>
    </section>

    <section className={styles.scopeSection}>
      <div>
        <p className={styles.sectionLabel}>Coverage</p>
        <h2>Current source scope</h2>
      </div>
      <div className={styles.scopeCopy}>
        <p>Funded-project scope currently comes from the approved OpenCoesione 2021–2027 EU-cohesion operation-list publication family. Procurement evidence comes from Tenders Electronic Daily (TED).</p>
        <p><strong>OPEN is TED-scoped.</strong> It does not mean procurement cannot exist in national or below-threshold channels. ProcRun does not claim complete national procurement coverage, a complete bill of materials, every future purchase, win probability or buyer/contact intelligence.</p>
        <Link className={styles.plainLink} href="/methodology">Read the full methodology and source limits</Link>
      </div>
    </section>

    <section className={styles.priceSection}>
      <div>
        <p className={styles.sectionLabel}>ProcRun Portugal</p>
        <h2>€149 <span>/ month</span></h2>
        <p>Procurement runway workspace, evidence detail, supplier profile, saved opportunities, market context and customer-safe CSV export.</p>
      </div>
      <Link className="button large" href="/pricing">Pricing details</Link>
    </section>
  </PublicPage>;
}
