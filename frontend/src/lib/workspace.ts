export type AnalysisStatus = { state: string; status: string; freshness?: string; stale: boolean; ai_analyzed: boolean; error?: string; reason?: string; last_success?: { status: string; model?: string; evidence: string; revision?: number; fingerprint_known?: boolean }; last_local_revision?: number };
export type ConceptCounts = Record<string, { accepted: number; pending: number }>;
export type AutoSettings = { auto_enabled: boolean; quiet_seconds: number; cooldown_seconds: number; auto_window_seconds?: number; auto_weight_threshold?: number; auto_entity_threshold?: number; auto_project_threshold?: number; auto_change_types?: string[] };
export type Automation = { weight: number; entities: number; new_projects: number; threshold_met: boolean; quiet_remaining: number; cooldown_remaining: number; ready: boolean };
export type Kind = "DOMAIN" | "PROJECT" | "TOPIC" | "TAG";
export type Concept = { id: string; kind: Kind; name: string; description: string; aliases: string[]; domain: string | null; active: boolean; protected?: boolean; merged_into?: string };
export type Proposal = { kind: Kind; name: string; description: string; aliases: string[]; parent_domain?: string | null; domain?: string | null; supporting_repo_ids?: string[] };
export type Edge = { concept_id: string; source: "USER" | "RULE" | "AI" };
export type Repo = { analysis?: AnalysisStatus; label_count?: number; domain_ids?: string[]; key: string; id: number | null; name: string; description: string; owner: string; language: string | null; topics: string[]; html_url: string | null; private: boolean; source: string; synthetic?: boolean; default_branch: string | null; branch_count: number | null; sources: string[]; eligible: boolean; included?: boolean; favorite: boolean; starred: boolean; watched: boolean; organization: Record<string, Edge>; review_count: number; last_user_activity: string | null; activities?: { at: string; kind: string; actor_id: number }[] };
export type Source = { source: string; status: string; note: string; count?: number | null };
export type Run = { budget_mode?: string; budget_outcome?: { ceiling_usd: number; http_used: number; generation_used: number; estimated_usd: number; reserved_usd: number }; id: string; kind: string; status: string; created_at: string; processed: number; total: number; failed: number; stale?: number; message?: string; reason?: string; ai_mode?: string; evidence?: string; model?: string; outcomes: Record<string, { status: string; evidence: string; model?: string; seconds?: number; error?: string; usage?: { input_tokens: number; output_tokens: number } }> };
export type Draft = { id: string; proposals: Proposal[]; edited_proposals?: Proposal[]; status: string; notes: string; evidence: string; model?: string; revision: number };
export type Suggestion = { id: string; concept_id: string; kind: Kind; repo_key: string; reason: string; confidence: number; evidence_ids: string[]; status: string; evidence: string; model?: string };
export type Rule = { id: string; name: string; field: string; operator: string; value: string; concept_id: string };
export type AllowanceCount = { used: number; limit: number; remaining: number; lifetime_used: number; lifetime_limit: number };
export type Budget = { run_budget?: { held_usd: number; available_usd: number; pricing_version: string }; estimated_usd?: number; remaining_usd?: number; reserved_usd?: number; cap_usd?: number; calls?: number; revision?: number; http?: AllowanceCount; generations?: AllowanceCount; unavailable?: boolean };
export type AllowanceAudit = { revision: number; at: number; action: string; reason: string; after: { http: AllowanceCount; generations: AllowanceCount } };
export type RepoSummary = { labeled?: number; no_labels?: number; projects?: number; topics?: number; tags?: number; ai_analyzed?: number; stale?: number; repos: number; organized: number; uncategorized: number; review: number; suggestions: number };
export type Workspace = { automation: Automation; concept_counts?: ConceptCounts; repository_names?: Record<string, string>; preferences: RunPreferences; collection: string; summary?: RepoSummary; organization: { concepts: Record<string, Concept>; edges: Record<string, Record<string, Edge>>; suggestions: Record<string, Suggestion>; drafts: Record<string, Draft>; rules: Record<string, Rule>; runs: Record<string, Run>; audit: { id: string; at: string; verified: boolean; status: string }[]; control: AutoSettings & { generation: number; revision: number; version: number; processed_revision: number; active_run: string | null; resetting: boolean; auto_enabled: boolean; quiet_seconds: number; cooldown_seconds: number } }; coverage: { repos: number; organized: number; uncategorized: number; review: number }; source_coverage: Source[]; activity_coverage: Source[]; synced_at: string | null; live_ai_enabled: boolean; can_manage_allowance: boolean; budget: Budget };
export type RepoPage = { concept_counts?: ConceptCounts; summary?: RepoSummary; languages?: { value: string; label: string; count: number }[]; items: Repo[]; total: number; next_cursor: string | null; coverage: Source[] };
export type Profile = { extractor: string; hash: string; sha: string; phrases: { text: string; score: number; evidence_ids: string[] }[]; evidence: { id: string; section: string; text: string }[] };
export type Detail = { repo: Repo; profile: Profile | null; edges: Record<string, Edge>; rejections: string[] };
export type ResetScope = { associations: boolean; suggestions: boolean; drafts: boolean; history: boolean; feedback: boolean; cache: boolean; kinds: Kind[]; rules: boolean; restart: string };
export type ResetPlan = { plan_id: string; counts: Record<string, number>; expires_in: number; version: number; scope: ResetScope };

