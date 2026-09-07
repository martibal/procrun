import Link from "next/link";
import { PublicPage } from "@/components/public-site";

export default function PricingPage() {
  return <PublicPage>
    <section className="page-hero">
      <p className="small">Pricing</p>
      <h1 className="h1 public-h1">One professional launch package.</h1>
      <p className="lede lede-large">ProcRun is designed as a paid supplier-intelligence product rather than a freemium tender directory. No permanent free tier is planned.</p>
    </section>

    <section className="public-section pricing-wrap">
      <div>
        <div className="price-topline"><span>ProcRun Lombardia</span><span className="pill fixture">Launch package</span></div>
        <div className="price"><span className="currency">€</span>149<span className="period">/ month</span></div>
        <p className="lede">Professional procurement evidence for the current Lombardia source scope, with an explicit TED coverage boundary.</p>
        <div className="price-features">
          <div>Full opportunity corpus as it is processed</div>
          <div>Full customer-safe evidence detail for every accessible record</div>
          <div>Deterministic supplier relevance profile</div>
          <div>Filtering and search across the corpus</div>
          <div>Saved opportunities</div>
          <div>Market Intelligence</div>
          <div>Customer-safe CSV export</div>
        </div>
        <div className="notice scope"><strong>Checkout is not enabled in this development build.</strong> Authentication, billing, VAT/invoicing and final launch controls remain launch gates.</div>
        <div className="actions"><button className="button disabled large" disabled type="button">Checkout not yet enabled</button><Link className="button secondary" href="/login">Sign in</Link></div>
      </div>
      <aside className="pricing-aside">
        <h2>Before you subscribe</h2>
        <p>Current funded-project coverage is the approved OpenCoesione PR FESR Lombardia route.</p>
        <p>OPEN always means <strong>No relevant procurement found in TED as of the stated date.</strong> It does not establish absence outside TED.</p>
        <p>ProcRun does not charge to reveal hidden evidence on a public record. The paid service expands corpus breadth, supplier matching, filtering and workflow.</p>
        <p>ProcRun does not promise every future purchase, national procurement completeness, a complete bill of materials or win probability.</p>
        <Link className="text-link strong" href="/methodology">Read methodology</Link>
      </aside>
    </section>
  </PublicPage>;
}
