import type { Metadata } from "next";
import { BRANDING_DEFAULTS, LOGO_VARIANTS } from "@/config/branding";
import "./globals.css";

export const metadata: Metadata = process.env.GHM_UI === "preflight"
  ? { title: "GitHub Manager · Access preflight", description: "Local GitHub Manager Phase 0 access verification" }
  : { title: "GitHub Manager · Your work, organized", description: "Explore and organize your GitHub repositories with review-first AI.", icons: { icon: { url: LOGO_VARIANTS[BRANDING_DEFAULTS.variant].poster, type: "image/svg+xml" } } };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
