import Link from "next/link";
import { PublicPage } from "@/components/public-site";
import { opportunities } from "@/lib/read-model";

export default function DemoPage() {
  const real = opportunities.filter((item) => !item.isFixture);

  return <PublicPage>
    <section className="page-hero">
      <p className="small">Demo</p>
      <h1 className="h1 public-h1">See a real Lombardia opportunity and the evidence behind it.</h1>
      <p className="lede lede-large">This public demo uses customer-safe production records only. No synthetic opportunity is presented as real data.</p>
    </section>

    <section className="public-section">
      {real.length === 0 ? <div className="notice scope">No customer-safe production opportunity is currently available for the public demo.</div> : real.map((item) => (
        <article className="card flat" key={item.id}>
          <p className="small">{item.geography}</p>
          <h2 className="h2">{item.projectTitle}</h2>
          <p><strong>Demand identified:</strong> {item.component}</p>
          <p className="evidence">{item.projectEvidence}</p>
          <p className="small">{item.openWording ?? item.procurementEvidence ?? "Insufficient evidence for a safe conclusion."}</p>
          <details style={{marginTop:16}}>
            <summary>Show evidence detail</summary>
            <p className="small"><strong>Operation code:</strong> {item.projectId}</p>
            <p className="small"><strong>Approved funding:</strong> {item.valueEur ? `€${item.valueEur.toLocaleString("en-GB")}` : "Unavailable"}</p>
            <p className="small"><strong>Coverage:</strong> {item.coverage}</p>
            <p className="small"><strong>Cutoff:</strong> {item.cutoffDate}</p>
            <p className="small">{item.coverageNote}</p>
          </details>
        </article>
      ))}
    </section>

    <section className="public-section legal-copy">
      <h2>Source attribution</h2>
      <p>Source: Tenders Electronic Daily (TED), Publications Office of the European Union. ProcRun transforms and classifies the source data; the derived analysis is not an official EU publication or endorsement.</p>
      <p>Source: OpenCoesione, Lista beneficiari e operazioni 2021-2027 (PR FESR Lombardia), used under CC BY 4.0. ProcRun transforms and classifies the source data; the derived analysis is not an official OpenCoesione, Italian-government or EU publication or endorsement.</p>
      <p>Dekningen reflekterer det italienske overvåkingssystemets nåværende fyllingsgrad for 2021–2027-perioden og vil vokse i takt med at flere prosjekter registreres nasjonalt.</p>
      <div className="actions"><Link className="button" href="/pricing">View pricing</Link><Link className="button secondary" href="/login">Sign in</Link></div>
    </section>
  </PublicPage>;
}
