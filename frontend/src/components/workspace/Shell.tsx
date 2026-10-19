"use client";

import { SearchableSelect } from "./SearchableSelect";

import Link from "next/link";
import { useEffect, useRef, useState, type ReactNode } from "react";
import type { Identity } from "@/lib/api";
import type { Concept, ConceptCounts } from "@/lib/workspace";
import { Icon, ZenCat } from "./Icons";
import { TaxonomyBrowser } from "./TaxonomyBrowser";

type Navigate = (section: string, view?: string, concept?: string) => void;

export function WorkspaceShell({ identity, collection, section, view, activeConcept, concepts, counts, suggestions, syncDisabled, emptySamples, navigate, home, switchCollection, create, sync, loadSamples, assign, signOut, children }: {
  identity: Identity; collection: string; section: string; view: string; activeConcept: string; concepts: Concept[]; counts?: ConceptCounts; suggestions: number;
  syncDisabled: boolean; emptySamples: boolean; navigate: Navigate; switchCollection: (value: string) => void; create: () => void;
  sync: () => void; loadSamples: () => void; assign: (key: string, id: string) => void; signOut: () => void; home: () => void; children: ReactNode;
}) {
  const [drawer, setDrawer] = useState(false);
  const [mobile, setMobile] = useState(false);
  const drawerButton = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    const query = matchMedia("(max-width:760px)");
    const update = () => setMobile(query.matches);
    const timer = setTimeout(update, 0);
    query.addEventListener("change", update);
    return () => { clearTimeout(timer); query.removeEventListener("change", update); };
  }, []);
  const [menuOpen, setMenuOpen] = useState(false);
  const menu = useRef<HTMLDetailsElement>(null);
  const menuButton = useRef<HTMLElement>(null);
  const storageKey = `ghm-tree:${identity.user.id}:${collection}`;
  const choose = (id: string) => { navigate("repos", section === "repos" ? view : "all", id); setDrawer(false); if (menu.current) menu.current.open = false; };
  return <>
    <header className="wm-header">
      <button ref={drawerButton} className="wm-icon-button wm-drawer-toggle" aria-label={drawer ? "Close navigation" : "Open navigation"} aria-expanded={drawer} onClick={() => setDrawer(!drawer)}><Icon name="menu" /></button>
      <Link href="/" className="wm-brand" aria-label="GitHub Manager home" onClick={event => { event.preventDefault(); home(); setDrawer(false); }}><ZenCat /><span>GitHub Manager</span></Link>
      <label className="wm-header-workspace"><span>Workspace</span><SearchableSelect aria-label="Workspace collection" value={collection} onChange={value => switchCollection(value)} options={[({ value: "github", label: "My GitHub workspace" }), ({ value: "samples", label: "Public + synthetic demo" }), ({ value: "ground-truth", label: "Public - Ground Truth" })]} /></label>
      <nav className="wm-header-actions" aria-label="Workspace actions">
        <details className="wm-tree-menu" ref={menu} onToggle={e => setMenuOpen(e.currentTarget.open)} onKeyDown={e => { if (e.key === "Escape") { e.preventDefault(); if (menu.current) menu.current.open = false; menuButton.current?.focus(); } }}><summary ref={menuButton} aria-label="Browse taxonomy"><Icon name="domain" /><span>Browse taxonomy</span><Icon name="chevron" size={14} /></summary>{menuOpen && <div className="wm-tree-popover"><p>Browse or add memberships</p><TaxonomyBrowser concepts={concepts} counts={counts} assign={assign} active={activeConcept} choose={choose} storageKey={storageKey + ":header"} /></div>}</details>
        <button aria-label="AI Organization" className={`wm-action-ai ${section === "organizer" ? "wm-primary" : "wm-secondary"}`} onClick={() => navigate("organizer")}><Icon name="ai" /><span>AI Organization</span>{suggestions > 0 && <span className="wm-count">{suggestions}</span>}</button>
        <button aria-label="Content settings" className={`wm-action-content ${section === "content" ? "wm-primary" : "wm-secondary"}`} onClick={() => navigate("content")}><Icon name="settings" /><span>Content settings</span></button>
        <button className="wm-secondary wm-action-sync" aria-label={emptySamples ? "Load demo samples" : collection === "samples" ? "Sync samples" : "Sync GitHub"} disabled={syncDisabled} onClick={emptySamples ? loadSamples : sync}><Icon name={emptySamples ? "plus" : "sync"} /><span>{emptySamples ? "Load demo samples" : collection === "samples" ? "Sync samples" : "Sync GitHub"}</span></button>
      </nav>
      <details className="wm-account"><summary aria-label="Account menu"><span className="wm-avatar">{identity.user.login.slice(0, 2).toUpperCase()}</span></summary><div><strong>{identity.user.name || identity.user.login}</strong><small>@{identity.user.login} · Connected</small><button className="wm-secondary" aria-label="Sign out" onClick={signOut}><Icon name="logout" />Sign out</button></div></details>
    </header>
    {drawer && <button className="wm-drawer-scrim" aria-label="Close navigation overlay" onClick={() => setDrawer(false)} />}
    <aside className={`wm-sidebar ${drawer ? "is-open" : ""}`} aria-label="Repository navigation" inert={mobile && !drawer} aria-hidden={mobile && !drawer ? true : undefined} onKeyDown={e => { if (e.key === "Escape" && mobile) { setDrawer(false); drawerButton.current?.focus(); } }}>
      <details className="wm-collections" open><summary>Collections<Icon name="chevron" size={16} /></summary><nav aria-label="Repository collections">{[["my", "My Repos", "repos"], ["favorites", "Favorites", "star"], ["latest", "Latest Work", "clock"], ["uncategorized", "No project", "inbox"], ["all", collection === "samples" ? "Demo samples" : "Access candidates", "grid"]].map(([key, label, icon]) => <button key={key} className={`wm-nav ${section === "repos" && view === key && !activeConcept ? "is-active" : ""}`} onClick={() => { navigate("repos", key); setDrawer(false); }}><Icon name={icon} size={18} /><span>{label}</span></button>)}</nav></details>
      <div className="wm-nav-heading"><p className="wm-nav-label">Taxonomy</p><button aria-label="Add concept" className="wm-icon-button" onClick={create}><Icon name="plus" size={18} /></button></div>
      <nav className="wm-tree" aria-label="Domains and projects"><TaxonomyBrowser concepts={concepts} counts={counts} active={activeConcept} choose={choose} assign={assign} storageKey={storageKey} /></nav>
      <div className="wm-sidebar-status"><span className="wm-dot" /> Saved automatically</div>
    </aside>
    <main className="wm-main">{children}</main>
  </>;
}
