"use client";

import { useState } from "react";
import { displayLabel, request, type AutoSettings, type Automation } from "@/lib/workspace";

const changeTypes = ["CREATE", "CREATE_PROJECT", "EDIT", "ARCHIVE", "MERGE", "RULE", "EVIDENCE"];
export function AutomationSettings({ control, status, collection, csrf, disabled, refreshed }: {
  control: AutoSettings; status: Automation; collection: string; csrf: string; disabled: boolean; refreshed: () => Promise<void>;
}) {
  const [value, setValue] = useState<AutoSettings>({ auto_enabled: control.auto_enabled, quiet_seconds: control.quiet_seconds, cooldown_seconds: control.cooldown_seconds, auto_window_seconds: control.auto_window_seconds ?? 900, auto_weight_threshold: control.auto_weight_threshold ?? 6, auto_entity_threshold: control.auto_entity_threshold ?? 3, auto_project_threshold: control.auto_project_threshold ?? 2, auto_change_types: control.auto_change_types ?? changeTypes });
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  return <details className="wm-automation"><summary>Automatic organization · {control.auto_enabled ? "Enabled" : "Off"} · Configure thresholds</summary><form onSubmit={async e => { e.preventDefault(); setBusy(true); setMessage(""); setError(""); try { await request("/organizer/settings", collection, csrf, "PATCH", value); await refreshed(); setMessage("Automatic organization settings saved."); } catch (e) { setError((e as Error).message); } finally { setBusy(false); } }}>
    <label className="wm-check"><input type="checkbox" checked={value.auto_enabled} onChange={e => setValue({ ...value, auto_enabled: e.target.checked })} />Automatic organization after significant edits</label>
    <p>Trigger when weighted changes AND distinct entities reach their thresholds, OR enough new projects are created. Cosmetic edits never trigger AI. Previously analyzed repositories reconcile offline; fresh AI uses the saved count and budget for new eligible repositories. Explicit re-analysis remains manual.</p>
    <div className="wm-run-grid">{([
      ["auto_weight_threshold", "Weighted changes", 1, 100], ["auto_entity_threshold", "Distinct entities", 1, 100], ["auto_project_threshold", "New projects (0 disables)", 0, 100], ["auto_window_seconds", "Change window (seconds)", 60, 86400], ["quiet_seconds", "Quiet period (seconds)", 0, 3600], ["cooldown_seconds", "Cooldown (seconds)", 0, 86400],
    ] as const).map(([key, label, min, max]) => <label key={key}>{label}<input aria-label={label} type="number" min={min} max={max} required value={value[key]} onChange={e => setValue({ ...value, [key]: Number(e.target.value) })} /></label>)}</div>
    <fieldset><legend>Eligible change types</legend><div className="wm-actions wm-wrap">{changeTypes.map(type => <label className="wm-check" key={type}><input type="checkbox" checked={value.auto_change_types?.includes(type)} onChange={e => setValue({ ...value, auto_change_types: e.target.checked ? [...(value.auto_change_types ?? []), type] : value.auto_change_types?.filter(t => t !== type) })} />{displayLabel(type)}</label>)}</div><small>Weights: new project 3; project edit, merge, rule or evidence 2; other creates/edits and archive 1. Changes are counted once per scheduled run.</small></fieldset>
    {status && <p role="status">Current window: {status.weight} weighted changes · {status.entities} entities · {status.new_projects} new projects. {status.threshold_met ? "Threshold met" : "Threshold not met"}. Quiet wait {status.quiet_remaining}s · Cooldown {status.cooldown_remaining}s.</p>}
    {error && <p className="wm-error" role="alert">{error}</p>}{message && <p className="wm-notice" role="status">{message}</p>}<button className="wm-secondary" disabled={disabled || busy}>Save automatic settings</button>
  </form></details>;
}
