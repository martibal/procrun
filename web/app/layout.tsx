import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "ProcRun — infrastructure procurement runway",
    template: "%s — ProcRun",
  },
  description:
    "Evidence-first infrastructure procurement runway for suppliers, with source-evidenced matches and explicitly TED-scoped absence conclusions.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
