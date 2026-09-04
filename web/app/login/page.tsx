import Link from "next/link";

export default function LoginPage() {
  return <div className="public-shell">
    <div className="public-nav"><Link href="/" className="brand">ProcRun</Link><div className="nav"><Link href="/methodology">Methodology</Link><Link href="/pricing">Pricing</Link></div></div>
    <div className="eyebrow">Authentication shell</div>
    <h1 className="h1">Sign in to ProcRun.</h1>
    <p className="lede">Authentication wiring is intentionally not activated in this build slice. Account identity belongs to the control plane and is never analytical input.</p>
    <div className="card section" style={{maxWidth:540}}><p className="small">Development shell only. This page collects no credentials.</p><Link className="button" href="/app">Open fixture workspace</Link></div>
  </div>;
}
