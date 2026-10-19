# Ground Truth: Agent A/B visibility and pilot navigation

October 18, 2026. Implemented and loaded in the real local application at `http://127.0.0.1:3000`.

## Why the independent inputs were difficult to find

The full corpus contains 600 repositories with original proposed labels. The independent co-annotation pilot covers **30 repositories**, with **20 selected for the initial human-review queue**. The other 570 have original proposals but no independent Agent A/B annotations. Those proposals must not be presented as two-agent agreement.

Three interface/navigation problems obscured this distinction:

1. The comparison action sat below the editable review fields, making the original recommendation appear to be the only input.
2. The desktop pilot button disappeared at narrow screen widths, and nonpilot repositories did not explain why the comparison was absent. A globally ready pilot could also expose a comparison action for a repository without a pilot record.
3. Opening a pilot card selected its repository without constraining the review queue. **Confirm & next** could consequently advance into the full corpus and open a repository with no independent annotations.

## What changed

Pilot repositories now show an **Agent A & B inputs** section immediately below repository metadata. Each agent has its own purpose summary and colored Project, Topic and Tag suggestions. A prominent **Compare independent annotations** button exposes rationales, exact saved-source evidence, agreed/differing labels, derived Domains, missing concepts and declared reading scope.

Nonpilot repositories explicitly explain that their original proposal has no Agent A/B comparison. They offer a pilot-queue link that remains available on mobile. A comparison requires a ready pilot **and a record for the selected repository**.

A searchable **Repository review scope** control offers:

| Scope | Current coverage | Purpose |
|---|---:|---|
| All repositories | 600 | Browse the complete corpus and original proposals. |
| Initial human review | 20 | Review the preselected targeted and random audit cases. |
| Agent A/B pilot | 30 | Inspect every independently annotated pilot repository. |

Opening **Review** from a pilot card applies its twenty- or thirty-case scope and clears conflicting search/status/taxonomy filters. Manually changing scope preserves the other filters, guards unsaved edits and opens a matching case. **Confirm & next** uses the same scope as the list, including after a save removes the current record from a status filter.

The additive API parameter `annotation_scope=all|pilot|initial_queue` applies to both `/api/v1/corpus/repos` and `/api/v1/corpus/repos/{repository_id}/neighbors`. Selection happens before pagination. Explicit pilot requests fail visibly if pilot integrity/availability checks fail; they never silently broaden to the 600 repositories. The default remains `all`.

## How to review now

1. Refresh localhost and sign in again if prompted, then select **Public - Ground Truth**.
2. Choose **Repository review scope → Initial human review · 20**.
3. Read both summaries, then use **Compare independent annotations** to inspect evidence and disagreements.
4. Correct your editable review. Optionally stage one annotator's suggestions; staging clears the reviewed checks and does not save.
5. Explicitly review Projects, Topics and Tags, then **Confirm & next**. Use **Save draft** for unfinished work or **Needs evidence** for unresolved decisions.

Comparing is optional. Inspecting agent inputs does not overwrite a draft or saved human decision, stage suggestions, check review dimensions or confirm anything. Agent agreement remains a proposal, not calibrated confidence or human ground truth.

## Verification and preservation

- **57 backend checks passed** across corpus browsing, annotation adapters, review/draft persistence, pilot validation, scoped pagination/continuation and fixture-port protection. This includes six focused scope tests.
- **All 12 Ground Truth browser workflows passed** on isolated ports 3015/8015 using disposable identities/databases and real validated public sources. Coverage includes A/B visibility, mobile access, saved-draft inspection, pilot-scoped confirmation/continuation, full-corpus switching, source evidence, conflicts, session recovery and navigation guards.
- ESLint, TypeScript, Ruff/formatting and the production build passed. Actual desktop and mobile captures were inspected; see the [screens and validation notes](../design/workspace-refinement/agent-inputs-2026-10-18/README.md).
- The production frontend and backend were restarted with the existing live-AI launch setting. Frontend `/` and backend `/health` returned HTTP 200; sign-in returned a 302 redirect to GitHub with the configured non-fixture client. The test-only login route returned 404. No authenticated review was written to the real account for this smoke check.
- All **548 protected corpus/pilot/readiness artifacts** match the fresh baseline, including the API-budget database file. Personal workspace sections are unchanged. A new human review was saved by the user during this task: removing only that addition in a read-only comparison exactly reproduces the prior review-section hash; reversing only its control-version increment reproduces the prior organization-section hash. The actual saved record remains intact. The local database now has four human reviews; zero are in the independent pilot at this check.

The preservation result is recorded locally in `.tools/ab-visibility-preservation-result.json`. No source release, agent annotation, benchmark, registry or existing review was replaced. No new provider API call, OAuth scope, dependency, cloud resource or budget reset was needed. This change does not annotate the remaining 570 repositories or promote proposals to gold labels.

The [pilot handoff guide](agent-annotation-pilot-2026-10-17.md#use-the-app-for-human-review) has been updated with the new entry points and queue behavior. Existing pilot results and historical validation remain preserved.
