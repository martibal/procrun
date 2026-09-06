import Link from "next/link";

export default function OnboardingPage() {
  return <>
    <p className="small">Supplier Profile onboarding</p>
    <h1 className="h1">Tell ProcRun what your company supplies.</h1>
    <p className="lede">These choices determine relevance and filtering only. They never change source evidence, procurement state or the customer-safe data boundary.</p>

    <div className="notice safe"><strong>Development shell.</strong> Persistence and authentication wiring are not active yet. No named employee, personal email or phone number is requested here.</div>

    <div className="formgrid">
      <div className="field"><strong>Company name</strong><label className="small" htmlFor="company">Company or organisation</label><input id="company" type="text" placeholder="Company name" /></div>
      <div className="field"><strong>Target market</strong><label className="small" htmlFor="market">Launch geography</label><select id="market" defaultValue="lombardia"><option value="lombardia">Lombardia</option></select></div>
      <div className="field"><strong>Product categories</strong><div className="checkset"><span className="check">Equipment</span><span className="check">Systems</span><span className="check">Infrastructure works</span><span className="check">Technical services</span></div></div>
      <div className="field"><strong>CPV inclusions</strong><label className="small" htmlFor="cpv-in">Optional CPV codes or families</label><input id="cpv-in" type="text" placeholder="Optional" /></div>
      <div className="field"><strong>CPV exclusions</strong><label className="small" htmlFor="cpv-out">Optional CPV codes or families</label><input id="cpv-out" type="text" placeholder="Optional" /></div>
      <div className="field"><strong>Project value</strong><label className="small" htmlFor="value">Optional preferred value range</label><select id="value" defaultValue="any"><option value="any">Any value</option><option value="under-1m">Under €1m</option><option value="1m-5m">€1m–€5m</option><option value="5m-plus">€5m+</option></select></div>
    </div>

    <div className="actions"><Link className="button" href="/app">Continue to Opportunities</Link><Link className="button secondary" href="/app/profile">Open Supplier Profile</Link></div>
  </>;
}
