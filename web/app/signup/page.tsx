import { SignUp } from "@clerk/nextjs";
import Link from "next/link";

import { PublicPage } from "@/components/public-site";

export default function SignUpPage() {
  const configured = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY?.trim());

  return (
    <PublicPage>
      <section className="page-hero narrow-copy">
        <p className="small">Customer account</p>
        <h1 className="h1 public-h1">Create your ProcRun account.</h1>
        <p className="lede">
          Account identity is handled in the customer control plane and is never used as an analytical input.
        </p>
      </section>
      <section className="public-section auth-wrap">
        {configured ? (
          <SignUp routing="path" path="/signup" signInUrl="/login" />
        ) : (
          <div className="card auth-card">
            <h2>Registration is not configured.</h2>
            <p className="small">Production registration stays unavailable until the Clerk control-plane keys are configured.</p>
            <div className="actions">
              <Link className="button secondary large" href="/login">Sign in</Link>
              <Link className="button secondary large" href="/pricing">View pricing</Link>
            </div>
          </div>
        )}
      </section>
    </PublicPage>
  );
}
