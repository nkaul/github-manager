# Phase 0.9 — selectable Zen logos and KPI icons

Date: October 13, 2026. Status: **PASS**.

The approved Blue zen rays cat now has no tail throughout the animation, including its normal and meditating poses. It is the default app logo. The continuous blue aura remains available as the alternate. Both are self-hosted transparent GIFs, with static SVG posters for paused animation, reduced motion and the browser tab. The selected style appears on the header, sign-in screen and browser tab.

## Configuration and use

Open **Content settings → Appearance**, then choose **Blue zen rays** or **Continuous blue aura**. **Animate logo** pauses/resumes the selected style. The browser's reduced-motion preference uses the still poster automatically. **Restore default logo** clears the browser override.

Preferences persist in this browser across reloads, workspace collections and sign-out using `ghm:logo-preferences:v1`. Other browsers do not inherit them. App-wide defaults are in [branding.ts](../../frontend/src/config/branding.ts): `variant: "rays" | "orbit"` and `animate: boolean`. Rebuild after editing these defaults; an existing browser override takes precedence until restored.

All five compact KPI cards retain their labels and scoped counts and now include decorative icons: repository book for **In this view**, tag for **Labeled**, inbox for **No project**, review bubble for **Needs review**, and checked box for **Selected**. Icon colors follow each card's existing Material palette accent. Labels remain available to assistive technology.

## Validation

| Check | Result |
|---|---|
| Full product browser suite | **13 passed**; includes the new logo/KPI workflow and existing organization, taxonomy, budget, drag/drop and responsive workflows. |
| Final focused branding rerun | **1 passed**, after the radio-sizing and browser-tab changes. Covers saved selection/reload, animation on/off, reduced motion, default restore, sign-out logo, favicon and all five KPI icons. |
| Original preflight browser suite | **4 passed**; original preflight UI remains unchanged. |
| Static and production build | **PASS**: TypeScript, ESLint and Next production build. Backend test-server formatting/lint passed. No backend product code changed in this update. |
| Production runtime | **PASS**: login and all four app assets return 200; backend health reports Phase 0.9/local; OAuth configuration is present; anonymous identity returns 401. No browser page errors or desktop document overflow. Actual GitHub login was not repeated for this visual update. |
| Layout | Screenshots reviewed at 1920×1080 and 390×844; no horizontal document overflow. Appearance radio controls remain compact. |
| GIF quality | Decoded real GIFs have transparent, unclipped borders and infinite loops. Aura: 100 frames/4 seconds, all frames distinct. Rays: 150 frames/6 seconds, intentional holds and three pulses. Both encoded at 25fps. |
| Preservation | Earlier readiness/benchmark evidence and original demo media retained. The protected-evidence verifier passed for 163 files and original ledger rows (1 experiment, 34 calls, 29 cache entries), with the original preflight copy identical. The live workspace matches its pre-change SQLite backup; eight original media artifacts retain their manifest hashes. No provider HTTP calls or generation reservations were added by this update. |

App assets use 96×96 GIFs (aura 218,022 bytes; rays 200,898 bytes) displayed at compact header sizes. Larger 256/512 exports and reproducible rendering/QA scripts remain in [animated-v2](../design/logo-variants-20261013/animated-v2/). Earlier concepts and animation versions remain available unchanged. This revision introduces no packages or AWS changes.

## Review evidence

- [KPI icons and default rays logo, 1080p](private/demo/logo-kpis-20261013/branding-kpis-rays-1080p.png)
- [Appearance selector, 1080p](private/demo/logo-kpis-20261013/branding-appearance-1080p.png)
- [Appearance selector, phone](private/demo/logo-kpis-20261013/branding-appearance-phone.png)
- [Production sign-in screen, 1080p](private/demo/logo-kpis-20261013/production-login-1080p.png)
- [Production smoke results](private/demo/logo-kpis-20261013/production-smoke.json)
- [Decoded GIF and preview checks](../design/logo-variants-20261013/animated-v2/animation-qa.json)

Browser tests use disposable fixtures and do not modify the user's GitHub workspace. Local diagnostics and the pre-change backup are retained under `.tools/logo-app-baseline-20261013/`. Earlier narrated video/audio remains unchanged and predates these logo and Appearance controls.

The updated production app is running at **http://127.0.0.1:3000**. Sign in again after the backend restart; existing workspace data and AI allowance are retained.
