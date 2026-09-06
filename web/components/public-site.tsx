import Link from "next/link";

const publicLinks = [
  ["Demo", "/app"],
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
          <p className="small footer-copy">Evidence-first infrastructure procurement intelligence for suppliers.</p>
        </div>
        <div>
          <div className="footer-label">Product</div>
          <Link href="/app">Demo</Link>
          <Link href="/methodology">Methodology & coverage</Link>
          <Link href="/pricing">Pricing</Link>
          <Link href="/faq">FAQ</Link>
        </div>
        <div>
          <div className="footer-label">Account</div>
          <Link href="/login">Sign in</Link>
        </div>
        <div>
          <div className="footer-label">Legal</div>
          <Link href="/terms">Terms</Link>
          <Link href="/privacy">Privacy</Link>
        </div>
      </div>
      <div className="footer-bottom">
        <span>ProcRun transforms public source data into derived analysis.</span>
        <span>No source, government body or EU institution endorses ProcRun.</span>
      </div>
    </footer>
  );
}

export function PublicPage({ children }: { children: React.ReactNode }) {
  return <><PublicHeader /><main className="public-shell">{children}</main><PublicFooter /></>;
}
