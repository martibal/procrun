import Link from "next/link";
import { notFound } from "next/navigation";
import { loadCustomerView } from "@/lib/customer-view";

export const dynamic = "force-dynamic";

export default async function ProjectPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const view = await loadCustomerView();
  const project = view.projects.find((candidate) => candidate.operation_code === id);
  if (!project) notFound();
  const rows = view.opportunities.filter((item) => item.projectId === id);

  return <>
    <h1 className="h1">{project.project_title ?? project.source_evidence.text}</h1>
    <p className="lede">{[project.region, project.nuts_code].filter(Boolean).join(" · ") || "Geography not stated"}</p>

    <div className="grid">
      <div className="card"><div className="small">Project state</div><div className="kpi">{project.state}</div></div>
      <div className="card"><div className="small">Components</div><div className="kpi">{project.components.length}</div></div>
      <div className="card"><div className="small">Evidence cutoff</div><div className="kpi" style={{fontSize:20}}>{project.cutoff_date}</div></div>
    </div>

    <section className="section card flat">
      <div className="section-label">Exact admitted project source</div>
      <p className="small">{project.source_evidence.source_type} · {project.source_evidence.source_field} · offsets {project.source_evidence.start}–{project.source_evidence.end}</p>
      <p className="evidence">{project.source_evidence.text}</p>
      <p className="small"><a href={project.source_evidence.source_url} target="_blank" rel="noreferrer">Open published source</a></p>
    </section>

    {project.unresolved_source_evidence.length > 0 && <section className="section card flat"><div className="section-label">UNRESOLVED source evidence</div>{project.unresolved_source_evidence.map((span, index) => <div key={`${span.start}-${span.end}-${index}`} style={{marginTop:12}}><p className="evidence">{span.text}</p><p className="micro">{span.source_field} · offsets {span.start}–{span.end}</p></div>)}</section>}

    <section className="section">
      <div className="section-label">Components and procurement state</div>
      {rows.map((item) => <div className="card flat" style={{marginTop:16}} key={item.id}>
        <div style={{display:"flex", justifyContent:"space-between", gap:16, alignItems:"flex-start"}}><div><h2 className="h2" style={{marginTop:0}}>{item.component}</h2><p className="small">{item.componentCategory ?? "No bounded component category"}</p></div><span className={`pill ${item.state === "CLOSED" ? "closed" : item.state === "UNRESOLVED" ? "unresolved" : ""}`}>{item.state}</span></div>
        <p className="evidence">{item.projectEvidence}</p>
        <p className="small"><strong>ProcRun interpretation:</strong> {item.interpretation}</p>
        {item.procurementMatches.map((match) => <p className="micro" key={match.evidence_id}>TED {match.notice_id}: {match.evidence.text} · <a href={match.source_url} target="_blank" rel="noreferrer">source</a></p>)}
        <Link className="button secondary" href={`/app/opportunities/${encodeURIComponent(item.id)}`}>Inspect evidence chain</Link>
      </div>)}
    </section>

    <section className="grid two section">
      <div className="card flat"><div className="small">Project metadata</div><p className="small">Operation code: <strong>{project.operation_code}</strong><br />Programme: {project.programme ?? "Not stated"}<br />Project start: {project.project_start ?? "Not stated"}<br />Project end: {project.project_end ?? "Not stated"}<br />Approved funding: {project.approved_funding_eur != null ? `€${project.approved_funding_eur.toLocaleString("en-US")}` : "Not stated"}</p></div>
      <div className="card flat"><div className="small">Deterministic provenance</div><p className="micro">Content hash: {project.content_hash}<br />Read model: {project.read_model_version}<br />Orchestration: {project.orchestration_version}<br />Component rules: {project.component_rule_version}<br />Matching rules: {project.match_rule_version}<br />Project classifier: {project.project_classifier_version}</p></div>
    </section>
  </>;
}
