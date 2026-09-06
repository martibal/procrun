import { notFound } from "next/navigation";
import Link from "next/link";
import { getOpportunity } from "@/lib/read-model";

export default async function OpportunityPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const item = getOpportunity(id);
  if (!item) notFound();

  const conclusion = item.state === "OPEN"
    ? item.openWording
    : item.procurementEvidence ?? "Evidence is insufficient for a safe OPEN/CLOSED conclusion.";

  return <>
    <p className="small">Opportunity evidence</p>
    <h1 className="h1">{item.component}</h1>
    <p className="lede">{item.projectTitle} · {item.geography}</p>
    <div className="notice scope"><strong>Development workspace.</strong> This page demonstrates the customer-safe evidence contract. Fixture records are not customer-facing production data.</div>

    <div className="grid">
      <div className="card"><div className="small">State</div><div className="kpi">{item.state}</div></div>
      <div className="card"><div className="small">Negative-search scope</div><div className="kpi">{item.coverage}</div></div>
      <div className="card"><div className="small">Evidence cutoff</div><div className="kpi" style={{fontSize:20}}>{item.cutoffDate}</div></div>
    </div>

    <section className="section">
      <p className="small">Evidence chain</p>
      <div className="evidence-chain">
        <div className="chain-node"><p className="small">1. Project scope</p><p className="evidence">{item.projectEvidence}</p><div className="micro">Customer-safe source span</div></div>
        <div className="chain-arrow">→</div>
        <div className="chain-node"><p className="small">2. Procurement evidence</p><p>{item.procurementEvidence ?? "No accepted relevant TED procurement evidence at the cutoff."}</p><div className="micro">Matching cannot be inferred from similarity alone.</div></div>
        <div className="chain-arrow">→</div>
        <div className="chain-node"><p className="small">3. ProcRun conclusion</p><p><strong>{conclusion}</strong></p><div className="micro">State: {item.state} · coverage: {item.coverage}</div></div>
      </div>
    </section>

    {item.state === "OPEN" && <div className="notice scope"><strong>Coverage boundary:</strong> This does not establish absence outside TED, including purely national or below-threshold procedures.</div>}

    <section className="grid two section">
      <div className="card flat"><p className="small">Reproducibility</p><p className="small">Read-model version</p><p><strong>{item.sourceVersion}</strong></p><p className="micro">The browser receives this validated read object, never the raw TED/OpenCoesione response.</p></div>
      <div className="card flat"><p className="small">Project</p><p><strong>{item.projectTitle}</strong></p><p className="small">{item.valueEur ? `Project value €${item.valueEur.toLocaleString("en-US")}` : "Project value unavailable"}</p><Link href={`/app/projects/${item.projectId}`} className="button secondary">Open project</Link></div>
    </section>
  </>;
}
