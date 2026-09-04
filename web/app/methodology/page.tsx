export default function MethodologyPage() {
  return <>
    <div className="eyebrow">Methodology</div>
    <h1 className="h1">Evidence first. Coverage stated, not implied.</h1>
    <p className="lede">ProcRun separates source facts, matching evidence and derived conclusions so a customer can see exactly what supports each state.</p>
    <section className="card" style={{marginTop:24}}><h2>What OPEN means in the MVP</h2><p><strong>No relevant procurement found in TED as of DATE.</strong></p><p className="small">ProcRun in the MVP shows absence of a relevant match in TED. This is not a guarantee that no procurement exists outside TED, including purely national or below-threshold procedures.</p></section>
    <section className="card" style={{marginTop:16}}><h2>What we do not promise</h2><p className="small">No complete Portuguese procurement coverage. No complete bill of materials. No guaranteed future purchase. No win probability. No buyer-person intelligence. No source or EU endorsement.</p></section>
    <section className="card" style={{marginTop:16}}><h2>Source boundary</h2><p className="small">Browser, API and export surfaces consume only validated customer-safe read models. Raw source payloads never form part of the browser contract.</p></section>
  </>;
}
