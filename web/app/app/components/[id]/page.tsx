import { notFound } from "next/navigation";
import { getOpportunity } from "@/lib/read-model";

export default async function ComponentPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const item = getOpportunity(id);
  if (!item) notFound();
  return <>
    <p className="small">Component evidence</p>
    <h1 className="h1">{item.component}</h1>
    <div className="notice"><strong>Development view.</strong> Only the customer-safe read model is rendered.</div>
    <section className="card"><p className="small">Scope evidence</p><p className="evidence">{item.projectEvidence}</p></section>
    <section className="card" style={{marginTop:16}}><p className="small">Assessment</p><p><strong>{item.state}</strong></p><p className="small">{item.state === "OPEN" ? item.openWording : item.procurementEvidence ?? "Insufficient evidence for a safe OPEN/CLOSED conclusion."}</p><p className="small">Coverage: {item.coverage} · as of {item.cutoffDate}</p></section>
  </>;
}
