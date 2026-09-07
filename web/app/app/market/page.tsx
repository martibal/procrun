import { loadCategoryBaselines } from "@/lib/category-baselines";
import { opportunities } from "@/lib/read-model";

export const dynamic = "force-dynamic";

function days(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

export default async function MarketPage() {
  const total = opportunities.reduce((sum, item) => sum + (item.valueEur ?? 0), 0);
  const openValue = opportunities.filter((item) => item.state === "OPEN").reduce((sum, item) => sum + (item.valueEur ?? 0), 0);
  const states = ["OPEN", "CLOSED", "UNRESOLVED"] as const;
  const baselines = await loadCategoryBaselines();

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
        return <div key={state} style={{marginTop:18}}><div className="small"><strong>{state}</strong>: {count} item{count === 1 ? "" : "s"}</div><div className="bar"><span style={{width:`${pct}%`}} /></div></div>;
      })}
    </section>

    <section className="section">
      <p className="small">Observed category baselines</p>
      <h2 className="h2">How long comparable needs stayed OPEN before a verified CLOSED observation</h2>
      <p className="small">Each row uses the exact frozen component category and one first effective OPEN-to-CLOSED lifecycle per component. Corrected observations are excluded as baseline endpoints. These are descriptive ProcRun-observed durations, not total project duration and not a prediction.</p>
      {baselines === null ? (
        <p className="small">No production baseline is rendered without the configured history database.</p>
      ) : baselines.length === 0 ? (
        <p className="small">No completed OPEN-to-CLOSED histories are available yet.</p>
      ) : (
        <div style={{overflowX:"auto"}}>
          <table>
            <thead><tr><th>Category</th><th>p25 days</th><th>Median days</th><th>p75 days</th><th>n</th></tr></thead>
            <tbody>
              {baselines.map((baseline) => <tr key={baseline.category}>
                <td>{baseline.category}</td>
                <td>{days(baseline.p25Days)}</td>
                <td>{days(baseline.medianDays)}</td>
                <td>{days(baseline.p75Days)}</td>
                <td>{baseline.n}</td>
              </tr>)}
            </tbody>
          </table>
        </div>
      )}
      <p className="micro">Observation window for each category runs from its earliest included OPEN observation through its latest included CLOSED observation. No percentile ranking of a current opportunity is shown here; that is a separate feature with its own minimum-sample rule.</p>
    </section>

    <section className="section grid two">
      <div className="card flat"><p className="small">Coverage</p><p><strong>TED only for MVP negative search.</strong></p><p className="small">No relevant procurement found in TED as of the item cutoff does not establish absence outside TED.</p></div>
      <div className="card flat"><p className="small">Funded projects</p><p><strong>PR FESR Lombardia 2021–2027</strong></p><p className="small">The current live funded-project route is Lombardia only. Additional regions require separate source activation before customer-facing use.</p></div>
    </section>
  </>;
}
