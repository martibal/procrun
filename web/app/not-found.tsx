import Link from "next/link";
import { PublicPage } from "@/components/public-site";

export default function NotFoundPage() {
  return (
    <PublicPage>
      <section className="page-hero narrow-copy">
        <p className="small">404</p>
        <h1 className="h1 public-h1">Page not found.</h1>
        <p className="lede">The page may have moved, or the address may be incorrect.</p>
        <div className="actions">
          <Link className="button" href="/">Go to Home</Link>
          <Link className="button secondary" href="/demo">Open demo</Link>
        </div>
      </section>
    </PublicPage>
  );
}
