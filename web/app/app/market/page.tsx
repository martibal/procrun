import { opportunities } from "@/lib/read-model";

export default function MarketPage() {
  const total = opportunities.reduce((sum, item) => sum + (item.valueEur ?? 0), 0);
  return <>
    <div className="eyebrow">Market intelligence</div>
    <h1 className="h1">A bounded view of the indexed market.</h1>
    <p className="lede">Market context is secondary to evidence. Values below are fixture/read-model data and never imply coverage beyond TED.</p>
    <div className="notice"><strong>Fixture environment.</strong> Live market views will disclose missingness and source coverage.</div>
    <div className="grid">
      <div className="card"><div className="small">Fixture opportunities</div><div className="kpi">{opportunities.length}</div></div>
      <div className="card"><div className="small">Fixture project value</div><div className="kpi">€{(total/1_000_000).toFixed(1)}m</div></div>
      <div className="card"><div className="small">Negative-search scope</div><div className="kpi">TED</div></div>
    </div>
  </>;
}
