import Link from "next/link";
import { notFound } from "next/navigation";

import type { ProductionProjectComponent } from "@/lib/production-projects";
import { loadProductionProject } from "@/lib/production-projects";
import styles from "./project-detail.module.css";

export const dynamic = "force-dynamic";

function eur(value: number | null): string {
  if (value === null) return "Not reported";
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(value);
}

function percent(value: number | null): string {
  if (value === null) return "Not reported";
  return new Intl.NumberFormat("en-GB", { maximumFractionDigits: 1 }).format(value) + "%";
}

function statusCopy(item: ProductionProjectComponent): string {
  if (item.state === "OPEN") {
    return `No relevant procurement found in TED as of ${item.cutoffDate}.`;
  }
  if (item.state === "CLOSED") {
    return `Relevant procurement evidence was found in TED as of ${item.cutoffDate}.`;
  }
  return "Evidence remains insufficient for a safe OPEN/CLOSED conclusion.";
}

function NeedRow({ item }: { item: ProductionProjectComponent }) {
  return (
    <article className={styles.needRow}>
      <div className={styles.needTitleBlock}>
        <h3>{item.description}</h3>
        <span className={styles.state}>{item.state}</span>
      </div>

      <div className={styles.needBody}>
        <div>
          <p className={styles.detailLabel}>Why ProcRun identified this need</p>
          <p className={styles.evidenceQuote}>{item.scopeEvidence}</p>
        </div>

        <div>
          <p className={styles.detailLabel}>Procurement result</p>
          <p className={styles.resultCopy}>{statusCopy(item)}</p>
          {item.state === "CLOSED" && item.evidenceExcerpt ? (
            <p className={styles.procurementEvidence}>{item.evidenceExcerpt}</p>
          ) : null}
          {item.state === "CLOSED" && item.evidenceUrl ? (
            <p><a className="text-link strong" href={item.evidenceUrl}>Open procurement source</a></p>
          ) : null}
        </div>
      </div>

      <details className={styles.methodDetails}>
        <summary>Method details</summary>
        <p>Customer-facing classification: {item.category}</p>
        <p>Assessment cutoff: {item.cutoffDate}</p>
      </details>
    </article>
  );
}

