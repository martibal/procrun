import Link from "next/link";

import { ProjectBrowser } from "@/components/project-browser";
import { SinceLastVisitLine } from "@/components/since-last-visit-line";
import { loadProductionProjects } from "@/lib/production-projects";
import { loadSinceLastVisitSummary } from "@/lib/since-last-visit";
import styles from "./project-overview.module.css";

export const dynamic = "force-dynamic";

export default async function RunwayPage() {
  const [projects, summary] = await Promise.all([
    loadProductionProjects(),
    loadSinceLastVisitSummary(),
  ]);

  const actionableProjects = projects?.filter((project) => project.openCount > 0) ?? null;
  const totalProjects = actionableProjects?.length ?? 0;
  const totalOpen =
    actionableProjects?.reduce((sum, project) => sum + project.openCount, 0) ?? 0;
  const totalClosed =
    actionableProjects?.reduce((sum, project) => sum + project.closedCount, 0) ?? 0;
  const totalWithheld =
    projects?.reduce((sum, project) => sum + project.unresolvedCount, 0) ?? 0;

  return <>
    <p className="small">Projects</p>
    <h1 className="h1">Funded projects with identified purchasing needs</h1>

    <p className="lede">
      Browse funded projects where ProcRun has resolved at least one current purchasing need as OPEN.
    </p>

    <SinceLastVisitLine summary={summary} />

    {projects === null || actionableProjects === null ? (
      <div className="notice scope">
        <strong>Production database unavailable.</strong> The project overview is not replaced with fixture data when the configured production read source is unavailable.
      </div>
    ) : (
      <>
        <div className={styles.summaryStrip}>
          <div><span>Projects with OPEN needs</span><strong>{totalProjects}</strong></div>
          <div><span>OPEN purchasing needs</span><strong>{totalOpen}</strong></div>
          <div><span>Procurement evidence found</span><strong>{totalClosed}</strong></div>
          <div><span>Withheld pending verification</span><strong>{totalWithheld}</strong></div>
        </div>

        <p className={styles.withheldNote}>
          ProcRun does not present unresolved candidate needs as customer opportunities. They stay withheld until the evidence supports an OPEN or CLOSED conclusion.
        </p>

        <div className="actions">
          <Link className="button secondary" href="/app/market">
            Market Intelligence
          </Link>
          <Link className="button secondary" href="/app/profile">
            Supplier Profile
          </Link>
        </div>

        <ProjectBrowser projects={actionableProjects} />
      </>
    )}
  </>;
}
