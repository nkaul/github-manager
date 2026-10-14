import type { RepoSummary } from "@/lib/workspace";
import { Icon } from "./Icons";

export function ExplorerSummary({ summary, selected, selectedSummary }: { summary: RepoSummary; selected: number; selectedSummary?: RepoSummary | null }) {
  const cards = [["In this view", summary.repos, selected, "repos"], ["Labeled", summary.labeled ?? 0, selectedSummary?.labeled, "tag"], ["No project", summary.uncategorized, selectedSummary?.uncategorized, "inbox"], ["Needs review", summary.review, selectedSummary?.review, "review"], ["Selected", selected, undefined, "selected"]];
  return <div className="wm-stats" aria-label="Repository summary">{cards.map(([label, count, subtotal, icon], index) => <div key={label} className={`wm-stat wm-stat-tone-${index} ${label === "Selected" ? "wm-stat-selected" : ""}`}><span className="wm-stat-label"><Icon name={String(icon)} size={17} />{label}</span><strong>{count}</strong><small>{label === "Selected" ? "Across pages in this view" : selected > 0 ? `${subtotal ?? "…"} selected` : label === "Needs review" ? `${summary.suggestions} suggestions` : "Repositories in current scope"}</small></div>)}</div>;
}

export function ExplorerFilters({ query, language, visibility, days, latest, languages, total, loading, onQuery, onLanguage, onVisibility, onDays, clear }: {
  query: string; language: string; visibility: string; days: number; latest: boolean; languages: { value: string; label: string; count: number }[];
  total: number; loading: boolean; onQuery: (value: string) => void; onLanguage: (value: string) => void; onVisibility: (value: string) => void; onDays: (value: number) => void; clear: () => void;
}) {
  const filtered = !!query || !!language || visibility !== "all";
  return <><div className="wm-toolbar">
    <label className="wm-search"><Icon name="search" /><span className="wm-sr-only">Search repositories</span><input aria-label="Search repositories" value={query} onChange={e => onQuery(e.target.value)} placeholder="Search names, owners, concepts…" />{query && <button className="wm-icon-button" aria-label="Clear search" onClick={() => onQuery("")}><Icon name="close" size={16} /></button>}</label>
    <label className="wm-filter-field"><span>Language</span><input className="wm-language" aria-label="Language filter" list="repository-languages" value={language === "__UNKNOWN__" ? "Unknown" : language} onChange={e => onLanguage(e.target.value === "Unknown" ? "__UNKNOWN__" : e.target.value)} placeholder="All languages" /><datalist id="repository-languages">{languages.map(l => <option key={l.value} value={l.label}>{l.count} repositories</option>)}</datalist></label>
    <label className="wm-filter-field"><span>Visibility</span><select aria-label="Visibility filter" value={visibility} onChange={e => onVisibility(e.target.value)}><option value="all">All visibility</option><option value="public">Public</option><option value="private">Private</option></select></label>
    {latest && <label className="wm-filter-field"><span>Activity window</span><select aria-label="Activity window" value={days} onChange={e => onDays(Number(e.target.value))}>{[7, 14, 30, 90].map(d => <option key={d} value={d}>Last {d} days</option>)}</select></label>}
    <span className="wm-result-count" role="status">{loading ? "Updating…" : `${total} results`}</span>
  </div>{filtered && <div className="wm-active-filters"><Icon name="filter" size={16} />{query && <button className="wm-chip" onClick={() => onQuery("")}>Search: {query}<Icon name="close" size={14} /></button>}{language && <button className="wm-chip" onClick={() => onLanguage("")}>{language === "__UNKNOWN__" ? "Unknown language" : language}<Icon name="close" size={14} /></button>}{visibility !== "all" && <button className="wm-chip" onClick={() => onVisibility("all")}>{visibility}<Icon name="close" size={14} /></button>}<button className="wm-link" onClick={clear}>Clear filters</button></div>}</>;
}
