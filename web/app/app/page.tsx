import Link from "next/link";
import { redirect } from "next/navigation";

import { ProjectBrowser } from "@/components/project-browser";
import { SinceLastVisitLine } from "@/components/since-last-visit-line";
import { requireAccount } from "@/lib/auth";
import { loadProductionProjects } from "@/lib/production-projects";
import { rankProjectsForProfile } from "@/lib/relevance";
import { loadSinceLastVisitSummary } from "@/lib/since-last-visit";
import { loadSupplierProfile, syncComponentMatches } from "@/lib/supplier-profile";
import styles from "./project-overview.module.css";

export const dynamic = "force-dynamic";

export default async function RunwayPage() {
  const { accountId } = await requireAccount();
  const [projects, summary, profile] = await Promise.all([
    loadProductionProjects(),
    loadSinceLastVisitSummary(accountId),
    loadSupplierProfile(accountId),
  ]);

  if (!profile) redirect("/app/onboarding");

  const actionableProjects = projects?.filter((project) => project.openCount > 0) ?? null;
  const matchedProjects = actionableProjects
    ? rankProjectsForProfile(actionableProjects, profile)
    : null;
  const matchPersistenceOk = matchedProjects
    ? await syncComponentMatches(
        accountId,
        matchedProjects.flatMap((project) => project.matchingComponentIds),
      )
    : false;

  const totalProjects = matchedProjects?.length ?? 0;
  const totalOpen =
    matchedProjects?.reduce((sum, project) => sum + project.openCount, 0) ?? 0;
  const totalClosed =
    matchedProjects?.reduce((sum, project) => sum + project.closedCount, 0) ?? 0;
  const totalWithheld =
    projects?.reduce((sum, project) => sum + project.unresolvedCount, 0) ?? 0;
  const hasCpvConstraints = profile.cpvInclude.length > 0 || profile.cpvExclude.length > 0;

  return <>
    <p className="small">Opportunities</p>
    <h1 className="h1">Funded projects matched to your Supplier Profile</h1>

    <p className="lede">
      High and Medium relevance projects are prioritised from current OPEN purchasing needs. Relevance never changes the underlying evidence state.
    </p>

    <SinceLastVisitLine summary={summary} />

    {projects === null || actionableProjects === null || matchedProjects === null ? (
      <div className="notice scope">
        <strong>Production database unavailable.</strong> The opportunity feed is not replaced with fixture data when the configured production read source is unavailable.
      </div>
    ) : (
      <>
        {!matchPersistenceOk ? (
          <div className="notice scope">
            <strong>Match history unavailable.</strong> Current relevance can be shown, but ProcRun could not persist this account's match snapshot for since-last-visit history.
          </div>
        ) : null}

        {hasCpvConstraints ? (
          <div className="notice scope">
            <strong>CPV-constrained matches are withheld.</strong> The current customer-safe OPEN summary does not expose CPV, so ProcRun does not infer a CPV fit. Remove the CPV constraint to use category-based High and Medium matching.
          </div>
        ) : null}

        <div className={styles.summaryStrip}>
          <div><span>Matched projects</span><strong>{totalProjects}</strong></div>
          <div><span>OPEN needs in matched projects</span><strong>{totalOpen}</strong></div>
          <div><span>Procurement evidence found</span><strong>{totalClosed}</strong></div>
          <div><span>Withheld pending verification</span><strong>{totalWithheld}</strong></div>
        </div>

        <p className={styles.withheldNote}>
          ProcRun does not present unresolved candidate needs or Low relevance matches as standard-feed opportunities.
        </p>

        <div className="actions">
          <Link className="button secondary" href="/app/market">
            Market Intelligence
          </Link>
          <Link className="button secondary" href="/app/profile">
            Supplier Profile
          </Link>
        </div>

        <ProjectBrowser projects={matchedProjects} />
      </>
    )}
  </>;
}
