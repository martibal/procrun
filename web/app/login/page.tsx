import Link from "next/link";
import { PublicPage } from "@/components/public-site";

export default function LoginPage() {
  return <PublicPage>
    <section className="page-hero narrow-copy">
      <div className="eyebrow">Customer account</div>
      <h1 className="h1 public-h1">Sign in to ProcRun.</h1>
      <p className="lede">Production authentication is not active in this development build. Account identity belongs to the customer control plane and is never an analytical input.</p>
    </section>
    <section className="public-section auth-wrap">
      <div className="card auth-card">
        <h2>Development access</h2>
        <p className="small">This page does not collect credentials yet. You can inspect the fixture workspace while the production authentication and subscription flow is being built.</p>
        <div className="actions"><Link className="button large" href="/app">Open demo workspace</Link><Link className="button secondary large" href="/pricing">View pricing</Link></div>
      </div>
    </section>
  </PublicPage>;
}
