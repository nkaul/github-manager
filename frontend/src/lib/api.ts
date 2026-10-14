export type Config = { oauth_configured: boolean; callback_url: string; requested_scopes: string[] };
export type Identity = { user: { id: number; login: string; name: string | null }; scopes: string[]; csrf_token: string };
export type Coverage = { source: string; status: string; count: number | null; note: string };
export type Repo = { id: number; full_name: string; html_url: string; private: boolean; language: string | null; default_branch: string | null; sources: string[]; eligible: boolean; favorite: boolean };
export type RepoPage = { items: Repo[]; total: number; next_cursor: string | null; coverage: Coverage[] };
export type Report = { filename: string; rows: { check: string; evidence: string; status: string; detail: string }[] };

export async function api<T>(path: string, csrf?: string): Promise<T> {
  const response = await fetch(`/api/v1${path}`, { cache: "no-store", credentials: "same-origin",
    ...(csrf ? { method: "POST", headers: { "X-CSRF-Token": csrf } } : {}),
  });
  if (!response.ok) {
    const value = await response.json().catch(() => ({ detail: "Local API unavailable; start the backend and try again" }));
    throw new Error(value.detail || `Request failed (${response.status})`);
  }
  if (path === "/auth/logout") return undefined as T;
  return response.json();
}
