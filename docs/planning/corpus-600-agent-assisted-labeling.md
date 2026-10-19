# Repository labels with minimal human review

Date: October 16, 2026. Status: **PROPOSED — no new labeling or paid model runs started**.

The latest user direction allows LLM-assisted reading, summarization and labeling. The recommended approach is: **agents do the detailed reading and propose cited labels; an independent pass checks them; humans resolve uncertainty and audit a sample of the apparently easy cases.**

This changes the proposed review workload, while preserving the original corpus, its historical labels and prior reports. Earlier proposals remain available in the [detailed evaluation plan](corpus-600-human-verification-and-evaluation.md). Agreement between agents is useful evidence, not proof that they cannot share a mistake.

## Five practical steps

### 1. Start with thirty repositories

Use the existing reproducible thirty-repository development sample, three per domain. Agree on a one-page labeling guide: Project means an evidenced initiative relationship; Topics mean primary purpose; Tags mean primary technologies; Domains derive from Projects. A dependency is not automatically a Project relationship. Unknown remains a valid result.

Use saved snapshots initially. An agent reads each complete saved README and relevant retained documentation in manageable sections. Save actual reading coverage. Missing, unavailable or unread required material prevents a claim of complete review. Complete saved documentation does not mean every file in the repository was collected.

### 2. Have two agents reach their own conclusions

**Agent A** produces a short plain-language description and an evidence record: what the repository does, who it is for, whether it is a product/course/example/index, primary capabilities, technologies, product relationships, planned features and exclusions. It proposes known taxonomy IDs with exact supporting passages.

**Agent B** reads the original artifacts and independently proposes labels before seeing A's answers or the application's predictions. It must look for missing valid labels, not merely approve the first list. Give reference creation access to the known taxonomy and registry search; do not restrict it to the production retriever's current shortlist.

Retain full sources, detailed claims and source locations beside the summary. A short summary helps navigation; it does not contain every fact. Reuse these records for later taxonomy matching rather than repeatedly rereading unchanged sources. Agents are LLM-based; this reduces repeated processing, not total model usage to zero.

### 3. Check evidence and assign a review priority

A targeted verifier checks disagreements, supporting passages, negation, planned features, artifact type and missing primary labels. Scripts separately check IDs, source hashes and citation coordinates. Prefer a different approved model for the verifier when feasible; different model names still do not guarantee independent errors.

Each label gets its own confidence band, with the reasons visible:

| Band | Meaning | Action |
| --- | --- | --- |
| Green | Independent passes agree; direct source evidence fits the definition; evidence checks pass; no unresolved contradiction | Eligible for reduced human review after auditing; retain random checks |
| Amber | Evidence is indirect, interpretations differ, or primary-purpose/family scope is unclear | Show a short decision card to the human |
| Red | Required evidence is missing, contradictory or insufficient | Leave unknown; request more evidence only when useful |

Also rate whether the repository's label list is complete within the reviewed scope. Several individually strong labels do not prove that no important label was missed.

Start with these understandable evidence bands. Do not display invented “98% confidence” values. Later, use human-audit outcomes to estimate reliability for comparable Project/Topic/Tag cases, showing sample size and uncertainty. A model's self-reported percentage is not the probability that its answer is correct.

### 4. Give the human twenty short cards in the pilot

Select ten random agreed cases and ten uncertain/disputed cases; if fewer disputes exist, fill the remainder randomly. Each card contains a short purpose statement, proposed labels, why each was selected, a few quoted passages and full-source links. Ask: **Correct / Change / Unsure**, and **Is an important label missing?**

The human should expand source context when needed, rather than reread every file by default. Keep the random and risk-selected results separate: the random cases help check apparently safe automation; uncertain cases help repair definitions and errors. Twenty cards are an initial usability/calibration check, not enough to establish a precise high-accuracy claim across all domains or rare labels.

If Green cases contain a systematic mistake, correct the policy and recheck that affected group before scaling. Continue random auditing as more labels are created. Two agreeing agents can miss the same fact, so reviewing only disagreements is insufficient.

### 5. Scale in small batches and preserve review provenance

After the pilot, process the remaining corpus in batches of thirty. Route Amber cases to humans, preserve Red cases as unknown, and audit a random portion of Green cases. Determine the audit rate from observed errors and required reliability; do not promise a particular percentage of human effort saved in advance.

Export three clearly distinguished outcomes: **human-confirmed**, **AI-verified and audited at population level**, and **unresolved**. Use the larger reference set for broad diagnostics and the human-checked subset for a stronger accuracy check, with its actual sample/scope limitations. Preserve unknown-label masks and grouped evaluation splits. Frozen test labels must not become prompt examples or tuning data.

No new framework is required for the pilot: existing agents plus local Markdown/JSON/SQLite evidence records are sufficient. Agent reading uses model allowance. If external API calls are chosen, estimate and approve the bounded pilot schedule first; existing provider-attempt/dollar limits remain in force and are not reset by this plan. The user has allowed the approach, not unbounded spending or an immediate full-corpus rerun.

## What the human would see

Illustrative review card, not a new adjudication:

> **Repository purpose:** Python access to Airbyte connectors.  
> **Suggested Project:** Airbyte — explicit connector relationship.  
> **Topic caution:** Do not inherit production orchestration; the source explicitly excludes it.  
> **Confidence:** Green for the evidenced relationship if both independent passes agree; ambiguous extra Topics remain separate.  
> **Your action:** Correct / Change / Unsure; add a missing label if needed.

This existing corpus example explains the policy; its validation-split membership is preserved and it is not a new development-training example.

## Why this approach

Research on uncertainty-guided human/LLM co-annotation supports directing human effort where model judgments are uncertain. That supports this workflow design, not a promised error rate or workload reduction for GitHub repositories. [CoAnnotating](https://aclanthology.org/2023.emnlp-main.92/).

Confidence-calibration research distinguishes model scores from reliability established against observed correctness, including subgroup differences. Our initial bands are evidence/review indicators; statistical confidence estimates need sufficient human judgments. [Multicalibration for Confidence Scoring in LLMs](https://arxiv.org/abs/2404.04689).

The first deliverable is thirty detailed agent-reviewed records, a comparison/verification report and twenty short human-review cards. It should show the actual time/call cost, disagreement rate, missing-label corrections and Green-case audit errors before a full-corpus decision.
