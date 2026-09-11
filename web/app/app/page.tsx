import Link from "next/link";
import { OpportunityList } from "@/components/opportunity-list";
import { loadCustomerView, type CustomerOpportunity } from "@/lib/customer-view";

export const dynamic = "force-dynamic";

const PAGE_SIZES = [10, 25, 50] as const;
type PageSize = (typeof PAGE_SIZES)[number];

type SearchParams = {
  page?: string;
  rows?: string;
  q?: string;
  state?: string;
  need?: string;
  region?: string;
  funding?: string;
};

function parsePageSize(rawValue: string | undefined): PageSize {
  const parsed = Number.parseInt(rawValue ?? "10", 10);
  return PAGE_SIZES.includes(parsed as PageSize) ? (parsed as PageSize) : 10;
}

function queryHref(params: SearchParams, updates: Record<string, string | undefined>): string {
  const next = new URLSearchParams();
  const merged = { ...params, ...updates };
  for (const [key, value] of Object.entries(merged)) {
    if (value && value !== "ALL" && value !== "0") next.set(key, value);
  }
  const query = next.toString();
  return query ? `/app?${query}` : "/app";
}

function PageSizeControl({ pageSize, params, position }: { pageSize: PageSize; params: SearchParams; position: "top" | "bottom" }) {
  return (
    <nav className={`table-controls table-controls-${position}`} aria-label={`Rows per page ${position}`}>
      <span className="small">Projects per page</span>
      <div className="page-size-options">
        {PAGE_SIZES.map((size) => (
          <Link
            key={size}
            className={`page-size-option${pageSize === size ? " active" : ""}`}
            href={queryHref(params, { page: "1", rows: String(size) })}
            aria-current={pageSize === size ? "page" : undefined}
          >
            {size}
          </Link>
        ))}
      </div>
    </nav>
  );
}

function regionOf(item: CustomerOpportunity): string {
  return item.geography.split(" · ")[0] || "Not stated";
}

