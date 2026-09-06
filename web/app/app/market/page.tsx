import { opportunities } from "@/lib/read-model";

export default function MarketPage() {
  const total = opportunities.reduce((sum, item) => sum + (item.valueEur ?? 0), 0);
  const openValue = opportunities.filter((item) => item.state === "OPEN").reduce((sum, item) => sum + (item.valueEur ?? 0), 0);
  const states = ["OPEN", "CLOSED", "UNRESOLVED"] as const;

  return <>
    <p className="small">Market Intelligence</p>
    <h1 className="h1">Market context with the coverage boundary attached.</h1>
    <p className="lede">This development view summarises only the current customer-safe set. Production market measures must disclose their observation window, missingness and exact indexed scope.</p>
    <div className="notice scope"><strong>Development workspace.</strong> These totals are interface values, not a complete Lombardia or Italian procurement market-size claim.</div>

    <div className="grid">
      <div className="card"><div className="small">Current opportunities</div><div className="kpi">{opportunities.length}</div></div>
      <div className="card"><div className="small">Current project value</div><div className="kpi">€{(total / 1_000_000).toFixed(1)}m</div></div>
      <div className="card"><div className="small">TED-scoped OPEN value</div><div className="kpi">€{(openValue / 1_000_000).toFixed(1)}m</div></div>
    </div>

    <section className="section card flat">
      <p className="small">State distribution</p>
      <h2 className="h2">What the current evidence supports</h2>
      {states.map((state) => {
        const count = opportunities.filter((item) => item.state === state).length;
        const pct = opportunities.length ? Math.round((count / opportunities.length) * 100) : 0;
        return <div key={state} style={{marginTop:18}}><div className="small"><strong>{state}</strong> · {count} item{count === 1 ? "" : "s"}</div><div className="bar"><span style={{width:`${pct}%`}} /></div></div>;
      })}
    </section>

    <section className="section grid two">
      <div className="card flat"><p className="small">Coverage</p><p><strong>TED only for MVP negative search.</strong></p><p className="small">No relevant procurement found in TED as of the item cutoff does not establish absence outside TED.</p></div>
      <div className="card flat"><p className="small">Funded projects</p><p><strong>PR FESR Lombardia 2021–2027</strong></p><p className="small">The current live funded-project route is Lombardia only. Additional regions require separate source activation before customer-facing use.</p></div>
    </section>
  </>;
}
