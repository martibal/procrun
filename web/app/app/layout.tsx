import Link from "next/link";

const nav = [
  ["Runway", "/app"],
  ["Market", "/app/market"],
  ["Saved", "/app/saved"],
  ["Supplier profile", "/app/profile"],
  ["Account", "/app/account"],
] as const;

export default function AppLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="shell">
      <header className="topbar">
        <div className="topbar-inner">
          <Link href="/app" className="brand">ProcRun</Link>
          <div className="topmeta"><span className="status-dot" /> Fixture workspace · TED-scoped MVP</div>
          <nav className="nav"><Link href="/methodology">Methodology</Link><Link href="/pricing">Pricing</Link></nav>
        </div>
      </header>
      <div className="layout">
        <aside className="side">
          <div className="side-label">Workspace</div>
          {nav.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}
          <div className="side-footer">Customer-safe read model only<br />No raw source payloads</div>
        </aside>
        <main className="main">{children}</main>
      </div>
    </div>
  );
}
