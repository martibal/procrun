import Link from "next/link";
import type { CustomerOpportunity } from "@/lib/customer-view";

function stateClass(state: CustomerOpportunity["state"]): string {
  if (state === "CLOSED") return "closed";
  if (state === "UNRESOLVED") return "unresolved";
  return "";
}

function sourceTextCell(item: CustomerOpportunity) {
  const repeatsTitle = item.projectEvidenceType === "Project title" && item.projectEvidence.trim() === item.projectTitle.trim();

  if (repeatsTitle) {
    return (
      <>
        <div className="micro evidence-label">Project title</div>
        <div className="source-same-as-title">Same as the project title</div>
        <details className="source-text-details">
          <summary>Show exact source text</summary>
          <div className="evidence">{item.projectEvidence}</div>
        </details>
        {item.unresolvedEvidence.length > 0 && <div className="micro state-copy">Text needing review: {item.unresolvedEvidence.join(" | ")}</div>}
      </>
    );
  }

  return (
    <>
      <div className="micro evidence-label">{item.projectEvidenceType}</div>
      <div className="evidence source-text-preview">{item.projectEvidence}</div>
      {item.unresolvedEvidence.length > 0 && <div className="micro state-copy">Text needing review: {item.unresolvedEvidence.join(" | ")}</div>}
    </>
  );
}

export function OpportunityList({ items }: { items: readonly CustomerOpportunity[] }) {
  return (
    <div className="opportunity-table-wrap">
      <table className="opportunity-table">
        <thead>
          <tr>
            <th>Project / purchasing need</th>
            <th>Published source text</th>
            <th>What ProcRun found</th>
            <th>Status</th>
            <th aria-label="Open details" />
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>
                <div className="row-title">{item.projectTitle}</div>
                <div className="small">{item.componentId ? `Purchasing need: ${item.component}` : "Purchasing need: not identified from the published wording"}</div>
                <div className="micro">{item.geography}</div>
                {item.programme && <div className="micro">{item.programme}</div>}
                {item.valueEur != null && <div className="micro">Approved funding: €{item.valueEur.toLocaleString("en-US")}</div>}
              </td>
              <td>{sourceTextCell(item)}</td>
              <td>
                <p className="small interpretation">{item.interpretation}</p>
                {item.procurementEvidence && <p className="micro">Matching TED text: {item.procurementEvidence}</p>}
                <p className="micro">Checked against TED through {item.cutoffDate}</p>
              </td>
              <td>
                <span className={`pill ${stateClass(item.state)}`}>{item.state}</span>
              </td>
              <td className="table-action">
                <Link className="button" href={`/app/opportunities/${encodeURIComponent(item.id)}`}>View evidence</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
