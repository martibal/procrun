import { notFound } from "next/navigation";
import { PublicPage } from "@/components/public-site";
import { OpportunityDetail } from "@/components/opportunity-detail";
import { DATA_COMPLETENESS_DISCLOSURE, OPENCOESIONE_ATTRIBUTION, TED_ATTRIBUTION } from "@/lib/public-copy";
import { getPublicShowcaseOpportunity } from "@/lib/public-showcase";

export default async function PublicOpportunityPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const item = getPublicShowcaseOpportunity(id);
  if (!item) notFound();

  return <PublicPage>
    <section className="page-hero narrow-copy">
      <OpportunityDetail item={item} publicMode />
    </section>

    <section className="public-section legal-copy">
      <h2>Source attribution</h2>
      <p>{TED_ATTRIBUTION}</p>
      <p>{OPENCOESIONE_ATTRIBUTION}</p>
      <p>{DATA_COMPLETENESS_DISCLOSURE}</p>
    </section>
  </PublicPage>;
}
