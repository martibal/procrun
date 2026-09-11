import Link from "next/link";
import { OpportunityList } from "@/components/opportunity-list";
import { loadCustomerView } from "@/lib/customer-view";

export const dynamic = "force-dynamic";

const PAGE_SIZE = 100;

export default async function RunwayPage({ searchParams }: { searchParams: Promise<{ page?: string }> }) {
  const view = await loadCustomerView();
  const { page: rawPage } = await searchParams;
  const requestedPage = Number.parseInt(rawPage ?? "1", 10);
  const totalPages = Math.max(1, Math.ceil(view.opportunities.length / PAGE_SIZE));
  const page = Number.isFinite(requestedPage) ? Math.min(Math.max(requestedPage, 1), totalPages) : 1;
  const start = (page - 1) * PAGE_SIZE;
  const rows = view.opportunities.slice(start, start + PAGE_SIZE);

  if (view.mode === "missing") {
    return <>
      <h1 className="h1">Customer project intelligence.</h1>
      <p className="lede">This workspace only renders the hardened customer-safe production read model. It does not silently substitute fixture rows.</p>
      <div className="notice scope">
        <strong>No production snapshot is loaded locally.</strong>
        <p>From <code>C:\procrun</code>, run <code>py scripts\build_customer_snapshot.py</code>. When it completes, refresh this page.</p>
        <p className="micro">Expected local output: web/data/customer-runway.jsonl</p>
      </div>
    </>;
  }

  const projectState = (state: string) => view.projects.filter((project) => project.state === state).length;

  return <>
    <h1 className="h1">Customer project intelligence.</h1>
    <p className="lede">Every published project is represented from the hardened customer-safe read model. Exact source wording, ProcRun interpretation and accepted TED evidence remain separate.</p>

    <div className="notice scope"><strong>Live customer snapshot.</strong> {view.projects.length.toLocaleString("en-US")} projects · {view.opportunities.length.toLocaleString("en-US")} project/component rows · data through {view.cutoffDate}.</div>

    <div className="grid">
      <div className="card"><div className="small">Published projects</div><div className="kpi">{view.projects.length.toLocaleString("en-US")}</div><div className="micro">Every logical funded project represented</div></div>
      <div className="card"><div className="small">Resolved projects</div><div className="kpi">{(projectState("OPEN") + projectState("CLOSED") + projectState("PARTIAL")).toLocaleString("en-US")}</div><div className="micro">Evidence-bounded OPEN, CLOSED or PARTIAL</div></div>
      <div className="card"><div className="small">UNRESOLVED projects</div><div className="kpi">{projectState("UNRESOLVED").toLocaleString("en-US")}</div><div className="micro">Ambiguity retained with source wording visible</div></div>
    </div>

    <div className="actions">
      <Link className="button" href="/app/profile">Configure supplier profile</Link>
      <Link className="button secondary" href="/api/export">Export customer-safe CSV</Link>
    </div>

    <section className="section">
      <div className="section-label">All projects</div>
      <h2 className="h2">Evidence-bounded customer view</h2>
      <p className="small">Showing rows {view.opportunities.length ? start + 1 : 0}–{Math.min(start + PAGE_SIZE, view.opportunities.length)} of {view.opportunities.length.toLocaleString("en-US")}. Projects without an emitted component still appear as UNRESOLVED rows, so no published project disappears from the customer view.</p>
      <OpportunityList items={rows} />
      <div className="actions">
        {page > 1 && <Link className="button secondary" href={`/app?page=${page - 1}`}>Previous</Link>}
        <span className="small">Page {page} of {totalPages}</span>
        {page < totalPages && <Link className="button secondary" href={`/app?page=${page + 1}`}>Next</Link>}
      </div>
    </section>
  </>;
}
