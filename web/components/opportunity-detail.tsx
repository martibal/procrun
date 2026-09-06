import Link from "next/link";
import type { Opportunity } from "@/lib/read-model";

export function OpportunityDetail({ item, publicMode = false }: { item: Opportunity; publicMode?: boolean }) {
  const conclusion = item.state === "OPEN"
    ? item.openWording
    : item.procurementEvidence ?? "Evidence is insufficient for a safe OPEN/CLOSED conclusion.";

  return <>
    <p className="small">Opportunity evidence</p>
    <h1 className="h1">{item.component}</h1>
    <p className="lede">{item.projectTitle} · {item.geography}</p>

    <div className="grid">
      <div className="card"><div className="small">State</div><div className="kpi">{item.state}</div></div>
      <div className="card"><div className="small">Negative-search scope</div><div className="kpi">{item.coverage}</div></div>
      <div className="card"><div className="small">Evidence cutoff</div><div className="kpi" style={{fontSize:20}}>{item.cutoffDate}</div></div>
    </div>

    <section className="section">
      <div className="section-label">Source facts</div>
      <div className="card flat">
        <p className="small"><strong>Project title</strong></p><p>{item.projectTitle}</p>
        <p className="small"><strong>Location</strong></p><p>{item.geography}</p>
        {item.programme ? <><p className="small"><strong>Programme</strong></p><p>{item.programme}</p></> : null}
        {item.projectStart ? <><p className="small"><strong>Project start</strong></p><p>{item.projectStart}</p></> : null}
        <p className="small"><strong>Operation code</strong></p><p>{item.projectId}</p>
        <p className="small"><strong>Approved funding</strong></p><p>{item.valueEur ? `€${item.valueEur.toLocaleString("en-GB")}` : "Unavailable"}</p>
        <p className="small"><strong>Published project evidence</strong></p><p className="evidence">{item.projectEvidence}</p>
        {item.sourceUrl ? <p><a className="text-link strong" href={item.sourceUrl}>Open source publication</a></p> : null}
      </div>
    </section>

    <section className="section">
      <div className="section-label">ProcRun analysis</div>
      <div className="evidence-chain">
        <div className="chain-node"><p className="small"><strong>1. Identified need</strong></p><p>{item.component}</p><div className="micro">Supported by the project evidence shown above.</div></div>
        <div className="chain-arrow">→</div>
        <div className="chain-node"><p className="small"><strong>2. Procurement evidence</strong></p><p>{item.procurementEvidence ?? "No accepted relevant TED procurement evidence at the cutoff."}</p><div className="micro">Matching cannot be inferred from similarity alone.</div></div>
        <div className="chain-arrow">→</div>
        <div className="chain-node"><p className="small"><strong>3. Conclusion</strong></p><p><strong>{conclusion}</strong></p><div className="micro">State: {item.state} · coverage: {item.coverage}</div></div>
      </div>
    </section>

    {item.coverageNote ? <div className="notice scope"><strong>Coverage boundary:</strong> {item.coverageNote}</div> : null}

    <section className="section card flat">
      <div className="section-label">Reproducibility</div>
      <p className="small">Read-model version</p>
      <p><strong>{item.sourceVersion}</strong></p>
      <p className="micro">This view receives the validated customer-safe read object, never the raw TED/OpenCoesione response.</p>
    </section>

    <div className="actions">
      {publicMode
        ? <><Link className="button" href="/pricing">Find opportunities like this</Link><Link className="button secondary" href={`/demo/opportunities/${item.id}/history`}>View full history</Link><Link className="button secondary" href="/demo">Back to demo</Link></>
        : <><Link className="button secondary" href="/app">Back to opportunities</Link><Link className="button secondary" href={`/app/projects/${item.projectId}`}>Open project</Link></>}
    </div>
  </>;
}
