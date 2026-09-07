export default function AccountPage() {
  return <>
    <p className="small">Account</p>
    <h1 className="h1">Workspace and billing.</h1>
    <p className="lede">Control-plane account and billing data remain separate from ProcRun's intelligence plane.</p>
    <div className="coverage-list section">
      <div><strong>Plan</strong><p>ProcRun Lombardia, €149/month launch package.</p></div>
      <div><strong>Checkout</strong><p>Disabled until the web-phase launch gates are green.</p></div>
      <div><strong>Control-plane boundary</strong><p>Account and billing PII remain outside the intelligence plane.</p></div>
    </div>
  </>;
}