export async function request<T>(path: string, collection: string, csrf?: string, method = "GET", body?: unknown): Promise<T> {
  const separator = path.includes("?") ? "&" : "?";
  const response = await fetch(`/api/v1${path}${separator}collection=${collection}`, {
    method, cache: "no-store", credentials: "same-origin",
    headers: { ...(csrf ? { "X-CSRF-Token": csrf } : {}), ...(body === undefined ? {} : { "Content-Type": "application/json" }) },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  const value = await response.json().catch(() => ({ detail: "Local service unavailable" }));
  if (!response.ok) throw new WorkspaceError(typeof value.detail === "string" ? value.detail : "Request validation failed; check the form fields", response.status, value.code, value.conflicts);
  return value as T;
}

export type RepoScope = { view: string; q?: string; language?: string; visibility?: string; concept?: string; days?: number };
export type RunPreferences = { taxonomy_count: number; classification_count: number; budget_mode: "FIXED" | "ADAPTIVE"; budget_usd: number };
export type RunPlan = { skipped: { key: string; name: string; reason: string }[]; fresh_ai: number; offline: number; previously_analyzed_inputs: number; plan_id: string; input: { mode: string; budget_mode: string; reanalyze?: boolean; reanalysis_reason?: string }; requested: number; eligible: number; chosen: number; excluded: { key: string; name: string; reason: string }[]; repositories: { key: string; name: string; language: string | null; analysis_status?: string; freshness?: string; prior_taxonomy?: boolean }[]; generations: number; http_requests: number; upper_usd: number; can_start: boolean; blocked_reason: string | null; strategy: string; note: string };

export type TaxonomyConflict = { id?: string; type: string; field: string; term: string; normalized?: string; incoming_name: string; kind: Kind; message: string; proposal_index?: number; alias_index?: number | null; existing?: Concept; suggested_name?: string; actions?: { kind: string; label: string }[] };
export type TaxonomyCheck = { valid: boolean; conflicts: TaxonomyConflict[]; reused: { id: string; name: string; kind: Kind; message: string }[] };
export class WorkspaceError extends Error {
  constructor(message: string, public status: number, public code?: string, public conflicts?: TaxonomyConflict[]) { super(message); this.name = "WorkspaceError"; }
}
export const displayLabel = (value: string) => (({ SYNC: "GitHub Sync", DISCOVER: "Discover Taxonomy", REDISCOVER: "Rediscover Taxonomy", FULL_CLASSIFICATION: "Full Classification", INCREMENTAL: "Incremental Classification", EXTRACT: "Extract Evidence", WAITING_FOR_REAUTH: "Waiting for Sign-in", CANCELLED_STALE: "Cancelled — Workspace Changed", PARTIAL_FAILED: "Partially Failed", LIVE_PROVIDER: "Live AI", REPLAY: "Cached AI", FIXTURE: "Test Fixture", LOCAL_RULES: "Local Rules", LOCAL_MATCH: "Local Suggestion", STORED_ANALYSIS: "Stored Analysis", OFFLINE_RECONCILED: "Reconciled Offline", UNKNOWN: "No Recorded Analysis", NEW: "Not Yet Analyzed", SUCCEEDED: "Analysis Complete", UNCERTAIN: "Outcome Unknown" } as Record<string, string>)[value] || value.toLowerCase().replaceAll("_", " ").replace(/\b\w/g, c => c.toUpperCase()).replace(/\bAi\b/g, "AI").replace(/\bGithub\b/g, "GitHub"));
