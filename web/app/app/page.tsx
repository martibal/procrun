import Link from "next/link";
import { OpportunityList } from "@/components/opportunity-list";
import { opportunities } from "@/lib/read-model";

export default function RunwayPage() {
  const open = opportunities.filter((item) => item.state === "OPEN").length;
  const closed = opportunities.filter((item) => item.state === "CLOSED").length;
  const unresolved = opportunities.filter((item) => item.state === "UNRESOLVED").length;

  return <>
    <div className="eyebrow">Supplier runway</div>
    <h1 className="h1">Source evidence on the left. ProcRun interpretation on the right.</h1>
    <p className="lede">The workspace keeps exact project wording separate from the state ProcRun derives from it. OPEN is a bounded TED conclusion; ambiguity remains UNRESOLVED and visible.</p>

    <div className="notice scope"><strong>Fixture workspace.</strong> These rows demonstrate the customer-safe contract. Production uses the same separation of exact source wording, procurement evidence and derived interpretation.</div>

    <div className="grid">
      <div className="card"><div className="small">TED-scoped OPEN</div><div className="kpi">{open}</div><div className="micro">No qualifying TED match at cutoff</div></div>
      <div className="card"><div className="small">CLOSED</div><div className="kpi">{closed}</div><div className="micro">Accepted exact procurement evidence exists</div></div>
      <div className="card"><div className="small">UNRESOLVED</div><div className="kpi">{unresolved}</div><div className="micro">Source wording remains visible</div></div>
    </div>

    <div className="actions">
      <Link className="button" href="/app/profile">Configure supplier profile</Link>
      <Link className="button secondary" href="/api/export">Export fixture CSV</Link>
    </div>

    <section className="section">
      <div className="section-label">Opportunity feed</div>
      <h2 className="h2">Evidence-bounded project view</h2>
      <p className="small">Supplier relevance may affect ordering, but it never changes the evidence-derived OPEN, CLOSED or UNRESOLVED state.</p>
      <OpportunityList items={opportunities} />
    </section>
  </>;
}
