import Link from "next/link";
import { notFound } from "next/navigation";

import { loadProductionProject } from "@/lib/production-projects";

export const dynamic = "force-dynamic";

function eur(value: number | null): string {
  if (value === null) return "Unavailable";

  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(value);
}

export default async function ProjectPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const project = await loadProductionProject(decodeURIComponent(id));

  if (!project) notFound();

  const openCount = project.components.filter(
    (item) => item.state === "OPEN",
  ).length;

  const closedCount = project.components.filter(
    (item) => item.state === "CLOSED",
  ).length;

  const unresolvedCount = project.components.filter(
    (item) => item.state === "UNRESOLVED",
  ).length;

  return <>
    <p className="small">Funded project</p>

    <h1 className="h1">
      {project.projectTitle ?? project.operationCode}
    </h1>

    <p className="lede">
      {project.region ?? project.nutsCode ?? "Location unavailable"}
    </p>

    <div className="coverage-list section">
      <div>
        <strong>Operation code</strong>
        <p>{project.operationCode}</p>
      </div>

      <div>
        <strong>Programme</strong>
        <p>{project.programme ?? "Unavailable"}</p>
      </div>

      <div>
        <strong>Approved funding</strong>
        <p>{eur(project.approvedFundingEur)}</p>
      </div>

      <div>
        <strong>Project start</strong>
        <p>{project.projectStart ?? "Unavailable"}</p>
      </div>

      <div>
        <strong>Project end</strong>
        <p>{project.projectEnd ?? "Unavailable"}</p>
      </div>
    </div>

    <section className="section">
      <p className="small">Published project evidence</p>
      <p className="evidence">{project.projectScopeText}</p>
    </section>

    <section className="section">
      <p className="small">Purchasing needs</p>
      <h2 className="h2">{project.components.length} identified components</h2>

      <p className="small">
        {openCount} OPEN · {closedCount} CLOSED · {unresolvedCount} UNRESOLVED
      </p>

      <div className="list">
        {project.components.map((item) => (
          <div className="row" key={item.componentId}>
            <div>
              <strong>{item.description}</strong>
              <p className="micro">{item.category}</p>
            </div>

            <div>
              <span className="pill">{item.state}</span>
              <p className="small">As of {item.cutoffDate}</p>
            </div>

            <div>
              <p className="small">{item.scopeEvidence}</p>

              {item.state === "CLOSED" && item.evidenceExcerpt ? (
                <>
                  <p className="micro">
                    Procurement evidence: {item.evidenceExcerpt}
                  </p>

                  {item.evidenceUrl ? (
                    <p>
                      <a
                        className="text-link strong"
                        href={item.evidenceUrl}
                      >
                        Open procurement source
                      </a>
                    </p>
                  ) : null}
                </>
              ) : null}

              {item.state === "OPEN" ? (
                <p className="micro">
                  No relevant procurement found in TED as of {item.cutoffDate}.
                </p>
              ) : null}
            </div>
          </div>
        ))}
      </div>
    </section>

    <div className="notice scope">
      <strong>Coverage boundary.</strong> OPEN means no relevant procurement was found in the indexed TED query universe through the stated cutoff. It does not establish absence outside TED, including national or below-threshold procedures.
    </div>

    <div className="actions">
      <Link className="button secondary" href="/app">
        Back to projects
      </Link>
    </div>
  </>;
}
