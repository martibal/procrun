import { notFound } from "next/navigation";
import Link from "next/link";
import { getOpportunity } from "@/lib/read-model";

export default async function OpportunityPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const item = getOpportunity(id);
  if (!item) notFound();

  return <>
    <h1 className="h1">{item.component}</h1>
    <p className="lede">{item.projectTitle} · {item.geography}</p>
    <div className="notice scope"><strong>Fixture workspace.</strong> This page demonstrates the customer-safe evidence contract. Source wording and ProcRun interpretation are intentionally rendered as separate layers.</div>

    <div className="grid">
      <div className="card"><div className="small">State</div><div className="kpi">{item.state}</div></div>
      <div className="card"><div className="small">Negative-search scope</div><div className="kpi">{item.coverage}</div></div>
      <div className="card"><div className="small">Evidence cutoff</div><div className="kpi" style={{fontSize:20}}>{item.cutoffDate}</div></div>
    </div>

    <section className="section">
      <div className="section-label">Evidence chain</div>
      <div className="evidence-chain">
        <div className="chain-node">
          <div className="small">1 · Exact source wording</div>
          <div className="micro">{item.projectEvidenceType}</div>
          <p className="evidence">{item.projectEvidence}</p>
          <div className="micro">Verbatim admitted project evidence. This text is not a ProcRun rewrite.</div>
        </div>
        <div className="chain-arrow">→</div>
        <div className="chain-node">
          <div className="small">2 · Procurement evidence</div>
          <p>{item.procurementEvidence ?? "No accepted exact TED procurement evidence is attached to this fixture at the cutoff."}</p>
          <div className="micro">Evidence must satisfy the frozen production rules; similarity alone is insufficient.</div>
        </div>
        <div className="chain-arrow">→</div>
        <div className="chain-node">
          <div className="small">3 · ProcRun interpretation</div>
          <p><strong>{item.interpretation}</strong></p>
          <div className="micro">Derived state: {item.state} · coverage: {item.coverage}</div>
        </div>
      </div>
    </section>

    {item.state === "OPEN" && item.openWording && <div className="notice scope"><strong>OPEN wording:</strong> {item.openWording}<br /><br /><strong>Coverage boundary:</strong> This does not establish absence outside TED or under different wording, classification or procurement routes.</div>}
    {item.state === "UNRESOLVED" && <div className="notice scope"><strong>Why source wording is shown:</strong> UNRESOLVED does not replace ambiguity with a synthetic explanation. The exact admitted project wording remains visible so the customer can inspect the evidence behind the bounded interpretation.</div>}

    <section className="grid two section">
      <div className="card flat"><div className="small">Reproducibility</div><p className="small">Read-model version</p><p><strong>{item.sourceVersion}</strong></p><p className="micro">The browser receives this validated read object, never the raw TED/OpenCoesione response.</p></div>
      <div className="card flat"><div className="small">Project</div><p><strong>{item.projectTitle}</strong></p><p className="small">{item.valueEur ? `Fixture project value €${item.valueEur.toLocaleString("en-US")}` : "Project value unavailable"}</p><Link href={`/app/projects/${item.projectId}`} className="button secondary">Open project shell</Link></div>
    </section>
  </>;
}
