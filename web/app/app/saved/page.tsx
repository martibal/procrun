import Link from "next/link";
import { OpportunityList } from "@/components/opportunity-list";
import { opportunities } from "@/lib/read-model";

export default function SavedPage() {
  const saved = opportunities.slice(0, 2);
  return <>
    <div className="eyebrow">Saved</div>
    <h1 className="h1">Keep the evidence you want to revisit.</h1>
    <p className="lede">Saved items remain references to customer-safe read-model objects; they never persist raw source responses.</p>
    <Link className="button" href="/api/export">Export customer-safe CSV</Link>
    <OpportunityList items={saved} />
  </>;
}
