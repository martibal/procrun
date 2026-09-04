import Link from "next/link";
import { OpportunityList } from "@/components/opportunity-list";
import { opportunities } from "@/lib/read-model";

export default function RunwayPage() {
  const open = opportunities.filter((item) => item.state === "OPEN").length;
  const closed = opportunities.filter((item) => item.state === "CLOSED").length;
  const unresolved = opportunities.filter((item) => item.state === "UNRESOLVED").length;

  return <>
    <div className="eyebrow">Supplier runway</div>
    <h1 className="h1">See what the evidence supports — and where it stops.</h1>
    <p className="lede">The MVP combines a deterministic supplier profile with TED procurement evidence. OPEN is always a bounded negative-search conclusion, never a statement that procurement does not exist elsewhere.</p>

    <div className="notice scope"><strong>Fixture workspace.</strong> These opportunities come only from the frozen customer-safe fixture adapter. No source payload is rendered here. OPEN means “No relevant procurement found in TED as of the stated date.”</div>

    <div className="grid">
      <div className="card"><div className="small">TED-scoped OPEN</div><div className="kpi">{open}</div><div className="micro">No relevant TED match at cutoff</div></div>
      <div className="card"><div className="small">Evidence matched</div><div className="kpi">{closed}</div><div className="micro">Accepted procurement evidence exists</div></div>
      <div className="card"><div className="small">Unresolved</div><div className="kpi">{unresolved}</div><div className="micro">Ambiguity stays visible</div></div>
    </div>

    <div className="actions">
      <Link className="button" href="/app/profile">Configure supplier profile</Link>
      <Link className="button secondary" href="/api/export">Export fixture CSV</Link>
    </div>

    <section className="section">
      <div className="section-label">Opportunity feed</div>
      <h2 className="h2">Evidence-ranked workspace</h2>
      <p className="small">State is determined by the evidence contract. Supplier relevance can change ordering, never OPEN/CLOSED/UNRESOLVED.</p>
      <OpportunityList items={opportunities} />
    </section>
  </>;
}
