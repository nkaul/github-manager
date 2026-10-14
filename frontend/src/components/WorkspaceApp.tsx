"use client";

import { useCallback, useEffect, useRef, useState, type FormEvent, type ReactNode } from "react";
import { api, type Config, type Identity } from "@/lib/api";
import { request, type AllowanceAudit, type Budget, type Concept, type Detail, type Draft, type Kind, type Proposal, type Repo, type RepoPage, type ResetPlan, type ResetScope, type Workspace, type RepoSummary, type TaxonomyCheck, type TaxonomyConflict, WorkspaceError, displayLabel } from "@/lib/workspace";
import "./workspace.css";
import "./workspace-theme.css";
import { Icon, ZenCat } from "./workspace/Icons";
import { LogoSettings } from "./workspace/LogoSettings";
import { RunSetup } from "./workspace/RunSetup";
import { WorkspaceShell } from "./workspace/Shell";
import { AutomationSettings } from "./workspace/AutomationSettings";
import { ReviewQueue } from "./workspace/ReviewQueue";
import { ExplorerFilters, ExplorerSummary } from "./workspace/ExplorerTools";

const kinds: Kind[] = ["DOMAIN", "PROJECT", "TOPIC", "TAG"];
const title = displayLabel;
const date = (value?: string | null) => value ? new Date(value).toLocaleString(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }) : "Not yet";
const activeRun = (s: string) => ["QUEUED", "RUNNING", "WAITING_FOR_REAUTH"].includes(s);
type Action = (path: string, method?: string, body?: unknown) => Promise<unknown>;

function Modal({ title: heading, children, close }: { title: string; children: ReactNode; close: () => void }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement;
    ref.current?.querySelector<HTMLElement>("button,input,select,textarea")?.focus();
    return () => previous?.focus();
  }, []);
  return <div className="wm-backdrop" onMouseDown={e => { if (e.target === e.currentTarget) close(); }}>
    <div className="wm-modal" role="dialog" aria-modal="true" aria-label={heading} ref={ref} onKeyDown={e => {
      if (e.key === "Escape") close();
      if (e.key === "Tab") {
        const nodes = Array.from(ref.current?.querySelectorAll<HTMLElement>("button:not(:disabled),input:not(:disabled),textarea,select,a[href]") || []);
        const first = nodes[0], last = nodes[nodes.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last?.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first?.focus(); }
      }
    }}><div className="wm-modal-head"><h2>{heading}</h2><button className="wm-icon-button" onClick={close} aria-label="Close dialog"><Icon name="close" /></button></div>{children}</div>
  </div>;
}

