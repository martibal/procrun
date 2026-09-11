import type { Metadata } from "next";
import "./globals.css";
import "./launch-web.css";

export const metadata: Metadata = {
  title: {
    default: "ProcRun — funded-project procurement evidence",
    template: "%s — ProcRun",
  },
  description:
    "Evidence-bounded funded-project procurement intelligence with exact source wording, TED procurement evidence and explicit OPEN/CLOSED/UNRESOLVED interpretation.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
