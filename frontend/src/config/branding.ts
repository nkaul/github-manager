/** App-wide defaults. Content settings → Appearance can override them in this browser. */
export type LogoVariant = "orbit" | "rays";
export type LogoPreferences = { variant: LogoVariant; animate: boolean };

export const BRANDING_DEFAULTS: LogoPreferences = {
  variant: "rays",
  animate: true,
};

export const LOGO_VARIANTS = {
  orbit: {
    label: "Continuous blue aura",
    description: "A peaceful cat inside a continuously rotating blue aura.",
    animation: "/branding/v2/zen-loop-orbit-96.gif",
    poster: "/branding/v2/zen-loop-orbit-poster.svg",
  },
  rays: {
    label: "Blue zen rays",
    description: "A tail-free cat enters meditation and softly pulses blue rays.",
    animation: "/branding/v2/zen-loop-rays-96.gif",
    poster: "/branding/v2/zen-loop-rays-poster.svg",
  },
} as const;
