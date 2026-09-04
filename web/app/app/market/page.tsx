import { opportunities } from "@/lib/read-model";

export default function MarketPage() {
  const total = opportunities.reduce((sum, item) => sum + (item.valueEur ?? 0), 0);
  const openValue = opportunities.filter((item) => item.state === "OPEN").reduce((sum, item) => sum + (item.valueEur ?? 0), 0);
  const states = ["OPEN", "CLOSED", "UNRESOLVED"] as const;

  return <>
    <div className="eyebrow">Market intelligence</div>
    <h1 className="h1">Market context with the coverage boundary attached.</h1>
    <p className="lede">This view summarises only the customer-safe fixture set. In production, TED market measures will disclose their observation window, missingness and exact indexed scope.</p>
    <div className="notice scope"><strong>Fixture workspace.</strong> These totals are interface fixtures, not market-size claims and not Portuguese national procurement totals.</div>

    <div className="grid">
      <div className="card"><div className="small">Fixture opportunities</div><div className="kpi">{opportunities.length}</div></div>
      <div className="card"><div className="small">Fixture project value</div><div className="kpi">€{(total / 1_000_000).toFixed(1)}m</div></div>
      <div className="card"><div className="small">TED-scoped OPEN value</div><div className="kpi">€{(openValue / 1_000_000).toFixed(1)}m</div></div>
    </div>

    <section className="section card flat">
      <div className="section-label">State distribution</div>
      <h2 className="h2">What the current fixture evidence supports</h2>
      {states.map((state) => {
        const count = opportunities.filter((item) => item.state === state).length;
        const pct = opportunities.length ? Math.round((count / opportunities.length) * 100) : 0;
        return <div key={state} style={{marginTop:18}}><div className="small"><strong>{state}</strong> · {count} item{count === 1 ? "" : "s"}</div><div className="bar"><span style={{width:`${pct}%`}} /></div></div>;
      })}
    </section>

    <section className="section grid two">
      <div className="card flat"><div className="eyebrow">Coverage</div><p><strong>TED only for MVP negative search.</strong></p><p className="small">No relevant procurement found in TED as of the item cutoff does not establish absence outside TED.</p></div>
      <div className="card flat"><div className="eyebrow">Funded-project expansion</div><p><strong>OpenCoesione 2021–2027</strong></p><p className="small">Italian funded-project data remains fixture-only in the browser until live transfer/E2E acceptance is green.</p></div>
    </section>
  </>;
}
