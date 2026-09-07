import { OpportunityList } from "@/components/opportunity-list";
import { getOpportunityByComponentId, opportunities } from "@/lib/read-model";

export default async function SavedPage({ searchParams }: { searchParams: Promise<{ changed?: string }> }) {
  const { changed } = await searchParams;
  const saved = opportunities.slice(0, 2);
  const changedOpportunity = changed ? getOpportunityByComponentId(changed) : undefined;
  return <>
    <p className="small">Saved opportunities</p>
    <h1 className="h1">Keep evidence-bearing opportunities in one review queue.</h1>
    <p className="lede">Saved state is a workspace convenience only. It never changes ProcRun evidence classification or supplier relevance.</p>
    {changed ? (
      <p className="small">
        <strong>Status changed since your previous summary:</strong>{" "}
        {changedOpportunity ? `${changedOpportunity.projectTitle} — ${changedOpportunity.component}` : changed}
      </p>
    ) : null}
    <div className="notice"><strong>Development workspace.</strong> Saved items are deterministic fixture selections until account persistence is connected.</div>
    <OpportunityList items={saved} />
  </>;
}
