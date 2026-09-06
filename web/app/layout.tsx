import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "ProcRun — Infrastructure procurement intelligence",
    template: "%s | ProcRun",
  },
  description: "Evidence-first infrastructure procurement intelligence for suppliers. See funded-project scope, procurement evidence and remaining TED-scoped runway.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
