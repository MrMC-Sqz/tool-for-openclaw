import "./globals.css";

import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "OpenClaw Skill Explorer + Risk Scanner",
  description: "MVP foundation for discovering and evaluating OpenClaw skills.",
};

type RootLayoutProps = {
  children: ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          <header className="border-b border-slate-200 bg-white">
            <nav className="mx-auto flex w-full max-w-6xl items-center justify-between px-4 py-3">
              <Link href="/" className="text-sm font-semibold text-slate-900">
                OpenClaw Skill Explorer
              </Link>
              <div className="flex items-center gap-4 text-sm">
                <Link href="/skills" className="text-slate-700 hover:text-slate-900">
                  Skills
                </Link>
                <Link href="/scan" className="text-slate-700 hover:text-slate-900">
                  Manual Scan
                </Link>
              </div>
            </nav>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
