import Link from "next/link";
import type { Opportunity } from "@/lib/read-model";

type HistoricalPosition = {
  currentAgeDays: number;
  n: number;
  percentile: number;
};

function ordinalPercentile(value: number): string {
  const rounded = Math.round(value);
  const mod100 = rounded % 100;

  if (mod100 >= 11 && mod100 <= 13) {
    return `${rounded}th percentile`;
  }

  switch (rounded % 10) {
    case 1:
      return `${rounded}st percentile`;
    case 2:
      return `${rounded}nd percentile`;
    case 3:
      return `${rounded}rd percentile`;
    default:
      return `${rounded}th percentile`;
  }
}

export function OpportunityDetail({
  item,
  publicMode = false,
  historicalPosition = null,
}: {
  item: Opportunity;
  publicMode?: boolean;
  historicalPosition?: HistoricalPosition | null;
}) {
  const conclusion = item.state === "OPEN"
    ? item.openWording
    : item.procurementEvidence ?? "Evidence is insufficient for a safe OPEN/CLOSED conclusion.";

  const showHistoricalPosition =
    !publicMode &&
    item.state === "OPEN" &&
    historicalPosition !== null;

  return <>
    <p className="small">Opportunity evidence</p>
    <h1 className="h1">{item.component}</h1>
    <p className="lede">{item.projectTitle}<br />{item.geography}</p>

    <div className="coverage-list section">
      <div><strong>State</strong><p>{item.state}</p></div>
      <div><strong>Negative-search scope</strong><p>{item.coverage}</p></div>
      <div><strong>Evidence cutoff</strong><p>{item.cutoffDate}</p></div>
    </div>

    <section className="section">
      <p className="small">Source facts</p>
      <div className="coverage-list">
        <div><strong>Project title</strong><p>{item.projectTitle}</p></div>
        <div><strong>Location</strong><p>{item.geography}</p></div>
        {item.programme ? <div><strong>Programme</strong><p>{item.programme}</p></div> : null}
        {item.projectStart ? <div><strong>Project start</strong><p>{item.projectStart}</p></div> : null}
        <div><strong>Operation code</strong><p>{item.projectId}</p></div>
        <div><strong>Approved funding</strong><p>{item.valueEur ? `€${item.valueEur.toLocaleString("en-GB")}` : "Unavailable"}</p></div>
        <div><strong>Published project evidence</strong><p className="evidence">{item.projectEvidence}</p></div>
      </div>
      {item.sourceUrl ? <p><a className="text-link strong" href={item.sourceUrl}>Open source publication</a></p> : null}
    </section>

    <section className="section">
      <p className="small">ProcRun analysis</p>
      <div className="coverage-list">
        <div>
          <strong>Identified need</strong>
          <p>{item.component}</p>
          <p className="micro">Supported by the project evidence shown above.</p>
        </div>

        <div>
          <strong>Procurement evidence</strong>
          <p>{item.procurementEvidence ?? "No accepted relevant TED procurement evidence at the cutoff."}</p>
          <p className="micro">Matching cannot be inferred from similarity alone.</p>
        </div>

        <div>
          <strong>Conclusion</strong>
          <p>{conclusion}</p>
          <p className="micro">State: {item.state}<br />Coverage: {item.coverage}</p>
        </div>

        {showHistoricalPosition ? (
          <div>
            <strong>Historical position</strong>
            <p>{ordinalPercentile(historicalPosition.percentile)}</p>
            <p className="micro">
              Current observed OPEN duration: {historicalPosition.currentAgeDays} days.
              {" "}Compared with {historicalPosition.n} completed {historicalPosition.n === 1 ? "procurement" : "procurements"} in the same component category.
            </p>
            <p className="micro">
              Descriptive historical position only. It is not a prediction or a delay assessment.
            </p>
          </div>
        ) : null}
      </div>
    </section>

    {item.coverageNote ? <div className="notice scope"><strong>Coverage boundary:</strong> {item.coverageNote}</div> : null}

    <section className="section">
      <p className="small">Reproducibility</p>
      <div className="coverage-list">
        <div><strong>Read-model version</strong><p>{item.sourceVersion}</p></div>
      </div>
      <p className="micro">This view receives the validated customer-safe read object, never the raw TED/OpenCoesione response.</p>
    </section>

    <div className="actions">
      {publicMode
        ? <><Link className="button" href="/pricing">Find opportunities like this</Link><Link className="button secondary" href={`/demo/opportunities/${item.id}/history`}>View full history</Link><Link className="button secondary" href="/demo">Back to demo</Link></>
        : <><Link className="button secondary" href="/app">Back to opportunities</Link><Link className="button secondary" href={`/app/projects/${item.projectId}`}>Open project</Link></>}
    </div>
  </>;
}