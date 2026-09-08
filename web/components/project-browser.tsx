"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import type { ProductionProjectSummary, ProjectNeedState } from "@/lib/production-projects";
import styles from "./project-browser.module.css";

type StateFilter = "ALL" | ProjectNeedState;

function eur(value: number | null): string {
  if (value === null) return "Unavailable";
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(value);
}

function cutoff(project: ProductionProjectSummary): string {
  return project.earliestCutoffDate === project.latestCutoffDate
    ? project.latestCutoffDate
    : `${project.earliestCutoffDate}–${project.latestCutoffDate}`;
}

function uniqueDescriptions(project: ProductionProjectSummary, state: ProjectNeedState): string[] {
  return Array.from(
    new Set(project.needs.filter((item) => item.state === state).map((item) => item.description)),
  ).sort();
}

export function ProjectBrowser({ projects }: { projects: ProductionProjectSummary[] }) {
  const [query, setQuery] = useState("");
  const [need, setNeed] = useState("ALL");
  const [state, setState] = useState<StateFilter>("ALL");
  const [minimumFunding, setMinimumFunding] = useState(0);

  const needOptions = useMemo(
    () => Array.from(new Set(projects.flatMap((project) => project.needs.map((item) => item.description)))).sort(),
    [projects],
  );

  const filtered = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase();

    return projects.filter((project) => {
      if (need !== "ALL" && !project.needs.some((item) => item.description === need)) return false;
      if (state !== "ALL" && !project.needs.some((item) => item.state === state)) return false;
      if ((project.approvedFundingEur ?? 0) < minimumFunding) return false;

      if (!normalizedQuery) return true;
      const haystack = [
        project.projectTitle,
        project.operationCode,
        project.programme,
        project.region,
        project.nutsCode,
        ...project.needs.map((item) => item.description),
      ]
        .filter(Boolean)
        .join(" ")
        .toLocaleLowerCase();
      return haystack.includes(normalizedQuery);
    });
  }, [minimumFunding, need, projects, query, state]);

  const clearFilters = () => {
    setQuery("");
    setNeed("ALL");
    setState("ALL");
    setMinimumFunding(0);
  };

  return (
    <section className={styles.browser}>
      <div className={styles.headingRow}>
        <div>
          <p className={styles.sectionLabel}>Project overview</p>
          <h2>{filtered.length === projects.length ? `${projects.length} funded projects` : `${filtered.length} of ${projects.length} projects`}</h2>
        </div>
        <p className={styles.scopeNote}>
          OPEN is a TED-scoped negative-search conclusion, not proof that procurement is absent elsewhere.
        </p>
      </div>

      <div className={styles.filters} aria-label="Project filters">
        <label className={styles.searchField}>
          <span>Search</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Project, code, programme or need"
          />
        </label>

        <label>
          <span>Purchasing need</span>
          <select value={need} onChange={(event) => setNeed(event.target.value)}>
            <option value="ALL">All needs</option>
            {needOptions.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
        </label>

        <label>
          <span>Procurement state</span>
          <select value={state} onChange={(event) => setState(event.target.value as StateFilter)}>
            <option value="ALL">All states</option>
            <option value="OPEN">Has OPEN need</option>
            <option value="UNRESOLVED">Has UNRESOLVED need</option>
            <option value="CLOSED">Has CLOSED need</option>
          </select>
        </label>

        <label>
          <span>Minimum funding</span>
          <select value={minimumFunding} onChange={(event) => setMinimumFunding(Number(event.target.value))}>
            <option value={0}>Any amount</option>
            <option value={25000}>€25k+</option>
            <option value={100000}>€100k+</option>
            <option value={500000}>€500k+</option>
            <option value={1000000}>€1m+</option>
          </select>
        </label>

        <button type="button" className={styles.clearButton} onClick={clearFilters}>
          Clear filters
        </button>
      </div>

      <div className={styles.resultHeader}>
        <span>{filtered.length} matching projects</span>
        <span>Sorted by OPEN needs, then total identified needs</span>
      </div>

      {filtered.length === 0 ? (
        <div className={styles.emptyState}>
          No projects match the current filters. Try a broader purchasing need, state or funding range.
        </div>
      ) : (
        <div className={styles.projectList}>
          {filtered.map((project) => {
            const openNeeds = uniqueDescriptions(project, "OPEN");
            const unresolvedNeeds = uniqueDescriptions(project, "UNRESOLVED");
            const closedNeeds = uniqueDescriptions(project, "CLOSED");

            return (
              <article className={styles.projectRow} key={project.operationCode}>
                <div className={styles.projectIdentity}>
                  <Link href={`/app/projects/${encodeURIComponent(project.operationCode)}`} className={styles.projectTitle}>
                    {project.projectTitle ?? project.operationCode}
                  </Link>
                  <div className={styles.operationCode}>{project.operationCode}</div>
                </div>

                <div className={styles.needColumn}>
                  <div className={styles.needHeading}>Potential purchasing needs</div>
                  {openNeeds.length > 0 ? (
                    <div className={styles.needGroup}>
                      {openNeeds.map((item) => (
                        <span className={styles.needOpen} key={`open-${item}`}>{item}<small>OPEN</small></span>
                      ))}
                    </div>
                  ) : null}
                  {unresolvedNeeds.length > 0 ? (
                    <div className={styles.needGroup}>
                      {unresolvedNeeds.map((item) => (
                        <span className={styles.needUnresolved} key={`unresolved-${item}`}>{item}<small>UNRESOLVED</small></span>
                      ))}
                    </div>
                  ) : null}
                  {openNeeds.length === 0 && unresolvedNeeds.length === 0 ? (
                    <p className={styles.noOutstanding}>No current OPEN or UNRESOLVED needs.</p>
                  ) : null}
                  {closedNeeds.length > 0 ? (
                    <p className={styles.closedNote}>{closedNeeds.length} need{closedNeeds.length === 1 ? "" : "s"} with procurement evidence found</p>
                  ) : null}
                </div>

                <dl className={styles.projectMeta}>
                  <div>
                    <dt>Programme</dt>
                    <dd>{project.programme ?? "Unavailable"}</dd>
                  </div>
                  <div>
                    <dt>Location</dt>
                    <dd>{project.region ?? project.nutsCode ?? "Unavailable"}</dd>
                  </div>
                  <div>
                    <dt>Approved funding</dt>
                    <dd className={styles.numeric}>{eur(project.approvedFundingEur)}</dd>
                  </div>
                  <div>
                    <dt>Cutoff</dt>
                    <dd className={styles.numeric}>{cutoff(project)}</dd>
                  </div>
                </dl>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
