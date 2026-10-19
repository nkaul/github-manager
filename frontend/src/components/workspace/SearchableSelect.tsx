"use client";

import { useEffect, useId, useLayoutEffect, useMemo, useRef, useState, type CSSProperties, type KeyboardEvent } from "react";
import { createPortal } from "react-dom";
import "./SearchableSelect.css";

export type SearchableSelectOption = { value: string; label: string; disabled?: boolean; group?: string; searchText?: string; alwaysVisible?: boolean };

type Props = {
  value: string;
  onChange: (value: string, query?: string) => void;
  options: SearchableSelectOption[];
  id?: string;
  name?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
  placeholder?: string;
  style?: CSSProperties;
  "aria-label"?: string;
  "aria-labelledby"?: string;
  "aria-describedby"?: string;
};

const normalize = (text: string) => text.normalize("NFKC").toLocaleLowerCase();

/** Single-select combobox: filtering never changes the committed value. */
export function SearchableSelect({ value, onChange, options, id, name, required, disabled, className = "", placeholder, style, ...aria }: Props) {
  const generatedId = useId();
  const inputId = id || `wm-select-${generatedId}`;
  const listId = `${inputId}-list`;
  const input = useRef<HTMLInputElement>(null);
  const popup = useRef<HTMLDivElement>(null);
  const anchor = useRef<HTMLSpanElement>(null);
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [active, setActive] = useState<string | null>(null);
  const [host, setHost] = useState<Element | null>(null);
  const [position, setPosition] = useState<CSSProperties>({ visibility: "hidden" });
  const committed = options.find(option => option.value === value);
  const matches = useMemo(() => {
    const term = normalize(query.trim());
    return options.filter(option => option.alwaysVisible || !term || normalize(`${option.label} ${option.group || ""} ${option.searchText || ""}`).includes(term));
  }, [options, query]);
  const enabled = matches.filter(option => !option.disabled);
  const activeValue = enabled.some(option => option.value === active) ? active : enabled[0]?.value ?? null;
  const optionId = (option: SearchableSelectOption) => `${listId}-${options.indexOf(option)}`;

  // A typed query is not a valid selection. Required forms validate the committed ID.
  useEffect(() => {
    input.current?.setCustomValidity(required && (!value || !committed || committed.disabled) ? "Choose an available option from the list." : "");
  }, [value, committed, required]);

  function show(edge?: "first" | "last") {
    if (disabled) return;
    setHost(input.current?.closest('[role="dialog"],dialog') || input.current?.closest(".wm-app") || document.body);
    setQuery("");
    const available = options.filter(option => !option.disabled);
    setActive(edge === "last" ? available.at(-1)?.value ?? null : edge === "first" ? available[0]?.value ?? null : available.find(option => option.value === value)?.value ?? available[0]?.value ?? null);
    setOpen(true);
  }
  function close() { setOpen(false); setQuery(""); }
  function choose(option: SearchableSelectOption) {
    if (option.disabled) return;
    close();
    onChange(option.value, query.trim());
    input.current?.focus();
  }
  function keyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Escape" && open) {
      event.preventDefault(); event.stopPropagation(); close(); return;
    }
    if (event.key === "Tab") { close(); return; }
    if (["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) {
      // Home/End retain ordinary text editing while closed.
      if (!open && ["Home", "End"].includes(event.key)) return;
      event.preventDefault(); event.stopPropagation();
      if (!open) { show(event.key === "ArrowUp" ? "last" : "first"); return; }
      const index = enabled.findIndex(option => option.value === activeValue);
      const next = event.key === "Home" ? 0 : event.key === "End" ? enabled.length - 1 : Math.max(0, Math.min(enabled.length - 1, index + (event.key === "ArrowDown" ? 1 : -1)));
      setActive(enabled[next]?.value ?? null);
    }
    if (event.key === "Enter" && open) {
      event.preventDefault(); event.stopPropagation();
      const option = enabled.find(option => option.value === activeValue);
      if (option) choose(option);
    }
  }

  useLayoutEffect(() => {
    if (!open || disabled) return;
    function updatePosition() {
      if (!anchor.current?.isConnected) return;
      const rect = anchor.current.getBoundingClientRect();
      const margin = 12;
      const width = Math.min(Math.max(rect.width, 260), innerWidth - margin * 2);
      const below = innerHeight - rect.bottom - margin - 4;
      const above = rect.top - margin - 4;
      const goAbove = below < 180 && above > below;
      const maxHeight = Math.max(48, Math.min(280, goAbove ? above : below));
      const height = Math.min(popup.current?.scrollHeight || 280, maxHeight);
      setPosition({ left: Math.max(margin, Math.min(rect.left, innerWidth - width - margin)), width, top: goAbove ? rect.top - height - 4 : rect.bottom + 4, maxHeight });
    }
    updatePosition();
    window.addEventListener("resize", updatePosition);
    window.addEventListener("scroll", updatePosition, true);
    return () => { window.removeEventListener("resize", updatePosition); window.removeEventListener("scroll", updatePosition, true); };
  }, [open, disabled, matches]);

  useEffect(() => {
    if (!open) return;
    function outside(event: PointerEvent) {
      const target = event.target as Node;
      if (!anchor.current?.contains(target) && !popup.current?.contains(target)) close();
    }
    document.addEventListener("pointerdown", outside, true);
    return () => document.removeEventListener("pointerdown", outside, true);
  }, [open]);

  useEffect(() => {
    if (!open || !activeValue) return;
    const option = matches.find(item => item.value === activeValue);
    if (option) document.getElementById(optionId(option))?.scrollIntoView({ block: "nearest" });
  }, [activeValue, open, query]); // eslint-disable-line react-hooks/exhaustive-deps

  const expanded = open && !disabled;
  return <span ref={anchor} className={`wm-select ${className}`} style={style} data-disabled={disabled || undefined}>
    <input ref={input} id={inputId} className="wm-select-input" type="text" role="combobox" autoComplete="off" spellCheck={false}
      value={expanded ? query : committed?.label || value} placeholder={expanded ? committed?.label || placeholder || "Search options…" : placeholder || "Choose an option"}
      disabled={disabled} required={required} aria-required={required || undefined} aria-expanded={expanded} aria-controls={expanded ? listId : undefined} aria-autocomplete="list"
      aria-activedescendant={expanded && activeValue !== null ? optionId(matches.find(option => option.value === activeValue)!) : undefined} {...aria}
      onFocus={event => event.currentTarget.select()} onClick={() => { if (!expanded) show(); }}
      onChange={event => { if (!expanded) setHost(input.current?.closest('[role="dialog"],dialog') || input.current?.closest(".wm-app") || document.body); setOpen(true); setQuery(event.target.value); setActive(null); }}
      onBlur={() => close()} onKeyDown={keyDown} />
    <span className="wm-select-indicator" aria-hidden="true"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="m7 10 5 5 5-5" /></svg></span>
    {name && <input type="hidden" name={name} value={value} disabled={disabled} />}
    {expanded && host && createPortal(<div ref={popup} id={listId} className="wm-select-popup" role="listbox" aria-label="Available options" style={position} onMouseDown={event => event.preventDefault()}>
      {matches.length ? matches.map((option, index) => <div key={option.value}>
        {option.group && (index === 0 || matches[index - 1].group !== option.group) && <div className="wm-select-group">{option.group}</div>}
        <div id={optionId(option)} role="option" aria-selected={option.value === value} aria-disabled={option.disabled || undefined} data-value={option.value}
          className={`wm-select-option ${option.value === activeValue ? "is-active" : ""}`} onPointerMove={() => { if (!option.disabled) setActive(option.value); }} onClick={event => { event.preventDefault(); event.stopPropagation(); choose(option); }}>
          <span>{option.label}</span>{option.value === value && <span className="wm-select-check" aria-hidden="true">✓</span>}
        </div>
      </div>) : <div className="wm-select-empty" role="status">No matching options</div>}
    </div>, host)}
  </span>;
}
