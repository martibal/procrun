import { PublicPage } from "@/components/public-site";

export default function PricingPage() {
  return <PublicPage>
    <section className="page-hero narrow-copy">
      <p className="small">Pricing</p>
      <h1 className="public-h1">One professional launch package.</h1>
      <p className="lede-large">ProcRun is priced at €149/month for the launch product. Pricing is fixed; payment remains intentionally disabled until merchant, tax, invoicing, domain/TLS and final control-plane integrations are complete.</p>
    </section>

    <section className="public-section pricing-wrap">
      <div className="price-card">
        <div className="price-topline"><span>ProcRun</span><span>Launch package</span></div>
        <div className="price"><span className="currency">€</span>149<span className="period">/ month</span></div>
        <div className="price-features">
          <div>Evidence-bounded funded-project runway</div>
          <div>Exact project wording and derived state shown separately</div>
          <div>TED procurement evidence</div>
          <div>Supplier workspace and saved opportunities</div>
          <div>Customer-safe export surfaces</div>
        </div>
        <div className="notice scope"><strong>Checkout remains disabled.</strong> No payment is accepted from this build. Activation is a separate launch-integration step and does not change the evidence rules described on this site.</div>
      </div>
      <aside className="pricing-aside">
        <h2>What the subscription does not change</h2>
        <p>OPEN remains a TED-bounded conclusion under the frozen exact-evidence rules.</p>
        <p>A paid subscription never expands that state into a claim that procurement is absent outside TED or under different wording, classification or procurement routes.</p>
      </aside>
    </section>
  </PublicPage>;
}
