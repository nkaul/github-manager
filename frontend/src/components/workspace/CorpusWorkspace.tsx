"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import type { Identity } from "@/lib/api";
import { request, WorkspaceError } from "@/lib/workspace";
import { Icon, ZenCat } from "./Icons";
import { SearchableSelect } from "./SearchableSelect";
import { LabelChip } from "./LabelChip";
import { AnnotationInputs, AnnotationPilotQueue, CorpusAnnotations, type AgentAnnotation, type PilotDetail, type PilotSummary } from "./CorpusAnnotations";
import { CorpusConceptDialog, type ReferenceConcept, type ReferenceKind, type RegistryContext, type RegistryView } from "./CorpusConceptDialog";
import "./corpus.css";

type Kind = "PROJECT" | "TOPIC" | "TAG";
type AnnotationScope = "all" | "pilot" | "initial_queue";
type Dimensions = { projects: boolean; topics: boolean; tags: boolean };
type Citation = { path?: string; quote?: string; start_line?: number; end_line?: number; app_input_channel?: string; field?: string; sha256?: string };
type Concept = ReferenceConcept & { repository_count: number; reviewed_repository_count?: number };
type Label = { id: string; name: string; kind: string; decision?: string; rationale?: string; evidence: Citation[] };
type Editor = { purpose: string; label_ids: string[]; dimensions: Dimensions; notes: string; additional_evidence: Record<string, { path: string; quote: string }>; annotation_pilot_sha256: string | null; registry_context: RegistryContext | null };
type Review = Omit<Editor, "annotation_pilot_sha256"> & { revision: number; status: string; history: unknown[]; annotation_pilot_sha256?: string | null };
type Draft = Editor & { revision: number; base_review_revision: number; stale?: boolean; status?: string };
type Row = { repository_id: number; full_name: string; url: string; sampling_domain: string; purpose: string; language: string; split: string; review_status: string; labels: Label[]; commit: string; has_draft?: boolean; draft_revision?: number };
type RepoPage = { items: Row[]; total: number; offset?: number; limit?: number };
type Summary = { release_id: string; manifest_sha256: string; total: number; human_confirmed: number; reviewed: number; drafts?: number; domains: Record<string, number>; registry: Concept[]; registry_context: RegistryContext; registry_extension_count: number; annotation_pilot?: PilotSummary };
type Detail = { inventory: Row; proposal: { purpose: string; status: string; labels: Label[]; derived_domains: string[]; conflicts: unknown[]; cross_reviews?: unknown[] }; review: Review | null; draft?: Draft | null; files: { path: string; role: string; bytes: number; sha256: string }[]; eligibility: unknown; read_coverage: unknown; release_id: string; manifest_sha256: string; registry_context: RegistryContext; registry: ReferenceConcept[]; review_registry_context: RegistryContext; annotation_pilot?: PilotDetail };
type Source = { path: string; sha256: string; commit: string; text: string; role?: string };
type ActiveCitation = Citation & { label: string; rationale?: string };
const collection = "ground-truth";
const kinds: Kind[] = ["PROJECT", "TOPIC", "TAG"];
const dimensionKey = { PROJECT: "projects", TOPIC: "topics", TAG: "tags" } as const;
const emptyDimensions = (): Dimensions => ({ projects: false, topics: false, tags: false });
const readable = (value: string) => value.replaceAll("_", " ").toLowerCase().replace(/^./, c => c.toUpperCase());
const emptyEditor = (): Editor => ({ purpose: "", label_ids: [], dimensions: emptyDimensions(), notes: "", additional_evidence: {}, annotation_pilot_sha256: null, registry_context: null });
function editorFrom(detail: Detail, useDraft = true): Editor {
  const saved = (useDraft && detail.draft) || detail.review;
  return {
    purpose: saved?.purpose ?? detail.proposal.purpose ?? "",
    label_ids: [...(saved?.label_ids ?? [...new Set(detail.proposal.labels.filter(l => (l.decision || "SUPPORTED") === "SUPPORTED").map(l => l.id))])],
    dimensions: { ...emptyDimensions(), ...saved?.dimensions }, notes: saved?.notes || "",
    additional_evidence: structuredClone(saved?.additional_evidence || {}), annotation_pilot_sha256: saved?.annotation_pilot_sha256 || null, registry_context: detail.registry_context,
  };
}
function withRegistry(previous: Summary | null, value: RegistryView): Summary | null {
  if (!previous || previous.registry_context.revision > value.registry_context.revision) return previous;
  const counts = new Map(previous.registry.map(concept => [concept.id, concept]));
  return { ...previous, registry_context: value.registry_context, registry_extension_count: value.extension_count,
    registry: value.registry.map(concept => ({ ...concept, repository_count: counts.get(concept.id)?.repository_count || 0, reviewed_repository_count: counts.get(concept.id)?.reviewed_repository_count || 0 })) };
}
const fingerprint = (editor: Editor) => JSON.stringify({ ...editor, label_ids: [...editor.label_ids].sort() });

