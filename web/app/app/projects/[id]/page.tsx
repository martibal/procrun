import { notFound } from "next/navigation";
import { opportunities } from "@/lib/read-model";

export default async function ProjectPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const items = opportunities.filter((item) => item.projectId === id);
  if (items.length === 0) notFound();
  const first = items[0];
  return <>
    <div className="eyebrow">Funded project</div>
    <h1 className="h1">{first.projectTitle}</h1>
    <p className="lede">{first.geography}</p>
    <div className="notice"><strong>Fixture environment.</strong> Funded-project screens remain non-live until OpenCoesione source-transfer and end-to-end acceptance are green.</div>
    <section className="card"><div className="eyebrow">Source-evidenced project scope</div><p className="evidence">{first.projectEvidence}</p></section>
    <div className="list">{items.map((item) => <div className="row" key={item.id}><div><strong>{item.component}</strong></div><div><span className="pill">{item.state}</span><p className="small">Coverage: {item.coverage} · {item.cutoffDate}</p></div><div className="small">{item.sourceVersion}</div></div>)}</div>
  </>;
}
