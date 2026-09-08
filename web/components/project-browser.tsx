"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { saveNeedAction } from "@/app/app/saved/actions";
import type { PersonalizedProject } from "@/lib/relevance";
import styles from "./project-browser.module.css";

function eur(value: number | null): string {
  if (value === null) return "Unavailable";
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(value);
}

function cutoff(project: PersonalizedProject): string {
  return project.earliestCutoffDate === project.latestCutoffDate
    ? project.latestCutoffDate
    : `${project.earliestCutoffDate}–${project.latestCutoffDate}`;
}

function matchingOpenNeeds(project: PersonalizedProject) {
  return project.needs
    .filter((item) => item.state === "OPEN")
    .map((item) => ({
      ...item,
      componentIds: item.componentIds.filter((id) => project.matchingComponentIds.includes(id)),
    }))
    .filter((item) => item.componentIds.length > 0);
}

export function ProjectBrowser({ projects }: { projects: PersonalizedProject[] }) {
  const [query, setQuery] = useState("");
  const [relevance, setRelevance] = useState<"ALL" | "HIGH" | "MEDIUM">("ALL");
  const [need, setNeed] = useState("ALL");
  const [minimumFunding, setMinimumFunding] = useState(0);

  const needOptions = useMemo(
    () => Array.from(new Set(projects.flatMap((project) => matchingOpenNeeds(project).map((item) => item.description)))).sort(),
    [projects],
  );

  const filtered = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase();
    return projects.filter((project) => {
      const openNeeds = matchingOpenNeeds(project);
      if (relevance !== "ALL" && project.relevanceBand !== relevance) return false;
      if (need !== "ALL" && !openNeeds.some((item) => item.description === need)) return false;
      if ((project.approvedFundingEur ?? 0) < minimumFunding) return false;
      if (!normalizedQuery) return true;
      return [project.projectTitle, project.operationCode, project.programme, project.region, project.nutsCode, ...openNeeds.map((item) => item.description)]
        .filter(Boolean).join(" ").toLocaleLowerCase().includes(normalizedQuery);
    });
  }, [minimumFunding, need, projects, query, relevance]);

  const exportHref = useMemo(() => {
    const params = new URLSearchParams({ scope: "filtered" });
    if (query.trim()) params.set("q", query.trim());
    if (relevance !== "ALL") params.set("relevance", relevance);
    if (need !== "ALL") params.set("need", need);
    if (minimumFunding > 0) params.set("minimumFunding", String(minimumFunding));
    return `/app/export?${params.toString()}`;
  }, [minimumFunding, need, query, relevance]);

  const clearFilters = () => {
    setQuery("");
    setRelevance("ALL");
    setNeed("ALL");
    setMinimumFunding(0);
  };

  return (
    <section className={styles.browser}>
      <div className={styles.headingRow}>
        <div>
          <p className={styles.sectionLabel}>Opportunity feed</p>
          <h2>{filtered.length === projects.length ? `${projects.length} matched projects` : `${filtered.length} of ${projects.length} projects`}</h2>
        </div>
        <p className={styles.scopeNote}>Standard feed shows only High and Medium relevance. Evidence state remains independent of relevance.</p>
      </div>

      <div className={styles.filters} aria-label="Opportunity filters">
        <label className={styles.searchField}><span>Search</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Project, code, programme or need" /></label>
        <label><span>Relevance</span><select value={relevance} onChange={(event) => setRelevance(event.target.value as "ALL" | "HIGH" | "MEDIUM")}><option value="ALL">High + Medium</option><option value="HIGH">High</option><option value="MEDIUM">Medium</option></select></label>
        <label><span>Purchasing need</span><select value={need} onChange={(event) => setNeed(event.target.value)}><option value="ALL">All OPEN needs</option>{needOptions.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
        <label><span>Minimum funding</span><select value={minimumFunding} onChange={(event) => setMinimumFunding(Number(event.target.value))}><option value={0}>Any amount</option><option value={25000}>€25k+</option><option value={100000}>€100k+</option><option value={500000}>€500k+</option><option value={1000000}>€1m+</option></select></label>
        <button type="button" className={styles.clearButton} onClick={clearFilters}>Clear filters</button>
      </div>

      <div className={styles.resultHeader}><span>{filtered.length} matching projects</span><span><Link className="text-link strong" href={exportHref}>Export filtered CSV</Link></span></div>

      {filtered.length === 0 ? (
        <div className={styles.emptyState}>No High or Medium relevance projects match the current filters. Review your Supplier Profile or broaden the feed filters.</div>
      ) : (
        <div className={styles.projectList}>
          {filtered.map((project) => {
            const openNeeds = matchingOpenNeeds(project);
            return (
              <article className={styles.projectRow} key={project.operationCode}>
                <div className={styles.projectIdentity}>
                  <span className={project.relevanceBand === "HIGH" ? styles.relevanceHigh : styles.relevanceMedium}>{project.relevanceBand === "HIGH" ? "High relevance" : "Medium relevance"}</span>
                  <div><Link href={`/app/projects/${encodeURIComponent(project.operationCode)}`} className={styles.projectTitle}>{project.projectTitle ?? project.operationCode}</Link></div>
                  <div className={styles.operationCode}>{project.operationCode}</div>
                </div>

                <div className={styles.needColumn}>
                  <div className={styles.needHeading}>OPEN purchasing needs</div>
                  <div className={styles.needGroup}>
                    {openNeeds.map((item) => (
                      <span className={styles.needOpen} key={`${item.description}-${item.componentIds.join("-")}`}>
                        {item.description}<small>OPEN</small>
                        <form action={saveNeedAction}>
                          {item.componentIds.map((componentId) => <input key={componentId} type="hidden" name="componentId" value={componentId} />)}
                          <button className={styles.saveButton} type="submit">Save</button>
                        </form>
                      </span>
                    ))}
                  </div>
                  {project.closedCount > 0 ? <p className={styles.closedNote}>{project.closedCount} need{project.closedCount === 1 ? "" : "s"} with procurement evidence found</p> : null}
                </div>

                <dl className={styles.projectMeta}>
                  <div><dt>Programme</dt><dd>{project.programme ?? "Unavailable"}</dd></div>
                  <div><dt>Location</dt><dd>{project.region ?? project.nutsCode ?? "Unavailable"}</dd></div>
                  <div><dt>Approved funding</dt><dd className={styles.numeric}>{eur(project.approvedFundingEur)}</dd></div>
                  <div><dt>Cutoff</dt><dd className={styles.numeric}>{cutoff(project)}</dd></div>
                </dl>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
