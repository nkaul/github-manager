"use client";

import { useSyncExternalStore } from "react";
import { BRANDING_DEFAULTS, type LogoPreferences } from "@/config/branding";

export const LOGO_STORAGE_KEY = "ghm:logo-preferences:v1";
const CHANGE_EVENT = "ghm:logo-preferences-changed";
const DEFAULT_SNAPSHOT = JSON.stringify(BRANDING_DEFAULTS);

function snapshot(): string {
  try {
    const value = JSON.parse(localStorage.getItem(LOGO_STORAGE_KEY) || DEFAULT_SNAPSHOT);
    if ((value?.variant === "orbit" || value?.variant === "rays") && typeof value.animate === "boolean") {
      return JSON.stringify({ variant: value.variant, animate: value.animate });
    }
  } catch { /* An unavailable/invalid preference uses the configured default. */ }
  return DEFAULT_SNAPSHOT;
}

function subscribe(changed: () => void) {
  window.addEventListener("storage", changed);
  window.addEventListener(CHANGE_EVENT, changed);
  return () => { window.removeEventListener("storage", changed); window.removeEventListener(CHANGE_EVENT, changed); };
}

export function useLogoPreferences(): LogoPreferences {
  const value = useSyncExternalStore(subscribe, snapshot, () => DEFAULT_SNAPSHOT);
  return JSON.parse(value) as LogoPreferences;
}

export function updateLogoPreferences(patch: Partial<LogoPreferences>) {
  const value = { ...JSON.parse(snapshot()), ...patch } as LogoPreferences;
  localStorage.setItem(LOGO_STORAGE_KEY, JSON.stringify(value));
  window.dispatchEvent(new Event(CHANGE_EVENT));
}

export function resetLogoPreferences() {
  localStorage.removeItem(LOGO_STORAGE_KEY);
  window.dispatchEvent(new Event(CHANGE_EVENT));
}
