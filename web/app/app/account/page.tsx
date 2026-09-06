export default function AccountPage() {
  return <>
    <p className="small">Account</p>
    <h1 className="h1">Workspace and billing.</h1>
    <p className="lede">Control-plane account and billing data remain separate from ProcRun's intelligence plane.</p>
    <div className="grid">
      <div className="card"><div className="small">Plan</div><div className="kpi" style={{fontSize:22}}>ProcRun Lombardia</div><p className="small">€149/month launch package</p></div>
      <div className="card"><div className="small">Checkout</div><div className="kpi" style={{fontSize:22}}>Disabled</div><p className="small">Remains disabled until the web-phase launch gates are green.</p></div>
      <div className="card"><div className="small">Data plane</div><div className="kpi" style={{fontSize:22}}>Separated</div><p className="small">Account PII never enters analytical context.</p></div>
    </div>
  </>;
}
