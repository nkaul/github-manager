"use client";

import { useEffect, useRef, useState } from "react";
import { request, WorkspaceError } from "@/lib/workspace";
import { Icon } from "./Icons";
import { SearchableSelect } from "./SearchableSelect";

export type ReferenceKind = "DOMAIN" | "PROJECT" | "TOPIC" | "TAG";
export type RegistryContext = { revision: number; sha256: string };
export type ReferenceConcept = { id: string; name: string; kind: string; description: string; aliases?: string[]; domain: string | null; active?: boolean; origin?: string; repository_count?: number };
export type RegistryView = { registry: ReferenceConcept[]; registry_context: RegistryContext; extension_count: number };
type Conflict = { term: string; message: string; existing?: ReferenceConcept };
type Form = { name: string; description: string; aliases: string; domain: string };
const blank = (): Form => ({ name: "", description: "", aliases: "", domain: "" });
const title = (kind: string) => kind[0] + kind.slice(1).toLowerCase();
const normalized = (value: string) => value.normalize("NFKC").toLocaleLowerCase().replace(/[^\p{L}\p{N}+#]+/gu, " ").trim();

export function CorpusConceptDialog({ kind, initialName, concepts, context, csrf, onRegistry, onChoose, close }: {
  kind: ReferenceKind; initialName: string; concepts: ReferenceConcept[]; context: RegistryContext; csrf: string;
  onRegistry: (value: RegistryView) => void; onChoose: (concept: ReferenceConcept) => void; close: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [form, setForm] = useState<Form>(() => ({ ...blank(), name: initialName }));
  const [parent, setParent] = useState<Form>(blank);
  const [creatingParent, setCreatingParent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [stale, setStale] = useState(false);
  const [conflictParent, setConflictParent] = useState(false);
  useEffect(() => { if (dialog.current && !dialog.current.open) dialog.current.showModal(); }, []);
  const domains = concepts.filter(c => c.kind === "DOMAIN" && c.active !== false);
  const similar = concepts.filter(c => {
    const query = normalized(form.name);
    return c.kind === kind && query.length >= 2 && [c.name, ...(c.aliases || [])].some(term => normalized(term).includes(query) || query.includes(normalized(term)));
  }).slice(0, 5);
  const aliases = (value: string) => value.split(/[,\n]/).map(a => a.trim()).filter(Boolean);

  function chooseExisting(concept: ReferenceConcept, asParent = false) {
    if (asParent) { setForm(value => ({ ...value, domain: concept.id })); setCreatingParent(false); setConflicts([]); setError(""); setNotice(`Using existing Domain “${concept.name}”. Your Project fields are preserved.`); }
    else onChoose(concept);
  }
  async function refresh() {
    setBusy(true); setError("");
    try { onRegistry(await request<RegistryView>("/corpus/registry", "ground-truth")); setStale(false); setConflicts([]); setNotice("Vocabulary refreshed. Your fields are preserved; review and submit again."); }
    catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }
  async function create(asParent = false) {
    const input = asParent ? parent : form;
    if (busy || stale || !input.name.trim() || !input.description.trim()) return;
    if (!asParent && (creatingParent || (kind === "PROJECT" && !input.domain))) return;
    setBusy(true); setError(""); setConflicts([]); setConflictParent(asParent);
    try {
      const value = await request<RegistryView & { concept: ReferenceConcept }>("/corpus/registry/concepts", "ground-truth", csrf, "POST", {
        kind: asParent ? "DOMAIN" : kind, name: input.name.trim(), description: input.description.trim(),
        aliases: aliases(input.aliases), domain: !asParent && kind === "PROJECT" ? input.domain || null : null,
        registry_context: context,
      });
      onRegistry(value);
      if (asParent) { setForm(previous => ({ ...previous, domain: value.concept.id })); setCreatingParent(false); setParent(blank()); setNotice(`Domain “${value.concept.name}” created and selected. Finish your Project below.`); }
      else onChoose(value.concept);
    } catch (e) {
      setError((e as Error).message);
      if (e instanceof WorkspaceError) {
        setStale(e.code === "CORPUS_REGISTRY_CONFLICT");
        setConflicts((e.payload?.conflicts as Conflict[]) || []);
      }
    } finally { setBusy(false); }
  }
  return <dialog ref={dialog} className="corpus-dialog corpus-concept-dialog" aria-labelledby="corpus-concept-title" onCancel={event => { event.preventDefault(); if (!busy) close(); }}>
    <form onSubmit={event => { event.preventDefault(); void create(); }}>
      <div className="corpus-dialog-heading"><h2 id="corpus-concept-title">Create {title(kind)}</h2><button type="button" className="wm-icon-button" disabled={busy} aria-label="Close concept creation" onClick={close}><Icon name="close" size={16} /></button></div>
      <div className="corpus-dialog-body corpus-concept-fields">
        <p>{kind === "DOMAIN" ? "Create a broad category, then select it as a Project’s parent. Domains appear on repositories through their Projects." : "Define a reusable concept. Creating it will add it to your review; confirmation still needs source evidence and your review."}</p>
        {error && <div className="corpus-concept-error" role="alert">{!conflicts.length && <p>{error}</p>}{conflicts.map((item, index) => <div key={index}><p>{item.message}</p>{item.existing && <><p>{item.existing.description}</p><button type="button" className="wm-secondary" disabled={busy || stale} onClick={() => chooseExisting(item.existing!, conflictParent)}>Use existing {title(item.existing.kind)} {item.existing.name}</button></>}</div>)}{stale && <button type="button" className="wm-secondary" disabled={busy} onClick={() => void refresh()}>Refresh vocabulary</button>}</div>}
        {notice && <p className="corpus-concept-notice" role="status">{notice}</p>}
        <label className="corpus-field">Name<input aria-label={`New ${title(kind)} name`} required maxLength={100} value={form.name} disabled={busy} onChange={event => { setForm(value => ({ ...value, name: event.target.value })); setConflicts([]); }} placeholder={kind === "PROJECT" ? "Product or initiative name" : "Canonical name"} /></label>
        {similar.length > 0 && <div className="corpus-concept-similar"><strong>Possible existing concepts</strong><p>Check the definitions before creating another concept.</p>{similar.map(item => <div key={item.id}><span><strong>{item.name}</strong><small>{item.description}</small></span><button type="button" className="wm-secondary" disabled={busy || stale} onClick={() => chooseExisting(item)}>Use existing</button></div>)}</div>}
        <label className="corpus-field">Definition<textarea aria-label={`New ${title(kind)} definition`} required maxLength={1000} rows={3} disabled={busy} value={form.description} onChange={event => setForm(value => ({ ...value, description: event.target.value }))} placeholder="What belongs here? Explain its purpose and boundaries." /></label>
        <label className="corpus-field">Aliases <small>Optional · separate with commas</small><input aria-label={`New ${title(kind)} aliases`} maxLength={1200} disabled={busy} value={form.aliases} onChange={event => { setForm(value => ({ ...value, aliases: event.target.value })); setConflicts([]); }} /></label>
        {kind === "PROJECT" && <>
          <label className="corpus-field">Parent Domain<SearchableSelect aria-label="New Project parent Domain" required value={form.domain} disabled={busy} onChange={domain => setForm(value => ({ ...value, domain }))} options={[{ value: "", label: "Choose a Domain", disabled: true }, ...domains.map(c => ({ value: c.id, label: c.name, searchText: (c.aliases || []).join(" ") }))]} /></label>
          {!creatingParent ? <button type="button" className="wm-link" disabled={busy} onClick={() => { setCreatingParent(true); setError(""); setConflicts([]); }}>Create a missing Domain</button> : <fieldset className="corpus-concept-parent" disabled={busy}><legend>Create parent Domain</legend><label className="corpus-field">Domain name<input aria-label="New parent Domain name" maxLength={100} value={parent.name} onChange={event => setParent(value => ({ ...value, name: event.target.value }))} /></label><label className="corpus-field">Domain definition<textarea aria-label="New parent Domain definition" rows={2} maxLength={1000} value={parent.description} onChange={event => setParent(value => ({ ...value, description: event.target.value }))} /></label><div className="corpus-concept-parent-actions"><button type="button" className="wm-secondary" disabled={stale || !parent.name.trim() || !parent.description.trim()} onClick={() => void create(true)}>Create Domain &amp; select</button><button type="button" className="wm-link" onClick={() => { setCreatingParent(false); setError(""); setConflicts([]); }}>Cancel Domain creation</button></div></fieldset>}
        </>}
        <p className="corpus-helper">Your additions are saved separately from the original corpus and A/B suggestions. Assignments stay editable until you save a draft or confirm.</p>
      </div>
      <div className="corpus-dialog-footer"><button type="button" className="wm-secondary" disabled={busy} onClick={close}>Cancel</button><button type="submit" className="wm-primary" disabled={busy || stale || creatingParent || !form.name.trim() || !form.description.trim() || (kind === "PROJECT" && !form.domain)}>{busy ? "Saving…" : kind === "DOMAIN" ? "Create Domain" : `Create ${title(kind)} & assign`}</button></div>
    </form>
  </dialog>;
}
