import { OpportunityList } from "@/components/opportunity-list";
import { opportunities } from "@/lib/read-model";

export default function SavedPage() {
  const saved = opportunities.slice(0, 2);
  return <>
    <div className="eyebrow">Saved opportunities</div>
    <h1 className="h1">Keep evidence-bearing opportunities in one review queue.</h1>
    <p className="lede">Saved state is a workspace convenience only. It never changes ProcRun evidence classification or supplier relevance.</p>
    <div className="notice"><strong>Fixture workspace.</strong> Saved items are deterministic fixture selections until account persistence is connected.</div>
    <OpportunityList items={saved} />
  </>;
}
