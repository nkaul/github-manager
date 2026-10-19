# Prompt patterns

The variable fields below are intentional reusable prompt parameters. Fill them from the current task and verified content contract, rather than copying a previous project's facts.

## New illustrated figure

```text
Create a friendly, publication-quality hand-drawn technical explainer.
Use the supplied images as STYLE REFERENCES ONLY.
White paper, expressive dark pen outlines, readable handwritten headings,
indigo/blue with restrained purple, soft lavender/light-blue marker accents,
recognizable semantic objects, circled steps and clearly directed arrows.
Favor an illustrated mechanism over generic service-name boxes.

Audience and viewer question: {{audience_and_question}}
Purpose and consequence: {{purpose_and_consequence}}
Title: {{title}}
Composition / reading path: {{composition}}
Inputs, visible operations and outputs: {{mechanism}}
Required exact labels/numbers/units: {{exact_content}}
Other facts that must remain: {{coverage}}
Status and caveats: {{status_and_caveats}}
Placement / aspect ratio / target size: {{delivery}}

Preserve all stated facts and qualifications. Do not invent features, schemas,
measurements, evidence coordinates or deployed components. Make all essential
text readable with generous margins. If the content cannot fit, propose a
linked figure sequence rather than omitting facts or shrinking the lettering.
```

## Focused correction

```text
Edit the supplied existing figure. Preserve its illustrations, reading order,
palette, technical facts and all regions not named here.
Region to change: {{region}}
Current incorrect wording/relationship: {{observed_error}}
Exact correction and factual reason: {{correction}}
Content/numbers that must remain unchanged: {{preserve}}
Export as a new version, keeping the original available.
```

## Illustrated animation beat

```text
Section name and spoken purpose: {{orientation}}
Viewer question: {{question}}
Starting data/state: {{input}}
Information-carrying motion: {{operation}}
Result held for reading: {{output}}
Practical implication: {{consequence}}
Qualification and evidence: {{caveat_and_source}}
Narration phrase / measured cue: {{timing}}
Transition to next beat: {{connection}}
Keep the paper/ink/marker style and readable exact text.
```
