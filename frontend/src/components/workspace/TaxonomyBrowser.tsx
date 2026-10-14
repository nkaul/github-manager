"use client";

import { useEffect, useState, type DragEvent } from "react";
import type { Concept, ConceptCounts } from "@/lib/workspace";
import { Icon } from "./Icons";

export function TaxonomyBrowser({ concepts, counts = {}, active, choose, assign, storageKey }: {
  concepts: Concept[]; counts?: ConceptCounts; active: string; choose: (id: string) => void;
  assign: (payload: string, id: string) => void; storageKey: string;
}) {
  const [mode, setMode] = useState("PROJECT");
  const [query, setQuery] = useState("");
  const [collapsed, setCollapsed] = useState<string[]>([]);
  const [over, setOver] = useState("");
  useEffect(() => {
    const timer = setTimeout(() => { try { setCollapsed(JSON.parse(localStorage.getItem(storageKey) || "[]")); } catch { setCollapsed([]); } }, 0);
    return () => clearTimeout(timer);
  }, [storageKey]);
  function toggle(id: string) {
    setCollapsed(old => { const next = old.includes(id) ? old.filter(x => x !== id) : [...old, id]; localStorage.setItem(storageKey, JSON.stringify(next)); return next; });
  }
  function drop(e: DragEvent, id: string) { e.preventDefault(); setOver(""); const payload = e.dataTransfer.getData("text/plain"); if (payload) assign(payload, id); }
  const matches = (c: Concept) => [c.name, ...c.aliases].join(" ").toLocaleLowerCase().includes(query.toLocaleLowerCase());
  const badge = (id: string) => <span className="wm-taxonomy-counts" aria-hidden="true"><span>{counts[id]?.accepted ?? 0}</span>{!!counts[id]?.pending && <small title="Repositories awaiting review">+{counts[id].pending}</small>}</span>;
  const target = (c: Concept) => ({
    onDragOver: (e: DragEvent) => { e.preventDefault(); setOver(c.id); if (c.kind === "DOMAIN") setCollapsed(old => old.filter(id => id !== c.id)); },
    onDragLeave: () => setOver(""), onDrop: (e: DragEvent) => drop(e, c.id),
  });
  const leaf = (c: Concept) => <li key={c.id}><button aria-label={c.name} className={`wm-project wm-taxonomy-node ${active === c.id ? "is-active" : ""} ${over === c.id ? "is-drop-target" : ""}`} title={`${c.name}${c.aliases.length ? ` · ${c.aliases.join(", ")}` : ""} · ${counts[c.id]?.accepted ?? 0} accepted repositories · Drop to add membership`} onClick={() => choose(c.id)} {...target(c)}><Icon name={c.kind === "PROJECT" ? "folder" : c.kind === "TOPIC" ? "topic" : "tag"} size={17} /><span>{c.name}</span>{badge(c.id)}</button></li>;
  return <div className="wm-taxonomy-browser">
    <div className="wm-taxonomy-modes" role="tablist" aria-label="Taxonomy types">{[["PROJECT", "Projects"], ["TOPIC", "Topics"], ["TAG", "Tags"]].map(([key, label]) => <button key={key} role="tab" aria-selected={mode === key} onClick={() => { setMode(key); setQuery(""); }}>{label}</button>)}</div>
    <label className="wm-taxonomy-search"><Icon name="search" size={16} /><input aria-label="Search taxonomy names or aliases" value={query} onChange={e => setQuery(e.target.value)} placeholder="Names or aliases…" /></label>
    <p className="wm-taxonomy-legend">Accepted · <span>+ pending review</span></p>
    <ul className="wm-project-tree" aria-label={`${mode === "PROJECT" ? "Domains and projects" : mode === "TOPIC" ? "Topics" : "Tags"} list`} onKeyDown={e => {
      if (!["ArrowDown", "ArrowUp", "Home", "End"].includes(e.key)) return;
      const items = [...e.currentTarget.querySelectorAll<HTMLButtonElement>("button")];
      const i = items.indexOf(document.activeElement as HTMLButtonElement);
      e.preventDefault(); items[e.key === "Home" ? 0 : e.key === "End" ? items.length - 1 : (i + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length]?.focus();
    }}>
      {mode === "PROJECT" ? concepts.filter(c => c.kind === "DOMAIN" && (matches(c) || concepts.some(p => p.domain === c.id && matches(p)))).map(d => <li key={d.id}>
        <div className="wm-domain-row"><button className="wm-disclosure" aria-label={`${collapsed.includes(d.id) ? "Expand" : "Collapse"} ${d.name}`} aria-expanded={!collapsed.includes(d.id)} onClick={() => toggle(d.id)}><Icon name="chevron" size={16} /></button><button aria-label={d.name} className={`wm-domain ${active === d.id ? "is-active" : ""} ${over === d.id ? "is-drop-target" : ""}`} onClick={() => choose(d.id)} title={`${d.name} · Drop to choose a project`} {...target(d)}><Icon name="domain" size={18} /><span>{d.name}</span>{badge(d.id)}</button></div>
        {(!collapsed.includes(d.id) || query) && <ul>{concepts.filter(p => p.kind === "PROJECT" && p.domain === d.id && (matches(p) || matches(d))).map(leaf)}</ul>}
      </li>) : concepts.filter(c => c.kind === mode && matches(c)).sort((a, b) => a.name.localeCompare(b.name)).map(leaf)}
      {!concepts.some(c => c.kind === mode) && <li className="wm-tree-empty">No {mode === "PROJECT" ? "projects" : mode === "TOPIC" ? "topics" : "tags"} yet. Create content or discover a taxonomy.</li>}
    </ul>
  </div>;
}
