export default function ProfilePage() {
  return <>
    <div className="eyebrow">Supplier profile</div>
    <h1 className="h1">Define the work you want ProcRun to prioritise.</h1>
    <p className="lede">Supplier relevance is deterministic. Profile choices can filter and order opportunities; they never change evidence state and are never presented as win probability.</p>

    <div className="notice safe"><strong>Onboarding shell.</strong> Persistence/auth wiring is intentionally disabled in this fixture build. No buyer-person or contact-person intelligence is collected.</div>

    <div className="formgrid">
      <div className="field"><strong>Infrastructure domains</strong><div className="checkset"><span className="check">Water & wastewater</span><span className="check">Rail & transport</span><span className="check">Ports & coastal</span><span className="check">Energy systems</span><span className="check">Resilience & fire</span></div></div>
      <div className="field"><strong>CPV families</strong><label className="small" htmlFor="cpv">Example category filter</label><select id="cpv" defaultValue="equipment"><option value="equipment">Equipment & systems</option><option value="works">Infrastructure works</option><option value="services">Technical services</option></select></div>
      <div className="field"><strong>Geography</strong><label className="small" htmlFor="geo">MVP relevance area</label><select id="geo" defaultValue="pt"><option value="pt">Portugal · TED-scoped procurement</option><option value="it">Italy · funded-project fixture only</option></select></div>
      <div className="field"><strong>Project value</strong><label className="small" htmlFor="value">Minimum project value</label><select id="value" defaultValue="1m"><option value="any">Any</option><option value="1m">€1m+</option><option value="5m">€5m+</option><option value="10m">€10m+</option></select></div>
    </div>

    <div className="actions"><button className="button disabled" type="button" disabled>Save profile after auth wiring</button></div>
  </>;
}
