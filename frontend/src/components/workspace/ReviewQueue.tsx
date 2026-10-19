"use client";

import { SearchableSelect } from "./SearchableSelect";
import { LabelChip } from "./LabelChip";

import { useState } from "react";
import { displayLabel, request, type Concept, type Edge, type Suggestion } from "@/lib/workspace";

export function ReviewQueue({ suggestions, concepts, edges, names, collection, csrf, disabled, refreshed }: {
  suggestions: Suggestion[]; concepts: Record<string, Concept>; edges: Record<string, Record<string, Edge>>;
  names: Record<string, string>; collection: string; csrf: string; disabled: boolean; refreshed: () => Promise<void>;
}) {
  const [kind, setKind] = useState("");
  const [concept, setConcept] = useState("");
  const [repo, setRepo] = useState("");
  const [group, setGroup] = useState("repo");
  const [selected, setSelected] = useState<string[]>([]);
  const [review, setReview] = useState<"accept" | "reject" | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const filtered = suggestions.filter(s => (!kind || s.kind === kind) && (!concept || s.concept_id === concept) && (!repo || `${names[s.repo_key] || s.repo_key} ${s.repo_key}`.toLowerCase().includes(repo.toLowerCase())));
  const chosen = suggestions.filter(s => selected.includes(s.id));
  const groups = new Map<string, Suggestion[]>();
  for (const s of filtered) { const key = group === "repo" ? s.repo_key : s.concept_id; groups.set(key, [...(groups.get(key) || []), s]); }
  function resetSelection() { setSelected([]); setReview(null); setMessage(""); }
  async function decide(ids: string[], decision: "accept" | "reject") {
    setBusy(true); setError(""); setMessage("");
    try {
      const result = await request<{ outcomes: { id: string; status: string; reason?: string }[] }>("/organizer/suggestions/batch", collection, csrf, "POST", { ids, decision });
      setMessage(result.outcomes.map(o => `${names[suggestions.find(s => s.id === o.id)?.repo_key || ""] || "Repository"}: ${displayLabel(o.status)}${o.reason ? ` — ${o.reason}` : ""}`).join("; "));
      setSelected([]); setReview(null); await refreshed();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }
  return <section className="wm-panel" aria-label="Assignment review"><div className="wm-panel-heading"><div><h2>Suggestions for your review</h2><p>Review proposed additions beside existing memberships. Accepting makes a protected USER decision.</p></div><span className="wm-badge">{suggestions.length} pending</span></div>
    <div className="wm-review-filters"><label>Type<SearchableSelect aria-label="Review taxonomy type" value={kind} onChange={value => { setKind(value); setConcept(""); resetSelection(); }} options={[({ value: "", label: "Projects, topics and tags" }), ...["PROJECT", "TOPIC", "TAG"].map(k => ({ value: k, label: displayLabel(k) }))]} /></label><label>Concept<SearchableSelect aria-label="Review concept" value={concept} onChange={value => { setConcept(value); resetSelection(); }} options={[({ value: "", label: "All concepts" }), ...Object.values(concepts).filter(c => c.active && c.kind !== "DOMAIN" && (!kind || c.kind === kind)).map(c => ({ value: c.id, label: c.name }))]} /></label><label>Repository<input aria-label="Review repository" value={repo} onChange={e => { setRepo(e.target.value); resetSelection(); }} placeholder="Name or ID" /></label><label>Group by<SearchableSelect aria-label="Group suggestions by" value={group} onChange={value => setGroup(value)} options={[({ value: "repo", label: "Repository" }), ({ value: "concept", label: "Concept" })]} /></label></div>
    {filtered.length > 0 && <div className="wm-review-bulk"><label className="wm-check"><input aria-label="Select visible suggestions" type="checkbox" checked={filtered.every(s => selected.includes(s.id))} onChange={e => { setSelected(e.target.checked ? filtered.map(s => s.id) : []); setReview(null); }} />Select filtered suggestions ({filtered.length})</label><span>{chosen.length} selected</span><button className="wm-secondary wm-small" disabled={!chosen.length || disabled || busy} onClick={() => setReview("accept")}>Review selected acceptance</button><button className="wm-secondary wm-small" disabled={!chosen.length || disabled || busy} onClick={() => setReview("reject")}>Review selected rejection</button></div>}
    {review && chosen.length > 0 && <div className="wm-review-confirm" aria-label="Selected review summary"><h3>{review === "accept" ? "Accept" : "Reject"} {chosen.length} selected proposals?</h3><ul>{chosen.map(s => <li key={s.id}>{names[s.repo_key] || s.repo_key} → {displayLabel(s.kind)}: {concepts[s.concept_id]?.name}</li>)}</ul><p>Each item is checked for current access, evidence and manual decisions. Stale items will be reported and skipped.</p><button className="wm-primary" disabled={busy || disabled} onClick={() => decide(chosen.map(s => s.id), review)}>Confirm selected {review === "accept" ? "acceptance" : "rejection"}</button><button className="wm-link" onClick={() => setReview(null)}>Cancel</button></div>}
    {message && <p className="wm-notice" role="status">{message}</p>}{error && <p className="wm-error" role="alert">{error}</p>}
    {[...groups].map(([key, items]) => <div className="wm-review-group" key={key}><h3>{group === "repo" ? names[key] || key : concepts[key]?.name}</h3>{items.map(s => <article className="wm-suggestion" key={s.id}>
      <label className="wm-review-select"><input type="checkbox" aria-label={`Select suggestion ${s.id}`} checked={selected.includes(s.id)} onChange={e => { setSelected(e.target.checked ? [...selected, s.id] : selected.filter(id => id !== s.id)); setReview(null); }} /></label><div className="wm-suggestion-body"><span className={`wm-kind wm-${s.kind.toLowerCase()}`}>{displayLabel(s.kind)}</span><h3><LabelChip id={s.concept_id} kind={s.kind}>{concepts[s.concept_id]?.name || s.concept_id}</LabelChip></h3><small>{names[s.repo_key] || s.repo_key}</small><p>Existing: {Object.keys(edges[s.repo_key] || {}).filter(id => concepts[id]?.active).map(id => concepts[id].name).join(", ") || "No accepted labels"}</p><p>{s.reason}</p><small>Evidence: {s.evidence_ids.join(", ")} · {displayLabel(s.evidence)}{s.evidence === "LOCAL_MATCH" ? " · Human review required" : " · Model confidence is uncalibrated"}</small></div><div className="wm-actions"><button className="wm-secondary" disabled={disabled || busy} onClick={() => decide([s.id], "reject")}>Reject</button><button className="wm-primary" disabled={disabled || busy} onClick={() => decide([s.id], "accept")}>Accept</button></div>
    </article>)}</div>)}
    {!filtered.length && <div className="wm-empty wm-compact"><span className="wm-empty-icon">✧</span><h3>{suggestions.length ? "No suggestions match these filters." : "No pending suggestions."}</h3><p>Publish taxonomy and run classification or offline reconciliation to find supported connections.</p></div>}
  </section>;
}
