import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "ProcRun",
  description: "Evidence-first procurement intelligence",
};

const nav = [
  ["Runway", "/app"],
  ["Market", "/app/market"],
  ["Saved", "/app/saved"],
  ["Profile", "/app/profile"],
  ["Account", "/app/account"],
  ["Methodology", "/methodology"],
] as const;

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <header className="topbar">
            <Link href="/app" className="brand">ProcRun</Link>
            <nav className="nav"><Link href="/methodology">Methodology</Link><Link href="/pricing">Pricing</Link></nav>
          </header>
          <div className="layout">
            <aside className="side">
              {nav.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}
            </aside>
            <main className="main">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