export function CorpusWorkspace({ identity, switchCollection, signOut }: { identity: Identity; switchCollection: (value: string) => void; signOut: () => void }) {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [page, setPage] = useState<RepoPage | null>(null);
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("");
  const [assignedDomain, setAssignedDomain] = useState("");
  const [concepts, setConcepts] = useState<Record<Kind, string>>({ PROJECT: "", TOPIC: "", TAG: "" });
  const [status, setStatus] = useState("");
  const [labelBasis, setLabelBasis] = useState("proposals");
  const [annotationScope, setAnnotationScope] = useState<AnnotationScope>("all");
  const [offset, setOffset] = useState(0);
  const [version, setVersion] = useState(0);
  const [detail, setDetail] = useState<Detail | null>(null);
  const [editor, setEditor] = useState<Editor>(emptyEditor);
  const [source, setSource] = useState<Source | null>(null);
  const [sourcePath, setSourcePath] = useState("");
  const [sourceBusy, setSourceBusy] = useState(false);
  const [sourceError, setSourceError] = useState("");
  const [citation, setCitation] = useState<ActiveCitation | null>(null);
  const [expandedEvidence, setExpandedEvidence] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [queueBusy, setQueueBusy] = useState(false);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [sourceOpen, setSourceOpen] = useState(false);
  const [activePanel, setActivePanel] = useState("review");
  const [conflict, setConflict] = useState(false);
  const [latest, setLatest] = useState<Detail | null>(null);
  const [retryNext, setRetryNext] = useState<number | null>(null);
  const [createKind, setCreateKind] = useState<ReferenceKind | null>(null);
  const [createName, setCreateName] = useState("");
  const [registryStale, setRegistryStale] = useState(false);
  const baseline = useRef(fingerprint(emptyEditor()));
  const activeRepository = useRef<number | null>(null);
  const detailGeneration = useRef(0);
  const sourceGeneration = useRef(0);
  const busyRef = useRef(false);
  const autoOpen = useRef(true);
  const pendingLeave = useRef<(() => void) | null>(null);
  const sourceOpener = useRef<HTMLElement | null>(null);
  const leaveDialog = useRef<HTMLDialogElement>(null);
  const pilotDialog = useRef<HTMLDialogElement>(null);
  const comparisonDialog = useRef<HTMLDialogElement>(null);
  const guideDialog = useRef<HTMLDialogElement>(null);
  const filterPanel = useRef<HTMLDivElement>(null);
  const filterTrigger = useRef<HTMLButtonElement>(null);
  const sourcePane = useRef<HTMLElement>(null);
  const closeSourceButton = useRef<HTMLButtonElement>(null);
  const searchInput = useRef<HTMLInputElement>(null);
  const confirmButton = useRef<HTMLButtonElement>(null);
  const byId = useMemo(() => Object.fromEntries((summary?.registry || []).map(c => [c.id, c])), [summary]);
  const dirty = Boolean(detail && fingerprint(editor) !== baseline.current);
  const original = new Set(detail?.proposal.labels.filter(l => (l.decision || "SUPPORTED") === "SUPPORTED").map(l => l.id));
  const added = editor.label_ids.filter(id => !original.has(id));
  const missingEvidence = added.filter(id => !editor.additional_evidence[id]?.path || !editor.additional_evidence[id]?.quote.trim());
  const reviewedCount = Object.values(editor.dimensions).filter(Boolean).length;
  const canConfirm = Boolean(detail && editor.purpose.trim() && reviewedCount === 3 && !missingEvidence.length && !conflict && !registryStale && !busy);
  const selectedDomains = [...new Set(editor.label_ids.filter(id => byId[id]?.kind === "PROJECT").map(id => byId[id]?.domain).filter((id): id is string => Boolean(id)))];
  const filterCount = Number(Boolean(domain)) + Number(Boolean(assignedDomain)) + Object.values(concepts).filter(Boolean).length;
  const loadSummary = useCallback(() => request<Summary>("/corpus", collection).then(value => setSummary(previous => previous && previous.registry_context.revision > value.registry_context.revision ? { ...value, registry: previous.registry, registry_context: previous.registry_context, registry_extension_count: previous.registry_extension_count } : value)), []);
  const working = useCallback((value: boolean) => { busyRef.current = value; setBusy(value); }, []);
  const closeEvidence = useCallback(() => {
    setSourceOpen(false);
    requestAnimationFrame(() => {
      const opener = sourceOpener.current;
      if (opener?.isConnected && !opener.closest("[inert]") && !sourcePane.current?.classList.contains("is-open")) opener.focus();
    });
  }, []);

  const openSource = useCallback(async (rid: number, path: string) => {
    const generation = ++sourceGeneration.current;
    setSourcePath(path); setSource(null); setSourceBusy(true); setSourceError("");
    try {
      const value = await request<Source>(`/corpus/repos/${rid}/source?path=${encodeURIComponent(path)}`, collection);
      if (generation === sourceGeneration.current && rid === activeRepository.current) setSource(value);
    } catch (e) {
      if (generation === sourceGeneration.current && rid === activeRepository.current) setSourceError((e as Error).message);
    } finally {
      if (generation === sourceGeneration.current && rid === activeRepository.current) setSourceBusy(false);
    }
  }, []);

  const loadRepository = useCallback(async (rid: number) => {
    const generation = ++detailGeneration.current;
    const previous = activeRepository.current;
    activeRepository.current = rid;
    working(true); setError(""); setCitation(null); setSourceOpen(false); setFiltersOpen(false);
    try {
      const value = await request<Detail>(`/corpus/repos/${rid}`, collection);
      if (generation !== detailGeneration.current) return false;
      const next = editorFrom(value);
      baseline.current = fingerprint(next);
      setDetail(value); setEditor(next); setRegistryStale(false); setSummary(previous => withRegistry(previous, { registry: value.registry, registry_context: value.registry_context, extension_count: value.registry.filter(c => c.origin === "HUMAN_REFERENCE_EXTENSION").length })); setExpandedEvidence(""); setConflict(Boolean(value.draft?.stale)); setLatest(value.draft?.stale ? value : null);
      setActivePanel("review"); setRetryNext(null); setSource(null); setSourcePath(""); ++sourceGeneration.current;
      if (value.draft?.stale) setNotice("Your saved draft has an older base. Compare the latest review before saving.");
      if (value.files[0]) void openSource(rid, value.files[0].path);
      return true;
    } catch (e) {
      if (generation === detailGeneration.current) { activeRepository.current = previous; setError((e as Error).message); }
      return false;
    } finally { if (generation === detailGeneration.current) working(false); }
  }, [openSource, working]);

  const queuePath = useCallback((at: number) => {
    const params = new URLSearchParams({ q: query, domain, assigned_domain: assignedDomain, status, offset: String(at), limit: "25", label_basis: labelBasis, annotation_scope: annotationScope });
    Object.values(concepts).filter(Boolean).forEach(id => params.append("concept_ids", id));
    return `/corpus/repos?${params}`;
  }, [query, domain, assignedDomain, status, concepts, annotationScope, labelBasis]);

  useEffect(() => {
    let alive = true;
    request<Summary>("/corpus/open", collection, identity.csrf_token, "POST").then(value => { if (alive) setSummary(value); }).catch(e => { if (alive) setError(e.message); });
    return () => { alive = false; };
  }, [identity.csrf_token]);
  useEffect(() => {
    let alive = true;
    const timer = setTimeout(() => {
      setQueueBusy(true);
      request<RepoPage>(queuePath(offset), collection).then(value => {
        if (!alive) return;
        setPage(value);
        if (activeRepository.current === null && autoOpen.current && value.items[0]) void loadRepository(value.items[0].repository_id);
      }).catch(e => { if (alive) setError(e.message); }).finally(() => { if (alive) setQueueBusy(false); });
    }, 180);
    return () => { alive = false; clearTimeout(timer); };
  }, [queuePath, offset, version, loadRepository]);
  useEffect(() => () => { ++detailGeneration.current; ++sourceGeneration.current; }, []);
  useEffect(() => {
    const beforeUnload = (event: BeforeUnloadEvent) => { if (dirty) { event.preventDefault(); event.returnValue = ""; } };
    window.addEventListener("beforeunload", beforeUnload);
    return () => window.removeEventListener("beforeunload", beforeUnload);
  }, [dirty]);
  useEffect(() => {
    if (!filtersOpen) return;
    const outside = (event: PointerEvent) => { if (!filterPanel.current?.contains(event.target as Node) && !filterTrigger.current?.contains(event.target as Node) && !(event.target as Element).closest?.(".wm-select-popup")) setFiltersOpen(false); };
    const escape = (event: KeyboardEvent) => { if (event.defaultPrevented) return; if (event.key === "Escape") { event.stopPropagation(); setFiltersOpen(false); filterTrigger.current?.focus(); } };
    document.addEventListener("pointerdown", outside); document.addEventListener("keydown", escape);
    return () => { document.removeEventListener("pointerdown", outside); document.removeEventListener("keydown", escape); };
  }, [filtersOpen]);
  useEffect(() => {
    if (!sourceOpen) return;
    closeSourceButton.current?.focus();
    const key = (event: KeyboardEvent) => {
      if (event.defaultPrevented) return;
      if (event.key === "Escape") { event.preventDefault(); event.stopPropagation(); closeEvidence(); }
      if (event.key === "Tab") {
        const controls = [...(sourcePane.current?.querySelectorAll<HTMLElement>("button,input,select,textarea,summary,a[href],[tabindex]") || [])].filter(node => node.tabIndex >= 0 && !node.hasAttribute("disabled") && node.getClientRects().length > 0);
        if (event.shiftKey && document.activeElement === controls[0]) { event.preventDefault(); controls.at(-1)?.focus(); }
        else if (!event.shiftKey && document.activeElement === controls.at(-1)) { event.preventDefault(); controls[0]?.focus(); }
      }
    };
    const resize = () => { if (window.innerWidth >= 1400 || window.innerWidth <= 780) setSourceOpen(false); };
    document.addEventListener("keydown", key); window.addEventListener("resize", resize);
    return () => { document.removeEventListener("keydown", key); window.removeEventListener("resize", resize); };
  }, [sourceOpen, closeEvidence]);
  useEffect(() => { if (source && citation?.quote) document.getElementById("corpus-source-quote")?.scrollIntoView({ block: "center" }); }, [source, citation]);
  useEffect(() => {
    const key = (event: KeyboardEvent) => {
      if (event.defaultPrevented) return;
      if (document.querySelector(".corpus-app dialog[open]")) return;
      if (event.key === "/" && !(event.target as HTMLElement).closest("input,textarea,[contenteditable=true]")) { event.preventDefault(); searchInput.current?.focus(); }
      if ((event.ctrlKey || event.metaKey) && event.key === "Enter" && !event.repeat && !confirmButton.current?.disabled) { event.preventDefault(); confirmButton.current?.click(); }
    };
    document.addEventListener("keydown", key); return () => document.removeEventListener("keydown", key);
  }, []);

  function requestLeave(action: () => void) {
    if (busyRef.current) { setNotice("Wait for the current request to finish before leaving this review."); return; }
    if (!dirty) { action(); return; }
    pendingLeave.current = action; leaveDialog.current?.showModal();
  }
  function navigate(rid: number) {
    if (activeRepository.current === rid && detail?.inventory.repository_id === rid) { setActivePanel("review"); return; }
    requestLeave(() => { autoOpen.current = false; setNotice(""); void loadRepository(rid); });
  }
  function openPilotRepository(rid: number, scope: "pilot" | "initial_queue") {
    pilotDialog.current?.close();
    requestLeave(() => {
      autoOpen.current = false; setNotice(""); setAnnotationScope(scope); setQuery(""); setDomain(""); setAssignedDomain(""); setConcepts({ PROJECT: "", TOPIC: "", TAG: "" }); setStatus(""); setOffset(0);
      if (activeRepository.current === rid && detail?.inventory.repository_id === rid) setActivePanel("review");
      else void loadRepository(rid);
    });
  }
  function changeAnnotationScope(value: AnnotationScope) {
    if (value === annotationScope) return;
    requestLeave(() => {
      autoOpen.current = true; activeRepository.current = null; ++detailGeneration.current; ++sourceGeneration.current;
      setDetail(null); setSource(null); setCitation(null); setSourceOpen(false); setNotice(""); setAnnotationScope(value); setOffset(0);
    });
  }
  function closeReview() {
    requestLeave(() => { autoOpen.current = false; activeRepository.current = null; ++detailGeneration.current; ++sourceGeneration.current; setDetail(null); setSource(null); setCitation(null); setSourceOpen(false); });
  }
  function updateSelected(next: string[]) {
    const changed = new Set([...editor.label_ids.filter(id => !next.includes(id)), ...next.filter(id => !editor.label_ids.includes(id))].map(id => byId[id]?.kind));
    setEditor(value => ({ ...value, label_ids: next, dimensions: { projects: value.dimensions.projects && !changed.has("PROJECT"), topics: value.dimensions.topics && !changed.has("TOPIC"), tags: value.dimensions.tags && !changed.has("TAG") } }));
  }
  function updateEvidence(id: string, evidence: { path: string; quote: string }) {
    const key = dimensionKey[byId[id]?.kind as Kind];
    setEditor(value => ({ ...value, additional_evidence: { ...value.additional_evidence, [id]: evidence }, dimensions: key ? { ...value.dimensions, [key]: false } : value.dimensions }));
  }
  function addKnownLabel(id: string) {
    if (!id || editor.label_ids.includes(id)) return;
    updateSelected([...editor.label_ids, id]);
    if (!original.has(id)) setExpandedEvidence(id);
  }
  function showEvidence() {
    setActivePanel("evidence");
    if (window.innerWidth > 780 && window.innerWidth < 1400) { sourceOpener.current = document.activeElement as HTMLElement; setSourceOpen(true); }
  }
  function inspectEvidence(id: string) {
    if (!detail) return;
    const label = detail.proposal.labels.find(item => item.id === id && (item.decision || "SUPPORTED") === "SUPPORTED") || detail.proposal.labels.find(item => item.id === id);
    const proof = editor.additional_evidence[id] || label?.evidence.find(item => item.path && detail.files.some(file => file.path === item.path)) || label?.evidence[0];
    setCitation({ ...proof, label: byId[id]?.name || id, rationale: label?.rationale || (original.has(id) ? "Read the source and decide whether it establishes this label." : "Your added positive needs an exact saved-source quote.") });
    if (proof?.path && detail.files.some(file => file.path === proof.path)) void openSource(detail.inventory.repository_id, proof.path);
    else if (proof) { ++sourceGeneration.current; setSource(null); setSourcePath(""); setSourceBusy(false); setSourceError(""); }
    else if (!original.has(id)) setExpandedEvidence(id);
    showEvidence();
  }
  function stageAnnotation(annotation: AgentAnnotation) {
    if (!detail?.annotation_pilot?.sidecar_manifest_sha256) return;
    if ((dirty || detail.review || detail.draft) && !window.confirm("Replace the editable form with this annotator's suggestions? Saved records remain unchanged until you explicitly save.")) return;
    const evidence: Editor["additional_evidence"] = {};
    for (const label of annotation.labels) {
      if (original.has(label.id)) continue;
      const proof = label.evidence.find(item => detail.files.some(file => file.path === item.path));
      if (proof) evidence[label.id] = { path: proof.path, quote: proof.quote };
    }
    setEditor({ purpose: annotation.purpose, label_ids: [...annotation.positive_ids], dimensions: emptyDimensions(), notes: editor.notes, additional_evidence: evidence, annotation_pilot_sha256: detail.annotation_pilot.sidecar_manifest_sha256, registry_context: editor.registry_context });
    setError(""); setNotice("Suggestions staged, not saved. Review all three groups and their source evidence."); comparisonDialog.current?.close(); setActivePanel("review");
  }
  function payload() {
    return { ...editor, additional_evidence: Object.fromEntries(Object.entries(editor.additional_evidence).filter(([id]) => editor.label_ids.includes(id))) };
  }
  function openCreation(kind: ReferenceKind, initialName = "") {
    if (busyRef.current || registryStale || !summary) return;
    setCreateName(initialName); setCreateKind(kind);
  }
  function applyRegistry(value: RegistryView) {
    setSummary(previous => withRegistry(previous, value));
    setDetail(previous => previous ? { ...previous, registry_context: value.registry_context, registry: value.registry } : previous);
    setEditor(previous => ({ ...previous, registry_context: value.registry_context, dimensions: emptyDimensions() }));
    setRegistryStale(false);
  }
  function chooseCreatedConcept(concept: ReferenceConcept) {
    setCreateKind(null);
    if (concept.kind === "DOMAIN") { setNotice(`Domain “${concept.name}” is available. Choose it as a Project’s parent; it is not assigned directly to this repository.`); return; }
    const key = dimensionKey[concept.kind as Kind];
    setEditor(previous => ({ ...previous, label_ids: [...new Set([...previous.label_ids, concept.id])], dimensions: { ...previous.dimensions, [key]: false } }));
    if (!original.has(concept.id)) setExpandedEvidence(concept.id);
    setNotice(`${readable(concept.kind)} “${concept.name}” selected in your editable review. Add supporting evidence and review before confirming.`);
  }
  async function refreshVocabulary() {
    if (busyRef.current) return;
    working(true); setError("");
    try { applyRegistry(await request<RegistryView>("/corpus/registry", collection)); setNotice("Vocabulary refreshed. Your edits are preserved; review the three groups before saving again."); }
    catch (e) { setError((e as Error).message); }
    finally { working(false); }
  }
  async function saveDraft() {
    if (!detail || busyRef.current || conflict || registryStale) return false;
    working(true); setError("");
    try {
      const draft = await request<Draft>(`/corpus/repos/${detail.inventory.repository_id}/draft`, collection, identity.csrf_token, "PUT", {
        ...payload(), status: "NEEDS_REVIEW", release_id: detail.release_id, manifest_sha256: detail.manifest_sha256,
        expected_revision: detail.draft?.revision || 0, base_review_revision: detail.review?.revision || 0,
      });
      baseline.current = fingerprint(editor);
      setDetail({ ...detail, draft }); setVersion(value => value + 1);
      setNotice(`Draft saved · revision ${draft.revision}. This is not a human confirmation.`);
      void loadSummary().catch(() => {});
      return true;
    } catch (e) { handleSaveError(e); return false; }
    finally { working(false); }
  }
  function handleSaveError(e: unknown) {
    setError((e as Error).message);
    if (e instanceof WorkspaceError && e.code === "CORPUS_REGISTRY_CONFLICT") { setRegistryStale(true); setNotice("Your edits are preserved. Refresh the review vocabulary before saving again."); }
    if (e instanceof WorkspaceError && ["CORPUS_REVIEW_CONFLICT", "CORPUS_DRAFT_CONFLICT"].includes(e.code || "")) { setConflict(true); setLatest(null); setNotice("Your edits are preserved. Compare the latest saved record before applying another save."); }
  }
  async function advanceAfterSave(rid: number) {
    try {
      const params = new URLSearchParams(queuePath(0).split("?")[1]);
      params.delete("offset"); params.delete("limit");
      const neighbors = await request<{ next: Row | null; next_index: number | null }>(`/corpus/repos/${rid}/neighbors?${params}`, collection);
      if (!neighbors.next || neighbors.next_index === null) { setRetryNext(null); setNotice("Review saved. You reached the end of the current queue."); return; }
      setOffset(Math.floor(neighbors.next_index / 25) * 25);
      const opened = await loadRepository(neighbors.next.repository_id);
      if (!opened) { setRetryNext(rid); setNotice("Review saved; the next repository could not be opened. Retry navigation without saving again."); }
      else setRetryNext(null);
    } catch {
      setRetryNext(rid); setNotice("Review saved; the next queue item could not be loaded. Retry navigation without saving again.");
    }
  }
  async function saveReview(decision: "HUMAN_CONFIRMED" | "UNRESOLVED", advance = false) {
    if (!detail || busyRef.current || conflict || registryStale) return;
    if (decision === "HUMAN_CONFIRMED" && !canConfirm) return;
    if (missingEvidence.length) { setError("New positive labels need exact saved-source quotes before a final decision. Save an incomplete draft while you gather evidence."); return; }
    working(true); setError("");
    try {
      const review = await request<Review>(`/corpus/repos/${detail.inventory.repository_id}/review`, collection, identity.csrf_token, "PUT", {
        ...payload(), status: decision, release_id: detail.release_id, manifest_sha256: detail.manifest_sha256,
        expected_revision: detail.review?.revision || 0, expected_draft_revision: detail.draft?.revision || 0,
      });
      const saved = { ...detail, review, draft: null };
      const savedEditor = editorFrom(saved, false);
      baseline.current = fingerprint(savedEditor); setEditor(savedEditor); setDetail(saved); setVersion(value => value + 1);
      setNotice(`Review saved · revision ${review.revision}. ${decision === "HUMAN_CONFIRMED" ? "Human confirmed." : "Needs evidence."}`);
      try { await loadSummary(); } catch { setNotice(`Review saved · revision ${review.revision}; summary refresh failed. Your decision is saved.`); }
      if (advance) await advanceAfterSave(detail.inventory.repository_id);
    } catch (e) { handleSaveError(e); }
    finally { working(false); }
  }
  async function compareLatest() {
    if (!detail || busyRef.current) return;
    working(true);
    try { setLatest(await request<Detail>(`/corpus/repos/${detail.inventory.repository_id}`, collection)); }
    catch (e) { setError((e as Error).message); }
    finally { working(false); }
  }
  function resolveConflict(reapply: boolean) {
    if (!latest) return;
    applyRegistry({ registry: latest.registry, registry_context: latest.registry_context, extension_count: latest.registry.filter(c => c.origin === "HUMAN_REFERENCE_EXTENSION").length });
    const savedEditor = editorFrom(latest, false);
    baseline.current = fingerprint(savedEditor);
    setDetail(latest); setEditor(reapply ? { ...editor, registry_context: latest.registry_context, dimensions: emptyDimensions() } : savedEditor);
    setConflict(false); setLatest(null); setError(""); setNotice(reapply ? "Your edits were reapplied to the latest base. Review all three groups again before confirming." : "Latest saved review loaded. No new decision was saved.");
    if (latest.files[0]) void openSource(latest.inventory.repository_id, latest.files[0].path);
  }
  function changeFilter(action: () => void) { action(); setOffset(0); }
  function keepReviewFocusVisible(scroller: HTMLDivElement, target: HTMLElement) {
    requestAnimationFrame(() => {
      if (!scroller.isConnected || document.activeElement !== target) return;
      const bounds = scroller.getBoundingClientRect();
      const footer = scroller.parentElement?.querySelector(".corpus-decision-footer")?.getBoundingClientRect();
      const focused = target.getBoundingClientRect();
      const top = bounds.top + 12;
      const bottom = Math.min(bounds.bottom, footer?.top ?? bounds.bottom) - 12;
      if (focused.bottom > bottom) scroller.scrollTop += focused.bottom - bottom;
      else if (focused.top < top) scroller.scrollTop -= top - focused.top;
    });
  }
  const activeFilters = [
    ...(domain ? [{ key: "sampling", label: `Sampling: ${readable(domain)}`, clear: () => setDomain("") }] : []),
    ...(assignedDomain ? [{ key: "assigned", label: `Assigned: ${byId[assignedDomain]?.name || assignedDomain}`, clear: () => setAssignedDomain("") }] : []),
    ...kinds.filter(kind => concepts[kind]).map(kind => ({ key: kind, label: `${readable(kind)}: ${byId[concepts[kind]]?.name || concepts[kind]}`, clear: () => setConcepts(value => ({ ...value, [kind]: "" })) })),
  ];
  const citationUnavailable = Boolean(citation && (!citation.path || !detail?.files.some(file => file.path === citation.path)));
  const citationMetadata = Boolean(citation?.app_input_channel?.includes("METADATA") || (!citation?.path && citation?.quote));
  const sourceQuoteIndex = source && citation?.path === source.path && citation.quote ? source.text.indexOf(citation.quote) : -1;
  const outsideQueue = detail && !page?.items.some(row => row.repository_id === detail.inventory.repository_id);
  const bindingMatches = Boolean(latest && detail && latest.manifest_sha256 === detail.manifest_sha256 && latest.inventory.commit === detail.inventory.commit);

  return <div className="wm-app corpus-app">
    <header className="wm-header corpus-header" inert={sourceOpen}>
      <Link href="/" className="wm-brand" aria-label="GitHub Manager home" onClick={event => { event.preventDefault(); requestLeave(() => switchCollection("github")); }}><ZenCat /><span>GitHub Manager</span></Link>
      <label className="corpus-workspace-switch"><span className="sr-only">Workspace</span><SearchableSelect aria-label="Workspace collection" value={collection} onChange={value => requestLeave(() => switchCollection(value))} options={[{ value: "github", label: "My GitHub workspace" }, { value: "samples", label: "Public + synthetic demo" }, { value: collection, label: "Public - Ground Truth" }]} /></label>
      <nav className="wm-header-actions"><button className="wm-secondary" onClick={() => guideDialog.current?.showModal()}>Review guide</button><Link className="wm-secondary corpus-export" href="/api/v1/corpus/reviews/export?collection=ground-truth" prefetch={false} download><Icon name="download" size={16} />Export reviews</Link><button className="wm-secondary corpus-signout" onClick={() => requestLeave(signOut)}>Sign out</button></nav>
    </header>
    <main className="corpus-main">
      <div className="corpus-page-heading" inert={sourceOpen}><div><h1>Public - Ground Truth</h1><p>Original proposals need your review. Unlisted labels remain unknown.</p></div><div className="corpus-stats" aria-label="Corpus review progress"><span><strong>{summary?.total ?? "…"}</strong> repositories</span><span><strong>{summary?.registry.length ?? "…"}</strong> review concepts</span><span><strong>{summary?.human_confirmed ?? 0}</strong> Confirmed by you</span></div></div>
      <div className="corpus-toolbar" inert={sourceOpen}>
        <label className="corpus-search"><Icon name="search" size={16} /><input ref={searchInput} type="search" aria-label="Search corpus repositories" value={query} onChange={e => changeFilter(() => setQuery(e.target.value))} placeholder="Search repositories…" /><kbd>/</kbd></label>
        <SearchableSelect className="corpus-annotation-scope" aria-label="Repository review scope" value={annotationScope} disabled={busy} onChange={value => changeAnnotationScope(value as AnnotationScope)} options={[{ value: "all", label: `All repositories · ${summary?.total ?? "…"}` }, { value: "initial_queue", label: `Initial human review · ${summary?.annotation_pilot?.queue.filter(row => row.audit_selection).length ?? 0}`, disabled: summary?.annotation_pilot?.state !== "READY" }, { value: "pilot", label: `Agent A/B pilot · ${summary?.annotation_pilot?.queue.length ?? 0}`, disabled: summary?.annotation_pilot?.state !== "READY" }]} />
        <SearchableSelect className="corpus-status" aria-label="Review status" value={status} onChange={value => changeFilter(() => setStatus(value))} options={[{ value: "", label: "All review statuses" }, ...["PROPOSED", "DISPUTED", "NEEDS_REVIEW", "UNRESOLVED", "HUMAN_CONFIRMED"].map(value => ({ value, label: readable(value) }))]} />
        <button ref={filterTrigger} className={`wm-secondary corpus-filter-trigger ${filtersOpen ? "is-active" : ""}`} aria-expanded={filtersOpen} aria-controls="corpus-filter-panel" onClick={() => setFiltersOpen(value => !value)}><Icon name="filter" size={16} />Filters{filterCount > 0 && <span>{filterCount}</span>}</button>
        <div className="corpus-toolbar-end"><span>{labelBasis === "reviewed" ? "Your saved reviews" : "Original proposals"}</span>{summary?.annotation_pilot && summary.annotation_pilot.state !== "NOT_RUN" && <button className="wm-secondary" onClick={() => pilotDialog.current?.showModal()}>Annotation pilot{summary.annotation_pilot.state === "READY" ? ` · ${summary.annotation_pilot.queue.length}` : ""}</button>}<button className="wm-secondary corpus-show-source" onClick={showEvidence}><Icon name="repos" size={16} />Evidence</button></div>
        {filtersOpen && <div id="corpus-filter-panel" ref={filterPanel} className="corpus-filter-panel" role="dialog" aria-label="Filter corpus repositories"><div className="corpus-popover-heading"><h2>Filter repositories</h2><button className="wm-icon-button" aria-label="Close filters" onClick={() => { setFiltersOpen(false); filterTrigger.current?.focus(); }}><Icon name="close" size={16} /></button></div><div className="corpus-filter-body"><label>Label filter basis<SearchableSelect aria-label="Label filter basis" value={labelBasis} onChange={value => changeFilter(() => setLabelBasis(value))} options={[{ value: "proposals", label: "Original proposals" }, { value: "reviewed", label: "Your saved reviews" }]} /><small>Choose your saved reviews to browse added concepts. Drafts stay separate.</small></label><label>Sampling domain<SearchableSelect aria-label="Sampling domain" value={domain} onChange={value => changeFilter(() => setDomain(value))} options={[{ value: "", label: "All domains" }, ...Object.entries(summary?.domains || {}).sort().map(([value, count]) => ({ value, label: `${readable(value)} · ${count}` }))]} /><small>Coverage sampling, not a membership.</small></label><label>Assigned domain<SearchableSelect aria-label="Assigned domain" value={assignedDomain} onChange={value => changeFilter(() => setAssignedDomain(value))} options={[{ value: "", label: "All assigned domains" }, ...(summary?.registry || []).filter(c => c.kind === "DOMAIN").map(c => ({ value: c.id, label: `${c.name} · ${labelBasis === "reviewed" ? c.reviewed_repository_count || 0 : c.repository_count}` }))]} /><small>Derived from Projects in the selected label basis.</small></label>{kinds.map(kind => <label key={kind}>{readable(kind)}<SearchableSelect aria-label={`Filter by ${kind.toLowerCase()}`} value={concepts[kind]} onChange={value => changeFilter(() => setConcepts(previous => ({ ...previous, [kind]: value })))} options={[{ value: "", label: `All ${kind.toLowerCase()}s` }, ...(summary?.registry || []).filter(c => c.kind === kind).sort((a,b) => a.name.localeCompare(b.name)).map(c => ({ value: c.id, label: c.name }))]} /></label>)}</div><div className="corpus-popover-footer"><button className="wm-link" onClick={() => changeFilter(() => { setDomain(""); setAssignedDomain(""); setConcepts({ PROJECT: "", TOPIC: "", TAG: "" }); })}>Clear filters</button><button className="wm-secondary" onClick={() => { setFiltersOpen(false); filterTrigger.current?.focus(); }}>Done</button></div></div>}
      </div>
      {activeFilters.length > 0 && <div className="corpus-active-filters" inert={sourceOpen}>{activeFilters.map(item => <button key={item.key} className="corpus-filter-chip" onClick={() => changeFilter(item.clear)} aria-label={`Remove ${item.label} filter`}>{item.label}<Icon name="close" size={12} /></button>)}</div>}
      {error && <div className="corpus-message corpus-error" role="alert" inert={sourceOpen}><span>{error}</span><button aria-label="Dismiss error" onClick={() => setError("")}><Icon name="close" size={16} /></button></div>}
      {notice && <div className="corpus-message corpus-notice" role="status" inert={sourceOpen}><span>{notice}</span><button aria-label="Dismiss notice" onClick={() => setNotice("")}><Icon name="close" size={16} /></button></div>}
      <div className="corpus-mobile-tabs" inert={sourceOpen} role="tablist" aria-label="Review workspace sections" onKeyDown={event => { const panels = ["queue", "review", "evidence"]; const index = panels.indexOf(activePanel); const next = event.key === "ArrowRight" ? (index + 1) % panels.length : event.key === "ArrowLeft" ? (index + panels.length - 1) % panels.length : event.key === "Home" ? 0 : event.key === "End" ? panels.length - 1 : -1; if (next < 0) return; event.preventDefault(); setActivePanel(panels[next]); setSourceOpen(false); event.currentTarget.querySelectorAll<HTMLButtonElement>("[role=tab]")[next]?.focus(); }}>{["queue", "review", "evidence"].map(panel => <button key={panel} role="tab" tabIndex={activePanel === panel ? 0 : -1} aria-selected={activePanel === panel} aria-controls={`corpus-${panel}-pane`} onClick={() => { setActivePanel(panel); setSourceOpen(false); }}>{readable(panel)}{panel === "queue" ? ` · ${page?.total ?? 0}` : ""}</button>)}</div>
      <div className="corpus-layout" data-active-panel={activePanel}>
        <section id="corpus-queue-pane" className="corpus-queue" inert={sourceOpen} aria-label="Repository queue"><div className="corpus-pane-heading"><div><h2>Review queue</h2><span>{queueBusy ? "Updating…" : `${page?.total ?? 0} results`}</span></div><span>{page?.total ? offset + 1 : 0}–{Math.min(offset + 25, page?.total || 0)}</span></div><div className="corpus-queue-list" aria-busy={queueBusy}>{page?.items.map(row => <button key={row.repository_id} className="corpus-queue-item" aria-label={`Review ${row.full_name}`} aria-current={detail?.inventory.repository_id === row.repository_id ? "true" : undefined} disabled={busy} onClick={() => navigate(row.repository_id)}><strong>{row.full_name}</strong><p>{row.purpose || "Purpose requires review"}</p><span><small>{row.has_draft ? "Draft · " : ""}{readable(row.review_status)}</small><small>{readable(row.sampling_domain)}</small></span></button>)}{page && !page.items.length && <p className="corpus-empty">No repositories match. Try a shorter search or clear a filter.</p>}</div><div className="corpus-pagination"><span>{page?.total ?? 0} results</span><button className="wm-secondary" aria-label="Previous queue page" disabled={busy || !offset} onClick={() => setOffset(Math.max(0, offset - 25))}>Previous</button><button className="wm-secondary" aria-label="Next queue page" disabled={busy || offset + 25 >= (page?.total || 0)} onClick={() => setOffset(offset + 25)}>Next</button></div></section>
        <section id="corpus-review-pane" className="corpus-review" inert={sourceOpen} aria-label="Repository evidence review" aria-busy={busy}>
          {detail ? <><div className="corpus-review-scroll" onFocusCapture={event => keepReviewFocusVisible(event.currentTarget, event.target as HTMLElement)}><div className="corpus-repository-heading"><div><h2>{detail.inventory.full_name}</h2></div><a href={detail.inventory.url} target="_blank" rel="noreferrer" aria-label="Open repository on GitHub"><Icon name="external" size={16} /></a><button className="wm-icon-button" disabled={busy} aria-label="Close review" onClick={closeReview}><Icon name="close" size={16} /></button></div><div className="corpus-repository-meta"><span>{detail.inventory.language || "Language unknown"}</span><span>Sampled: {readable(detail.inventory.sampling_domain)}</span><span>{detail.review ? readable(detail.review.status) : "Proposed"} · revision {detail.review?.revision || 0}</span>{outsideQueue && <span>Outside this queue page</span>}</div>
            {conflict && <div className="corpus-conflict"><strong>Newer saved work needs review.</strong><p>Your current edits are preserved. Compare before replacing or reapplying them.</p>{!latest ? <button className="wm-secondary" disabled={busy} onClick={() => void compareLatest()}>Compare latest saved record</button> : <><p><strong>Latest review · revision {latest.review?.revision || 0}</strong><br />{latest.review?.purpose || latest.proposal.purpose}</p><p>{(latest.review?.label_ids || []).map(id => byId[id]?.name || id).join(" · ") || "No saved retained labels"}</p><div><button className="wm-secondary" onClick={() => resolveConflict(false)}>Use latest saved review</button><button className="wm-secondary" disabled={!bindingMatches} onClick={() => resolveConflict(true)}>Reapply my edits</button></div>{!bindingMatches && <p>Source or release bindings changed. Quotes cannot be reapplied automatically.</p>}</>}</div>}
            <AnnotationInputs pilot={detail.annotation_pilot} concepts={byId} total={summary?.total || 0} pilotCount={summary?.annotation_pilot?.queue.length || 0} busy={busy} compare={() => comparisonDialog.current?.showModal()} openPilot={() => pilotDialog.current?.showModal()} />
            {registryStale && <div className="corpus-conflict" role="alert"><strong>Reference vocabulary changed.</strong><p>Your edits are preserved. Refresh the vocabulary and review the groups before saving.</p><button className="wm-secondary" disabled={busy} onClick={() => void refreshVocabulary()}>Refresh review vocabulary</button></div>}
            <p className="corpus-review-basis">{detail.draft ? "Your saved draft" : detail.review ? "Your saved human review" : editor.annotation_pilot_sha256 ? "Your editable review · includes staged agent suggestions" : "Your editable review · starts from the original corpus proposal"}</p>
            <label className="corpus-field corpus-purpose">Repository purpose<textarea aria-label="Repository purpose" rows={2} value={editor.purpose} disabled={busy} onChange={e => setEditor(value => ({ ...value, purpose: e.target.value, dimensions: emptyDimensions() }))} /></label>
            <div className="corpus-derived-domains" role="group" aria-label="Derived Domains"><span>Domains from retained Projects</span><button type="button" className="wm-link corpus-create-domain" disabled={busy || registryStale} onClick={() => openCreation("DOMAIN")}>Create Domain</button>{selectedDomains.length ? selectedDomains.map(id => <LabelChip id={id} kind="DOMAIN" key={id}>{byId[id]?.name || id}</LabelChip>) : <span>None</span>}</div>
            <p className="corpus-helper corpus-domain-help">Domains appear automatically from the Projects you select below. <span className="corpus-registry-version">Review vocabulary v{editor.registry_context?.revision || 0}{summary?.registry_extension_count ? ` · ${summary.registry_extension_count} added by you` : ""}</span></p>
            <div className="corpus-labels-heading"><h3>Your retained labels</h3><span>{editor.label_ids.length} retained</span></div><p className="corpus-helper">Add, remove or replace assignments in each group. Check Reviewed after inspecting the evidence.</p>
            <div className="corpus-label-groups" role="group" aria-label="Retained labels">{kinds.map(kind => {
              const ids = editor.label_ids.filter(id => byId[id]?.kind === kind), key = dimensionKey[kind];
              const available = (summary?.registry || []).filter(c => c.kind === kind && !editor.label_ids.includes(c.id)).sort((a, b) => a.name.localeCompare(b.name));
              return <section className="corpus-label-group" key={kind} aria-label={`${readable(kind)} labels`}><div className="corpus-group-heading"><h4>{readable(kind)}s <span>{ids.length} retained</span></h4><div className="corpus-group-actions"><SearchableSelect className="corpus-add-kind" aria-label={`Add ${readable(kind)}`} value="" disabled={busy || registryStale} onChange={(value, query) => value === `__CREATE_${kind}__` ? openCreation(kind, query) : addKnownLabel(value)} options={[{ value: "", label: `Add ${readable(kind)}…`, disabled: true }, ...available.map(c => ({ value: c.id, label: c.name, searchText: (c.aliases || []).join(" ") })), { value: `__CREATE_${kind}__`, label: `+ Create ${readable(kind)}…`, alwaysVisible: true }]} /><label><input type="checkbox" aria-label={`${readable(kind)}s reviewed`} disabled={busy} checked={editor.dimensions[key]} onChange={e => setEditor(value => ({ ...value, dimensions: { ...value.dimensions, [key]: e.target.checked } }))} />Reviewed</label></div></div>{ids.map(id => <div className="corpus-retained-entry" key={id}><div className="corpus-label-row"><div className="corpus-label-name"><LabelChip id={id} kind={kind}>{byId[id]?.name || id}</LabelChip>{!original.has(id) && <small>Added by you{editor.additional_evidence[id]?.quote ? " · quote attached" : " · evidence needed"}</small>}</div><button className="corpus-evidence-button" disabled={busy} aria-label={`Evidence for ${byId[id]?.name || id}`} onClick={() => inspectEvidence(id)}><Icon name="repos" size={14} />Evidence</button><button className="wm-icon-button" disabled={busy} aria-label={`Remove ${readable(kind).toLowerCase()} ${byId[id]?.name || id}`} onClick={() => updateSelected(editor.label_ids.filter(value => value !== id))}><Icon name="close" size={14} /></button></div>{!original.has(id) && <details className="corpus-added-evidence" open={expandedEvidence === id} onToggle={e => { if (!e.currentTarget.open && expandedEvidence === id) setExpandedEvidence(""); }}><summary onClick={e => { e.preventDefault(); setExpandedEvidence(value => value === id ? "" : id); }}>Exact source evidence{editor.additional_evidence[id]?.quote ? " · attached" : " · required"}</summary><label className="corpus-field">Saved source<SearchableSelect aria-label={`Evidence file for ${byId[id]?.name || id}`} value={editor.additional_evidence[id]?.path || ""} disabled={busy} onChange={path => updateEvidence(id, { path, quote: editor.additional_evidence[id]?.quote || "" })} options={[{ value: "", label: "Choose saved source" }, ...detail.files.map(file => ({ value: file.path, label: `${file.role} · ${file.path}` }))]} /></label><label className="corpus-field">Exact quote supporting {byId[id]?.name}<textarea aria-label={`Exact quote supporting ${byId[id]?.name || id}`} rows={3} disabled={busy} value={editor.additional_evidence[id]?.quote || ""} onChange={e => updateEvidence(id, { path: editor.additional_evidence[id]?.path || "", quote: e.target.value })} /></label><p className="corpus-helper">The final save validates this quote against the pinned saved source. Incomplete evidence can be saved as a draft.</p></details>}</div>)}{!ids.length && <p className="corpus-empty-group">{kind === "PROJECT" ? "No Project selected. Add a known family, or leave empty when none applies." : `No retained ${kind.toLowerCase()}s. Review this group even when empty.`}</p>}{kind === "PROJECT" && <button type="button" className="wm-link corpus-missing-project" disabled={busy} onClick={() => openCreation("PROJECT")}>+ Create missing Project</button>}</section>;
            })}</div>
            <details className="corpus-notes"><summary>Notes &amp; missing concepts <span>Optional</span></summary><label className="sr-only" htmlFor="corpus-review-notes">Review notes</label><textarea id="corpus-review-notes" aria-label="Review notes" rows={3} disabled={busy} value={editor.notes} onChange={e => setEditor(value => ({ ...value, notes: e.target.value }))} placeholder="Explain a correction, uncertainty or missing concept." /></details>
            <div className="corpus-review-links"><details><summary>Original proposed labels</summary><p><strong>Original purpose</strong><br />{detail.proposal.purpose || "Purpose requires review"}</p>{detail.proposal.labels.map((label, i) => <div className="corpus-original-label" key={`${label.id}:${i}`}><strong>{label.kind} · <LabelChip id={label.id} kind={label.kind}>{label.name}</LabelChip> · {label.decision || "SUPPORTED"}</strong><p>{byId[label.id]?.description}</p><p>{label.rationale}</p>{label.evidence.map((proof, index) => <div key={index}><span>{proof.path || "GitHub metadata"}{proof.start_line ? ` · lines ${proof.start_line}–${proof.end_line}` : ""}</span><pre>{proof.quote}</pre>{proof.path && detail.files.some(file => file.path === proof.path) && <button className="wm-secondary" onClick={() => { setCitation({ ...proof, label: label.name, rationale: label.rationale }); void openSource(detail.inventory.repository_id, proof.path!); showEvidence(); }}>Open saved source</button>}</div>)}</div>)}</details><details><summary>Eligibility, audit &amp; reading scope</summary><p>Source audit: {readable(detail.proposal.status)}. Cross-review is not human confirmation. Full retention does not imply full semantic reading.</p><pre>{JSON.stringify({ eligibility: detail.eligibility, conflicts: detail.proposal.conflicts, independent_audit: detail.proposal.cross_reviews, reading_scope: detail.read_coverage }, null, 2)}</pre></details><details><summary>Review history · {detail.review?.history.length || 0}</summary><pre>{JSON.stringify(detail.review?.history || [], null, 2)}</pre></details></div>
          </div><footer className="corpus-decision-footer"><div className="corpus-save-state"><span className={dirty ? "is-dirty" : ""}>{busy ? "Working…" : dirty ? "Unsaved changes" : detail.draft ? `Draft saved · revision ${detail.draft.revision}` : detail.review ? `Saved review · revision ${detail.review.revision}` : "No unsaved changes"}</span><span>{reviewedCount} of 3 groups reviewed</span></div><div className="corpus-decision-actions"><button className="wm-secondary" disabled={busy || conflict || registryStale} onClick={() => void saveDraft()}>Save draft</button><button className="wm-link" disabled={busy || conflict || registryStale} onClick={() => void saveReview("UNRESOLVED")}>Needs evidence</button>{retryNext !== null ? <button className="wm-primary" disabled={busy} onClick={() => requestLeave(() => { working(true); void advanceAfterSave(retryNext).finally(() => working(false)); })}>Next repository<Icon name="chevron" size={14} /></button> : <button ref={confirmButton} className="wm-primary" disabled={!canConfirm} aria-describedby="corpus-confirm-help" onClick={() => void saveReview("HUMAN_CONFIRMED", true)}>Confirm &amp; next<Icon name="chevron" size={14} /></button>}</div><span className="sr-only" id="corpus-confirm-help">{conflict ? "Resolve the saved-record conflict first." : missingEvidence.length ? "New positives need a source path and exact quote." : "Review purpose and all three groups before confirming. Control or Command plus Enter confirms and advances."}</span></footer></> : <div className="corpus-start"><Icon name="review" size={28} /><h2>{busy ? "Loading repository…" : "Select a repository"}</h2><p>Open a queue item to review its purpose, labels and saved evidence.</p></div>}
        </section>
        <section id="corpus-evidence-pane" ref={sourcePane} className={`corpus-source-pane ${sourceOpen ? "is-open" : ""}`} role={sourceOpen ? "dialog" : "region"} aria-modal={sourceOpen || undefined} aria-label="Saved source evidence"><div className="corpus-pane-heading"><h2>Source evidence</h2><button ref={closeSourceButton} className="wm-icon-button corpus-source-close" aria-label="Close evidence" onClick={closeEvidence}><Icon name="close" size={16} /></button></div><div className="corpus-source-scroll">{detail ? <>{citation && <div className="corpus-citation"><strong>{citation.label}</strong><p>{citation.rationale}</p>{citation.quote && <blockquote>{citation.quote}</blockquote>}<span>{citationMetadata ? `GitHub metadata${citation.field ? ` · ${citation.field}` : ""}` : citation.path || "Proposal evidence"}{!citationUnavailable && citation.start_line ? ` · lines ${citation.start_line}–${citation.end_line}` : ""}</span>{citationUnavailable && <p className="corpus-helper">No matching saved document was opened. This quote is a separate {citationMetadata ? "metadata" : "proposal"} reference.</p>}{citationUnavailable && citation.path && <details className="corpus-provenance"><summary>Evidence snapshot reference</summary><p>{citation.path}</p>{citation.sha256 && <p>SHA-256 {citation.sha256}</p>}</details>}</div>}<label className="corpus-field">Source document<SearchableSelect aria-label="Source document" value={sourcePath} disabled={busy} onChange={path => { setCitation(null); void openSource(detail.inventory.repository_id, path); }} options={[{ value: "", label: "Select a saved document", disabled: true }, ...detail.files.map(file => ({ value: file.path, label: `${file.role} · ${file.path}` }))]} /></label>{sourceBusy && <p className="corpus-helper" aria-live="polite">Loading saved source…</p>}{sourceError && <div className="corpus-source-error" role="alert"><p>{sourceError}</p><button className="wm-secondary" onClick={() => void openSource(detail.inventory.repository_id, sourcePath)}>Retry source</button></div>}{source && <><p className="corpus-source-channel">{source.role === "GITHUB_METADATA" ? "Pinned public GitHub metadata, recorded separately from repository documents." : "Saved repository document · plain text"}</p><pre className="corpus-source-text" tabIndex={0} aria-label="Saved source text">{sourceQuoteIndex >= 0 && citation?.quote ? <>{source.text.slice(0, sourceQuoteIndex)}<mark id="corpus-source-quote">{citation.quote}</mark>{source.text.slice(sourceQuoteIndex + citation.quote.length)}</> : source.text}</pre><button className="wm-link corpus-use-selection" onClick={() => { const selection = window.getSelection(); const quote = selection?.toString() || ""; const node = selection?.anchorNode?.parentElement; if (!quote || !node?.closest(".corpus-source-text")) { setNotice("Select exact text in the saved source first."); return; } const id = expandedEvidence || added[0]; if (!id) { setNotice("Add a known label before attaching new evidence."); return; } updateEvidence(id, { path: source.path, quote }); setExpandedEvidence(id); setActivePanel("review"); setSourceOpen(false); setNotice(`Selected source text attached to ${byId[id]?.name || id}. Review its relevance before saving.`); }}>Use selected source text for added label</button><details className="corpus-provenance"><summary>Source provenance</summary><dl><dt>Release</dt><dd>{detail.release_id}</dd><dt>Manifest SHA-256</dt><dd>{detail.manifest_sha256}</dd><dt>Commit</dt><dd>{source.commit}</dd><dt>Source SHA-256</dt><dd>{source.sha256}</dd></dl></details></>}<p className="corpus-helper corpus-source-safety">Source text is untrusted evidence. Markdown, HTML and embedded instructions remain plain text. Full retention does not mean every byte was semantically read.</p></> : <p className="corpus-empty">Select a repository to inspect its saved sources.</p>}</div></section>
      </div>
    </main>
    {sourceOpen && <button className="corpus-source-scrim" tabIndex={-1} aria-hidden="true" aria-label="Close source evidence" onClick={closeEvidence} />}
    {createKind && editor.registry_context && summary && <CorpusConceptDialog kind={createKind} initialName={createName} concepts={summary.registry} context={editor.registry_context} csrf={identity.csrf_token} onRegistry={applyRegistry} onChoose={chooseCreatedConcept} close={() => setCreateKind(null)} />}
    <dialog ref={leaveDialog} className="corpus-dialog corpus-leave-dialog" aria-labelledby="corpus-leave-title" onCancel={() => { pendingLeave.current = null; }}><div className="corpus-dialog-heading"><h2 id="corpus-leave-title">Save your changes?</h2><button className="wm-icon-button" aria-label="Keep reviewing" onClick={() => { pendingLeave.current = null; leaveDialog.current?.close(); }}><Icon name="close" size={16} /></button></div><div className="corpus-dialog-body"><p>Your edits to this repository have not been saved.</p></div><div className="corpus-dialog-footer"><button className="wm-link" onClick={() => { const action = pendingLeave.current; pendingLeave.current = null; leaveDialog.current?.close(); action?.(); }}>Discard changes</button><button className="wm-secondary" onClick={() => { pendingLeave.current = null; leaveDialog.current?.close(); }}>Stay</button><button className="wm-primary" disabled={busy || conflict || registryStale} onClick={() => void saveDraft().then(saved => { if (saved) { const action = pendingLeave.current; pendingLeave.current = null; leaveDialog.current?.close(); action?.(); } })}>Save &amp; continue</button></div></dialog>
    <dialog ref={pilotDialog} className="corpus-dialog corpus-pilot-dialog" aria-labelledby="corpus-pilot-title"><div className="corpus-dialog-heading"><h2 id="corpus-pilot-title">Independent annotation pilot</h2><button className="wm-icon-button" aria-label="Close annotation pilot" onClick={() => pilotDialog.current?.close()}><Icon name="close" size={16} /></button></div><div className="corpus-dialog-body">{summary?.annotation_pilot && <AnnotationPilotQueue pilot={summary.annotation_pilot} busy={busy} inspect={openPilotRepository} />}</div><div className="corpus-dialog-footer"><button className="wm-secondary" onClick={() => pilotDialog.current?.close()}>Done</button></div></dialog>
    <dialog ref={comparisonDialog} className="corpus-dialog corpus-comparison-dialog" aria-labelledby="corpus-comparison-title"><div className="corpus-dialog-heading"><h2 id="corpus-comparison-title">Independent annotations</h2><button className="wm-icon-button" aria-label="Close comparison" onClick={() => comparisonDialog.current?.close()}><Icon name="close" size={16} /></button></div><div className="corpus-dialog-body">{detail?.annotation_pilot && <CorpusAnnotations pilot={detail.annotation_pilot} concepts={byId} files={detail.files} busy={busy} openSource={path => { comparisonDialog.current?.close(); setCitation(null); void openSource(detail.inventory.repository_id, path); showEvidence(); }} stage={stageAnnotation} />}</div><div className="corpus-dialog-footer"><button className="wm-secondary" onClick={() => comparisonDialog.current?.close()}>Done</button></div></dialog>
    <dialog ref={guideDialog} className="corpus-dialog" aria-labelledby="corpus-guide-title"><div className="corpus-dialog-heading"><h2 id="corpus-guide-title">Review guide</h2><button className="wm-icon-button" aria-label="Close review guide" onClick={() => guideDialog.current?.close()}><Icon name="close" size={16} /></button></div><div className="corpus-dialog-body"><p>Read the purpose and evidence, retain or remove labels, and explicitly acknowledge Projects, Topics and Tags. Multiple labels and derived Domains are supported. Unlisted labels remain unknown.</p><p>Use each group’s Add picker to reuse a concept or choose + Create. A new Project requires a parent Domain; you can create that Domain without losing your Project fields. Domains appear from assigned Projects. Creating a concept saves its definition; the assignment still needs a saved draft or confirmed review.</p><p>Save draft stores unfinished work separately. Needs evidence records an unresolved final review. Confirm &amp; next saves a human confirmation and opens the next queue item only after success.</p><p>New positives need an exact quote from a saved source. Original proposals, source provenance, review history and independent annotations remain inspectable. Agreement is not human confirmation. To browse saved assignments, choose Filters → Label filter basis → Your saved reviews.</p><p><kbd>/</kbd> focuses repository search. <kbd>Ctrl/⌘ + Enter</kbd> confirms and advances only when prerequisites are met. No group is reviewed automatically.</p></div><div className="corpus-dialog-footer"><button className="wm-secondary" onClick={() => guideDialog.current?.close()}>Done</button></div></dialog>
  </div>;
}
