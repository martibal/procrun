import { PublicPage } from "@/components/public-site";

export default function PricingPage() {
  return <PublicPage>
    <section className="page-hero narrow-copy">
      <p className="small">Pricing</p>
      <h1 className="public-h1">One professional launch package.</h1>
      <p className="lede-large">ProcRun is intended for business and professional use and is planned at €149/month for the launch product. Payment remains disabled until merchant disclosures, tax/invoicing terms, domain/TLS and the final customer control plane are complete.</p>
    </section>

    <section className="public-section pricing-wrap">
      <div className="price-card">
        <div className="price-topline"><span>ProcRun</span><span>Business launch package</span></div>
        <div className="price"><span className="currency">€</span>149<span className="period">/ month</span></div>
        <div className="price-features">
          <div>Evidence-bounded funded-project runway</div>
          <div>Permitted source evidence kept separate from derived state</div>
          <div>TED procurement evidence</div>
          <div>Supplier workspace and saved opportunities</div>
          <div>Customer-safe export surfaces</div>
        </div>
        <div className="notice scope"><strong>Checkout remains disabled.</strong> This price is pre-launch information, not an offer that can currently be accepted. No paid contract is formed through this build.</div>
      </div>
      <aside className="pricing-aside">
        <h2>What the subscription does not change</h2>
        <p>OPEN remains a TED-bounded conclusion under the frozen exact-evidence rules.</p>
        <p>Source wording is shown only where the applicable reuse basis permits commercial republication; restricted sources expose structured facts, citations and official links instead.</p>
        <p>A paid subscription never expands these boundaries into legal advice, an eligibility verdict or a claim that procurement is absent outside TED.</p>
      </aside>
    </section>
  </PublicPage>;
}
