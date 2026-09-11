import Link from "next/link";

const primaryNav = [
  ["Opportunities", "/app"],
  ["Saved", "/app/saved"],
  ["Market", "/app/market"],
] as const;

const accountNav = [
  ["Supplier Profile", "/app/profile"],
  ["Account", "/app/account"],
] as const;

export default function AppLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="shell">
      <header className="topbar">
        <div className="topbar-inner" style={{ paddingRight: 40 }}>
          <Link href="/app" className="brand">ProcRun</Link>
          <nav className="workspace-nav" aria-label="Workspace navigation">
            {primaryNav.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}
          </nav>
          <nav className="workspace-nav secondary" aria-label="Account navigation" style={{ paddingRight: 4 }}>
            {accountNav.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}
          </nav>
        </div>
      </header>
      <div className="layout">
        <main className="main">{children}</main>
      </div>
    </div>
  );
}
