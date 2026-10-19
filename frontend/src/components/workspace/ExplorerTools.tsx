import { SearchableSelect } from "./SearchableSelect";
import type { RepoSummary } from "@/lib/workspace";
import { Icon } from "./Icons";

export function ExplorerSummary({ summary, selected, selectedSummary }: { summary: RepoSummary; selected: number; selectedSummary?: RepoSummary | null }) {
  const cards = [["In this view", summary.repos, selected, "repos"], ["Labeled", summary.labeled ?? 0, selectedSummary?.labeled, "tag"], ["No project", summary.uncategorized, selectedSummary?.uncategorized, "inbox"], ["Needs review", summary.review, selectedSummary?.review, "review"], ["Selected", selected, undefined, "selected"]];
  return <div className="wm-stats" aria-label="Repository summary">{cards.map(([label, count, subtotal, icon]) => {
    const detail = selected > 0 ? label === "Selected" ? "Across pages" : `${subtotal ?? "…"} selected` : label === "Needs review" && summary.suggestions ? `${summary.suggestions} suggestions` : "";
    return <div key={label} className={`wm-stat ${detail ? "has-detail" : ""} ${label === "Selected" ? `wm-stat-selected ${selected > 0 ? "is-selected" : ""}` : ""}`}><span className="wm-stat-label"><Icon name={String(icon)} size={16} />{label}</span><strong>{count}</strong>{detail && <small>{detail}</small>}</div>;
  })}</div>;
}

export function ExplorerFilters({ query, language, visibility, days, latest, languages, total, loading, onQuery, onLanguage, onVisibility, onDays, organizationView, onOrganizationView, clear }: {
  query: string; language: string; visibility: string; days: number; latest: boolean; languages: { value: string; label: string; count: number }[];
  total: number; loading: boolean; onQuery: (value: string) => void; onLanguage: (value: string) => void; onVisibility: (value: string) => void; onDays: (value: number) => void; organizationView: string; onOrganizationView: (value: string) => void; clear: () => void;
}) {
  const filtered = !!query || !!language || visibility !== "all";
  return <><div className="wm-toolbar">
    <label className="wm-search"><Icon name="search" /><span className="wm-sr-only">Search repositories</span><input aria-label="Search repositories" value={query} onChange={e => onQuery(e.target.value)} placeholder="Search names, owners, concepts…" />{query && <button className="wm-icon-button" aria-label="Clear search" onClick={() => onQuery("")}><Icon name="close" size={16} /></button>}</label>
    <label className="wm-filter-field"><span>Language</span><SearchableSelect aria-label="Language filter" value={language} onChange={onLanguage} options={[{ value: "", label: "All languages" }, ...languages.map(l => ({ value: l.value, label: l.label }))]} /></label>
    <label className="wm-filter-field"><span>Visibility</span><SearchableSelect aria-label="Visibility filter" value={visibility} onChange={value => onVisibility(value)} options={[({ value: "all", label: "All visibility" }), ({ value: "public", label: "Public" }), ({ value: "private", label: "Private" })]} /></label>
    <label className="wm-filter-field wm-organization-filter"><span>Organization view</span><SearchableSelect aria-label="Organization status view" value={organizationView} onChange={onOrganizationView} options={[["my", "My Repos"], ["all", "Entire collection"], ["favorites", "Favorites"], ["latest", "Latest Work"], ["uncategorized", "No project"], ["no_labels", "No labels"], ["needs_review", "Needs review"], ["no_match", "No AI match"], ["failed", "Failed / blocked"], ["stale", "Stale analysis"]].map(([value, label]) => ({ value, label }))} /></label>
    {latest && <label className="wm-filter-field"><span>Activity window</span><SearchableSelect aria-label="Activity window" value={String(days)} onChange={value => onDays(Number(value))} options={[...[7, 14, 30, 90].map(d => ({ value: String(d), label: ["Last ", d, " days"].join("") }))]} /></label>}
    <span className="wm-result-count" role="status">{loading ? "Updating…" : `${total} results`}</span>
  </div>{filtered && <div className="wm-active-filters"><Icon name="filter" size={16} />{query && <button className="wm-chip" onClick={() => onQuery("")}>Search: {query}<Icon name="close" size={14} /></button>}{language && <button className="wm-chip" onClick={() => onLanguage("")}>{language === "__UNKNOWN__" ? "Unknown language" : language}<Icon name="close" size={14} /></button>}{visibility !== "all" && <button className="wm-chip" onClick={() => onVisibility("all")}>{visibility}<Icon name="close" size={14} /></button>}<button className="wm-link" onClick={clear}>Clear filters</button></div>}</>;
}
