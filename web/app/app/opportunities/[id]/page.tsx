import { notFound } from "next/navigation";
import { OpportunityDetail } from "@/components/opportunity-detail";
import { getOpportunity } from "@/lib/read-model";

export default async function OpportunityPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const item = getOpportunity(id);
  if (!item) notFound();

  return <OpportunityDetail item={item} />;
}
