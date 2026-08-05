import "./globals.css";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Mintic.AI - Autonomous Trading System",
  description: "Multi-agent trade deliberation with unbendable safety lock risk enforcement",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-slate-950 text-slate-100">{children}</body>
    </html>
  );
}
