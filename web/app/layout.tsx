import type { Metadata } from "next";
import { IBM_Plex_Mono, Piazzolla, Public_Sans } from "next/font/google";
import "./globals.css";

const piazzolla = Piazzolla({
  subsets: ["latin"],
  variable: "--font-piazzolla",
  display: "swap",
});

const publicSans = Public_Sans({
  subsets: ["latin"],
  variable: "--font-public-sans",
  display: "swap",
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-ibm-plex-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "ProcRun — Infrastructure procurement intelligence",
    template: "%s | ProcRun",
  },
  description: "Evidence-first infrastructure procurement intelligence for suppliers in Lombardia.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${piazzolla.variable} ${publicSans.variable} ${ibmPlexMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
