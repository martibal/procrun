import Link from "next/link";

export default function LoginPage() {
  return <>
    <div className="eyebrow">Authentication shell</div>
    <h1 className="h1">Sign in to ProcRun.</h1>
    <p className="lede">Authentication provider wiring is intentionally not activated in this build slice. Account identity belongs to the control plane and is never analytical input.</p>
    <div className="card" style={{maxWidth:520, marginTop:24}}><p className="small">Development shell only. No credentials are collected by this fixture page.</p><Link className="button" href="/app">Open fixture workspace</Link></div>
  </>;
}
