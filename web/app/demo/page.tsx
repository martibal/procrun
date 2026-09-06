import Link from "next/link";
import { PublicPage } from "@/components/public-site";
import { DATA_COMPLETENESS_DISCLOSURE, OPENCOESIONE_ATTRIBUTION, TED_ATTRIBUTION } from "@/lib/public-copy";
import { getPublicShowcaseOpportunities } from "@/lib/public-showcase";

export default function DemoPage() {
  const showcase = getPublicShowcaseOpportunities();

  return <PublicPage>
    <section className="page-hero">
      <p className="small">Demo</p>
      <h1 className="h1 public-h1">See a real Lombardia opportunity and the evidence behind it.</h1>
      <p className="lede lede-large">This public showcase is intentionally limited in breadth. Every opportunity shown here exposes the full customer-safe evidence detail for that record.</p>
    </section>

    <section className="public-section">
      {showcase.length === 0 ? <div className="notice scope">No approved customer-safe opportunity is currently in the public showcase.</div> : showcase.map((item) => (
        <article className="card flat" key={item.id}>
          <p className="small">{item.geography}</p>
          <h2 className="h2">{item.projectTitle}</h2>
          <p><strong>Demand identified:</strong> {item.component}</p>
          <p className="evidence">{item.projectEvidence}</p>
          <p className="small">{item.openWording ?? item.procurementEvidence ?? "Insufficient evidence for a safe conclusion."}</p>
          <div className="actions">
            <Link className="button" href={`/demo/opportunities/${item.id}`}>View full evidence</Link>
          </div>
        </article>
      ))}
    </section>

    <section className="public-section legal-copy">
      <h2>Source attribution</h2>
      <p>{TED_ATTRIBUTION}</p>
      <p>{OPENCOESIONE_ATTRIBUTION}</p>
      <p>{DATA_COMPLETENESS_DISCLOSURE}</p>
      <p className="small">The paid service expands access to the opportunity corpus, supplier-profile matching, filtering and workflow. It does not unlock hidden evidence on the individual records shown here.</p>
      <div className="actions"><Link className="button" href="/pricing">View pricing</Link><Link className="button secondary" href="/login">Sign in</Link></div>
    </section>
  </PublicPage>;
}
