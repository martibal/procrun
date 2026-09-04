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
    <div className="eyebrow">Opportunity evidence</div>
    <h1 className="h1">{item.component}</h1>
    <p className="lede">{item.projectTitle} · {item.geography}</p>
    <div className="notice scope"><strong>Fixture workspace.</strong> This page demonstrates the customer-safe evidence contract, not live source data.</div>

    <div className="grid">
      <div className="card"><div className="small">State</div><div className="kpi">{item.state}</div></div>
      <div className="card"><div className="small">Negative-search scope</div><div className="kpi">{item.coverage}</div></div>
      <div className="card"><div className="small">Evidence cutoff</div><div className="kpi" style={{fontSize:20}}>{item.cutoffDate}</div></div>
    </div>

    <section className="section">
      <div className="section-label">Evidence chain</div>
      <div className="evidence-chain">
        <div className="chain-node"><div className="eyebrow">1 · Project scope</div><p className="evidence">{item.projectEvidence}</p><div className="micro">Source-safe fixture span</div></div>
        <div className="chain-arrow">→</div>
        <div className="chain-node"><div className="eyebrow">2 · Procurement evidence</div><p>{item.procurementEvidence ?? "No accepted relevant TED procurement evidence at the cutoff."}</p><div className="micro">Matching cannot be inferred from similarity alone.</div></div>
        <div className="chain-arrow">→</div>
        <div className="chain-node"><div className="eyebrow">3 · ProcRun conclusion</div><p><strong>{conclusion}</strong></p><div className="micro">State: {item.state} · coverage: {item.coverage}</div></div>
      </div>
    </section>

    {item.state === "OPEN" && <div className="notice scope"><strong>Coverage boundary:</strong> This does not establish absence outside TED, including purely national or below-threshold procedures.</div>}

    <section className="grid two section">
      <div className="card flat"><div className="eyebrow">Reproducibility</div><p className="small">Read-model version</p><p><strong>{item.sourceVersion}</strong></p><p className="micro">The browser receives this validated read object, never the raw TED/OpenCoesione response.</p></div>
      <div className="card flat"><div className="eyebrow">Project</div><p><strong>{item.projectTitle}</strong></p><p className="small">{item.valueEur ? `Fixture project value €${item.valueEur.toLocaleString("en-US")}` : "Project value unavailable"}</p><Link href={`/app/projects/${item.projectId}`} className="button secondary">Open project shell</Link></div>
    </section>
  </>;
}
