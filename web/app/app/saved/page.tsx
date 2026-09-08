import Link from "next/link";

import { requireAccount } from "@/lib/auth";
import { loadSavedOpportunities } from "@/lib/saved-opportunities";
import { removeSavedOpportunityAction } from "./actions";

export const dynamic = "force-dynamic";

function eur(value: number | null): string {
  if (value === null) return "Unavailable";
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(value);
}

export default async function SavedPage({ searchParams }: { searchParams: Promise<{ changed?: string }> }) {
  const { accountId } = await requireAccount();
  const { changed } = await searchParams;
  const saved = await loadSavedOpportunities(accountId);

  return <>
    <p className="small">Saved opportunities</p>
    <h1 className="h1">Keep evidence-bearing opportunities in one review queue.</h1>
    <p className="lede">Saved state is account-scoped workspace state only. It never changes evidence classification or supplier relevance.</p>

    {changed ? <p className="small"><strong>Status changed since your previous summary:</strong> {changed}</p> : null}

    {saved === null ? (
      <div className="notice scope"><strong>Saved Opportunities unavailable.</strong> ProcRun could not load this account's saved queue from the production database.</div>
    ) : saved.length === 0 ? (
      <div className="notice">No saved opportunities yet. Save an OPEN need from a matched project to build this review queue.</div>
    ) : (
      <>
        <div className="actions">
          <Link className="button secondary" href="/app/export?scope=saved">Export saved CSV</Link>
        </div>
        <div className="coverage-list">
          {saved.map((item) => (
            <div key={item.componentId}>
              <strong>{item.description}</strong>
              <p>{item.projectTitle ?? item.operationCode}</p>
              <p className="small">{item.state} · cutoff {item.cutoffDate} · {item.region ?? item.nutsCode ?? "Location unavailable"} · {eur(item.approvedFundingEur)}</p>
              <div className="actions">
                <Link className="button secondary" href={`/app/projects/${encodeURIComponent(item.operationCode)}`}>Open project</Link>
                <form action={removeSavedOpportunityAction}>
                  <input type="hidden" name="componentId" value={item.componentId} />
                  <button className="button secondary" type="submit">Remove</button>
                </form>
              </div>
            </div>
          ))}
        </div>
      </>
    )}
  </>;
}
