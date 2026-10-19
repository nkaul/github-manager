"use client";

import { useState } from "react";
import styles from "./CorpusAnnotations.module.css";
import { LabelChip } from "./LabelChip";

type Evidence = { path: string; sha256: string; quote: string; start_line: number; end_line: number };
export type AgentAnnotation = {
  purpose: string;
  purpose_evidence: Evidence[];
  positive_ids: string[];
  labels: { id: string; rationale: string; evidence: Evidence[] }[];
  producer: { runtime: string; model: string | null; model_description: string };
  source_reading: { path: string; complete: boolean; intervals: number[][]; note: string }[];
  group_scope: Record<string, { status: string; reason: string }>;
  conflicts: string[];
  missing_concepts: { kind: string; name: string; description: string; evidence: Evidence[] }[];
  caveats: string[];
};
type PilotRecord = {
  annotations: { a: AgentAnnotation; b: AgentAnnotation };
  comparison: { agreed_ids: string[]; a_only_ids: string[]; b_only_ids: string[]; review_band: string; review_reasons: string[] };
  audit_selection: string | null;
};
export type PilotDetail = { state: string; sidecar_manifest_sha256?: string | null; record: PilotRecord | null };
export type PilotSummary = {
  state: string;
  reason?: string;
  reviewed_by_you: number;
  confirmed_by_you: number;
  summary: { repositories: number; review_bands: Record<string, number>; human_queue: Record<string, number> };
  queue: { repository_id: number; full_name: string; sampling_domain: string; review_band: string; audit_selection: string | null; review_status: string }[];
};
type Concept = { name: string; kind: string; description: string; domain?: string | null };
const readable = (value: string) => value.replaceAll("_", " ").toLowerCase();

export function AnnotationInputs({ pilot, concepts, total, pilotCount, busy, compare, openPilot }: {
  pilot?: PilotDetail;
  concepts: Record<string, Concept>;
  total: number;
  pilotCount: number;
  busy: boolean;
  compare: () => void;
  openPilot: () => void;
}) {
  const record = pilot?.state === "READY" ? pilot.record : null;
  if (!record) {
    const unavailable = pilot?.state === "INVALID";
    return <section className={`${styles.availability} ${unavailable ? styles.unavailable : ""}`} aria-label="Agent annotation availability">
      <strong>{unavailable ? "Agent inputs withheld" : pilot?.state === "PARTIAL" ? "Independent agent inputs are still in progress" : "No Agent A/B annotations for this repository"}</strong>
      <p>{unavailable ? "Pilot integrity validation failed. Original corpus proposals and your saved human review remain separate." : pilot?.state === "READY" ? `The independent pilot covers ${pilotCount} of ${total} repositories. This repository has its original corpus proposal, not an Agent A/B comparison.` : "This repository has its original corpus proposal. A validated independent comparison is not available yet."}</p>
      {pilotCount > 0 && <button type="button" className="wm-link" disabled={busy} onClick={openPilot}>Open Agent A/B pilot queue · {pilotCount}</button>}
    </section>;
  }
  return <section className={styles.inputs} aria-label="Agent A and B inputs">
    <div className={styles.inputsHeading}><div><h3>Agent A &amp; B inputs</h3><p>Independent suggestions · not your saved human decision</p></div><button type="button" className="wm-secondary" disabled={busy} onClick={compare}>Compare independent annotations</button></div>
    <div className={styles.inputPasses}>{(["a", "b"] as const).map(key => {
      const annotation = record.annotations[key];
      return <article key={key} aria-label={`Agent ${key.toUpperCase()} summary`}><h4>Agent {key.toUpperCase()}<span>{annotation.positive_ids.length} labels</span></h4><p>{annotation.purpose}</p><div className={styles.inputLabels}>{["PROJECT", "TOPIC", "TAG"].map(kind => {
        const ids = annotation.positive_ids.filter(id => concepts[id]?.kind === kind);
        return <div key={kind}><strong>{`${kind.charAt(0)}${kind.slice(1).toLowerCase()}s`}</strong><div className="wm-chips">{ids.length ? ids.map(id => <LabelChip key={id} id={id} kind={kind}>{concepts[id]?.name || id}</LabelChip>) : <span className={styles.none}>None proposed</span>}</div></div>;
      })}</div></article>;
    })}</div>
    <p className={styles.inputsHelp}>Compare to see each agent’s rationale, exact source evidence, differences and reading scope. Agreement can still be wrong. Staging is optional and never saves or confirms a review.</p>
  </section>;
}

export function AnnotationPilotQueue({ pilot, busy, inspect }: { pilot: PilotSummary; busy: boolean; inspect: (id: number, scope: "pilot" | "initial_queue") => void }) {
  const [all, setAll] = useState(false);
  if (pilot.state === "NOT_RUN") return null;
  if (pilot.state === "INVALID") return <p className={styles.warning} role="alert">{pilot.reason} Your saved human reviews remain separate.</p>;
  if (pilot.state !== "READY") return <p className={styles.pending}><strong>Agent annotation pilot in progress.</strong> {pilot.summary.repositories || 30} development repositories selected. Independent passes will appear here after validation. No additional provider API calls.</p>;
  const items = pilot.queue.filter(row => all || row.audit_selection);
  return <details className={styles.queue} open>
    <summary>Independent annotation pilot · {pilot.queue.length} repositories · {pilot.confirmed_by_you} confirmed by you</summary>
    <p>Two source-first Codex agents read independently. These are LLM-assisted proposals, not human ground truth. Review the targeted cases and the random audit sample; agreement can share mistakes. Opening a card keeps Confirm &amp; next within this {all ? "pilot" : "initial human-review"} queue.</p>
    <div className={styles.toolbar}><strong>{items.length} {all ? "pilot repositories" : "human-review cards"}</strong><button className="wm-secondary" type="button" onClick={() => setAll(!all)}>{all ? "Show human-review queue" : "Show all pilot repositories"}</button><span>{pilot.reviewed_by_you} reviewed by you · Additional API calls: 0 · Agent allowance: unmeasured</span></div>
    <div className={styles.queueRows}>{items.map(row => <div className={styles.queueRow} key={row.repository_id}><div><strong>{row.full_name}</strong><small>{row.sampling_domain} · {readable(row.review_band)} evidence band · {readable(row.audit_selection || "not selected for initial audit")} · {readable(row.review_status)}</small></div><button className="wm-secondary" disabled={busy} onClick={() => inspect(row.repository_id, all ? "pilot" : "initial_queue")}>Review<span className={styles.srOnly}> {row.full_name}</span></button></div>)}</div>
  </details>;
}

