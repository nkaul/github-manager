# Agent annotation pilot — execution record

Date: October 17, 2026. Authorized by the user's request to start the pilot with subagents and make assignments available in the app. The subsequent correction chooses the agents' existing intelligence instead of additional provider API calls.

## Scope and independence

Select thirty repositories from the frozen English V2 release: three per sampling domain, development split only, by a fixed label-blind hash ordering. Preserve the release, original proposals, taxonomy IDs, source snapshots, validation/test allocation, prior reports and all human decisions.

Two Codex agents independently read the saved README and supplied supporting artifacts for every selected repository. They receive the full known registry and trusted metadata, but not original agent labels, summaries, app predictions or each other's answers. A coordinator creates blind packets, records source bindings and validates outputs; it does not manufacture semantic annotations with keyword rules.

Each annotation retains purpose, artifact type, capabilities, primary technologies, evidenced initiative relationships, limitations, exact quotations, actual reading scope, missing concepts and uncertainty. Complete stored files and complete reading are separate facts. Topics follow primary purpose, Tags primary technology, Projects require the defined relationship, Domains derive from Projects. Absence is UNKNOWN, not an implicit negative.

The user's subsequent clarification explicitly permits multiple relevant Projects, Topics, Tags and derived Domains per repository. There is no one-per-kind cap. Reviewers actively check for missing primary associations; multiple valid family relationships produce the union of their parent Domains. Do not pad outputs with incidental mentions or force an unregistered initiative into a nearby Project.

## Cost and provenance

No additional OpenAI/provider API calls, model downloads or external tracing. Existing model/API budget ledgers and environment settings remain untouched. Report external API requests and incremental API spend as zero; Codex-agent allowance consumption is unmeasured, not free or zero tokens. Record the actual available producer identity without inventing a model name, temperature or API usage receipt.

This pilot evaluates source-based co-annotation and review usability. It does not measure the app's API integration, a particular externally invoked model, production retrieval accuracy or final benchmark F1.

## Persistence and human review

Keep work under ignored `docs/validation/private/corpus-600-v2/annotation-pilot/`, separately from the immutable `release/`. Save selection, registry/source bindings, blind packets, independent annotations, validator findings, comparison, human-review queue and a Markdown report. An additive app reader exposes the validated sidecar in **Public - Ground Truth**.

The UI must distinguish original corpus proposals, Annotator A, Annotator B and the user's saved review. Show agreed and differing labels with evidence and actual read scope. Use evidence/review bands with visible reasons, not invented percentage confidence. Select ten agreed cases reproducibly for random audit and ten uncertain/disputed cases for targeted review; fill shortages transparently and keep the selection categories separate.

The user can inspect sources and deliberately stage a suggested correction into their editable review. Staging cannot confirm a record or check reviewed dimensions automatically. Added positives still need exact source quotes; final validation, optimistic revision, owner isolation and review history remain intact. Labels outside the selected decisions remain unknown. No human-confirmed status is written by the pilot.

The app integration is authorized pilot work. The broader aesthetic redesign remains an isolated preview awaiting approval; it is not a prerequisite for annotation or a reason to overwrite the current UI wholesale.

## Completion gates

1. Thirty reproducibly selected development records; no validation/test leakage into the pilot.
2. Two actual independent annotations per selected record, or explicit incomplete status and retained failures.
3. Canonical IDs, source/file/release bindings, quote coordinates, per-file read coverage and domain derivation validated.
4. Comparison and review queue generated with clear denominators; agreement never relabeled as human ground truth.
5. Results and evidence visible in the app; human saves remain separate and require deliberate actions.
6. Focused validation, app/API/browser regression checks and a saved Markdown execution report.

Do not scale to all 600 or replace fixtures based solely on pilot agreement. Human review and audits determine the next batch and any policy corrections.
