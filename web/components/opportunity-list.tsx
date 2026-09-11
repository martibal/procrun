import Link from "next/link";
import type { Opportunity } from "@/lib/read-model";

function stateClass(state: Opportunity["state"]): string {
  if (state === "CLOSED") return "closed";
  if (state === "UNRESOLVED") return "unresolved";
  return "";
}

export function OpportunityList({ items }: { items: readonly Opportunity[] }) {
  return (
    <div className="opportunity-table-wrap">
      <table className="opportunity-table">
        <thead>
          <tr>
            <th>Project / component</th>
            <th>Exact source wording</th>
            <th>ProcRun interpretation</th>
            <th>State</th>
            <th aria-label="Open details" />
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>
                <div className="row-title">{item.component}</div>
                <div className="small">{item.projectTitle}</div>
                <div className="micro">{item.geography}</div>
              </td>
              <td>
                <div className="micro evidence-label">{item.projectEvidenceType}</div>
                <div className="evidence">{item.projectEvidence}</div>
              </td>
              <td>
                <p className="small interpretation">{item.interpretation}</p>
                {item.procurementEvidence && <p className="micro">TED evidence: {item.procurementEvidence}</p>}
                <p className="micro">Coverage: {item.coverage} · cutoff: {item.cutoffDate}</p>
              </td>
              <td>
                <span className={`pill ${stateClass(item.state)}`}>{item.state}</span>
                {item.state === "OPEN" && item.openWording && <p className="micro state-copy">{item.openWording}</p>}
              </td>
              <td className="table-action">
                <Link className="button" href={`/app/opportunities/${item.id}`}>Inspect evidence</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
