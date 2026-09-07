import { notFound } from "next/navigation";
import { OpportunityDetail } from "@/components/opportunity-detail";
import { loadOpenCategoryPercentile } from "@/lib/category-baselines";
import { getOpportunity } from "@/lib/read-model";

export const dynamic = "force-dynamic";

export default async function OpportunityPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const item = getOpportunity(id);
  if (!item) notFound();

  const historicalPosition = item.state === "OPEN"
    ? await loadOpenCategoryPercentile(item.componentId, item.cutoffDate)
    : null;

  return (
    <OpportunityDetail
      item={item}
      historicalPosition={historicalPosition}
    />
  );
}