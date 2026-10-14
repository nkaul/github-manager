# Phase 0.9 — Selective AI allowance controls

Date: October 12, 2026. Status: **PASS; updated localhost app running**.

The user requested an explanation of Access candidates and the ability to reset/selectively override the exhausted 20/20 request allowance. The old fixed generation ceiling was also exhausted; changing HTTP alone would not restore inference. [ADR 0003](../adr/0003-local-ai-allowance-controls.md) records the approved local change.

Delivered **AI Organization → Manage API allowance** with new-window renewal, independently selectable HTTP/generation limits, reasons, recent audit history and lifetime counters. Updates require a configured local budget operator, an authenticated session, same Origin and CSRF token. Stale revisions cannot apply twice. The existing workspace owner's numeric GitHub ID is configured in ignored backend/.env; the server-only setting is documented in the example. The [operator guide](../development/ai-allowance.md) includes UI and CLI instructions.

Access candidates now explains its discovery/review role and the **Details → Include in My Repos** action. This does not grant GitHub access or modify upstream repositories.

## Applied renewal

| Measure | Before | After |
|---|---|---|
| Current HTTP window | 20/20 | **0/20** |
| Current generation window | 10/10 | **0/10** |
| Lifetime application HTTP attempts | 20 | **20, unchanged** |
| Cumulative generation reservations | 44 | **44, unchanged** |
| Cumulative estimated spend | $0.060911 | **$0.060911, unchanged** |
| Outstanding reservation | $0 | **$0, unchanged** |
| Cumulative spending ceiling | $5 | **$5, unchanged** |
| Allowance revision | 0 | **1** |

The renewal adds admission for 20 HTTP attempts and ten generations; cumulative admission ceilings are now 40 application HTTP attempts and 54 generation reservations. It deletes no usage, reports, caches or reservations. The private before/after receipt is saved in the ignored demo validation directory. No real OpenAI request was made by this update or its validation.

## Validation

| Check | Result |
|---|---|
| Complete backend suite | **121 passed** in 6.63 seconds |
| Product browser acceptance | **5 passed**, including renewal, selected generation-only update, history and persistence |
| Original browser regression | **4 passed**, original test source preserved |
| Ruff lint / format | PASS; 55 Python files formatted |
| Frontend ESLint / TypeScript | PASS |
| Final production Next.js build | PASS |
| Restarted frontend / backend | HTTP 200; product present; health phase=0.9, storage=local |
| Anonymous allowance audit route | HTTP 401 |
| Preservation verifier | PASS: 163 protected files; 34 historical API records; 29 historical cache records; original preflight UI identical |
| Existing packaged video/audio/captions/metadata checksums | Unchanged |

New backend cases exercise concurrent HTTP/generation admission, selective changes without usage reset, rejection of limits below usage, bounded values/unknown spending overrides, stale concurrent renewal, operator/CSRF checks, shared collection scope and durable reopening. A mock HTTP transport exercises the actual LangChain/provider hooks past the old 44-generation ceiling, then confirms the new cap blocks further requests. The original dollar reservation and bound-violation checks remain in the application adapter. These are offline/mock-provider checks, not a new live quality benchmark.

The production app was restarted with live mode enabled at **http://127.0.0.1:3000**. The restart invalidated in-memory login sessions; sign in again. Saved workspace data is retained. UI changes do not require new OAuth App registration or model/key changes. Cloud resources and GitHub repositories were untouched. The completed video and earlier 20/20 results remain historical evidence; current counters are available in the app.
