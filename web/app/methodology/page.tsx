import Link from "next/link";

export default function MethodologyPage() {
  return <div className="public-shell">
    <div className="public-nav"><Link href="/" className="brand">ProcRun</Link><div className="nav"><Link href="/pricing">Pricing</Link><Link href="/app">Workspace</Link></div></div>
    <div className="eyebrow">Methodology</div>
    <h1 className="h1">Evidence first. Coverage stated, not implied.</h1>
    <p className="lede">ProcRun separates source facts, matching evidence and derived conclusions so the customer can inspect what supports each state.</p>
    <section className="card flat section"><h2 className="h2">What OPEN means in the MVP</h2><p><strong>No relevant procurement found in TED as of DATE.</strong></p><p className="small">This is not a guarantee that no procurement exists outside TED, including purely national or below-threshold procedures. Incomplete TED retrieval cannot produce OPEN.</p></section>
    <section className="card flat section"><h2 className="h2">What we do not promise</h2><p className="small">No complete Portuguese procurement coverage. No complete Italian public-investment coverage. No complete bill of materials. No guaranteed future purchase. No win probability. No buyer-person intelligence. No source or EU endorsement.</p></section>
    <section className="card flat section"><h2 className="h2">Source boundary</h2><p className="small">Browser, API and export surfaces consume only validated customer-safe read models. Raw TED or OpenCoesione responses never form part of the browser contract.</p></section>
    <section className="card flat section"><h2 className="h2">OpenCoesione expansion boundary</h2><p className="small">The approved funded-project source contract is limited to the 2021–2027 EU-cohesion operation-list publication. Italian funded-project data remains non-live in the customer interface until transfer/end-to-end acceptance is green.</p></section>
  </div>;
}
