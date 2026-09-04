import Link from "next/link";
import type { Opportunity } from "@/lib/read-model";

export function OpportunityList({ items }: { items: readonly Opportunity[] }) {
  return (
    <div className="list">
      {items.map((item) => (
        <div className="row" key={item.id}>
          <div>
            <div className="small">{item.projectTitle}</div>
            <strong>{item.component}</strong>
            <div className="evidence">{item.projectEvidence}</div>
          </div>
          <div>
            <span className={`pill ${item.state === "CLOSED" ? "closed" : ""}`}>{item.state}</span>
            <p className="small">{item.state === "OPEN" ? item.openWording : item.procurementEvidence ?? "Evidence remains insufficient for a safe OPEN/CLOSED conclusion."}</p>
            <p className="small">Coverage: {item.coverage} · as of {item.cutoffDate}</p>
          </div>
          <div><Link className="button" href={`/app/opportunities/${item.id}`}>Inspect evidence</Link></div>
        </div>
      ))}
    </div>
  );
}
