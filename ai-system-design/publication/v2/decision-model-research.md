# Could a decision model help GitHub Manager?

Research date: **October 15, 2026**. This is an architectural investigation of TypeSafe AI's **Jev**, requested by the user. No Jev SDK was installed, key configured, account probed or model called. None of the proposals below is implemented in GitHub Manager.

## Start with the decision the product needs

Classification already has a bounded answer space: approved Project, Topic and Tag IDs. Its harder question is whether supplied evidence supports each relationship under the user's primary-purpose policy. That makes a specialized decision interface worth investigating.

Taxonomy discovery has a different job. It creates candidate names, definitions, aliases and a collection-level structure. A decision model cannot replace that open-ended generation merely by choosing from existing labels. It could help review a proposed duplicate or relationship once candidate options exist.

TypeSafe describes Jev as a System One model accepting state and typed questions, with structured probabilistic decisions rather than open-ended prose. The architectural opportunity is to separate bounded judgments from vocabulary generation; the product must still own policy and state. [TypeSafe announcement](https://typesafe.ai/blog/introducing-system-one-models-and-jev).

## What the interface provides

The documented primitives are Choice (one option), Score (a defined scale) and Noul (probability of a yes/no statement). Questions can share one state in a request, but their answers are independent; a result is not hidden context for another question. Dependent judgments need explicit composition in code or another request. [Primitives](https://docs.typesafe.ai/primitives).

This matters because GitHub Manager is **multi-label**. A repository may support two Projects and several useful labels. One global Choice among all taxonomy IDs would change the task and force false competition. A better experiment would judge candidate relationships separately, or make a small Choice about the support status of each candidate. Other/unsupported/insufficient-context outcomes must remain expressible. [Choice](https://docs.typesafe.ai/primitives/choice).

An unexecuted, project-specific request sketch is saved in [jev-proposed-request.json](examples/jev-proposed-request.json). Its use of actual Orion text does not make it a tested integration. It intentionally contains no invented model response or confidence value.

## Candidate placements

| Placement | Narrow judgment | Benefit to test | Failure or cost to watch |
|---|---|---|---|
| After sparse retrieval | Does this candidate fit the repository's primary purpose? | Fewer distracting candidates in the generation request. | Filtering can lose a correct label; a cheaper decision may create a more expensive false negative. |
| Before evidence packing | Does this passage support a candidate relationship? | Put the decisive passage into the compact context, rather than early link/banner text. | More passage/candidate questions, additional latency, and a new failure point before classification. |
| Instead of the bounded assignment stage | Is each approved relationship supported, unsupported or unclear? | Reduce dependence on prose generation for closed-vocabulary selection. | Multiple-label consistency, evidence selection, explanations and policy fidelity still need handling. |
| In review triage | Does the available evidence justify sending this suggestion for closer review? | Direct limited attention to uncertain cases. | Overconfident incorrect answers can hide the very cases a person should see. |
| During taxonomy review | Are two proposed concepts likely aliases or distinct initiatives? | Better review ordering and duplicate suggestions. | Similar wording is not proof of identity. User-approved merges and deterministic term reservations remain authoritative. |

The first experiment should operate in **shadow mode** on retained public/synthetic evidence: record the decision without changing accepted relationships or skipping the current baseline. An isolated evaluation harness would need separate approval and a finite spending limit before any live calls.

## Apply the idea to the concrete examples

For Orion API, ask about explicit initiative membership in Orion, primary API purpose, and use of FastAPI/Python as technology. The shared `platform` word that retrieved Forge is weak evidence. The new layer should reject that distractor without discarding Orion.

For the negated API fixture, ask whether the text explicitly supports Project membership while retaining the denial of Helios/Orion. Keyword presence is not enough. Negation, contradictory evidence and absent context need separate evaluation cases.

For FastAPI itself, retain the primary-purpose policy. Mentioning Pydantic does not automatically make Data Validation a desired primary Topic; comparing performance with Go does not establish Go implementation. If a decision model filters snippets first, test whether it selects the real purpose passage that the current compacting heuristic misses.

For Orion audit, support both Orion and Compliance Audit when the evidence explicitly names both. Independent candidate questions preserve this possibility; a single winner-takes-all class does not.

For unknown-empty, return an abstention or no-match path. Do not force a label merely because typed outputs guarantee a valid answer shape.

## Confidence needs application-specific validation

Choice confidence is computed from its probability distribution. The documented formula is `(p_max - 1/n) / (1 - 1/n)`, where `n` is the number of choices. With three options and top probability 0.6, confidence is 0.4. Noul has no separate confidence field. These quantities are not interchangeable with the current classifier's self-reported 0.99 values. [Confidence](https://docs.typesafe.ai/confidence).

The formula also does not prove empirical calibration on this task. A sharply peaked wrong answer remains wrong. Evaluate probability reliability, errors at high confidence and the tradeoff between coverage and accepted-error risk. Tune thresholds on a calibration partition and assess them on an untouched evaluation partition. Do not choose thresholds from the final test results.

Because candidate decisions from one repository are correlated, thousands of candidate pairs are not thousands of independent repositories. Report repository-level/grouped uncertainty and per-kind results. Project membership, primary Topic support and dependency Tags have different error patterns and may need different thresholds.

## Evidence beyond the product announcement

TypeSafe's public workflow evaluations use model-consensus references and assume the workflow code is correct. They are useful demonstrations of task decomposition, but they are not human-reviewed ground truth for GitHub Manager. [Vendor workflow evaluation methodology](https://evals.typesafe.ai/).

Two recent primary preprints provide useful cautions. Li and colleagues report strong knowledge/commonsense multiple-choice results alongside weaker mathematical performance. Ling and colleagues report that cheaper decisions did not translate uniformly into better task completion across agent workflows, with auxiliary work absorbing some savings. These are results on other tasks, not a repository-organizer benchmark. [Li et al., arXiv v1](https://arxiv.org/abs/2610.11978v1), [Ling et al., arXiv v1](https://arxiv.org/abs/2610.13092v1).

This note reviewed the preprint abstracts and publication metadata; it does not claim a full methods audit, peer-review status or independent replication. Their contribution here is to motivate task-specific evaluation and measurement per successful outcome.

## Version, reliability and provider implications

As reviewed on October 15, the model documentation lists `jev-1.13.0` and `jev-1.14.0`; its alias table still points `jev-latest` to 1.13 and `jev-preview` to 1.14. A future experiment should pin a version and record the returned ID rather than silently follow an alias. Verify account availability before execution. [Model reference](https://docs.typesafe.ai/models).

The 1.13 limitation guide documents sensitivity to literal wording, irrelevant context, adversarial content and option order, along with arithmetic and generation limitations. Those are reasons to test negation, prompt injection, reordered options and distractor-heavy states; they do not establish that 1.14 has identical behavior or fixes every issue. [Version-specific limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13).

The current OpenAI admission hook does not cover another provider automatically. An integration would need a provider adapter, request-size/cost policy, rate snapshots, retry/timeout handling, unknown-outcome holds, cache identity, durable provenance and finite fallback admission. SDK retries must be configured deliberately. A more efficient call must not bypass the no-repeat receipt or silently authorize paid re-analysis.

Before sending data to a new provider, review applicable retention, processing and consent terms. TypeSafe's legal page distinguishes enterprise zero-retention availability; that is not evidence that any prospective account has it enabled. The existing verified-public/synthetic input restriction should remain the starting policy. [Data-handling documentation](https://docs.typesafe.ai/legal).

Deterministic decisions stay in code: private-input authorization, budget arithmetic, canonical-ID validity, normalized reservations, user precedence, protected rejections, freshness fences and execution permissions. A model can offer a semantic judgment; it cannot grant itself authority over these contracts.

## Proposed evaluation, before adoption

Use an independent, human-reviewed repository set with broader ecosystems and realistic Project-positive cases. Keep related repositories and initiative variants together when splitting data. Include out-of-vocabulary initiatives, no-match cases, near-neighbor names, shared frameworks, negative membership statements, multilingual purpose text and adversarial instructions.

Compare three approaches under the same task semantics and relevant evidence:

1. Existing lexical retrieval plus structured LLM classification.
2. The same retrieval with a decision-model filter or relevance judgment, followed by the existing classifier when admitted.
3. Decomposed decision-model classification, with explicit abstention and a bounded LLM/human fallback path.

Hold evidence fixed first to isolate decision quality; evaluate improved evidence packing separately. Include a simpler lexical/rule baseline where the judgment can be made deterministically. Keep the historical 20-case regression results frozen and report them separately.

| Layer | Measurements |
|---|---|
| Retrieval/packing | Expected-label candidate recall, decisive-passage inclusion, errors introduced by filtering |
| Assignment | Per-kind and micro precision/recall/F1, incorrect Project memberships, primary/secondary confusion, NO_MATCH and insufficient-context behavior |
| Uncertainty | Brier score or appropriate multi-class counterpart, reliability plots, high-confidence error rate, selective risk versus coverage |
| Workflow | Human corrections, review burden, preserved user decisions, fallback rate and successful completion |
| Resources | Total latency and spending, all provider requests, retries, fallback, storage and reviewer effort |
| Robustness | Option-order changes, paraphrases, negation, multilingual input, adversarial text, provider failures and version changes |

Set an adoption criterion before viewing the evaluation outcomes: preserve the agreed quality and authority gates, then assess whether reduced resource use or better review targeting justifies the added provider and maintenance complexity. No numerical improvement threshold is selected here without a product-level error tolerance and baseline.

The current classification round's estimated inference spending was already $0.003319 for 20 reused cases. That makes total workflow value especially important: an extra layer can add engineering and review costs even if its unit token price is lower. The decision to adopt should rest on correct, useful outcomes rather than a vendor speed or pricing headline.
