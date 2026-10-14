"use client";

import { useState } from "react";
import Image from "next/image";
import { LOGO_VARIANTS, type LogoVariant, type LogoPreferences } from "@/config/branding";
import { resetLogoPreferences, updateLogoPreferences, useLogoPreferences } from "@/lib/branding";

export function LogoSettings() {
  const preferences = useLogoPreferences();
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  function save(patch: Partial<LogoPreferences>) {
    setError("");
    try { updateLogoPreferences(patch); setMessage("Logo preference saved in this browser."); }
    catch { setError("Browser storage is unavailable; the default logo is still active."); }
  }
  return <section className="wm-panel wm-appearance" aria-label="Appearance settings"><div className="wm-panel-heading"><div><h2>Appearance</h2><p>Choose your logo for the header and sign-in screen. Changes are saved in this browser.</p></div></div>
    <fieldset className="wm-logo-choices"><legend className="wm-sr-only">Logo style</legend>{(Object.entries(LOGO_VARIANTS) as [LogoVariant, typeof LOGO_VARIANTS[LogoVariant]][]).map(([key, logo]) => <label key={key} className={`wm-logo-choice ${preferences.variant === key ? "is-selected" : ""}`}>
      <input type="radio" name="logo-style" value={key} checked={preferences.variant === key} onChange={() => save({ variant: key })} />
      <Image src={logo.poster} alt="" width={72} height={72} unoptimized />
      <span><strong>{logo.label}</strong><small>{logo.description}</small></span>
    </label>)}</fieldset>
    <div className="wm-logo-options"><label className="wm-check"><input type="checkbox" checked={preferences.animate} onChange={e => save({ animate: e.target.checked })} />Animate logo</label><small>Your reduced-motion preference automatically uses a still icon.</small><button className="wm-link" onClick={() => { try { resetLogoPreferences(); setError(""); setMessage("Default logo restored."); } catch { setError("Browser storage is unavailable."); } }}>Restore default logo</button></div>
    {message && <p className="wm-logo-feedback" role="status">{message}</p>}{error && <p className="wm-error" role="alert">{error}</p>}
  </section>;
}
