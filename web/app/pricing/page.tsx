import Link from "next/link";
import { PublicPage } from "@/components/public-site";

export default function PricingPage() {
  return <PublicPage>
    <section className="page-hero">
      <div className="eyebrow">Pricing</div>
      <h1 className="h1 public-h1">One professional launch package.</h1>
      <p className="lede lede-large">ProcRun is designed as a paid supplier-intelligence product rather than a freemium tender directory. No permanent free tier is planned.</p>
    </section>

    <section className="public-section pricing-wrap">
      <div className="price-card">
        <div className="price-topline"><span>ProcRun Lombardia</span><span className="pill fixture">Launch package</span></div>
        <div className="price"><span className="currency">€</span>149<span className="period">/ month</span></div>
        <p className="lede">Professional procurement evidence for the current Lombardia source scope, with an explicit TED coverage boundary.</p>
        <div className="price-features">
          <div>Opportunity and procurement-runway workspace</div>
          <div>Project and component evidence detail</div>
          <div>Deterministic supplier relevance profile</div>
          <div>Saved opportunities</div>
          <div>TED procurement market context</div>
          <div>Customer-safe CSV export</div>
          <div>Methodology, source attribution and coverage disclosure</div>
        </div>
        <div className="notice scope"><strong>Checkout is not enabled in this development build.</strong> Authentication, billing, VAT/invoicing and final launch controls are being implemented in the customer web phase.</div>
        <button className="button disabled large full" disabled type="button">Checkout not yet enabled</button>
      </div>
      <aside className="pricing-aside">
        <h2>Before you subscribe</h2>
        <p>Current funded-project coverage is the approved OpenCoesione PR FESR Lombardia route.</p>
        <p>OPEN always means <strong>No relevant procurement found in TED as of the stated date.</strong> It does not establish absence outside TED.</p>
        <p>ProcRun does not promise every future purchase, national procurement completeness, a complete bill of materials or win probability.</p>
        <Link className="text-link strong" href="/methodology">Read methodology →</Link>
      </aside>
    </section>
  </PublicPage>;
}