export default async function ProjectPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const project = await loadProductionProject(decodeURIComponent(id));

  if (!project) notFound();

  const openComponents = project.components.filter((item) => item.state === "OPEN");
  const closedComponents = project.components.filter((item) => item.state === "CLOSED");
  const unresolvedComponents = project.components.filter((item) => item.state === "UNRESOLVED");
  const withheldCount = unresolvedComponents.length;
  const remainingReported = project.approvedFundingEur !== null && project.executedFundingEur !== null
    ? project.approvedFundingEur - project.executedFundingEur
    : null;
  const executionPct = project.approvedFundingEur !== null
    && project.approvedFundingEur > 0
    && project.executedFundingEur !== null
    ? (project.executedFundingEur / project.approvedFundingEur) * 100
    : null;
  const coverageNote = project.components[0]?.coverageNote ?? null;

  return <>
    <div className={styles.hero}>
      <p className="small">Funded project</p>
      <h1 className="h1">{project.projectTitle ?? project.operationCode}</h1>
      <p className="lede">{project.region ?? project.nutsCode ?? "Location unavailable"}</p>
    </div>

    <section className={styles.overview}>
      <div className={styles.sectionHeading}>
        <p className={styles.sectionLabel}>Project overview</p>
        <h2>Funding, timing and programme context</h2>
      </div>

      <dl className={styles.facts}>
        <div><dt>Approved funding</dt><dd>{eur(project.approvedFundingEur)}</dd></div>
        <div><dt>Reported executed funding</dt><dd>{eur(project.executedFundingEur)}</dd></div>
        <div><dt>Approved less reported executed</dt><dd>{eur(remainingReported)}</dd></div>
        <div><dt>Reported execution</dt><dd>{percent(executionPct)}</dd></div>
        <div><dt>Project start</dt><dd>{project.projectStart ?? "Not reported"}</dd></div>
        <div><dt>Project end</dt><dd>{project.projectEnd ?? "Not reported"}</dd></div>
        <div><dt>Programme</dt><dd>{project.programme ?? "Not reported"}</dd></div>
        <div><dt>Fund</dt><dd>{project.fund ?? "Not reported"}</dd></div>
        <div><dt>Theme</dt><dd>{project.theme ?? "Not reported"}</dd></div>
        <div><dt>Objective</dt><dd>{project.objective ?? "Not reported"}</dd></div>
      </dl>

      <p className={styles.fundingNote}>
        Funding figures are reported project fields. Approved less reported executed is a deterministic arithmetic difference, not an estimate of the procurement budget still available.
      </p>
    </section>

    <section className={styles.scopeSection}>
      <p className={styles.sectionLabel}>Published project scope</p>
      <p className={styles.scopeEvidence}>{project.projectScopeText || "No project scope text is available in the admitted customer-safe fields."}</p>
      <div className={styles.identifiers}>
        <span>Operation code <strong>{project.operationCode}</strong></span>
        {project.nutsCode ? <span>NUTS <strong>{project.nutsCode}</strong></span> : null}
      </div>
    </section>

    <section className={styles.needsSection}>
      <div className={styles.needsHeading}>
        <div>
          <p className={styles.sectionLabel}>Current purchasing opportunities</p>
          <h2>What this project may still need to buy</h2>
        </div>
        <p>{openComponents.length} OPEN purchasing need{openComponents.length === 1 ? "" : "s"}</p>
      </div>

      {openComponents.length > 0 ? (
        <div className={styles.needList}>
          {openComponents.map((item) => <NeedRow item={item} key={item.componentId} />)}
        </div>
      ) : (
        <p className={styles.resultCopy}>ProcRun is not presenting any current purchasing need for this project.</p>
      )}
    </section>

    {closedComponents.length > 0 ? (
      <section className={styles.needsSection}>
        <div className={styles.needsHeading}>
          <div>
            <p className={styles.sectionLabel}>Procurement already found</p>
            <h2>Needs with matching TED evidence</h2>
          </div>
          <p>{closedComponents.length} CLOSED</p>
        </div>
        <div className={styles.needList}>
          {closedComponents.map((item) => <NeedRow item={item} key={item.componentId} />)}
        </div>
      </section>
    ) : null}

    {withheldCount > 0 ? (
      <section className={styles.coverageSection}>
        <p className={styles.sectionLabel}>Withheld candidate needs</p>
        <h2>Why these rows remain UNRESOLVED</h2>
        <p>
          ProcRun is withholding {withheldCount} candidate purchasing need{withheldCount === 1 ? "" : "s"} from the standard opportunity feed because the procurement evidence is not sufficient to classify them safely as OPEN or CLOSED.
        </p>
        <p className={styles.coverageClarification}>
          The project-source text below is shown verbatim from the admitted evidence used to identify each candidate need. It is not a generated explanation or a reason code.
        </p>
        <table className="table">
          <thead>
            <tr>
              <th>Candidate need</th>
              <th>State</th>
              <th>Why unresolved</th>
              <th>Project source text</th>
              <th>Assessment cutoff</th>
            </tr>
          </thead>
          <tbody>
            {unresolvedComponents.map((item) => (
              <tr key={item.componentId}>
                <td>{item.description}</td>
                <td><span className="pill unresolved">UNRESOLVED</span></td>
                <td>Evidence is insufficient for a safe OPEN/CLOSED conclusion.</td>
                <td><span className="evidence">{item.scopeEvidence}</span></td>
                <td>{item.cutoffDate}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className={styles.coverageClarification}>
          These rows are visible for transparency only. They are not presented as active opportunities and do not require customer investigation.
        </p>
      </section>
    ) : null}

    <section className={styles.coverageSection}>
      <p className={styles.sectionLabel}>Evidence and coverage</p>
      <p>{coverageNote ?? "Coverage information unavailable."}</p>
      <p className={styles.coverageClarification}>
        OPEN means no relevant procurement was found in the complete TED query universe through the stated cutoff. It does not establish absence outside TED, including national or below-threshold procedures.
      </p>
    </section>

    <div className="actions">
      <Link className="button secondary" href="/app">Back to projects</Link>
    </div>
  </>;
}
