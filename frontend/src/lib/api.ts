export type Config = { oauth_configured: boolean; callback_url: string; requested_scopes: string[] };
export type SessionInfo = { expires_in_seconds: number; warning_seconds: number; renewable: boolean; extension_seconds: number; received_at_ms?: number };
export type Identity = { user: { id: number; login: string; name: string | null }; scopes: string[]; csrf_token: string; session?: SessionInfo };
export type Coverage = { source: string; status: string; count: number | null; note: string };
export type Repo = { id: number; full_name: string; html_url: string; private: boolean; language: string | null; default_branch: string | null; sources: string[]; eligible: boolean; favorite: boolean };
export type RepoPage = { items: Repo[]; total: number; next_cursor: string | null; coverage: Coverage[] };
export type Report = { filename: string; rows: { check: string; evidence: string; status: string; detail: string }[] };

export const SESSION_EXPIRED_EVENT = "ghm:session-expired";
export const GITHUB_SIGN_IN_PATH = "/api/v1/auth/github/start";
let sessionGeneration = 0;
export function acknowledgeSession() { sessionGeneration++; }
export function currentSessionGeneration() { return sessionGeneration; }

export class ApiError extends Error {
  constructor(message: string, public status: number, public code?: string) { super(message); this.name = "ApiError"; }
}

export async function apiFetch(url: string, init: RequestInit = {}, timeoutMs = 30_000): Promise<Response> {
  const generation = sessionGeneration;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, { ...init, signal: init.signal ? AbortSignal.any([init.signal, controller.signal]) : controller.signal });
    if (response.status === 401 && generation === sessionGeneration && typeof window !== "undefined") window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
    // Keep the deadline active while receiving JSON too, not just response headers.
    const body = await response.arrayBuffer();
    if (generation !== sessionGeneration) throw new ApiError("Your session changed. Refresh the view before continuing.", 409, "SESSION_CHANGED");
    return new Response([204, 205, 304].includes(response.status) ? null : body, { status: response.status, statusText: response.statusText, headers: response.headers });
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (controller.signal.aborted) throw new ApiError("The request timed out. Your session may still be valid. Check the operation's status before retrying a save or sync.", 504, "REQUEST_TIMEOUT");
    if (init.signal?.aborted) throw error;
    throw new ApiError("Cannot reach the service. Check the connection and retry; saved work is preserved.", 503, "SERVICE_UNAVAILABLE");
  } finally { clearTimeout(timer); }
}

export async function api<T>(path: string, csrf?: string): Promise<T> {
  const response = await apiFetch(`/api/v1${path}`, { cache: "no-store", credentials: "same-origin",
    ...(csrf ? { method: "POST", headers: { "X-CSRF-Token": csrf } } : {}),
  });
  if (!response.ok) {
    const value = await response.json().catch(() => ({ detail: "Local API unavailable; start the backend and try again" }));
    throw new ApiError(value.detail || `Request failed (${response.status})`, response.status, value.code);
  }
  if (path === "/auth/logout") return undefined as T;
  return response.json();
}
