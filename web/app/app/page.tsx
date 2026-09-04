import { OpportunityList } from "@/components/opportunity-list";
import { opportunities } from "@/lib/read-model";

export default function RunwayPage() {
  const open = opportunities.filter((item) => item.state === "OPEN").length;
  const closed = opportunities.filter((item) => item.state === "CLOSED").length;
  return <>
    <div className="eyebrow">Supplier runway</div>
    <h1 className="h1">Procurement evidence, before the tender-search workflow.</h1>
    <p className="lede">This shell is running against the frozen customer-safe fixture read model. Every OPEN conclusion is TED-scoped and carries its actual cutoff.</p>
    <div className="notice"><strong>Fixture environment.</strong> No item on this screen is represented as live production data.</div>
    <div className="grid">
      <div className="card"><div className="small">TED-scoped open</div><div className="kpi">{open}</div></div>
      <div className="card"><div className="small">Evidence matched</div><div className="kpi">{closed}</div></div>
      <div className="card"><div className="small">Coverage boundary</div><div className="kpi">TED</div></div>
    </div>
    <OpportunityList items={opportunities} />
  </>;
}
