import Link from "next/link";
import { OpportunityList } from "@/components/opportunity-list";
import { loadCustomerView } from "@/lib/customer-view";

export const dynamic = "force-dynamic";

const PAGE_SIZES = [10, 25, 50] as const;
type PageSize = (typeof PAGE_SIZES)[number];

function parsePageSize(rawValue: string | undefined): PageSize {
  const parsed = Number.parseInt(rawValue ?? "10", 10);
  return PAGE_SIZES.includes(parsed as PageSize) ? (parsed as PageSize) : 10;
}

function PageSizeControl({ pageSize, position }: { pageSize: PageSize; position: "top" | "bottom" }) {
  return (
    <nav className={`table-controls table-controls-${position}`} aria-label={`Rows per page ${position}`}>
      <span className="small">Rows per page</span>
      <div className="page-size-options">
        {PAGE_SIZES.map((size) => (
          <Link
            key={size}
            className={`page-size-option${pageSize === size ? " active" : ""}`}
            href={`/app?page=1&rows=${size}`}
            aria-current={pageSize === size ? "page" : undefined}
          >
            {size}
          </Link>
        ))}
      </div>
    </nav>
  );
}

export default async function RunwayPage({ searchParams }: { searchParams: Promise<{ page?: string; rows?: string }> }) {
  const view = await loadCustomerView();
  const { page: rawPage, rows: rawRows } = await searchParams;
  const pageSize = parsePageSize(rawRows);
  const requestedPage = Number.parseInt(rawPage ?? "1", 10);
  const totalPages = Math.max(1, Math.ceil(view.opportunities.length / pageSize));
  const page = Number.isFinite(requestedPage) ? Math.min(Math.max(requestedPage, 1), totalPages) : 1;
  const start = (page - 1) * pageSize;
  const rows = view.opportunities.slice(start, start + pageSize);

  if (view.mode === "missing") {
    return <>
      <h1 className="h1">Customer project intelligence.</h1>
      <p className="lede">This workspace only renders the hardened customer-safe production read model. It does not silently substitute fixture rows.</p>
      <div className="notice scope">
        <strong>No production snapshot is loaded locally.</strong>
        <p>From <code>C:\procrun</code>, run <code>python scripts\build_customer_snapshot.py</code>. When it completes, refresh this page.</p>
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

    <section className="section runway-section">
      <div className="section-label">All projects</div>
      <h2 className="h2">Evidence-bounded customer view</h2>
      <p className="small">Showing rows {view.opportunities.length ? start + 1 : 0}–{Math.min(start + pageSize, view.opportunities.length)} of {view.opportunities.length.toLocaleString("en-US")}. Projects without an emitted component still appear as UNRESOLVED rows, so no published project disappears from the customer view.</p>
      <PageSizeControl pageSize={pageSize} position="top" />
      <OpportunityList items={rows} />
      <div className="table-footer-controls">
        <div className="actions pagination-actions">
          {page > 1 && <Link className="button secondary" href={`/app?page=${page - 1}&rows=${pageSize}`}>Previous</Link>}
          <span className="small">Page {page} of {totalPages}</span>
          {page < totalPages && <Link className="button secondary" href={`/app?page=${page + 1}&rows=${pageSize}`}>Next</Link>}
        </div>
        <PageSizeControl pageSize={pageSize} position="bottom" />
      </div>
    </section>
  </>;
}
