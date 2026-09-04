import Link from "next/link";

export default function PricingPage() {
  return <div className="public-shell">
    <div className="public-nav"><Link href="/" className="brand">ProcRun</Link><div className="nav"><Link href="/methodology">Methodology</Link><Link href="/app">Workspace</Link></div></div>
    <div className="eyebrow">Pricing</div>
    <h1 className="h1">One launch package.</h1>
    <p className="lede">Professional procurement evidence with an explicit coverage boundary. No permanent free tier is planned.</p>
    <div className="card section" style={{maxWidth:560}}><div className="small">ProcRun Portugal</div><div className="kpi">€149 / month</div><p className="small">TED-scoped opportunity feed, evidence detail, supplier profile, saved opportunities, market context and customer-safe CSV export.</p><div className="notice scope"><strong>Checkout disabled.</strong> Paid release still requires A19 and green CI. This fixture build is not accepting payment.</div><button className="button disabled" disabled type="button">Checkout not yet enabled</button></div>
  </div>;
}
