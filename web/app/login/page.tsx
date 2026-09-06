import Link from "next/link";
import { PublicPage } from "@/components/public-site";

export default function LoginPage() {
  return <PublicPage>
    <section className="page-hero narrow-copy">
      <p className="small">Customer account</p>
      <h1 className="h1 public-h1">Sign in to ProcRun.</h1>
      <p className="lede">Production authentication is not active in this development build. Account identity belongs to the customer control plane and is never an analytical input.</p>
    </section>
    <section className="public-section auth-wrap">
      <div className="card auth-card">
        <h2>Development access</h2>
        <p className="small">This page does not collect credentials yet. The next step in the defined first-login journey is Supplier Profile onboarding.</p>
        <div className="actions"><Link className="button large" href="/app/onboarding">Open onboarding shell</Link><Link className="button secondary large" href="/pricing">View pricing</Link></div>
      </div>
    </section>
  </PublicPage>;
}
