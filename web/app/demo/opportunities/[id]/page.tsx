import { notFound } from "next/navigation";
import { PublicPage } from "@/components/public-site";
import { OpportunityDetail } from "@/components/opportunity-detail";
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
      <p>Source: Tenders Electronic Daily (TED), Publications Office of the European Union. ProcRun transforms and classifies the source data; the derived analysis is not an official EU publication or endorsement.</p>
      <p>Source: OpenCoesione, Lista beneficiari e operazioni 2021-2027 (PR FESR Lombardia), used under CC BY 4.0. ProcRun transforms and classifies the source data; the derived analysis is not an official OpenCoesione, Italian-government or EU publication or endorsement.</p>
      <p>Dekningen reflekterer det italienske overvåkingssystemets nåværende fyllingsgrad for 2021–2027-perioden og vil vokse i takt med at flere prosjekter registreres nasjonalt.</p>
    </section>
  </PublicPage>;
}
