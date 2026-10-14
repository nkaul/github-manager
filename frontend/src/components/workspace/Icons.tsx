"use client";

import { useEffect, type ReactNode } from "react";
import Image from "next/image";
import { LOGO_VARIANTS } from "@/config/branding";
import { useLogoPreferences } from "@/lib/branding";

const paths: Record<string, ReactNode> = {
  repos: <><rect x="4" y="3" width="16" height="18" rx="3" /><path d="M8 3v18M12 8h4M12 12h4" /></>,
  star: <path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9Z" />,
  clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
  inbox: <><path d="m4 5-2 10v4h20v-4L20 5Z" /><path d="M2 15h6l2 3h4l2-3h6" /></>,
  grid: <><rect x="3" y="3" width="7" height="7" rx="2" /><rect x="14" y="3" width="7" height="7" rx="2" /><rect x="3" y="14" width="7" height="7" rx="2" /><rect x="14" y="14" width="7" height="7" rx="2" /></>,
  folder: <path d="M3 7V5a2 2 0 0 1 2-2h5l2 3h7a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z" />,
  topic: <><circle cx="12" cy="12" r="8" /><path d="M8 9h8M8 12h8M8 15h5" /></>,
  tag: <><path d="M3 4h8l10 10-7 7L3 10Z" /><circle cx="7.5" cy="7.5" r="1" /></>,
  domain: <><rect x="8" y="3" width="8" height="6" rx="2" /><rect x="2" y="16" width="8" height="5" rx="2" /><rect x="14" y="16" width="8" height="5" rx="2" /><path d="M12 9v4M6 16v-3h12v3" /></>,
  chevron: <path d="m9 5 7 7-7 7" />,
  search: <><circle cx="10.5" cy="10.5" r="6.5" /><path d="m16 16 5 5" /></>,
  filter: <><path d="M4 7h16M7 12h10M10 17h4" /></>,
  sync: <><path d="M20 8a8 8 0 0 0-14-3L3 8m0-5v5h5M4 16a8 8 0 0 0 14 3l3-3m0 5v-5h-5" /></>,
  ai: <><path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5ZM20 2v4M18 4h4" /></>,
  settings: <><path d="m9 3-1 3-3 1-2 4 2 2v4l4 2 3-1 3 1 4-2v-4l2-2-2-4-3-1-1-3Z" /><circle cx="12" cy="12" r="3" /></>,
  plus: <path d="M12 5v14M5 12h14" />,
  external: <><path d="M14 3h7v7M21 3 10 14M10 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-5" /></>,
  close: <path d="m6 6 12 12M6 18 18 6" />,
  logout: <><path d="M10 3H4v18h6M14 7l5 5-5 5M8 12h11" /></>,
  menu: <path d="M4 6h16M4 12h16M4 18h16" />,
  checklist: <><rect x="4" y="3" width="16" height="18" rx="3" /><path d="m8 9 2 2 4-4M8 16h8" /></>,
  review: <><path d="M4 4h16v12H9l-5 4Z" /><path d="M8 8h8M8 12h5" /></>,
  selected: <><rect x="3" y="3" width="18" height="18" rx="5" /><path d="m7 12 3 3 7-7" /></>,
  check: <path d="m5 12 4 4L19 6" />,
  lock: <><rect x="5" y="10" width="14" height="11" rx="3" /><path d="M8 10V7a4 4 0 0 1 8 0v3" /></>,
};

export function Icon({ name, size = 20 }: { name: string; size?: number }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">{paths[name] || paths.folder}</svg>;
}

/** Selected Zen Loop GIF with a static source for reduced motion or paused animation. */
export function ZenCat() {
  const preferences = useLogoPreferences();
  const logo = LOGO_VARIANTS[preferences.variant];
  useEffect(() => {
    for (const icon of document.querySelectorAll<HTMLLinkElement>('link[rel~="icon"]')) {
      icon.href = logo.poster;
      icon.type = "image/svg+xml";
    }
  }, [logo.poster]);
  return <span className="wm-logo" data-logo={preferences.variant} data-animated={preferences.animate} aria-hidden="true">
    <picture><source media="(prefers-reduced-motion: reduce)" srcSet={logo.poster} />
      <Image className="wm-zen-cat" src={preferences.animate ? logo.animation : logo.poster} alt="" width={96} height={96} unoptimized loading="eager" draggable={false} />
    </picture>
  </span>;
}
