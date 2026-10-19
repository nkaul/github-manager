# Agent A/B inputs — actual Ground Truth screens

Captured October 18, 2026 from the actual application on isolated browser-test ports 3015/8015. The tests read the validated public corpus and independent pilot sidecar; the identity and saved draft are disposable QA records. They do not represent user annotation or a production sign-in. The real application remains on 3000/8000.

## What changed

- A prominent Agent A & B inputs section shows independent purpose summaries and grouped Project/Topic/Tag suggestions before the editable human review. The comparison opens each agent’s rationale, exact evidence and reading scope.
- Repositories outside the thirty-case independent pilot now explain the absence of A/B data and provide a direct pilot-queue entry. Their original corpus proposal remains a separate layer.
- The searchable review-scope control exposes all 600 repositories, the initial twenty human-review cases and all thirty pilot cases. Opening a pilot card sets that queue scope and clears conflicting filters. Confirm & next stays in that scope.
- Inspecting a comparison does not replace a saved human review/draft, stage an annotator or mark any group reviewed. Staging remains explicit; saving remains explicit.

## Screens

| Screenshot | What it verifies |
|---|---|
| [Pilot inputs, desktop](agent-inputs-pilot-1920.png) | Both independent summaries and colored grouped labels; a saved QA draft remains a separate editable layer. |
| [Full comparison, desktop](agent-inputs-comparison-1920.png) | Independent rationale, evidence and scope remain available. |
| [Pilot inputs, mobile](agent-inputs-pilot-390.png) | The comparison entry is visible at 390 px; the review scrolls without horizontal page overflow. |
| [Outside pilot, desktop](agent-inputs-nonpilot-1920.png) | Explicit coverage explanation and pilot queue entry. |
| [Outside pilot, mobile](agent-inputs-nonpilot-390.png) | Pilot entry remains available even though the desktop toolbar is hidden. |
| [Review, 1280 px](redesign-1280.png) | Compact review and bounded evidence sheet layout remain supported. |

## Validation

All **12 Ground Truth browser workflows passed** on isolated ports, including the new coverage/mobile, saved-draft inspection and pilot-scoped Confirm & next cases. Existing label colors, navigation guards, final-save conflict handling, incomplete drafts, source evidence, session recovery and responsive layout checks remain passing. Frontend lint and TypeScript checks passed. Root integration owns production build/restart and protected-data verification.

The pilot has thirty dual annotations, not six hundred. These screenshots do not imply further model calls, calibrated confidence, semantic reading completeness or additional human confirmation.
