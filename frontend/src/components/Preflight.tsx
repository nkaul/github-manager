"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, Config, Identity, RepoPage, Report } from "@/lib/api";

type View = "my" | "favorites" | "all";

export default function Home() {
  const [config, setConfig] = useState<Config | null>(null);
  const [identity, setIdentity] = useState<Identity | null>(null);
  const [data, setData] = useState<RepoPage | null>(null);
  const [view, setView] = useState<View>("my");
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [ready, setReady] = useState(false);
  const [report, setReport] = useState<Report | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([api<Config>("/pretest/config"), api<Identity>("/me").catch(() => null)])
      .then(([cfg, me]) => { if (active) {
        setConfig(cfg); setIdentity(me);
        if (new URLSearchParams(window.location.search).get("auth") === "cancelled") {
          setError("GitHub sign-in was cancelled. You can try again when ready.");
          window.history.replaceState(null, "", "/");
        }
      } })
      .catch((err) => { if (active) setError(err.message); })
      .finally(() => { if (active) setReady(true); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!identity) return;
    let active = true;
    const timer = setTimeout(() => {
      setBusy(true);
      setError("");
      api<RepoPage>(`/repos?view=${view}&q=${encodeURIComponent(query)}`)
        .then((value) => { if (active) setData(value); })
        .catch((err) => { if (active) setError(err.message); })
        .finally(() => { if (active) setBusy(false); });
    }, 200);
    return () => { active = false; clearTimeout(timer); };
  }, [identity, view, query]);

  async function more() {
    if (!data?.next_cursor || busy) return;
    setBusy(true);
    try {
      const next = await api<RepoPage>(`/repos?view=${view}&q=${encodeURIComponent(query)}&cursor=${encodeURIComponent(data.next_cursor)}`);
      setData({ ...next, items: [...data.items, ...next.items] });
    } catch (err) { setError((err as Error).message); }
    finally { setBusy(false); }
  }

  async function verify() {
    if (!identity) return;
    setBusy(true); setError("");
    try {
      setReport(await api<Report>("/pretest/github/run", identity.csrf_token));
      setData(await api<RepoPage>(`/repos?view=${view}&q=${encodeURIComponent(query)}`));
    } catch (err) { setError((err as Error).message); }
    finally { setBusy(false); }
  }

  async function logout() {
    if (!identity) return;
    try {
      await api<void>("/auth/logout", identity.csrf_token);
      setIdentity(null); setData(null); setReport(null);
    } catch (err) { setError((err as Error).message); }
  }

  return <div className="shell">
    <aside>
      <Link className="brand" href="/"><span className="brand-mark">G</span> GitHub Manager</Link>
      <div className="workspace"><span className="dot" /> Workspace <small>PHASE 0</small></div>
      <p className="nav-label">REPOSITORIES</p>
      {([["my", "My repositories"], ["favorites", "Favorites"], ["all", "Access candidates"]] as const).map(([key, title]) =>
        <button key={key} className={`nav-item ${view === key ? "active" : ""}`} onClick={() => { setView(key); setData(null); }} aria-pressed={view === key}>{title}</button>)}
      <div className="sidebar-note"><strong>Access preflight</strong><p>Confirm your GitHub connection before building your organization workspace.</p><span>Read-only calls</span></div>
    </aside>
    <main>
      <header><span className="breadcrumb">Workspace <span>/</span> Access preflight</span><span className={`connection ${identity ? "connected" : ""}`}><span className="dot" />{identity ? "GitHub connected" : "GitHub disconnected"}</span></header>
      <section className="heading"><div><p className="eyebrow">PHASE 0 · PRE-TESTING</p><h1>Start with a verified connection.</h1><p>Check your identity, explore accessible repositories, and capture the results.</p></div>
        {identity && <button className="secondary" onClick={logout}>Sign out</button>}
      </section>
      {error && <div className="notice error" role="alert">{error}</div>}
      {!ready ? <div className="panel">Checking the local API…</div> : !identity ? <section className="panel connect-panel">
        <div className="connector-logo">GH</div><h2>Connect your GitHub account</h2><p>Use your account to verify access to public and private repositories, stars, watches, and teams.</p>
        <a className={`primary ${!config?.oauth_configured ? "disabled" : ""}`} aria-disabled={!config?.oauth_configured} href={config?.oauth_configured ? "/api/v1/auth/github/start" : undefined}>Continue with GitHub <span>↗</span></a>
        <p className="scope-note">OAuth App scopes: {config?.requested_scopes.join(", ") || "unavailable"}. GitHub’s repo scope includes write permission; this application makes read-only repository calls.</p>
        {!config?.oauth_configured && <div className="setup"><h3>One-time OAuth App setup</h3><ol><li><a href="https://github.com/settings/applications/new" target="_blank" rel="noreferrer">Register an OAuth App on GitHub ↗</a></li><li>Homepage: <code>http://127.0.0.1:3000</code><br />Callback: <code>{config?.callback_url || "http://127.0.0.1:3000/api/v1/auth/github/callback"}</code></li><li>Put the client ID and secret in <code>backend/.env</code>, then restart the backend and reload this page.</li></ol><p>Keep secrets in the backend environment. Browser login is optional until registration is ready.</p></div>}
      </section> : <>
        <section className="identity panel"><div className="avatar">{identity.user.login.slice(0, 2).toUpperCase()}</div><div><h2>{identity.user.name || identity.user.login}</h2><p>@{identity.user.login} <span>·</span> GitHub ID {identity.user.id}</p></div><div className="identity-detail"><strong>OAuth App</strong><p>{identity.scopes.join(", ") || "No scopes returned"}</p></div></section>
        <section className="repo-panel panel"><div className="panel-heading"><div><h2>{view === "my" ? "My repositories" : view === "favorites" ? "Favorites" : "Access candidates"}</h2><p>{view === "my" ? "Owner, collaborator, team and recent contribution sources." : view === "favorites" ? "A union of observed stars and watches." : "All discovered sources. Organization access alone does not establish relevance."}</p></div><span className="count">{data?.total ?? "—"} repositories</span></div>
          <label className="search"><span>Search repositories</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Filter by owner or repository name…" /></label>
          <div aria-live="polite">{!data ? <p className="empty">{busy ? "Fetching repositories and access sources…" : "Waiting for repository results…"}</p> : !data.items.length ? <p className="empty">No repositories observed in this view. Review source coverage below.</p> : data.items.map((repo) => <article className="repo" key={repo.id}><div><a href={repo.html_url} target="_blank" rel="noreferrer">{repo.full_name} <span>↗</span></a><span className="visibility">{repo.private ? "Private" : "Public"}</span><p>{repo.language || "Language unknown"} <span>·</span> {repo.default_branch || "Default branch unknown"}</p></div><div className="sources">{repo.sources.map((source) => <span key={source}>{source.toLowerCase().replace("_", " ")}</span>)}</div></article>)}</div>
          {data?.next_cursor && <button className="secondary load-more" disabled={busy} onClick={more}>{busy ? "Loading…" : "Load more repositories"}</button>}
        </section>
        <section className="panel coverage"><div className="panel-heading"><div><h2>Source coverage</h2><p>Observed API results require known fixtures to confirm completeness. Restricted organizations may require approval or SSO.</p></div><button className="primary" disabled={busy} onClick={verify}>{busy ? "Checking…" : "Verify access & save report"}</button></div>
          <div className="coverage-grid">{data?.coverage.map((source) => <div className="coverage-item" key={source.source}><strong>{source.source.toLowerCase().replace("_", " ")}</strong><span className={source.status === "OBSERVED" ? "observed" : "limited"}>{source.status} · {source.count ?? "unknown"}</span><p>{source.note}</p></div>)}</div>
          {report && <div className="notice" role="status">Private Markdown report saved: <a href="/api/v1/pretest/github/report" download>{report.filename}</a>. Includes your GitHub login and ID for verification; repository names, private content, and tokens are omitted.</div>}
        </section>
      </>}
      <footer>Phase 0 preflight <span>·</span> Sessions expire or end when the backend restarts. AWS checks run separately through the local CLI.</footer>
    </main>
  </div>;
}
