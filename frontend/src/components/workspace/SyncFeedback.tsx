"use client";

import { useEffect, useRef, useState } from "react";
import type { Run } from "@/lib/workspace";
import { GITHUB_SIGN_IN_PATH } from "@/lib/api";
import "./session.css";

export function SyncFeedback({ current, failure, dismiss, retry }: { current: Run | null; failure: Run | null; dismiss: () => void; retry: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [remaining, setRemaining] = useState<number | null>(null);
  const [dismissedSlowRun, setDismissedSlowRun] = useState("");
  useEffect(() => {
    const started = current?.kind === "SYNC" && current.started_at ? Date.parse(current.started_at) : NaN;
    const limit = current?.timeout_seconds;
    const tick = () => setRemaining(Number.isFinite(started) && limit ? Math.max(0, Math.ceil(limit - (Date.now() - started) / 1000)) : null);
    const initial = setTimeout(tick, 0);
    const timer = setInterval(tick, 1000);
    return () => { clearTimeout(initial); clearInterval(timer); };
  }, [current?.kind, current?.started_at, current?.timeout_seconds]);
  const slow = Boolean(current?.kind === "SYNC" && remaining !== null && remaining <= 30 && dismissedSlowRun !== current.id);
  const open = Boolean(failure || slow);
  useEffect(() => {
    if (open && !dialog.current?.open) dialog.current?.showModal();
    if (!open && dialog.current?.open) dialog.current.close();
  }, [open]);
  function close() { if (failure) dismiss(); else if (current) setDismissedSlowRun(current.id); }
  return <dialog ref={dialog} className="session-dialog" aria-labelledby="sync-feedback-title" onCancel={event => { event.preventDefault(); close(); }}>
    <h2 id="sync-feedback-title">{failure ? failure.error_code?.includes("TIMEOUT") ? "GitHub Sync timed out" : "GitHub Sync stopped" : "GitHub Sync is taking longer than expected"}</h2>
    <p>{failure?.message || `Sync is still running. It will stop at its time limit in about ${remaining ?? 0} seconds and let you retry.`}</p>
    <p>Your saved repositories, labels and reviews are preserved. A Sync timeout does not by itself mean your sign-in expired.</p>
    <div className="session-actions"><button className="session-secondary" onClick={close}>{failure ? "Close" : "Keep browsing"}</button>{failure?.reauthentication_required ? <a className="session-primary" href={GITHUB_SIGN_IN_PATH}>Sign in again</a> : failure?.retryable && <button className="session-primary" disabled={Boolean(current)} onClick={() => { dismiss(); retry(); }}>Retry sync</button>}</div>
  </dialog>;
}
