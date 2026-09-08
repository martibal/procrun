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
  return `Procurement state could not be resolved from the current evidence as of ${item.cutoffDate}.`;
}

export default async function ProjectPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const project = await loadProductionProject(decodeURIComponent(id));

  if (!project) notFound();

  const openCount = project.components.filter((item) => item.state === "OPEN").length;
  const closedCount = project.components.filter((item) => item.state === "CLOSED").length;
  const unresolvedCount = project.components.filter((item) => item.state === "UNRESOLVED").length;
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
          <p className={styles.sectionLabel}>Potential purchasing needs</p>
          <h2>What this project may still need to buy</h2>
        </div>
        <p>{openCount} OPEN · {unresolvedCount} UNRESOLVED · {closedCount} CLOSED</p>
      </div>

      <div className={styles.needList}>
        {project.components.map((item) => (
          <article className={styles.needRow} key={item.componentId}>
            <div className={styles.needTitleBlock}>
              <h3>{item.description}</h3>
              <span className={`${styles.state} ${item.state === "UNRESOLVED" ? styles.unresolved : ""}`}>{item.state}</span>
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
        ))}
      </div>
    </section>

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