function ConceptForm({ item, concepts, save, close }: { item?: Concept; concepts: Concept[]; save: Action; close: () => void }) {
  const [kind, setKind] = useState<Kind>(item?.kind || "PROJECT");
  const [name, setName] = useState(item?.name || "");
  const [description, setDescription] = useState(item?.description || "");
  const [aliases, setAliases] = useState(item?.aliases.join(", ") || "");
  const [domain, setDomain] = useState(item?.domain || "");
  const [error, setError] = useState("");
  const [conflicts, setConflicts] = useState<TaxonomyConflict[]>([]);
  const [saving, setSaving] = useState(false);
  async function submit(e: FormEvent) {
    e.preventDefault(); setSaving(true); setError(""); setConflicts([]);
    try {
      const body = { name, description, aliases: aliases.split(",").map(s => s.trim()).filter(Boolean), domain: kind === "PROJECT" ? domain : null };
      await save(item ? `/taxonomy/concepts/${item.id}` : "/taxonomy/concepts", item ? "PATCH" : "POST", item ? body : { kind, ...body });
      close();
    } catch (e) { setError((e as Error).message); if (e instanceof WorkspaceError) setConflicts(e.conflicts || []); } finally { setSaving(false); }
  }
  return <Modal title={item ? "Edit concept" : "Create a concept"} close={close}><form onSubmit={submit} className="wm-form">
    {error && <div className="wm-error" role="alert">{error}</div>}
    {conflicts.map((c, i) => <div className="wm-conflict" key={i}><p>{c.message}</p>{c.existing && <small>{c.existing.active ? "Active" : "Archived — reservation retained"} {title(c.existing.kind)} · {c.existing.name}</small>}<div className="wm-actions wm-wrap">{c.suggested_name && <button type="button" className="wm-secondary wm-small" onClick={() => { setName(c.suggested_name!); setConflicts([]); setError(""); }}>Use name “{c.suggested_name}”</button>}{c.field === "alias" && <button type="button" className="wm-secondary wm-small" onClick={() => { setAliases(aliases.split(",").map(t => t.trim()).filter(Boolean).filter((_, j) => j !== c.alias_index).join(", ")); setConflicts([]); setError(""); }}>Remove alias “{c.term}”</button>}</div></div>)}
    <label>Type<select value={kind} disabled={!!item} onChange={e => setKind(e.target.value as Kind)}>{kinds.map(k => <option key={k}>{k}</option>)}</select></label>
    <label>Name<input required maxLength={100} value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Customer Platform" /></label>
    <label>Description<textarea maxLength={300} value={description} onChange={e => setDescription(e.target.value)} placeholder="Describe its purpose and boundaries" /></label>
    <label>Aliases <small>Comma-separated · up to six</small><input value={aliases} onChange={e => setAliases(e.target.value)} /></label>
    {kind === "PROJECT" && <label>Parent domain<select required value={domain} onChange={e => setDomain(e.target.value)}><option value="">Choose a domain</option>{concepts.filter(c => c.kind === "DOMAIN").map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select><small>Create a domain first if none exists.</small></label>}
    <div className="wm-actions"><button type="button" className="wm-secondary" onClick={close}>Cancel</button><button disabled={saving} className="wm-primary">{saving ? "Saving…" : "Save concept"}</button></div>
  </form></Modal>;
}

function DraftReview({ draft, revision, collection, csrf, save, close }: { draft: Draft; revision: number; collection: string; csrf: string; save: Action; close: (result?: "saved" | "published") => void }) {
  const [rows, setRows] = useState<Proposal[]>(draft.edited_proposals || draft.proposals);
  const [selected, setSelected] = useState(rows.map(() => true));
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [analysis, setAnalysis] = useState<TaxonomyCheck | null>(null);
  const [checkedKey, setCheckedKey] = useState("");
  const [checking, setChecking] = useState(false);
  const [undo, setUndo] = useState<{ rows: Proposal[]; selected: boolean[] } | null>(null);
  function change(index: number, patch: Partial<Proposal>) { setRows(rows.map((r, i) => i === index ? { ...r, ...patch } : r)); setMessage(""); setError(""); }
  function values() { return rows.filter((_, i) => selected[i]).map(p => ({ kind: p.kind, name: p.name, description: p.description, aliases: p.aliases, domain: p.kind === "PROJECT" ? p.domain || p.parent_domain || null : null })); }
  const payload = JSON.stringify({ draft_id: draft.id, expected_revision: revision, proposals: values() });
  const visible = checkedKey === payload ? analysis : null;
  useEffect(() => {
    let alive = true;
    const timer = setTimeout(async () => {
      if (!JSON.parse(payload).proposals.length) { setChecking(false); return; }
      setChecking(true);
      try { const checked = await request<TaxonomyCheck>("/taxonomy/drafts/check", collection, csrf, "POST", JSON.parse(payload)); if (alive) { setAnalysis(checked); setCheckedKey(payload); setError(""); } }
      catch (e) { if (alive) setError((e as Error).message); }
      finally { if (alive) setChecking(false); }
    }, 350);
    return () => { alive = false; clearTimeout(timer); };
  }, [payload, collection, csrf]);
  async function repair(action: string, conflict?: TaxonomyConflict) {
    setBusy(true); setError("");
    try {
      const result = await request<{ proposals: Proposal[]; check: TaxonomyCheck; message: string }>("/taxonomy/drafts/remediate", collection, csrf, "POST", { ...JSON.parse(payload), action, conflict_id: conflict?.id });
      const included = rows.filter((_, i) => selected[i]);
      const sources = action === "EXCLUDE" ? included.filter((_, i) => i !== conflict?.proposal_index) : included;
      setUndo({ rows, selected }); setRows(result.proposals.map((p, i) => ({ ...sources[i], ...p }))); setSelected(result.proposals.map(() => true)); setAnalysis(null); setMessage(result.message);
    } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }
  async function persist(publish: boolean) {
    setBusy(true); setError("");
    try {
      if (publish) {
        const checked = await request<TaxonomyCheck>("/taxonomy/drafts/check", collection, csrf, "POST", JSON.parse(payload));
        setAnalysis(checked); setCheckedKey(payload);
        if (!checked.valid) { setError("Resolve the conflicts below or exclude the affected proposals before publishing."); return; }
        await save("/taxonomy/drafts/publish", "POST", JSON.parse(payload));
      } else await save(`/taxonomy/drafts/${draft.id}`, "PATCH", { proposals: values() });
      close(publish ? "published" : "saved");
    } catch (e) {
      setError((e as Error).message);
      if (e instanceof WorkspaceError && e.conflicts) { setAnalysis({ valid: false, conflicts: e.conflicts, reused: [] }); setCheckedKey(payload); }
    } finally { setBusy(false); }
  }
  return <Modal title="Review taxonomy draft" close={close}><p className="wm-muted">Edit, exclude, or combine equivalent proposals by keeping one canonical row and adding aliases. Projects need a domain name. Nothing is published until you approve.</p>
    <div className="wm-inline"><span className="wm-badge">{draft.evidence === "REPLAY" ? "Reused AI result" : draft.evidence === "FIXTURE" ? "Test fixture draft" : "Live AI draft"}</span><span className="wm-muted">{draft.model} · revision {revision}</span></div>
    {error && <div className="wm-error" role="alert">{error}</div>}
    {message && <p className="wm-notice" role="status">{message}</p>}
    {undo && <button className="wm-secondary wm-small" disabled={busy} onClick={() => { setRows(undo.rows); setSelected(undo.selected); setUndo(null); setMessage("Last repair undone in this form. Live taxonomy is unchanged."); }}>Undo last repair</button>}
    <section className={`wm-conflict-panel ${visible?.valid ? "is-clear" : ""}`} aria-label="Taxonomy conflict check" aria-live="polite">
      <div className="wm-run-title"><h3>{!selected.some(Boolean) ? "No proposals selected" : checking || !visible ? "Checking names and aliases…" : visible.valid ? "Names and aliases are ready" : `${visible.conflicts.length} conflicts need review`}</h3>{!!visible?.conflicts.some(c => c.field === "alias") && <button className="wm-secondary wm-small" disabled={busy} onClick={() => repair("CLEAN_ALIASES")}>Remove conflicting aliases</button>}</div>
      <p>Names and aliases are unique within each type after case, punctuation and Unicode normalization. Archived concepts keep their reservations. Repairs change this form only; review before saving or publishing.</p>
      {visible?.conflicts.map((c, i) => <article className="wm-conflict" key={c.id || i}><strong>{c.proposal_index === undefined ? "Term conflict" : `Included proposal ${c.proposal_index + 1}`} · {title(c.kind)} · {c.field === "name" ? "Canonical name" : title(c.field)}</strong><p>{c.message}</p>{c.existing && <small>{c.existing.active ? "Active" : "Archived — reservation retained"} {title(c.existing.kind)}: {c.existing.name}</small>}<div className="wm-actions wm-wrap">{c.actions?.map(a => <button key={a.kind} className="wm-secondary wm-small" disabled={busy} onClick={() => repair(a.kind, c)}>{a.label}</button>)}{c.proposal_index !== undefined && <button className="wm-link" onClick={() => { const actual = rows.map((_, i) => i).filter(i => selected[i])[c.proposal_index!]; document.getElementById(`proposal-${actual + 1}-${c.field === "alias" ? "aliases" : c.field}`)?.focus(); }}>Edit manually</button>}</div></article>)}
      {visible?.reused.map(r => <p key={r.id} className="wm-reuse-note">{r.message}</p>)}
    </section>
    <div className="wm-draft-list">{rows.map((r, i) => <fieldset key={i} className={!selected[i] ? "wm-deselected" : ""}><legend><label><input type="checkbox" disabled={busy} checked={selected[i]} onChange={e => setSelected(selected.map((x, j) => j === i ? e.target.checked : x))} /> Include {title(r.kind)}</label></legend>
      <div className="wm-form-grid"><label>Name<input id={`proposal-${i + 1}-name`} aria-label={`Proposal ${i + 1} name`} disabled={busy} value={r.name} maxLength={100} onChange={e => change(i, { name: e.target.value })} /></label><label>Aliases<input id={`proposal-${i + 1}-aliases`} aria-label={`Proposal ${i + 1} aliases`} disabled={busy} value={r.aliases.join(", ")} onChange={e => change(i, { aliases: e.target.value.split(",").map(s => s.trim()).filter(Boolean) })} /></label></div>
      <label>Description<input disabled={busy} value={r.description} maxLength={300} onChange={e => change(i, { description: e.target.value })} /></label>
      {r.kind === "PROJECT" && <label>Domain name<input id={`proposal-${i + 1}-domain`} aria-label={`Proposal ${i + 1} domain`} disabled={busy} value={r.domain || r.parent_domain || ""} onChange={e => change(i, { domain: e.target.value, parent_domain: e.target.value })} /></label>}
      {r.supporting_repo_ids && <small>Supporting samples: {r.supporting_repo_ids.join(", ")}</small>}
    </fieldset>)}</div><p className="wm-muted">{draft.notes}</p><div className="wm-actions"><button className="wm-secondary" disabled={busy || !selected.some(Boolean)} onClick={() => persist(false)}>Save draft</button><button className="wm-primary" disabled={busy || !selected.some(Boolean)} onClick={() => persist(true)}>{busy ? "Saving…" : "Approve & publish taxonomy"}</button></div>
  </Modal>;
}

function AllowancePanel({ budget, collection, save, close }: { budget: Budget; collection: string; save: Action; close: () => void }) {
  const [initial] = useState(budget);
  const [action, setAction] = useState("RENEW");
  const [requests, setRequests] = useState(20);
  const [generations, setGenerations] = useState(10);
  const [updateRequests, setUpdateRequests] = useState(true);
  const [updateGenerations, setUpdateGenerations] = useState(false);
  const [reason, setReason] = useState("Local app testing");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [history, setHistory] = useState<AllowanceAudit[]>([]);
  useEffect(() => { request<AllowanceAudit[]>("/ai/allowance/history", collection).then(setHistory).catch(() => setError("Allowance history could not be loaded.")); }, [collection]);
  async function submit(e: FormEvent) {
    e.preventDefault(); setBusy(true); setError("");
    try {
      await save("/ai/allowance", "POST", { action, expected_revision: initial.revision,
        ...(action === "RENEW" || updateRequests ? { requests } : {}),
        ...(action === "RENEW" || updateGenerations ? { generations } : {}), reason });
      close();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }
  return <Modal title="Manage API allowance" close={close}><form onSubmit={submit}>
    <p>Renew a testing window or change only the selected limits. These controls are shared across local collections and logins. They preserve historical requests, spending, reservations, caches and reports.</p>
    <p className="wm-notice">Cumulative spending ceiling stays at ${initial.cap_usd ?? 5}. Estimated spending: ${initial.estimated_usd?.toFixed(6)}. No API call is made by this form.</p>
    <label className="wm-form">Allowance action<select value={action} onChange={e => { setAction(e.target.value); setRequests(e.target.value === "RENEW" ? 20 : initial.http?.limit ?? 20); setGenerations(e.target.value === "RENEW" ? 10 : initial.generations?.limit ?? 10); }}><option value="RENEW">Start a fresh allowance window</option><option value="SET_LIMITS">Selectively update current window limits</option></select></label>
    {action === "SET_LIMITS" && <label className="wm-check"><input type="checkbox" checked={updateRequests} onChange={e => setUpdateRequests(e.target.checked)} />Update HTTP request limit</label>}
    <label className="wm-form">HTTP requests in window<input type="number" min={action === "RENEW" ? 2 : initial.http?.used ?? 0} max={1000} required value={requests} disabled={action === "SET_LIMITS" && !updateRequests} onChange={e => { const n = Number(e.target.value); setRequests(n); if (action === "RENEW") setGenerations(Math.floor(n / 2)); }} /></label>
    {action === "SET_LIMITS" && <label className="wm-check"><input type="checkbox" checked={updateGenerations} onChange={e => setUpdateGenerations(e.target.checked)} />Update generation limit</label>}
    <label className="wm-form">Generations in window<input type="number" min={action === "RENEW" ? 0 : initial.generations?.used ?? 0} max={1000} required value={generations} disabled={action === "SET_LIMITS" && !updateGenerations} onChange={e => setGenerations(Number(e.target.value))} /></label>
    <p className="wm-muted">One generation normally uses two HTTP requests, including token counting. Renewal starts window usage at zero and adds the chosen allowance; lifetime totals remain visible. Updating a current limit retains its usage.</p>
    <label className="wm-form">Reason for allowance change<input minLength={3} maxLength={200} required value={reason} onChange={e => setReason(e.target.value)} /></label>
    {error && <p className="wm-error" role="alert">{error}</p>}
    <div className="wm-actions"><button type="button" className="wm-secondary" onClick={close}>Cancel</button><button className="wm-primary" disabled={busy || (action === "SET_LIMITS" && !updateRequests && !updateGenerations)}>{busy ? "Saving…" : action === "RENEW" ? "Renew allowance window" : "Save selected limits"}</button></div>
    <h3>Recent allowance changes</h3>{history.length ? history.slice(0, 5).map(h => <p className="wm-muted" key={h.revision}>#{h.revision} · {h.action === "RENEW" ? "New window" : "Limits updated"} · {h.after.http.limit} HTTP / {h.after.generations.limit} generations · {h.reason}</p>) : <p className="wm-muted">No operator changes recorded.</p>}
  </form></Modal>;
}

function ResetPanel({ save, close }: { save: Action; close: () => void }) {
  const [scope, setScope] = useState<ResetScope>({ associations: true, suggestions: true, drafts: true, history: true, feedback: false, cache: false, kinds: [], rules: false, restart: "NONE" });
  const [plan, setPlan] = useState<ResetPlan | null>(null);
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  function update(patch: Partial<ResetScope>) { setScope({ ...scope, ...patch }); setPlan(null); setConfirmation(""); }
  async function preview() { setError(""); setBusy(true); try { setPlan(await save("/organizer/reset/preview", "POST", scope) as ResetPlan); } catch (e) { setError((e as Error).message); } finally { setBusy(false); } }
  async function execute() { setError(""); setBusy(true); try { await save("/organizer/reset/execute", "POST", { plan_id: plan?.plan_id, confirmation }); close(); } catch (e) { setError((e as Error).message); setPlan(null); } finally { setBusy(false); } }
  return <Modal title="Reset & rediscovery" close={close}><p className="wm-muted">Reset selected application organization data. GitHub repositories, connection, metadata, Favorites and activity are preserved. Historical Phase 0/0.5 evidence, durable AI analysis receipts and the API spending ledger are preserved.</p>
    {error && <div className="wm-error" role="alert">{error}</div>}
    <div className="wm-form-grid"><fieldset><legend>AI organization data</legend>{([['associations','Automatic / rule assignments'],['suggestions','Pending classification suggestions'],['drafts','Unpublished taxonomy drafts'],['history','Detailed run history'],['cache','Extracted evidence cache']] as const).map(([key, label]) => <label className="wm-check" key={key}><input type="checkbox" checked={scope[key]} onChange={e => update({ [key]: e.target.checked })} />{label}</label>)}<small>Accepted mappings are USER decisions. Manual rejection tombstones stay protected.</small></fieldset>
      <fieldset><legend>User taxonomy and content</legend>{kinds.map(k => <label className="wm-check" key={k}><input type="checkbox" checked={scope.kinds.includes(k)} onChange={e => update({ kinds: e.target.checked ? [...scope.kinds, k] : scope.kinds.filter(x => x !== k) })} />{title(k)}s</label>)}<label className="wm-check"><input type="checkbox" checked={scope.rules} onChange={e => update({ rules: e.target.checked })} />Organization rules</label><small>Deleting concepts also removes their dependent USER and automatic memberships.</small></fieldset></div>
    <label className="wm-form">After verified cleanup<select value={scope.restart} onChange={e => update({ restart: e.target.value })}><option value="NONE">Return to workspace</option><option value="RECLASSIFY_EXISTING">Reclassify retained taxonomy (cached AI)</option><option value="DISCOVER_AND_RECONCILE">Create a new taxonomy draft (cached AI)</option></select></label>
    {!plan ? <div className="wm-actions"><button className="wm-secondary" onClick={close}>Cancel</button><button className="wm-primary" disabled={busy} onClick={preview}>Preview impact</button></div> : <div className="wm-impact"><h3>Server-verified impact</h3><div className="wm-impact-grid">{Object.entries(plan.counts).map(([key, count]) => <div key={key}><span>{title(key)}</span><strong>{count}</strong></div>)}</div><p className="wm-muted">Preview expires in five minutes. Any intervening workspace change requires a new preview.</p><label>Type exactly DELETE<input value={confirmation} onChange={e => setConfirmation(e.target.value)} autoComplete="off" placeholder="DELETE" /></label><div className="wm-actions"><button className="wm-secondary" onClick={() => setPlan(null)}>Change selection</button><button className="wm-danger" disabled={busy || confirmation !== "DELETE"} onClick={execute}>Confirm reset</button></div></div>}
  </Modal>;
}

function RuleForm({ concepts, save, close }: { concepts: Concept[]; save: Action; close: () => void }) {
  const [rule, setRule] = useState({ name: "", field: "language", operator: "equals", value: "", concept_id: "" });
  const [matches, setMatches] = useState<string[] | null>(null);
  const [error, setError] = useState("");
  function update(key: string, value: string) { setRule({ ...rule, [key]: value }); setMatches(null); }
  return <Modal title="Create organization rule" close={close}><form className="wm-form" onSubmit={async e => { e.preventDefault(); try { setMatches((await save("/content/rules/preview", "POST", rule) as { matches: string[] }).matches); setError(""); } catch (e) { setError((e as Error).message); } }}>
    {error && <div role="alert" className="wm-error">{error}</div>}
    <label>Rule name<input required maxLength={100} value={rule.name} onChange={e => update("name", e.target.value)} /></label>
    <div className="wm-form-grid"><label>Field<select value={rule.field} onChange={e => update("field", e.target.value)}>{["name", "owner", "language", "topic"].map(x => <option key={x}>{x}</option>)}</select></label><label>Condition<select value={rule.operator} onChange={e => update("operator", e.target.value)}><option>equals</option><option>contains</option></select></label></div>
    <label>Value<input required value={rule.value} maxLength={100} onChange={e => update("value", e.target.value)} /></label><label>Assign concept<select required value={rule.concept_id} onChange={e => update("concept_id", e.target.value)}><option value="">Choose a concept</option>{concepts.filter(c => c.kind !== "DOMAIN").map(c => <option key={c.id} value={c.id}>{c.kind} · {c.name}</option>)}</select></label>
    {matches && <div className="wm-notice">{matches.length} matching repositories. {matches.join(", ") || "No current matches."}</div>}
    <div className="wm-actions"><button className="wm-secondary">Preview matches</button><button type="button" className="wm-primary" disabled={matches === null} onClick={async () => { try { await save("/content/rules", "POST", rule); close(); } catch (e) { setError((e as Error).message); } }}>Approve rule</button></div>
  </form></Modal>;
}

export default function WorkspaceApp() {
  const [ready, setReady] = useState(false);
  const [identity, setIdentity] = useState<Identity | null>(null);
  const [config, setConfig] = useState<Config | null>(null);
  const [collection, setCollection] = useState("github");
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [page, setPage] = useState<RepoPage | null>(null);
  const [section, setSection] = useState("repos");
  const [view, setView] = useState("my");
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState("");
  const [visibility, setVisibility] = useState("all");
  const [conceptFilter, setConceptFilter] = useState("");
  const [days, setDays] = useState(14);
  const [selected, setSelected] = useState<string[]>([]);
  const [selectedSummary, setSelectedSummary] = useState<RepoSummary | null>(null);
  const [selectedSummaryKey, setSelectedSummaryKey] = useState("");
  const [dropAssignment, setDropAssignment] = useState<{ keys: string[]; concept: string } | null>(null);
  const [dropProject, setDropProject] = useState("");
  const [assignment, setAssignment] = useState("");
  const [aiMode, setAiMode] = useState("CACHE");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [modal, setModal] = useState<"create" | "edit" | "draft" | "reset" | "rule" | "detail" | "merge" | "archive" | "allowance" | null>(null);
  const [editing, setEditing] = useState<Concept | undefined>();
  const [draft, setDraft] = useState<Draft | null>(null);
  const [detail, setDetail] = useState<Detail | null>(null);
  const [mergeTarget, setMergeTarget] = useState("");
  const [kindFilter, setKindFilter] = useState<Kind>("DOMAIN");

  useEffect(() => {
    Promise.all([api<Config>("/pretest/config"), api<Identity>("/me").catch(() => null)])
      .then(([c, me]) => { setConfig(c); setIdentity(me); })
      .catch(e => setError(e.message)).finally(() => setReady(true));
  }, []);
  const refresh = useCallback(async () => {
    if (!identity) return;
    const value = await request<Workspace>("/workspace", collection);
    setWorkspace(value);
  }, [collection, identity]);
  useEffect(() => {
    if (!identity) return;
    let alive = true;
    const poll = async () => { try { const w = await request<Workspace>("/workspace", collection); if (alive) setWorkspace(w); } catch (e) { if (alive) setError((e as Error).message); } };
    poll(); const timer = setInterval(poll, 2000);
    return () => { alive = false; clearInterval(timer); };
  }, [identity, collection]);
  const version = workspace?.organization.control.version;
  const selectionSignature = JSON.stringify({ selected, collection, version });
  const repoPath = `/repos?view=${view}&q=${encodeURIComponent(query)}&language=${encodeURIComponent(language)}&visibility=${visibility}&concept=${encodeURIComponent(conceptFilter)}&days=${days}`;
  useEffect(() => {
    if (!identity || section !== "repos") return;
    let alive = true;
    const timer = setTimeout(async () => {
      setLoading(true);
      try { const data = await request<RepoPage>(repoPath, collection); if (alive) setPage(data); }
      catch (e) { if (alive) setError((e as Error).message); }
      finally { if (alive) setLoading(false); }
    }, 180);
    return () => { alive = false; clearTimeout(timer); };
  }, [identity, collection, section, repoPath, version]);

  useEffect(() => {
    if (!identity || !selected.length) return;
    let alive = true;
    request<RepoSummary>("/repos/summary", collection, identity.csrf_token, "POST", { repo_keys: selected }).then(value => { if (alive) { setSelectedSummary(value); setSelectedSummaryKey(selectionSignature); } }).catch(() => { if (alive) setSelectedSummary(null); });
    return () => { alive = false; };
  }, [identity, collection, selected, version, selectionSignature]);

  const concepts = Object.values(workspace?.organization.concepts || {}).filter(c => c.active);
  const conceptsById = workspace?.organization.concepts || {};
  const org = workspace?.organization;
  const runs = Object.values(org?.runs || {}).sort((a, b) => b.created_at.localeCompare(a.created_at));
  const current = org?.control.active_run ? org.runs[org.control.active_run] : null;
  const suggestions = Object.values(org?.suggestions || {}).filter(s => s.status === "PROPOSED");
  const drafts = Object.values(org?.drafts || {}).filter(d => d.status === "DRAFT");

  const save: Action = async (path, method = "POST", body) => {
    const value = await request(path, collection, identity?.csrf_token, method, body);
    await refresh();
    return value;
  };
  async function act(fn: () => Promise<unknown>, success?: string) {
    setBusy(true); setError(""); setNotice("");
    try { await fn(); if (success) setNotice(success); }
    catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }
  function navigate(s: string, v = view, concept = s === "organizer" ? conceptFilter : "") { setSection(s); setView(v); setConceptFilter(concept); if (s !== "organizer") setSelected([]); setError(""); }
  function changeFilter(change: () => void) { change(); if (selected.length) setNotice("Selection cleared because the filter scope changed."); setSelected([]); }
  function switchCollection(value: string) { setCollection(value); setWorkspace(null); setPage(null); setView(value === "samples" ? "all" : "my"); setSection("repos"); setSelected([]); setConceptFilter(""); setQuery(""); setModal(null); setDropAssignment(null); }

  function assign(keys: string[], conceptId: string, operation = "ADD") { return act(() => save("/repos/associations", "POST", { repo_keys: keys, concept_ids: [conceptId], operation }), operation === "ADD" ? "Manual assignment saved." : "Membership removed; AI rejection protected."); }
  function dropRepositories(payload: string, conceptId: string) {
    let keys: string[];
    try { const value = JSON.parse(payload); keys = value.keys; if (!Array.isArray(keys) || keys.some(k => typeof k !== "string") || keys.length > 500) throw new Error(); }
    catch { keys = [payload]; }
    keys = [...new Set(keys)];
    if (!keys.length) return;
    if (keys.length > 1 || conceptsById[conceptId]?.kind === "DOMAIN") { setDropAssignment({ keys, concept: conceptId }); setDropProject(""); }
    else assign(keys, conceptId);
  }
  async function inspect(repo: Repo) { await act(async () => { setDetail(await request<Detail>(`/repos/detail?key=${encodeURIComponent(repo.key)}`, collection)); setModal("detail"); }); }

  if (!ready) return <div className="wm-boot">Opening your workspace…</div>;
  if (!identity) return <div className="wm-login"><div className="wm-login-brand"><ZenCat /> GitHub Manager</div><main><div className="wm-login-copy"><p className="wm-eyebrow">A clearer view of your work</p><h1>Your repositories.<br />A workspace that<br /><em>makes sense.</em></h1><p>Find the connections across your GitHub work. Build a taxonomy with AI, make it your own, and keep every decision in your hands.</p><div className="wm-login-features"><span>✓ GitHub stays the source of truth</span><span>✓ AI suggestions, human decisions</span><span>✓ Private content stays out of model inputs</span></div></div><section className="wm-login-card"><div className="wm-github-symbol"><Icon name="lock" size={30} /></div><h2>Connect your GitHub account</h2><p>Sign in to discover your repositories and create your local workspace.</p>{error && <div className="wm-error" role="alert">{error}</div>}<a className={`wm-primary ${!config?.oauth_configured ? "wm-disabled" : ""}`} aria-disabled={!config?.oauth_configured} href={config?.oauth_configured ? "/api/v1/auth/github/start" : undefined}>Continue with GitHub <span>↗</span></a><small>OAuth App · GitHub calls are read-only.<br />GitHub’s repo scope includes write permission; this app does not write to repositories.</small>{!config?.oauth_configured && <div className="wm-notice"><h3>One-time OAuth App setup</h3><p>Use the existing Phase 0 setup guide and configure backend/.env.</p><code>{config?.callback_url}</code></div>}<div className="wm-local-note"><span className="wm-dot" /> Runs locally on your computer</div></section></main><footer>Local MVP · Next.js + FastAPI · Your GitHub token stays on the server</footer></div>;

  return <div className="wm-app">
    <WorkspaceShell identity={identity} collection={collection} section={section} view={view} activeConcept={conceptFilter} concepts={concepts} counts={section === "repos" ? page?.concept_counts || workspace?.concept_counts : workspace?.concept_counts} suggestions={suggestions.length} syncDisabled={busy || !!current || !!org?.control.resetting} emptySamples={collection === "samples" && !workspace?.coverage.repos} navigate={navigate} switchCollection={switchCollection} create={() => { setEditing(undefined); setModal("create"); }} sync={() => act(() => save("/sync"), "Sync queued; repositories remain available while it runs.")} loadSamples={() => act(() => save("/samples/load"), "Approved public and synthetic samples loaded.")} assign={dropRepositories} signOut={() => act(async () => { await api("/auth/logout", identity.csrf_token); setIdentity(null); setWorkspace(null); })}>
      <div className="wm-content"><div className="wm-page-heading"><div><p className="wm-eyebrow">{collection === "samples" ? "PUBLIC + SYNTHETIC DEMO" : "YOUR GITHUB WORKSPACE"}</p><h1>{section === "repos" ? conceptFilter ? conceptsById[conceptFilter]?.name || "Repositories" : ({ my: "My repositories", favorites: "Favorites", latest: "Latest work", uncategorized: "No project", no_labels: "No labels", needs_review: "Needs review", no_match: "No AI match", failed: "Failed or blocked analysis", stale: "Stale analysis", all: collection === "samples" ? "Demo collection" : "Access candidates" }[view]) : section === "content" ? "Make it your own." : "Organization, with oversight."}</h1><p>{section === "repos" ? view === "all" && collection === "github" ? "All repositories discovered through your account. Open details → Include in My Repos for relevant candidates; organization visibility alone does not establish a personal relationship." : "Explore your work. Connect the pieces. Keep control of the details." : section === "content" ? "Your canonical vocabulary, project structure, and organization rules." : "Review AI suggestions and keep your organization up to date."}</p></div></div>
      {collection === "samples" && <div className="wm-sample-note"><strong>Demo collection</strong> Approved cached public data and labeled synthetic initiatives. These samples do not imply ownership, favorites, or real GitHub activity.</div>}
      {error && <div className="wm-error" role="alert">{error}<button aria-label="Dismiss error" onClick={() => setError("")}>×</button></div>}{notice && <div className="wm-notice" role="status">{notice}<button aria-label="Dismiss notification" onClick={() => setNotice("")}>×</button></div>}
      {!workspace ? <div className="wm-panel wm-empty">Opening your persistent workspace…</div> : <>
        <ExplorerSummary summary={section === "repos" && page?.summary ? page.summary : workspace.summary || { ...workspace.coverage, suggestions: workspace.coverage.review }} selected={selected.length} selectedSummary={selectedSummaryKey === selectionSignature ? selectedSummary : null} />
        {current && <div className="wm-progress" role="status"><span className="wm-spinner" /><div><strong>{title(current.kind)} · {title(current.status)}</strong><p>{current.message || "Queued for the local worker"} · {current.processed}/{current.total}</p></div><progress aria-label={`${title(current.kind)} progress`} max={current.total || 1} value={current.total ? current.processed : undefined} /></div>}
        {org?.control.resetting && <div className="wm-notice">Reset fences are active. Selected data is hidden while cleanup is verified.</div>}
        {section === "repos" && <section className="wm-panel"><ExplorerFilters query={query} language={language} visibility={visibility} days={days} latest={view === "latest"} languages={page?.languages || []} total={page?.total || 0} loading={loading} onQuery={value => changeFilter(() => setQuery(value))} onLanguage={value => changeFilter(() => setLanguage(value))} onVisibility={value => changeFilter(() => setVisibility(value))} onDays={value => changeFilter(() => setDays(value))} clear={() => changeFilter(() => { setQuery(""); setLanguage(""); setVisibility("all"); })} />
          <div className="wm-coverage-detail"><label>Organization view<select aria-label="Organization status view" value={view} onChange={e => changeFilter(() => { setView(e.target.value); setConceptFilter(""); })}>{[["my", "My Repos"], ["all", "Entire collection"], ["favorites", "Favorites"], ["latest", "Latest Work"], ["uncategorized", "No project"], ["no_labels", "No labels"], ["needs_review", "Needs review"], ["no_match", "No AI match"], ["failed", "Failed / blocked"], ["stale", "Stale analysis"]].map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label><span>Accepted labels: {page?.summary?.projects ?? 0} with projects · {page?.summary?.topics ?? 0} with topics · {page?.summary?.tags ?? 0} with tags · {page?.summary?.no_labels ?? 0} with no labels. Counts overlap.</span></div>
          {view === "latest" && <div className="wm-table-note">User-authored contribution dates, not repository push times. {workspace.activity_coverage.map(s => `${s.status}: ${s.note}`).join(" ") || "Activity coverage has not been observed yet."}</div>}
          {selected.length > 0 && <div className="wm-bulk"><strong>{selected.length} selected</strong><select aria-label="Bulk assignment concept" value={assignment} onChange={e => setAssignment(e.target.value)}><option value="">Choose a project, topic or tag</option>{kinds.filter(k => k !== "DOMAIN").map(k => <optgroup key={k} label={title(k)}>{concepts.filter(c => c.kind === k).map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</optgroup>)}</select><button className="wm-primary wm-small" disabled={!assignment || busy} onClick={() => assign(selected, assignment)}>Add membership</button><button className="wm-secondary wm-small" disabled={!assignment || busy} onClick={() => assign(selected, assignment, "REMOVE")}>Remove & protect</button><button className="wm-link" onClick={() => setSelected([])}>Clear</button></div>}
          <div className="wm-table-scroll"><table className="wm-table"><thead><tr><th className="wm-check-col"><input type="checkbox" aria-label="Select visible repositories" checked={!!page?.items.length && page.items.every(r => selected.includes(r.key))} onChange={e => { const keys = page?.items.map(r => r.key) || []; setSelected(old => e.target.checked ? [...new Set([...old, ...keys])] : old.filter(key => !keys.includes(key))); }} /></th><th>Repository</th><th>Organization</th><th>Language</th><th>Activity / source</th><th /></tr></thead><tbody>{page?.items.map(repo => <tr key={repo.key} draggable onDragStart={e => { const keys = selected.includes(repo.key) ? selected : [repo.key]; e.dataTransfer.setData("text/plain", JSON.stringify({ keys })); e.dataTransfer.effectAllowed = "copy"; }}><td><input type="checkbox" aria-label={`Select ${repo.name}`} checked={selected.includes(repo.key)} onChange={e => setSelected(e.target.checked ? [...selected, repo.key] : selected.filter(k => k !== repo.key))} /></td><td><div className="wm-repo-name"><span className="wm-repo-icon"><Icon name="repos" size={17} /></span>{repo.html_url ? <a href={repo.html_url} target="_blank" rel="noreferrer">{repo.name} ↗</a> : <button className="wm-link" onClick={() => inspect(repo)}>{repo.name}</button>}<span className="wm-visibility">{repo.synthetic ? "Synthetic" : repo.private ? "Private" : "Public"}</span></div><p className="wm-description">{repo.description || "No description yet"}</p>{repo.starred && <span className="wm-mini-label">☆ Starred </span>}{repo.watched && <span className="wm-mini-label">◉ Watched</span>}</td><td><div className="wm-chips">{Object.entries(repo.organization).map(([cid, edge]) => <button key={cid} title={`${edge.source} · click to filter`} className={`wm-chip wm-${conceptsById[cid]?.kind.toLowerCase()}`} onClick={() => navigate("repos", "all", cid)}>{conceptsById[cid]?.name}<small>{edge.source === "USER" ? "✓" : "↳"}</small></button>)}{!Object.keys(repo.organization).length && <span className="wm-muted">No labels</span>}{repo.review_count > 0 && <button className="wm-review-chip" onClick={() => navigate("organizer")}>{repo.review_count} to review</button>}</div>{repo.analysis && <small className={`wm-analysis-status ${repo.analysis.stale ? "is-stale" : ""}`} title={`${repo.analysis.ai_analyzed ? "Validated AI analysis recorded" : "No confirmed real AI receipt"}${repo.analysis.last_success?.model ? ` · ${repo.analysis.last_success.model}` : ""}`}>{displayLabel(repo.analysis.status)}{repo.analysis.stale ? " · Update available" : repo.analysis.last_success && repo.analysis.freshness === "UNKNOWN" ? " · Input history unavailable" : ""}{repo.analysis.last_success?.evidence === "FIXTURE" ? " · Test fixture" : ""}</small>}</td><td><span className="wm-language-dot" />{repo.language || "Unknown"}</td><td><span className="wm-activity">{repo.last_user_activity ? date(repo.last_user_activity) : "No observed activity"}</span><small className="wm-source">{repo.sources.map(title).join(" · ")}</small></td><td><button className="wm-icon-button" aria-label={`Details for ${repo.name}`} onClick={() => inspect(repo)}><Icon name="external" size={18} /></button></td></tr>)}</tbody></table></div>
          {!page?.items.length && <div className="wm-empty"><div className="wm-empty-icon">▤</div><h3>{loading ? "Loading repositories…" : "Room for your work."}</h3><p>{collection === "samples" && view !== "all" ? "Samples are kept separate from your GitHub relationships. Open Demo samples to explore them." : workspace.coverage.repos ? "No repositories match this view or filter." : collection === "samples" ? "Load the approved public and synthetic collection to try the full workflow." : "Sync GitHub to import your repositories, stars and watches."}</p>{!workspace.coverage.repos && <button className="wm-primary" disabled={busy || !!current} onClick={() => act(() => save(collection === "samples" ? "/samples/load" : "/sync"))}>{collection === "samples" ? "Load demo samples" : "Start GitHub sync"}</button>}</div>}
          {page?.next_cursor && <div className="wm-table-footer"><button className="wm-secondary" disabled={busy} onClick={() => act(async () => { const next = await request<RepoPage>(`${repoPath}&cursor=${encodeURIComponent(page.next_cursor || "")}`, collection); setPage(current => current?.next_cursor === page.next_cursor ? { ...next, items: [...current.items, ...next.items] } : current); })}>Load more</button></div>}
        </section>}
        {section === "content" && <><LogoSettings /><section className="wm-panel"><div className="wm-panel-heading"><div><h2>Canonical content</h2><p>Stable identities, editable names. Your changes are always yours.</p></div><button className="wm-primary" onClick={() => { setEditing(undefined); setModal("create"); }}>+ Create concept</button></div><div className="wm-tabs">{kinds.map(k => <button key={k} className={kindFilter === k ? "is-active" : ""} onClick={() => setKindFilter(k)}>{title(k)}s <small>{concepts.filter(c => c.kind === k).length}</small></button>)}</div><div className="wm-concept-grid">{concepts.filter(c => c.kind === kindFilter).map(c => <article className="wm-concept-card" key={c.id}><span className={`wm-kind wm-${c.kind.toLowerCase()}`}>{c.kind}</span><h3>{c.name}</h3><p>{c.description || "Add a description to guide organization."}</p>{c.domain && <small>Domain: {conceptsById[c.domain]?.name}</small>}<div className="wm-chips">{c.aliases.map(a => <span className="wm-chip" key={a}>{a}</span>)}</div><p className="wm-concept-members">{workspace.concept_counts?.[c.id]?.accepted ?? 0} accepted repositories · {workspace.concept_counts?.[c.id]?.pending ?? 0} awaiting review</p><div className="wm-card-actions"><button className="wm-link" onClick={() => navigate("repos", "all", c.id)}>View repositories</button><button className="wm-link" onClick={() => { setEditing(c); setModal("edit"); }}>Edit</button>{!c.protected && <><button className="wm-link" onClick={() => { setEditing(c); setMergeTarget(""); setModal("merge"); }}>Merge</button><button className="wm-link wm-red" onClick={() => { setEditing(c); setModal("archive"); }}>Archive</button></>}</div></article>)}{!concepts.some(c => c.kind === kindFilter) && <div className="wm-empty"><h3>No {title(kindFilter)}s yet</h3><p>Create one, or discover a taxonomy with AI.</p></div>}</div></section><section className="wm-panel"><div className="wm-panel-heading"><div><h2>Organization rules</h2><p>Preview exact metadata/name conditions before applying them.</p></div><button className="wm-secondary" onClick={() => setModal("rule")}>+ Create rule</button></div>{Object.values(org?.rules || {}).map(r => <div className="wm-rule-row" key={r.id}><div><strong>{r.name}</strong><p>{r.field} {r.operator} “{r.value}” → {conceptsById[r.concept_id]?.name}</p></div><button className="wm-link wm-red" onClick={() => act(() => save(`/content/rules/${r.id}`, "DELETE"))}>Remove</button></div>)}{!Object.keys(org?.rules || {}).length && <p className="wm-padding wm-muted">No rules yet. Manual assignments and AI suggestions remain independent.</p>}</section></>}
        {section === "organizer" && <><section className="wm-panel"><div className="wm-panel-heading"><div><h2>Your organization controls</h2><p>Taxonomy revision {org?.control.revision} · processed revision {org?.control.processed_revision} · {org?.control.revision === org?.control.processed_revision ? "Up to date" : "Updates available"}</p></div><span className="wm-badge">Review-first AI</span></div><div className="wm-organizer-controls"><label>Inference mode<select aria-label="Inference mode" value={aiMode} onChange={e => setAiMode(e.target.value)}><option value="CACHE">Reuse validated cached AI</option><option value="LIVE" disabled={!workspace.live_ai_enabled}>Live AI · within approved cap</option><option value="RULES">Rules only · no model calls</option></select></label><RunSetup key={collection} collection={collection} csrf={identity.csrf_token} inference={aiMode} selected={selected} scope={{ view, q: query, language, visibility, concept: conceptFilter, days }} preferences={workspace.preferences} revision={org?.control.revision || 0} active={busy || !!current} canManage={workspace.can_manage_allowance} refreshed={refresh} /><div className="wm-budget"><span>Fixed HTTP request window <strong>{workspace.budget.http?.used ?? "—"}/{workspace.budget.http?.limit ?? "—"} HTTP requests</strong></span><span>Fixed generation window <strong>{workspace.budget.generations?.used ?? "—"}/{workspace.budget.generations?.limit ?? "—"} generations</strong></span><span>Experiment spend <strong>${workspace.budget.estimated_usd?.toFixed(6) ?? "unavailable"} / ${workspace.budget.cap_usd ?? 5}</strong></span><span>Available for runs <strong>${workspace.budget.run_budget?.available_usd.toFixed(6) ?? "—"}</strong></span><span>Run holds <strong>${workspace.budget.run_budget?.held_usd.toFixed(6) ?? "—"}</strong></span><small>Lifetime: {workspace.budget.http?.lifetime_used ?? "—"} application HTTP attempts · {workspace.budget.calls ?? "—"} cumulative generation reservations. Token-count requests are included. Prior benchmark spending is preserved.</small>{workspace.can_manage_allowance && <button className="wm-secondary wm-small" disabled={busy || !!current || workspace.budget.unavailable} onClick={() => setModal("allowance")}>Manage API allowance</button>}</div>{(workspace.budget.http?.remaining === 0 || workspace.budget.generations?.remaining === 0) && <p className="wm-notice">Fixed-count mode has reached a request or generation limit. Adaptive cost mode can use an explicitly reviewed run grant. {workspace.can_manage_allowance ? "Use Manage API allowance to start a new window or update selected limits." : "A configured local budget operator can renew the allowance."} Cached AI, extraction and rules remain available.</p>}<AutomationSettings key={collection + ":auto"} control={workspace.organization.control} status={workspace.automation} collection={collection} csrf={identity.csrf_token} disabled={busy || !!current} refreshed={refresh} /></div></section>
          {drafts.length > 0 && <section className="wm-panel"><div className="wm-panel-heading"><div><h2>Taxonomy drafts</h2><p>Review and publish a canonical vocabulary.</p></div><span className="wm-badge">{drafts.length} awaiting review</span></div>{drafts.map(d => <div className="wm-rule-row" key={d.id}><div><strong>{d.proposals.length} proposed concepts</strong><p>{d.model} · {d.evidence === "REPLAY" ? "Reused AI result" : d.evidence === "FIXTURE" ? "Test fixture" : "Live AI"}</p></div><div className="wm-actions"><button className="wm-link wm-red" onClick={() => act(() => save(`/taxonomy/drafts/${d.id}`, "DELETE"))}>Reject draft</button><button className="wm-primary" onClick={() => { setDraft(d); setModal("draft"); }}>Review draft</button></div></div>)}</section>}
          <ReviewQueue key={collection + ":review"} suggestions={suggestions} concepts={conceptsById} edges={org?.edges || {}} names={workspace.repository_names || {}} collection={collection} csrf={identity.csrf_token} disabled={busy || !!current} refreshed={refresh} />
          <section className="wm-panel"><div className="wm-panel-heading"><div><h2>Run history</h2><p>Committed outcomes, including partial failures and reused inference.</p></div></div>{runs.map(r => <details className="wm-run" key={r.id}><summary><span className={`wm-status ${activeRun(r.status) ? "wm-running" : r.status === "COMPLETED" ? "wm-success" : "wm-warning"}`}>{title(r.status)}</span><strong>{title(r.kind)}</strong><span>{r.processed}/{r.total} processed · {r.failed} failed</span><small>{date(r.created_at)}</small></summary><p>{r.message}</p>{r.budget_mode && <p>{r.budget_mode === "ADAPTIVE" ? "Adaptive cost budget" : "Fixed count limits"}{r.budget_outcome && ` · ${r.budget_outcome.http_used} HTTP attempts · $${r.budget_outcome.estimated_usd.toFixed(6)} estimated usage · $${r.budget_outcome.reserved_usd.toFixed(6)} unresolved`}</p>}{Object.entries(r.outcomes || {}).map(([key, value]) => <div className="wm-outcome" key={key}><strong>{key}</strong><span>{title(value.status)} · {title(value.evidence)} {value.model && `· ${value.model}`} {value.seconds !== undefined && `· ${value.seconds}s`}</span>{value.error && <small>{value.error}</small>}</div>)}</details>)}{!runs.length && <p className="wm-padding wm-muted">Your first run will appear here.</p>}</section>
          <section className="wm-panel wm-reset-card"><div><h2>Reset & rediscovery</h2><p>Clear selected organization state and start again. Your GitHub data and earlier readiness evidence are preserved.</p></div><button className="wm-secondary wm-red" onClick={() => setModal("reset")}>Preview reset</button>{org?.audit.map(a => <small key={a.id}>{date(a.at)} · {title(a.status)} · {a.verified ? "Cleanup verified" : "Pending verification"}</small>)}</section>
        </>}
        <section className="wm-coverage"><div><h3>Source coverage</h3><span>Last synced {date(workspace.synced_at)}</span></div><div className="wm-coverage-items">{workspace.source_coverage.map(s => <div key={s.source}><strong>{title(s.source)}</strong><span>{s.status}{s.count === undefined || s.count === null ? "" : ` · ${s.count}`}</span><p>{s.note}</p></div>)}{!workspace.source_coverage.length && <p>No sources observed yet. Sync to begin.</p>}</div></section>
      </>}
      <footer className="wm-footer">Local workspace · Your taxonomy and assignments survive restarts. <span>Sign in again after a backend restart.</span></footer>
    </div></WorkspaceShell>
    {dropAssignment && <Modal title="Confirm repository assignment" close={() => setDropAssignment(null)}><p>Add {dropAssignment.keys.length} {dropAssignment.keys.length === 1 ? "repository" : "repositories"} to {conceptsById[dropAssignment.concept]?.name}. Existing memberships are preserved; this makes no AI calls.</p>{conceptsById[dropAssignment.concept]?.kind === "DOMAIN" && <label className="wm-form">Project in this domain<select aria-label="Project for domain drop" value={dropProject} onChange={e => setDropProject(e.target.value)}><option value="">Choose an existing project</option>{concepts.filter(c => c.kind === "PROJECT" && c.domain === dropAssignment.concept).map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select><small>Domains derive through projects. Create a project in Content settings if this domain has none.</small></label>}<ul className="wm-drop-repositories">{dropAssignment.keys.map(key => <li key={key}>{workspace?.repository_names?.[key] || key}</li>)}</ul><div className="wm-actions"><button className="wm-primary" disabled={busy || (conceptsById[dropAssignment.concept]?.kind === "DOMAIN" && !dropProject)} onClick={() => act(async () => { await save("/repos/associations", "POST", { repo_keys: dropAssignment.keys, concept_ids: [dropProject || dropAssignment.concept], operation: "ADD" }); setDropAssignment(null); }, "Manual assignments saved. Previous AI analysis retained.")}>Confirm membership addition</button><button className="wm-secondary" onClick={() => setDropAssignment(null)}>Cancel</button></div></Modal>}
    {(modal === "create" || modal === "edit") && <ConceptForm key={editing?.id || "new"} item={modal === "edit" ? editing : undefined} concepts={concepts} save={save} close={() => setModal(null)} />}
    {modal === "draft" && draft && <DraftReview draft={draft} revision={org?.control.revision || 0} collection={collection} csrf={identity.csrf_token} save={save} close={result => { setModal(null); setNotice(result === "published" ? "Taxonomy published. Use classification to propose repository associations." : result === "saved" ? "Draft saved. Review and publish when ready." : ""); }} />}
    {modal === "reset" && <ResetPanel save={save} close={() => setModal(null)} />}
    {modal === "allowance" && workspace && <AllowancePanel budget={workspace.budget} collection={collection} save={save} close={() => setModal(null)} />}
    {modal === "rule" && <RuleForm concepts={concepts} save={save} close={() => setModal(null)} />}
    {modal === "merge" && editing && <Modal title="Merge canonical concepts" close={() => setModal(null)}><p className="wm-muted">Merge {editing.name} into an existing {title(editing.kind)}. The target keeps its ID; memberships are combined and aliases retained.</p><label className="wm-form">Merge into<select value={mergeTarget} onChange={e => setMergeTarget(e.target.value)}><option value="">Choose a target</option>{concepts.filter(c => c.kind === editing.kind && c.id !== editing.id && !c.protected).map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select></label><div className="wm-actions"><button className="wm-primary" disabled={!mergeTarget || busy} onClick={() => act(async () => { await save("/taxonomy/concepts/merge", "POST", { source: editing.id, target: mergeTarget }); setModal(null); }, "Concepts merged with stable target identity.")}>Confirm merge</button></div></Modal>}
    {modal === "archive" && editing && <Modal title={`Archive ${editing.name}`} close={() => setModal(null)}><p>Dependent memberships will be removed. Names and aliases remain reserved to prevent AI recreation.</p>{editing.kind === "DOMAIN" && <p>Surviving projects move to the protected Unassigned domain.</p>}<div className="wm-actions"><button className="wm-secondary" onClick={() => setModal(null)}>Cancel</button><button className="wm-danger" disabled={busy} onClick={() => act(async () => { await save(`/taxonomy/concepts/${editing.id}`, "DELETE"); setModal(null); })}>Archive concept</button></div></Modal>}
    {modal === "detail" && detail && <Modal title={detail.repo.name} close={() => setModal(null)}><div className="wm-detail-meta"><span className="wm-badge">{detail.repo.synthetic ? "Synthetic example" : detail.repo.private ? "Private · AI blocked" : "Public GitHub"}</span><p>{detail.repo.description || "No description"}</p><div>Language: {detail.repo.language || "Unknown"} · Branch: {detail.repo.default_branch || "Unknown"} · Branch count: {detail.repo.branch_count ?? "Unknown"}</div><small>Trusted source: {detail.repo.source} · ID {detail.repo.id ?? "synthetic"}</small></div><h3>Analysis and coverage</h3><p>{detail.repo.analysis ? `${displayLabel(detail.repo.analysis.status)}${detail.repo.analysis.stale ? " · Update available" : ""}` : "Analysis status appears in the repository list"}. Domains derive from project membership; Topics and Tags are independent facets.</p><h3>Current memberships</h3><div className="wm-chips">{Object.entries(org?.edges[detail.repo.key] || {}).map(([cid, edge]) => <span className="wm-chip" key={cid}>{conceptsById[cid]?.name} · {edge.source}<button aria-label={`Remove ${conceptsById[cid]?.name}`} onClick={() => assign([detail.repo.key], cid, "REMOVE")}>×</button></span>)}</div><label className="wm-form">Add membership<select value={assignment} onChange={e => setAssignment(e.target.value)}><option value="">Choose a concept</option>{concepts.filter(c => c.kind !== "DOMAIN").map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select></label><button className="wm-primary wm-small" disabled={!assignment || busy} onClick={() => assign([detail.repo.key], assignment)}>Save manual membership</button>{collection === "github" && !detail.repo.eligible && <button className="wm-secondary wm-small" onClick={() => act(() => save(`/repos/inclusion?key=${encodeURIComponent(detail.repo.key)}&include=${!detail.repo.included}`), "Explicit inclusion updated.")}>{detail.repo.included ? "Remove explicit inclusion" : "Include in My Repos"}</button>}<h3>Reusable intelligence</h3>{detail.profile ? <><p className="wm-muted">{detail.profile.extractor} · source {detail.profile.sha?.slice(0, 12) || "metadata only"}</p><div className="wm-chips">{detail.profile.phrases.map(p => <span className="wm-chip" key={p.text}>{p.text}</span>)}</div>{detail.profile.evidence.map(e => <div className="wm-evidence" key={e.id}><strong>{e.id} · {e.section}</strong><p>{e.text}</p></div>)}</> : <p className="wm-muted">{detail.repo.private ? "Private README-derived evidence is excluded under the approved policy." : "Extract evidence from AI Organization before inspecting this profile."}</p>}</Modal>}
  </div>;
}
