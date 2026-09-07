import Link from "next/link";
import type { Opportunity } from "@/lib/read-model";

function stateClass(state: Opportunity["state"]): string {
  if (state === "CLOSED") return "closed";
  if (state === "UNRESOLVED") return "unresolved";
  return "";
}

export function OpportunityList({ items }: { items: readonly Opportunity[] }) {
  return (
    <div className="list">
      {items.map((item) => (
        <article className="row" id={item.componentId} key={item.id}>
          <div>
            <div className="small">
              <span>{item.projectTitle}</span><br />
              <span>{item.geography}</span>
            </div>
            <div className="row-title">{item.component}</div>
            <div className="evidence">{item.projectEvidence}</div>
          </div>
          <div>
            <span className={`pill ${stateClass(item.state)}`}>{item.state}</span>
            <p className="small">
              {item.state === "OPEN"
                ? item.openWording
                : item.procurementEvidence ?? "Evidence remains insufficient for a safe OPEN/CLOSED conclusion."}
            </p>
            <p className="micro">Coverage: {item.coverage}<br />As of {item.cutoffDate}</p>
            <p className="micro">Version: {item.sourceVersion}</p>
          </div>
          <div>
            <Link className="button" href={`/app/opportunities/${item.id}`}>Inspect evidence</Link>
          </div>
        </article>
      ))}
    </div>
  );
}
