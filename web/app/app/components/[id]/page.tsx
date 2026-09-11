import { notFound } from "next/navigation";
import { loadCustomerView } from "@/lib/customer-view";

export const dynamic = "force-dynamic";

export default async function ComponentPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const view = await loadCustomerView();
  const item = view.opportunities.find((candidate) => candidate.componentId === id || candidate.id === id);
  if (!item) notFound();
  return <>
    <h1 className="h1">{item.component}</h1>
    <div className="notice"><strong>Published customer-safe read model.</strong> Only hardened source evidence and derived state are rendered.</div>
    <section className="card"><div className="small">Exact project evidence</div><p className="evidence">{item.projectEvidence}</p></section>
    <section className="card" style={{marginTop:16}}><div className="small">Assessment</div><p><strong>{item.state}</strong></p><p className="small">{item.interpretation}</p><p className="small">Coverage: {item.coverage} · as of {item.cutoffDate}</p></section>
  </>;
}
