"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api, currentSessionGeneration, GITHUB_SIGN_IN_PATH, type Identity } from "@/lib/api";
import "./session.css";

export function SessionGuard({ identity, update }: { identity: Identity; update: (identity: Identity) => void }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [deadline, setDeadline] = useState(0);
  const [remaining, setRemaining] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [dismissedWarning, setDismissedWarning] = useState("");
  const mounted = useRef(false);
  const requestGeneration = useRef(0);
  const checking = useRef(false);
  const checkedExpiry = useRef(false);
  const info = identity.session;
  useEffect(() => { const pending = requestGeneration; mounted.current = true; return () => { mounted.current = false; pending.current++; }; }, []);

  useEffect(() => {
    const end = info ? (info.received_at_ms ?? Date.now()) + info.expires_in_seconds * 1000 : 0;
    const timer = setTimeout(() => { setDeadline(end); setRemaining(info ? Math.ceil(info.expires_in_seconds) : null); checkedExpiry.current = false; }, 0);
    return () => clearTimeout(timer);
  }, [info]);

  const check = useCallback(async () => {
    if (checking.current) return;
    checking.current = true;
    const generation = ++requestGeneration.current;
    const session = currentSessionGeneration();
    try { const value = await api<Identity>("/me"); if (mounted.current && generation === requestGeneration.current && session === currentSessionGeneration()) update(value); }
    catch (failure) { if (mounted.current && generation === requestGeneration.current) setError((failure as Error).message); }
    finally { checking.current = false; }
  }, [update]);

  useEffect(() => {
    if (!deadline) return;
    const tick = () => {
      const seconds = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
      setRemaining(seconds);
      if (!seconds && !checkedExpiry.current) { checkedExpiry.current = true; void check(); }
    };
    const visible = () => { if (document.visibilityState === "visible") { tick(); void check(); } };
    const timer = setInterval(tick, 1000);
    document.addEventListener("visibilitychange", visible);
    window.addEventListener("focus", visible);
    return () => { clearInterval(timer); document.removeEventListener("visibilitychange", visible); window.removeEventListener("focus", visible); };
  }, [deadline, check]);

  const warningPhase = `${deadline}:${remaining !== null && remaining <= 10 ? "final" : "early"}`;
  const warning = Boolean(info && remaining !== null && remaining <= info.warning_seconds && dismissedWarning !== warningPhase);
  useEffect(() => {
    if (warning && !dialog.current?.open) dialog.current?.showModal();
    if (!warning && dialog.current?.open) dialog.current.close();
  }, [warning]);

  async function extend() {
    setBusy(true); setError("");
    const generation = ++requestGeneration.current;
    const session = currentSessionGeneration();
    try { const value = await api<Identity>("/auth/session/extend", identity.csrf_token); if (mounted.current && generation === requestGeneration.current && session === currentSessionGeneration()) update(value); }
    catch (failure) { if (mounted.current && generation === requestGeneration.current) setError((failure as Error).message); }
    finally { if (mounted.current) setBusy(false); }
  }

  return <dialog ref={dialog} className="session-dialog" aria-labelledby="session-warning-title" onCancel={event => { event.preventDefault(); setDismissedWarning(warningPhase); }}>
    <h2 id="session-warning-title">Your session is about to expire</h2>
    <p>{remaining === 0 ? "Checking whether your session is still available…" : `Your session ends in ${Math.floor((remaining || 0) / 60)}:${String((remaining || 0) % 60).padStart(2, "0")}.`}</p>
    <p>Save unfinished edits before your session ends. Saved reviews and repository organization are preserved.</p>
    {error && <p className="session-error" role="alert">{error}</p>}
    {!info?.renewable && <p>GitHub authorization is nearing its limit. Sign in again to continue.</p>}
    <div className="session-actions"><button className="session-secondary" disabled={busy} onClick={() => setDismissedWarning(warningPhase)}>Save work first</button>{info?.renewable ? <button className="session-primary" disabled={busy} onClick={() => void extend()}>{busy ? "Extending…" : "Extend session"}</button> : <a className="session-primary" href={GITHUB_SIGN_IN_PATH}>Sign in again</a>}</div>
    {remaining === 0 && error && <button className="session-secondary" disabled={busy} onClick={() => void check()}>Check connection again</button>}
  </dialog>;
}
