import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Ashwin Abhilash — AI/ML Engineer", description: "AI-aware developer portfolio powered by RepoMind." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
