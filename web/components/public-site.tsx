import Link from "next/link";
import { OPENCOESIONE_ATTRIBUTION, TED_ATTRIBUTION } from "@/lib/source-attribution";

const publicLinks = [
  ["Methodology", "/methodology"],
  ["Pricing", "/pricing"],
] as const;

export function PublicHeader() {
  return (
    <header className="public-header">
      <div className="public-header-inner">
        <Link href="/" className="brand" aria-label="ProcRun home">ProcRun</Link>
        <nav className="public-nav-links" aria-label="Primary navigation">
          {publicLinks.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}
        </nav>
        <div className="public-nav-actions">
          <Link href="/login" className="text-link">Sign in</Link>
          <Link href="/app" className="button compact">Open demo</Link>
        </div>
      </div>
    </header>
  );
}

export function PublicFooter() {
  return (
    <footer className="public-footer">
      <div className="public-footer-grid">
        <div>
          <Link href="/" className="brand">ProcRun</Link>
          <p className="small footer-copy">Evidence-bounded procurement intelligence for business and professional use.</p>
        </div>
        <div>
          <div className="footer-label">Explore</div>
          <Link href="/methodology">Methodology & coverage</Link>
          <Link href="/pricing">Pricing</Link>
        </div>
        <div>
          <div className="footer-label">Sources</div>
          <a href={OPENCOESIONE_ATTRIBUTION.licenceUrl} target="_blank" rel="noreferrer">OpenCoesione · {OPENCOESIONE_ATTRIBUTION.licence}</a>
          <a href={TED_ATTRIBUTION.licenceUrl} target="_blank" rel="noreferrer">TED · reuse terms</a>
        </div>
        <div>
          <div className="footer-label">Legal</div>
          <Link href="/terms">Terms</Link>
          <Link href="/privacy">Privacy</Link>
        </div>
      </div>
      <div className="footer-bottom">
        <span>{OPENCOESIONE_ATTRIBUTION.note}</span>
        <span>{TED_ATTRIBUTION.note}</span>
        <span>Paid checkout remains disabled until mandatory merchant disclosures are configured.</span>
      </div>
    </footer>
  );
}

export function PublicPage({ children }: { children: React.ReactNode }) {
  return <><PublicHeader /><main className="public-shell">{children}</main><PublicFooter /></>;
}