export default async function RunwayPage({ searchParams }: { searchParams: Promise<SearchParams> }) {
  const view = await loadCustomerView();
  const params = await searchParams;
  const pageSize = parsePageSize(params.rows);

  if (view.mode === "missing") {
    return <>
      <h1 className="h1">Projects and procurement status</h1>
      <p className="lede">No published project data is available in this environment yet.</p>
      <div className="notice scope">
        <strong>Customer data has not been loaded locally.</strong>
        <p>From <code>C:\procrun</code>, run <code>python scripts\build_customer_snapshot.py</code>, then refresh this page.</p>
      </div>
    </>;
  }

  const query = (params.q ?? "").trim().toLocaleLowerCase();
  const state = params.state ?? "ALL";
  const need = params.need ?? "ALL";
  const region = params.region ?? "ALL";
  const minimumFunding = Number.parseInt(params.funding ?? "0", 10) || 0;

  const filtered = view.opportunities.filter((item) => {
    if (state !== "ALL" && item.state !== state) return false;
    if (need !== "ALL" && item.component !== need) return false;
    if (region !== "ALL" && regionOf(item) !== region) return false;
    if ((item.valueEur ?? 0) < minimumFunding) return false;
    if (!query) return true;
    return [item.projectTitle, item.component, item.programme, item.geography, item.projectEvidence]
      .filter(Boolean)
      .join(" ")
      .toLocaleLowerCase()
      .includes(query);
  });

  const requestedPage = Number.parseInt(params.page ?? "1", 10);
  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const page = Number.isFinite(requestedPage) ? Math.min(Math.max(requestedPage, 1), totalPages) : 1;
  const start = (page - 1) * pageSize;
  const rows = filtered.slice(start, start + pageSize);

  const projectState = (value: string) => view.projects.filter((project) => project.state === value).length;
  const classifiedProjects = projectState("OPEN") + projectState("CLOSED") + projectState("PARTIAL");
  const needsReviewProjects = projectState("UNRESOLVED");
  const needOptions = [...new Set(view.opportunities.filter((item) => item.componentId).map((item) => item.component))].sort();
  const regionOptions = [...new Set(view.opportunities.map(regionOf).filter((value) => value !== "Not stated"))].sort();

  return <>
    <h1 className="h1">Projects and procurement status</h1>
    <p className="lede">Browse funded projects and see what ProcRun can determine from the published project text and procurement notices in TED.</p>

    <div className="notice scope"><strong>Current data.</strong> {view.projects.length.toLocaleString("en-US")} funded projects · updated through {view.cutoffDate}.</div>

    <div className="grid customer-summary-grid">
      <div className="card"><div className="small">Projects covered</div><div className="kpi">{view.projects.length.toLocaleString("en-US")}</div><div className="micro">Funded projects currently included in ProcRun</div></div>
      <div className="card"><div className="small">Projects with a classified purchasing need</div><div className="kpi">{classifiedProjects.toLocaleString("en-US")}</div><div className="micro">Projects where ProcRun can identify and assess at least one purchasing need</div></div>
    </div>
    <p className="review-coverage-note"><strong>{needsReviewProjects.toLocaleString("en-US")}</strong> additional projects are available for review because their published wording does not identify a purchasing need clearly enough for a reliable status. They remain searchable and are never hidden from the dataset.</p>

    <div className="actions">
      <Link className="button" href="/app/profile">Configure supplier profile</Link>
      <Link className="button secondary" href="/api/export">Export CSV</Link>
    </div>

    <section className="section runway-section">
      <div className="section-label">Project search</div>
      <h2 className="h2">Find the projects that matter to you</h2>
      <p className="small">Use the filters to narrow the list by status, purchasing need, location or funding. Source text and ProcRun's assessment are kept separate so you can see what each result is based on.</p>

      <details className="status-help">
        <summary>What do the statuses mean?</summary>
        <div className="status-guide" aria-label="Status definitions">
          <div><strong>OPEN</strong><span>A purchasing need is visible in the project text, and ProcRun found no matching procurement notice in TED up to the date shown.</span></div>
          <div><strong>CLOSED</strong><span>ProcRun found a TED procurement notice that matches the identified purchasing need.</span></div>
          <div><strong>UNRESOLVED</strong><span>The published wording is not specific enough to decide reliably whether a purchasing need is Open or Closed. The source text remains available for review.</span></div>
          <div><strong>PARTIAL</strong><span>A project contains more than one identified purchasing need and they do not all have the same status.</span></div>
        </div>
      </details>

      <form className="project-filters" method="get" action="/app">
        <label className="filter-search"><span>Search</span><input type="search" name="q" defaultValue={params.q ?? ""} placeholder="Project, programme, location or need" /></label>
        <label><span>Status</span><select name="state" defaultValue={state}><option value="ALL">All statuses</option><option value="OPEN">Open</option><option value="CLOSED">Closed</option><option value="UNRESOLVED">Unresolved</option></select></label>
        <label><span>Purchasing need</span><select name="need" defaultValue={need}><option value="ALL">All purchasing needs</option>{needOptions.map((value) => <option key={value} value={value}>{value}</option>)}</select></label>
        <label><span>Location</span><select name="region" defaultValue={region}><option value="ALL">All locations</option>{regionOptions.map((value) => <option key={value} value={value}>{value}</option>)}</select></label>
        <label><span>Minimum funding</span><select name="funding" defaultValue={String(minimumFunding)}><option value="0">Any amount</option><option value="25000">€25k+</option><option value="100000">€100k+</option><option value="500000">€500k+</option><option value="1000000">€1m+</option></select></label>
        <input type="hidden" name="rows" value={pageSize} />
        <div className="filter-actions"><button className="button" type="submit">Apply filters</button><Link className="button secondary" href={`/app?rows=${pageSize}`}>Clear</Link></div>
      </form>

      <div className="result-summary">
        <span className="small">Showing {filtered.length ? start + 1 : 0}–{Math.min(start + pageSize, filtered.length)} of {filtered.length.toLocaleString("en-US")} matching rows</span>
        <PageSizeControl pageSize={pageSize} params={params} position="top" />
      </div>

      <OpportunityList items={rows} />

      <div className="table-footer-controls">
        <div className="actions pagination-actions">
          {page > 1 && <Link className="button secondary" href={queryHref(params, { page: String(page - 1), rows: String(pageSize) })}>Previous</Link>}
          <span className="small">Page {page} of {totalPages}</span>
          {page < totalPages && <Link className="button secondary" href={queryHref(params, { page: String(page + 1), rows: String(pageSize) })}>Next</Link>}
        </div>
        <PageSizeControl pageSize={pageSize} params={params} position="bottom" />
      </div>
    </section>
  </>;
}
