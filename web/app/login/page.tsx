import Link from "next/link";
import { PublicPage } from "@/components/public-site";

export default function LoginPage() {
  return <PublicPage>
    <section className="page-hero narrow-copy auth-wrap">
      <p className="small">Customer account</p>
      <h1 className="public-h1">Sign in to ProcRun.</h1>
      <p className="lede-large">Account identity belongs to the customer control plane and is never used as analytical input.</p>
      <div className="auth-card section">
        <h2>Sign in is not configured.</h2>
        <p className="small">Production access stays closed until the selected authentication control-plane integration is configured. For local inspection, use the fixture workspace.</p>
        <div className="actions"><Link className="button" href="/app">Open demo workspace</Link><Link className="button secondary" href="/pricing">View pricing</Link></div>
      </div>
    </section>
  </PublicPage>;
}
