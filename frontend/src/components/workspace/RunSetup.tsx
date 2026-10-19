"use client";

import { SearchableSelect } from "./SearchableSelect";

import { useState } from "react";
import { request, displayLabel, type RunPlan, type RunPreferences, type RepoScope } from "@/lib/workspace";
import { Icon } from "./Icons";

export function RunSetup({ collection, csrf, inference, selected, scope, preferences, revision, active, canManage, refreshed }: {
  collection: string; csrf: string; inference: string; selected: string[]; scope: RepoScope; preferences: RunPreferences;
  revision: number; active: boolean; canManage: boolean; refreshed: () => Promise<void>;
}) {
  const [taxonomyCount, setTaxonomyCount] = useState(preferences.taxonomy_count);
  const [classificationCount, setClassificationCount] = useState(preferences.classification_count);
  const [selection, setSelection] = useState(selected.length ? "MANUAL" : "AUTO");
  const [source, setSource] = useState("CURRENT");
  const [budgetMode, setBudgetMode] = useState(preferences.budget_mode);
  const [budget, setBudget] = useState(preferences.budget_usd);
  const [reanalyze, setReanalyze] = useState(false);
  const [reason, setReason] = useState("");
  const [plan, setPlan] = useState<RunPlan | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  // A different inference/scope/manual selection invalidates the visible preview.
  const context = JSON.stringify({ inference, selected, scope, reanalyze, reason });
  const [previewContext, setPreviewContext] = useState("");
  const visiblePlan = previewContext === context ? plan : null;
  const defaults = { taxonomy_count: taxonomyCount, classification_count: classificationCount, budget_mode: budgetMode, budget_usd: budget };
  async function preview(mode: string) {
    setBusy(true); setError(""); setMessage(""); setPlan(null);
    try {
      const value = await request<RunPlan>("/organizer/preview", collection, csrf, "POST", {
        mode, ai_mode: inference, selection, repo_keys: selection === "MANUAL" ? selected : [],
        count: ["DISCOVER", "REDISCOVER"].includes(mode) ? taxonomyCount : classificationCount,
        reanalyze: mode !== "EXTRACT" && inference === "LIVE" && reanalyze, reanalysis_reason: mode !== "EXTRACT" && reanalyze ? reason : "",
        scope: source === "CURRENT" ? scope : { view: "all" }, budget_mode: budgetMode, budget_usd: budget,
      });
      setPlan(value); setPreviewContext(context);
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }
  async function start() {
    if (!visiblePlan) return;
    setBusy(true); setError("");
    try {
      await request("/organizer/execute", collection, csrf, "POST", { plan_id: visiblePlan.plan_id });
      setPlan(null); setMessage("Reviewed run queued. Progress and outcomes appear below."); await refreshed();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }
  const disabled = busy || active;
  return <section className="wm-run-setup" aria-label="AI run setup"><div className="wm-run-title"><div><h3>Choose your next run</h3><p>Choose a number automatically or use your manual selection. Preview the exact cohort before starting.</p></div><button className="wm-link" disabled={disabled} onClick={async () => { setBusy(true); setError(""); setPlan(null); try { await request("/organizer/preferences", collection, csrf, "PATCH", defaults); await refreshed(); setMessage("Run defaults saved. No work was started."); } catch (e) { setError((e as Error).message); } finally { setBusy(false); } }}>Save defaults</button></div>
    <div className="wm-run-grid">
      <label>Repository selection<SearchableSelect aria-label="Repository selection mode" value={selection} disabled={disabled} onChange={value => { setSelection(value); setPlan(null); }} options={[({ value: "AUTO", label: "Choose a number automatically" }), ({ value: "MANUAL", label: ["Manual selection (", selected.length, ")"].join("") })]} /></label>
      <label>Repository scope<SearchableSelect aria-label="AI repository scope" value={source} disabled={disabled} onChange={value => { setSource(value); setPlan(null); }} options={[({ value: "CURRENT", label: "Current view and filters" }), ({ value: "ALL", label: "Entire collection / access candidates" })]} /></label>
      <label>Taxonomy sample size<input aria-label="Taxonomy sample size" type="number" min={1} max={30} value={taxonomyCount} disabled={disabled} onChange={e => { setTaxonomyCount(Number(e.target.value)); setPlan(null); }} /></label>
      <label>Classification batch size<input aria-label="Classification batch size" type="number" min={1} max={30} value={classificationCount} disabled={disabled} onChange={e => { setClassificationCount(Number(e.target.value)); setPlan(null); }} /></label>
      <label>Budget mode<SearchableSelect aria-label="Budget mode" value={budgetMode} disabled={disabled} onChange={value => { setBudgetMode(value as RunPreferences["budget_mode"]); setPlan(null); }} options={[({ value: "FIXED", label: "Fixed HTTP / generation limits" }), ({ value: "ADAPTIVE", label: "Adaptive cost budget", disabled: !canManage })]} /></label>
      {budgetMode === "ADAPTIVE" && <label>Maximum per run (USD)<input aria-label="Maximum per run USD" type="number" min={0.001} max={5} step={0.001} value={budget} disabled={disabled} onChange={e => { setBudget(Number(e.target.value)); setPlan(null); }} /></label>}
    </div>
    <div className="wm-reanalysis"><label className="wm-check"><input type="checkbox" aria-label="Re-analyze with AI" checked={reanalyze} disabled={disabled || inference !== "LIVE"} onChange={e => { setReanalyze(e.target.checked); setPlan(null); }} />Re-analyze with AI · explicitly refresh taxonomy or classification</label><p>Previously analyzed repositories are reconciled offline by default. Choose Live AI and enable re-analysis for changed evidence, taxonomy or a reviewed retry. A missing project alone does not need another model call.</p>{reanalyze && inference === "LIVE" && <label>Reason for re-analysis<input aria-label="Reason for re-analysis" value={reason} minLength={3} maxLength={200} onChange={e => { setReason(e.target.value); setPlan(null); }} placeholder="For example: README changed or taxonomy expanded" /></label>}</div>
    <p className="wm-run-help">Up to 30 repositories per local run. Taxonomy combines evidence into one draft; classification can use one generation per repository. Adaptive mode derives finite call limits from the reviewed run, within the cumulative $5 ceiling.</p>
    <div className="wm-actions wm-wrap"><button className="wm-primary" disabled={disabled} onClick={() => preview(revision ? "REDISCOVER" : "DISCOVER")}><Icon name="ai" />{revision ? "Rediscover taxonomy" : "Discover taxonomy"}</button><button className="wm-secondary" disabled={disabled} onClick={() => preview("INCREMENTAL")}>Reorganize incremental</button><button className="wm-secondary" disabled={disabled} onClick={() => preview("FULL_CLASSIFICATION")}>Full classification</button><button className="wm-secondary" disabled={disabled} onClick={() => preview("EXTRACT")}>Extract evidence</button></div>
    <small>These buttons preview a run. Preview uses no OpenAI requests. Cached mode never falls back to paid inference.</small>
    {error && <p className="wm-error" role="alert">{error}</p>}{message && <p className="wm-notice" role="status">{message}</p>}
    {visiblePlan && <section className="wm-run-preview" aria-label="Run preview"><div className="wm-run-title"><h3>Review this {displayLabel(visiblePlan.input.mode)} run</h3><span className="wm-badge">{visiblePlan.input.budget_mode === "ADAPTIVE" ? "Adaptive dollars" : "Fixed limits"}</span></div><div className="wm-preview-numbers"><span>Requested<strong>{visiblePlan.requested}</strong></span><span>Eligible<strong>{visiblePlan.eligible}</strong></span><span>Chosen<strong>{visiblePlan.chosen}</strong></span><span>Excluded / deferred<strong>{visiblePlan.excluded.length}</strong></span></div>
      <p className="wm-notice">{visiblePlan.fresh_ai} repositories for fresh AI · {visiblePlan.offline} for offline reconciliation · {visiblePlan.previously_analyzed_inputs} previously analyzed inputs.{visiblePlan.input.reanalyze && ` Explicit re-analysis: ${visiblePlan.input.reanalysis_reason}`}</p>
      <p><strong>Conservative upper bound ${visiblePlan.upper_usd.toFixed(6)}</strong> · up to {visiblePlan.generations} generations / {visiblePlan.http_requests} HTTP attempts.</p><p>{visiblePlan.strategy}. {visiblePlan.note}</p>
      <ul className="wm-cohort-list">{visiblePlan.repositories.map(r => <li key={r.key}><Icon name="repos" size={16} /><strong>{r.name}</strong><span>{r.language || "Unknown language"} · {displayLabel(r.analysis_status || "UNKNOWN")}{r.freshness === "STALE" ? " · Changed taxonomy/evidence" : ""}{r.prior_taxonomy ? " · Prior taxonomy input" : ""}</span></li>)}</ul>
      {visiblePlan.excluded.length > 0 && <details><summary>Excluded or deferred repositories</summary><ul>{visiblePlan.excluded.map(r => <li key={r.key}>{r.name} — {r.reason}</li>)}</ul></details>}
      {visiblePlan.skipped?.length > 0 && <details><summary>Protected from repeat AI ({visiblePlan.skipped.length})</summary><ul>{visiblePlan.skipped.map(r => <li key={r.key}>{r.name} — {r.reason}</li>)}</ul></details>}
      {visiblePlan.blocked_reason && <p className="wm-notice">{visiblePlan.blocked_reason}</p>}
      <div className="wm-actions"><button className="wm-primary" disabled={disabled || !visiblePlan.can_start} onClick={start}>Start reviewed run</button><button className="wm-secondary" disabled={busy} onClick={() => setPlan(null)}>Cancel preview</button><small>Preview expires after 5 minutes.</small></div>
    </section>}
  </section>;
}
