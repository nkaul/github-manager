# Style and composition

## Visual language

The references use clean white paper, slightly irregular dark pen outlines, handwritten headings, recognizable human/document/robot illustrations, circled steps, flowing arrows, rounded paper notes and soft marker washes. The result should feel like a carefully explained sketchbook, with publication-quality spacing and legibility.

The central improvement over a generic box diagram is semantic illustration. A funnel visibly filters candidate labels; a booklet contains model input; a clipboard represents review; a retained receipt explains remembered work. The object and its state should help explain what happens, rather than merely decorate a rectangle labeled with a service name.

| Element | Useful default | Decision it supports |
|---|---|---|
| Background | White or a barely visible cool paper tint | Clear text and reusable publication placement |
| Ink/body copy | Dark charcoal/navy, e.g. `#182544` | Readability rather than color-only meaning |
| Main emphasis | Indigo `#3949AB`, blue `#1E69D6` | Headings, active step and principal flow |
| Secondary emphasis | Purple `#7E57C2` | A distinct phase, proposal or human decision |
| Soft washes | Lavender `#EEE9FF`, light blue `#E3F2FD` | Grouping and emphasis without heavy fills |
| Occasional accent | Muted yellow/green; red with an explicit label for rejection | Highlight a result, caution or exclusion |
| Strokes | Slightly uneven, rounded dark outlines | Consistent hand-drawn character |
| Typography | Readable handwritten heading; clear handwritten or neutral body | Warm explanation with correct technical text |

These hexadecimal values are reusable working defaults derived from the project's visual treatment, not a claim of pixel-exact color sampling of every raster reference. Adapt them for the user's brand and contrast needs. Avoid filling the entire illustration with deep purple.

## Composition choices

- **Product orientation:** person/source on the left, processing and decisions in the middle, useful workspace outcome on the right. Put deferred infrastructure in a separately labeled area.
- **Mechanism journey:** numbered stops, each with an input artifact, visible action and output. A two-row snake path can work for six steps; check that the row transition is unambiguous.
- **Evidence transformation:** opened source document → selected passages with real provenance → phrase/concept cards → bounded request. Put each limit beside the artifact it constrains.
- **Comparison:** matched before/after or two alternatives, using the same example and scale. Show the tradeoff, not only a winning checkmark.
- **Control loop:** separate admission, inference, local reuse and explicit refresh paths. Show receipts and state changes; label the condition controlling an arrow.
- **Evaluation:** show corpus composition, stage-specific measurements and interpretation limits. Do not let a large score overpower its denominator and caveat.

Use one dominant story per figure. Supporting checklist areas are useful when they remain subordinate to the illustrated mechanism. Not every explanation needs the same three-card or four-column layout.

## Characters, symbols and relationships

Keep a friendly human reviewer and small robot consistent across a series when they clarify roles. A robot represents a model/service, not authority or consciousness. Human approval must be visually distinct from generated suggestions. Reuse recognizable objects rather than changing the metaphor halfway through.

Brand marks require the task's actual approved asset treatment. The GitHub Manager project used an original calm cat mascot with selectable motion; that is a case-specific brand choice, not a requirement to put a cat in unrelated diagrams. Do not morph an integration vendor's logo into a new project identity.

An arrow means a real relationship or transition. Distinguish data movement, derivation, proposal, approval and optional future paths with labels and/or line treatments. Dashed future clouds must remain labeled proposed/deferred. Do not draw a nested hierarchy for independent facets or connect a browser directly to storage when access goes through a server.

## Size and text

Choose aspect ratio for placement: landscape suits workflows and video, while a vertical explainer may suit a feed. The previous landscape references are roughly 16:9. A requested 4K output is a target, not a promise that a generator returns that native resolution; inspect and report the real export dimensions.

Use generous edge margins, large headings and short phrases. In a 1920×1080 code-composed frame, a useful starting point is 44–64 px headings and about 30–36 px essential body text, with smaller qualifiers only if still readable at the actual player size. Treat these as starting points, not a substitute for inspection.

Long JSON, formulas and schemas often need deterministic text rendering or a separate exact technical companion. Preserve their meaning in the illustration and keep the exact artifact accessible. Do not trade full content coverage for tiny lettering.
