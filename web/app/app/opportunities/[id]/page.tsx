import { notFound } from "next/navigation";
import { getOpportunity } from "@/lib/read-model";

export default async function OpportunityPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const item = getOpportunity(id);
  if (!item) notFound();
  return <>
    <div className="eyebrow">Opportunity evidence</div>
    <h1 className="h1">{item.component}</h1>
    <p className="lede">{item.projectTitle} · {item.geography}</p>
    <div className="notice"><strong>Fixture environment.</strong> This page demonstrates the customer-safe read contract, not live source data.</div>
    <div className="grid">
      <div className="card"><div className="small">State</div><div className="kpi">{item.state}</div></div>
      <div className="card"><div className="small">Coverage</div><div className="kpi">{item.coverage}</div></div>
      <div className="card"><div className="small">As of</div><div className="kpi" style={{fontSize:20}}>{item.cutoffDate}</div></div>
    </div>
    <section className="card" style={{marginTop:16}}><div className="eyebrow">Project-scope evidence</div><p className="evidence">{item.projectEvidence}</p></section>
    <section className="card" style={{marginTop:16}}><div className="eyebrow">Procurement conclusion</div><p>{item.state === "OPEN" ? item.openWording : item.procurementEvidence ?? "UNRESOLVED: evidence is insufficient for a bounded conclusion."}</p>{item.state === "OPEN" && <p className="small">This does not establish absence outside TED, including purely national or below-threshold procedures.</p>}</section>
    <section className="card" style={{marginTop:16}}><div className="eyebrow">Version</div><p className="small">{item.sourceVersion}</p></section>
  </>;
}