export function CorpusAnnotations({ pilot, concepts, files, busy, openSource, stage }: {
  pilot: PilotDetail;
  concepts: Record<string, Concept>;
  files: { path: string }[];
  busy: boolean;
  openSource: (path: string) => void;
  stage: (annotation: AgentAnnotation) => void;
}) {
  if (pilot.state !== "READY" || !pilot.record) return null;
  const record = pilot.record;
  const labelNames = (ids: string[]) => ids.length ? <div className="wm-chips">{ids.map(id => <LabelChip key={id} id={id} kind={concepts[id]?.kind}>{`${concepts[id]?.kind || "Label"}: ${concepts[id]?.name || id}`}</LabelChip>)}</div> : "None";
  function evidence(items: Evidence[]) {
    return items.map((item, index) => <div className={styles.evidence} key={`${item.path}:${index}`}><strong>{item.path === "@github-metadata.json" ? "Saved GitHub metadata" : item.path} · lines {item.start_line}–{item.end_line}</strong><pre>{item.quote}</pre>{files.some(file => file.path === item.path) && <button className="wm-secondary" disabled={busy} onClick={() => openSource(item.path)}>Open saved source</button>}</div>);
  }
  return <section className={styles.comparison} aria-label="Independent agent annotations">
    <h3>Independent LLM agent annotations</h3>
    <p>Original corpus proposals remain in the review pane. Your human decision is a separate layer. Additional provider API calls: 0; agent allowance is unmeasured.</p>
    <div className={styles.outcome}><strong>{readable(record.comparison.review_band)} evidence band</strong><span>{record.comparison.review_reasons.join(" · ")}</span><small>This is a review priority, not a calibrated probability. Unlisted labels remain unknown.</small></div>
    <dl className={styles.differences}><dt>Agreed labels</dt><dd>{labelNames(record.comparison.agreed_ids)}</dd><dt>A only</dt><dd>{labelNames(record.comparison.a_only_ids)}</dd><dt>B only</dt><dd>{labelNames(record.comparison.b_only_ids)}</dd></dl>
    <div className={styles.passes}>{(["a", "b"] as const).map(key => {
      const annotation = record.annotations[key];
      const domains = [...new Set(annotation.positive_ids.filter(id => concepts[id]?.kind === "PROJECT").map(id => concepts[id]?.domain).filter((id): id is string => Boolean(id)))];
      return <article key={key}><h4>Annotator {key.toUpperCase()}</h4><p>{annotation.purpose}</p><p><strong>Derived Domains:</strong> {domains.length ? domains.map(id => <LabelChip key={id} id={id} kind="DOMAIN">{concepts[id]?.name || id}</LabelChip>) : "No evidenced known Project parent"}</p><details><summary>Purpose evidence</summary>{evidence(annotation.purpose_evidence)}</details>{annotation.labels.map(label => <details key={label.id}><summary>{concepts[label.id]?.kind} · <LabelChip id={label.id} kind={concepts[label.id]?.kind}>{concepts[label.id]?.name || label.id}</LabelChip></summary><p>{concepts[label.id]?.description}</p><p>{label.rationale}</p>{evidence(label.evidence)}</details>)}
        {annotation.missing_concepts.length > 0 && <div className={styles.warning}><strong>Missing concepts</strong>{annotation.missing_concepts.map((item, i) => <details key={i}><summary>{item.kind} · {item.name}</summary><p>{item.description}</p>{evidence(item.evidence)}</details>)}<small>These are proposals; no registry entry is created automatically.</small></div>}
        {annotation.conflicts.length > 0 && <p><strong>Conflicts:</strong> {annotation.conflicts.join(" · ")}</p>}
        {annotation.caveats.length > 0 && <p><strong>Caveats:</strong> {annotation.caveats.join(" · ")}</p>}
        <details><summary>Reading scope and producer provenance</summary><p>{annotation.producer.runtime} · {annotation.producer.model || "Exact model unavailable"} · {annotation.producer.model_description}</p>{Object.entries(annotation.group_scope).map(([kind, scope]) => <p key={kind}><strong>{kind}: {readable(scope.status)}</strong> — {scope.reason}</p>)}{annotation.source_reading.map(source => <p key={source.path}><strong>{source.path}</strong> · {source.complete ? "Declared complete reading" : "Partial / unread"} · {source.intervals.map(range => range.join("–")).join(", ") || "No intervals"}<br />{source.note}</p>)}<small>Intervals are reader declarations checked for structural consistency. They do not prove semantic correctness or repository-wide completeness.</small></details>
        <button className={`${styles.stage} wm-primary`} disabled={busy} onClick={() => stage(annotation)}>Stage annotator {key.toUpperCase()} in my review</button>
      </article>;
    })}</div>
    <p>Staging changes only your editable form and clears all reviewed checks. New labels still require valid source quotes. Read, correct and explicitly save your own decision.</p>
  </section>;
}
