import { loadCustomerView } from "@/lib/customer-view";

export const dynamic = "force-dynamic";

export default async function MarketPage() {
  const view = await loadCustomerView();
  if (view.mode === "missing") {
    return <>
      <h1 className="h1">Market context with the coverage boundary attached.</h1>
      <div className="notice scope"><strong>No production snapshot is loaded.</strong> Build web/data/customer-runway.jsonl with <code>py scripts\build_customer_snapshot.py</code>.</div>
    </>;
  }

  const totalFunding = view.projects.reduce((sum, project) => sum + (project.approved_funding_eur ?? 0), 0);
  const states = ["OPEN", "CLOSED", "PARTIAL", "UNRESOLVED"] as const;

  return <>
    <h1 className="h1">Market context with the coverage boundary attached.</h1>
    <p className="lede">This view summarises the published customer-safe funded-project snapshot. It is not a claim about the total addressable market or procurement outside the indexed scope.</p>
    <div className="notice scope"><strong>Published snapshot.</strong> {view.projects.length.toLocaleString("en-US")} funded projects · data through {view.cutoffDate}.</div>

    <div className="grid">
      <div className="card"><div className="small">Published projects</div><div className="kpi">{view.projects.length.toLocaleString("en-US")}</div></div>
      <div className="card"><div className="small">Approved project funding</div><div className="kpi">€{(totalFunding / 1_000_000_000).toFixed(2)}bn</div><div className="micro">Sum only where the source states approved funding</div></div>
      <div className="card"><div className="small">Evidence rows</div><div className="kpi">{view.opportunities.length.toLocaleString("en-US")}</div><div className="micro">Every project represented at least once</div></div>
    </div>

    <section className="section card flat">
      <div className="section-label">Project state distribution</div>
      <h2 className="h2">What the current evidence supports</h2>
      {states.map((state) => {
        const count = view.projects.filter((project) => project.state === state).length;
        const pct = view.projects.length ? Math.round((count / view.projects.length) * 100) : 0;
        return <div key={state} style={{marginTop:18}}><div className="small"><strong>{state}</strong> · {count.toLocaleString("en-US")} project{count === 1 ? "" : "s"}</div><div className="bar"><span style={{width:`${pct}%`}} /></div></div>;
      })}
    </section>

    <section className="section grid two">
      <div className="card flat"><div className="small">Procurement coverage</div><p><strong>Complete TED Italy query universe through each snapshot cutoff.</strong></p><p className="small">OPEN means only that no procurement match satisfying the frozen exact-evidence rules was found in that universe. It does not establish absence outside TED or under different wording/classification.</p></div>
      <div className="card flat"><div className="small">Funded-project source</div><p><strong>Approved OpenCoesione 2021–2027 source contract.</strong></p><p className="small">The browser consumes only the validated customer-safe read model; raw source envelopes and identity-shaped source fields are not exposed.</p></div>
    </section>
  </>;
}
