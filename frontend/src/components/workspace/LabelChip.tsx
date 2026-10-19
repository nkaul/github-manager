import type { CSSProperties, ReactNode } from "react";

// Material surfaces and darker inks keep small labels readable. This is an
// identity cue, never a status: hundreds of labels intentionally reuse hues.
export const LABEL_CHIP_PALETTE = [
  ["#e8eaf6", "#283593", "#9fa8da"], // Indigo
  ["#e3f2fd", "#0d47a1", "#90caf9"], // Blue
  ["#e1f5fe", "#01579b", "#81d4fa"], // Light Blue
  ["#e0f7fa", "#006064", "#80deea"], // Cyan
  ["#e0f2f1", "#004d40", "#80cbc4"], // Teal
  ["#e8f5e9", "#1b5e20", "#a5d6a7"], // Green
  ["#f1f8e9", "#33691e", "#c5e1a5"], // Light Green
  ["#f9fbe7", "#5b6119", "#dce775"], // Lime
  ["#fff8e1", "#795000", "#ffe082"], // Amber
  ["#fff3e0", "#8a3c00", "#ffcc80"], // Orange
  ["#fce4ec", "#880e4f", "#f48fb1"], // Pink
  ["#efebe9", "#4e342e", "#bcaaa4"], // Brown
] as const;

export function labelChipProps(id: string) {
  // FNV-1a over the canonical ID: rename, sort, filter and reload do not change
  // a label's color, and repeated labels share it across both workspaces.
  let hash = 2166136261;
  for (let i = 0; i < id.length; i++) hash = Math.imul(hash ^ id.charCodeAt(i), 16777619);
  const [background, ink, border] = LABEL_CHIP_PALETTE[(hash >>> 0) % LABEL_CHIP_PALETTE.length];
  return {
    "data-label-id": id,
    style: { "--label-bg": background, "--label-ink": ink, "--label-border": border } as CSSProperties,
  };
}

export function LabelChip({ id, kind, children }: { id: string; kind?: string; children: ReactNode }) {
  return <span className="wm-chip wm-label-chip" {...labelChipProps(id)} title={kind ? `${kind}: ${typeof children === "string" ? children : id}` : undefined}>{children}</span>;
}
