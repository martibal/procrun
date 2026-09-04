import { notFound } from "next/navigation";
import { getOpportunity } from "@/lib/read-model";

export default async function ComponentPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const item = getOpportunity(id);
  if (!item) notFound();
  return <>
    <div className="eyebrow">Component evidence</div>
    <h1 className="h1">{item.component}</h1>
    <div className="notice"><strong>Fixture environment.</strong> Only the customer-safe read model is rendered.</div>
    <section className="card"><div className="eyebrow">Scope evidence</div><p className="evidence">{item.projectEvidence}</p></section>
    <section className="card" style={{marginTop:16}}><div className="eyebrow">Assessment</div><p><strong>{item.state}</strong></p><p className="small">{item.state === "OPEN" ? item.openWording : item.procurementEvidence ?? "Insufficient evidence for a safe OPEN/CLOSED conclusion."}</p><p className="small">Coverage: {item.coverage} · as of {item.cutoffDate}</p></section>
  </>;
}
