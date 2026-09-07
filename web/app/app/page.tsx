import Link from "next/link";
import { OpportunityList } from "@/components/opportunity-list";
import { SinceLastVisitLine } from "@/components/since-last-visit-line";
import { opportunities } from "@/lib/read-model";
import { loadSinceLastVisitSummary } from "@/lib/since-last-visit";

export const dynamic = "force-dynamic";

export default async function RunwayPage() {
  const summary = await loadSinceLastVisitSummary();

  return <>
    <p className="small">Opportunities</p>
    <h1 className="h1">See what the evidence supports — and where it stops.</h1>
    <p className="small">{opportunities.length} opportunities match your profile</p>
    <SinceLastVisitLine summary={summary} />

    <p className="lede">The MVP combines a deterministic supplier profile with TED procurement evidence. OPEN is always a bounded negative-search conclusion, never a statement that procurement does not exist elsewhere.</p>

    <div className="notice scope"><strong>Development workspace.</strong> Fixture records are interface-only; customer-facing production data must come through the frozen customer-safe read model. OPEN means “No relevant procurement found in TED as of the stated date.”</div>

    <div className="actions">
      <Link className="button" href="/app/profile">Configure Supplier Profile</Link>
      <Link className="button secondary" href="/api/export">Export fixture CSV</Link>
    </div>

    <section className="section">
      <p className="small">Opportunity feed</p>
      <h2 className="h2">Evidence-ranked workspace</h2>
      <p className="small">State is determined by the evidence contract. Supplier relevance can change ordering, never OPEN/CLOSED/UNRESOLVED.</p>
      <OpportunityList items={opportunities} />
    </section>
  </>;
}
