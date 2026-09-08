"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import type { ProductionProjectSummary } from "@/lib/production-projects";
import styles from "./project-browser.module.css";

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

function uniqueOpenDescriptions(project: ProductionProjectSummary): string[] {
  return Array.from(
    new Set(project.needs.filter((item) => item.state === "OPEN").map((item) => item.description)),
  ).sort();
}

export function ProjectBrowser({ projects }: { projects: ProductionProjectSummary[] }) {
  const [query, setQuery] = useState("");
  const [need, setNeed] = useState("ALL");
  const [minimumFunding, setMinimumFunding] = useState(0);

  const needOptions = useMemo(
    () => Array.from(new Set(projects.flatMap((project) => uniqueOpenDescriptions(project)))).sort(),
    [projects],
  );

  const filtered = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase();

    return projects.filter((project) => {
      const openNeeds = project.needs.filter((item) => item.state === "OPEN");
      if (need !== "ALL" && !openNeeds.some((item) => item.description === need)) return false;
      if ((project.approvedFundingEur ?? 0) < minimumFunding) return false;

      if (!normalizedQuery) return true;
      const haystack = [
        project.projectTitle,
        project.operationCode,
        project.programme,
        project.region,
        project.nutsCode,
        ...openNeeds.map((item) => item.description),
      ]
        .filter(Boolean)
        .join(" ")
        .toLocaleLowerCase();
      return haystack.includes(normalizedQuery);
    });
  }, [minimumFunding, need, projects, query]);

  const clearFilters = () => {
    setQuery("");
    setNeed("ALL");
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
          Only purchasing needs ProcRun has resolved as OPEN are presented as current opportunities.
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
            <option value="ALL">All OPEN needs</option>
            {needOptions.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
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
          No projects match the current filters. Try a broader purchasing need or funding range.
        </div>
      ) : (
        <div className={styles.projectList}>
          {filtered.map((project) => {
            const openNeeds = uniqueOpenDescriptions(project);
            const closedCount = project.closedCount;

            return (
              <article className={styles.projectRow} key={project.operationCode}>
                <div className={styles.projectIdentity}>
                  <Link href={`/app/projects/${encodeURIComponent(project.operationCode)}`} className={styles.projectTitle}>
                    {project.projectTitle ?? project.operationCode}
                  </Link>
                  <div className={styles.operationCode}>{project.operationCode}</div>
                </div>

                <div className={styles.needColumn}>
                  <div className={styles.needHeading}>OPEN purchasing needs</div>
                  <div className={styles.needGroup}>
                    {openNeeds.map((item) => (
                      <span className={styles.needOpen} key={`open-${item}`}>{item}<small>OPEN</small></span>
                    ))}
                  </div>
                  {closedCount > 0 ? (
                    <p className={styles.closedNote}>{closedCount} need{closedCount === 1 ? "" : "s"} with procurement evidence found</p>
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
