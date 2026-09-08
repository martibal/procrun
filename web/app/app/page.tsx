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

  const totalProjects = projects?.length ?? 0;
  const totalComponents =
    projects?.reduce((sum, project) => sum + project.componentCount, 0) ?? 0;
  const totalOpen =
    projects?.reduce((sum, project) => sum + project.openCount, 0) ?? 0;
  const totalClosed =
    projects?.reduce((sum, project) => sum + project.closedCount, 0) ?? 0;
  const totalUnresolved =
    projects?.reduce((sum, project) => sum + project.unresolvedCount, 0) ?? 0;

  return <>
    <p className="small">Projects</p>
    <h1 className="h1">Funded projects with identified purchasing needs</h1>

    <p className="lede">
      Browse funded projects by the purchasing needs ProcRun has identified and their current procurement state.
    </p>

    <SinceLastVisitLine summary={summary} />

    {projects === null ? (
      <div className="notice scope">
        <strong>Production database unavailable.</strong> The project overview is not replaced with fixture data when the configured production read source is unavailable.
      </div>
    ) : (
      <>
        <div className={styles.summaryStrip}>
          <div><span>Projects</span><strong>{totalProjects}</strong></div>
          <div><span>Purchasing needs</span><strong>{totalComponents}</strong></div>
          <div><span>OPEN</span><strong>{totalOpen}</strong></div>
          <div><span>UNRESOLVED</span><strong>{totalUnresolved}</strong></div>
          <div><span>CLOSED</span><strong>{totalClosed}</strong></div>
        </div>

        <div className="actions">
          <Link className="button secondary" href="/app/market">
            Market Intelligence
          </Link>
          <Link className="button secondary" href="/app/profile">
            Supplier Profile
          </Link>
        </div>

        <ProjectBrowser projects={projects} />
      </>
    )}
  </>;
}
