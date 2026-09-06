export default function ProfilePage() {
  return <>
    <p className="small">Supplier Profile</p>
    <h1 className="h1">Define the work you want ProcRun to prioritise.</h1>
    <p className="lede">Supplier relevance is deterministic. Profile choices can filter and order opportunities; they never change evidence state and are never presented as win probability.</p>

    <div className="notice safe"><strong>Development shell.</strong> Persistence/auth wiring is intentionally disabled in this build. No named employee, personal email or phone number is required for the Supplier Profile.</div>

    <div className="formgrid">
      <div className="field"><strong>Product categories</strong><div className="checkset"><span className="check">Equipment</span><span className="check">Systems</span><span className="check">Infrastructure works</span><span className="check">Technical services</span></div></div>
      <div className="field"><strong>CPV families</strong><label className="small" htmlFor="cpv">Optional category filter</label><select id="cpv" defaultValue="equipment"><option value="equipment">Equipment & systems</option><option value="works">Infrastructure works</option><option value="services">Technical services</option></select></div>
      <div className="field"><strong>Geography</strong><label className="small" htmlFor="geo">Launch market</label><select id="geo" defaultValue="lombardia"><option value="lombardia">Lombardia</option></select></div>
      <div className="field"><strong>Project value</strong><label className="small" htmlFor="value">Optional preferred value range</label><select id="value" defaultValue="any"><option value="any">Any</option><option value="1m">€1m+</option><option value="5m">€5m+</option><option value="10m">€10m+</option></select></div>
    </div>

    <div className="actions"><button className="button disabled" type="button" disabled>Save profile after auth wiring</button></div>
  </>;
}
