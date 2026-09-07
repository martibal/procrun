import Link from "next/link";

import { SinceLastVisitLine } from "@/components/since-last-visit-line";
import { loadProductionProjects } from "@/lib/production-projects";
import { loadSinceLastVisitSummary } from "@/lib/since-last-visit";

export const dynamic = "force-dynamic";

function eur(value: number | null): string {
  if (value === null) return "Unavailable";

  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(value);
}

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
      Complete current ProcRun project set with customer-safe component and procurement states.
    </p>

    <SinceLastVisitLine summary={summary} />

    {projects === null ? (
      <div className="notice scope">
        <strong>Production database unavailable.</strong> The project overview is not replaced with fixture data when the configured production read source is unavailable.
      </div>
    ) : (
      <>
        <div className="grid">
          <div className="card">
            <div className="small">Projects</div>
            <div className="kpi">{totalProjects}</div>
          </div>

          <div className="card">
            <div className="small">Purchasing needs</div>
            <div className="kpi">{totalComponents}</div>
          </div>

          <div className="card">
            <div className="small">OPEN</div>
            <div className="kpi">{totalOpen}</div>
          </div>

          <div className="card">
            <div className="small">CLOSED</div>
            <div className="kpi">{totalClosed}</div>
          </div>

          <div className="card">
            <div className="small">UNRESOLVED</div>
            <div className="kpi">{totalUnresolved}</div>
          </div>
        </div>

        <div className="actions">
          <Link className="button secondary" href="/app/market">
            Market Intelligence
          </Link>
          <Link className="button secondary" href="/app/profile">
            Supplier Profile
          </Link>
        </div>

        <section className="section">
          <p className="small">Project overview</p>
          <h2 className="h2">{totalProjects} funded projects</h2>

          <p className="small">
            Projects appear here when ProcRun has at least one current customer-safe component observation.
            OPEN remains a TED-scoped negative-search conclusion, not proof that procurement is absent elsewhere.
          </p>

          {projects.length === 0 ? (
            <p>No current project records are available.</p>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table>
                <thead>
                  <tr>
                    <th>Project</th>
                    <th>Programme</th>
                    <th>Location</th>
                    <th>Approved funding</th>
                    <th>Needs</th>
                    <th>OPEN</th>
                    <th>CLOSED</th>
                    <th>UNRESOLVED</th>
                    <th>Cutoff</th>
                  </tr>
                </thead>

                <tbody>
                  {projects.map((project) => (
                    <tr key={project.operationCode}>
                      <td>
                        <Link
                          className="text-link strong"
                          href={`/app/projects/${encodeURIComponent(project.operationCode)}`}
                        >
                          {project.projectTitle ?? project.operationCode}
                        </Link>
                        <div className="micro">{project.operationCode}</div>
                      </td>

                      <td>{project.programme ?? "Unavailable"}</td>

                      <td>
                        {project.municipality
                          ? `${project.municipality}${project.region ? `, ${project.region}` : ""}`
                          : project.region ?? project.nutsCode ?? "Unavailable"}
                      </td>

                      <td>{eur(project.approvedFundingEur)}</td>

                      <td>{project.componentCount}</td>

                      <td>{project.openCount}</td>

                      <td>{project.closedCount}</td>

                      <td>{project.unresolvedCount}</td>

                      <td>
                        {project.earliestCutoffDate === project.latestCutoffDate
                          ? project.latestCutoffDate
                          : `${project.earliestCutoffDate}–${project.latestCutoffDate}`}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </>
    )}
  </>;
}