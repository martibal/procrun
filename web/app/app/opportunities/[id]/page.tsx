import Link from "next/link";
import { notFound } from "next/navigation";
import { loadCustomerView } from "@/lib/customer-view";

export const dynamic = "force-dynamic";

export default async function OpportunityPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const view = await loadCustomerView();
  const item = view.opportunities.find((candidate) => candidate.id === id);
  if (!item) notFound();

  return <>
    <h1 className="h1">{item.component}</h1>
    <p className="lede">{item.projectTitle} · {item.geography}</p>
    <div className="notice scope"><strong>Published customer-safe read model.</strong> Exact source wording, accepted TED evidence and ProcRun interpretation are rendered as separate layers.</div>

    <div className="grid">
      <div className="card"><div className="small">State</div><div className="kpi">{item.state}</div></div>
      <div className="card"><div className="small">Negative-search scope</div><div className="kpi">{item.coverage}</div></div>
      <div className="card"><div className="small">Evidence cutoff</div><div className="kpi" style={{fontSize:20}}>{item.cutoffDate}</div></div>
    </div>

    <section className="section">
      <div className="section-label">Evidence chain</div>
      <div className="evidence-chain">
        <div className="chain-node">
          <div className="small">1 · Exact project wording</div>
          <div className="micro">{item.projectEvidenceType}</div>
          <p className="evidence">{item.projectEvidence}</p>
          <p className="micro"><a href={item.sourceUrl} target="_blank" rel="noreferrer">Open published project source</a></p>
        </div>
        <div className="chain-arrow">→</div>
        <div className="chain-node">
          <div className="small">2 · Accepted procurement evidence</div>
          {item.procurementMatches.length === 0 ? <p>No accepted exact TED procurement evidence at the cutoff.</p> : item.procurementMatches.map((match) => <div key={match.evidence_id} style={{marginTop:12}}><p className="evidence">{match.evidence.text}</p><p className="micro">TED {match.notice_id} · {match.publication_date} · <a href={match.source_url} target="_blank" rel="noreferrer">source</a></p></div>)}
          <div className="micro">Similarity alone is never promoted to accepted evidence.</div>
        </div>
        <div className="chain-arrow">→</div>
        <div className="chain-node">
          <div className="small">3 · ProcRun interpretation</div>
          <p><strong>{item.interpretation}</strong></p>
          <div className="micro">Derived state: {item.state} · coverage: {item.coverage}</div>
        </div>
      </div>
    </section>

    {item.unresolvedEvidence.length > 0 && <div className="notice scope"><strong>UNRESOLVED source wording:</strong> {item.unresolvedEvidence.join(" | ")}</div>}
    {item.state === "OPEN" && item.openWording && <div className="notice scope"><strong>OPEN wording:</strong> {item.openWording}<br /><br /><strong>Coverage boundary:</strong> This does not establish absence outside TED or under different wording, classification or procurement routes.</div>}

    <section className="grid two section">
      <div className="card flat"><div className="small">Reproducibility</div><p className="small">Content hash</p><p className="micro">{item.contentHash}</p><p className="small">Read model: <strong>{item.readModelVersion}</strong></p><p className="micro">Orchestration: {item.orchestrationVersion}<br />Component rules: {item.componentRuleVersion}<br />Matching rules: {item.matchRuleVersion}<br />Project classifier: {item.projectClassifierVersion}</p></div>
      <div className="card flat"><div className="small">Project</div><p><strong>{item.projectTitle}</strong></p><p className="small">{item.valueEur != null ? `Approved funding €${item.valueEur.toLocaleString("en-US")}` : "Approved funding unavailable"}</p>{item.programme && <p className="small">{item.programme}</p>}<Link href={`/app/projects/${encodeURIComponent(item.projectId)}`} className="button secondary">Open full project</Link></div>
    </section>
  </>;
}
