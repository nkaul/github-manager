# Add missing Ground Truth concepts during review

October 18, 2026. Available in **Public - Ground Truth**. These controls edit your reference work; they are separate from taxonomy management in your personal GitHub collection.

## Assign an existing concept

1. Open a repository in **Public - Ground Truth** and read its saved evidence.
2. Use **Add Project**, **Add Topic** or **Add Tag** beside the corresponding group. Search names or aliases and select an existing concept. Multiple assignments are supported.
3. Remove an unsuitable assignment with its remove control. To replace it, remove it and add the appropriate concept.
4. For each new positive assignment, open its evidence field, choose a saved source file and enter an exact supporting quote. A quote must support the concept; merely occurring in the README is insufficient for a sound human judgement.
5. Check **Reviewed** for Projects, Topics and Tags after inspecting each group. Use **Save draft** for unfinished work or **Confirm & next** when ready.

## Create a missing Project, Topic or Tag

1. Open that group's **Add** picker and choose **+ Create Project…**, **+ Create Topic…** or **+ Create Tag…**. A typed search is carried into the new name field. Projects also have a visible **+ Create missing Project** action.
2. Enter a short canonical name and a definition that distinguishes the concept. Aliases are optional, separated with commas. Inspect similar existing concepts before creating another one.
3. For a Project, select its **Parent Domain**. If missing, select **Create a missing Domain**, complete the inline Domain fields and choose **Create Domain & select**. Your Project fields stay in place.
4. Choose **Create Project & assign**, **Create Topic & assign** or **Create Tag & assign**. This saves a reusable concept definition and stages its assignment in the editor. It does not save or confirm the repository review.
5. Attach supporting source evidence, inspect the groups and save a draft or confirm as above.

Creating a concept is a persistent operation. Cancelling a later review does not remove the concept definition. Similarly, a parent Domain already created in the Project form remains available if you subsequently cancel the Project. Cancelling before pressing a creation button creates nothing.

## Add a Domain

Use **Create Domain** beside **Domains from retained Projects**, or create one inside the Project form. Give it a name and definition. A Domain appears on a repository through the Projects assigned to that repository; creating a Domain alone does not assign it. To use a new Domain, create a Project under it, then assign that Project.

Existing Projects cannot be reparented in this flow. Reparenting would change other repositories' derived Domains and needs a separate impact review.

## Resolve a name conflict or a changed vocabulary

A reserved canonical name or alias may belong to an existing concept even if that concept is not assigned to this repository. The conflict names the term and existing concept and provides a reuse action. Reuse it when its definition fits, or change the new name/aliases when the concepts are genuinely distinct. Uniqueness is checked within each kind, across both original and newly created concepts.

If another tab changes the vocabulary, the form keeps your fields and asks you to refresh explicitly. If a review save encounters that change, choose **Refresh review vocabulary**, inspect the retained assignments and acknowledge the groups again. Saving is blocked until the stale vocabulary is refreshed; there is no automatic overwrite.

## Find saved assignments and export them

Open **Filters → Label filter basis → Your saved reviews**, then choose the relevant Domain, Project, Topic or Tag. This uses saved review assignments, including concepts you created. **Original proposals** remains available for inspecting the original suggestions. Unsaved edits and drafts are not counted as saved review assignments.

**Export reviews** includes the effective reference vocabulary, its revision/hash and extension history alongside saved reviews. Original proposals, sources and independent Agent A/B records remain unchanged. New reference additions are scoped to your account and corpus release and persist in the existing local SQLite workspace aggregate at `docs/validation/private/demo/app.sqlite3`; do not edit the frozen corpus files.

## What this means for evaluation

A concept you create was unavailable to the original fixed-registry annotators. Treat that as a vocabulary gap, separately from a missed known label. Freeze the vocabulary and reviewed scope before evaluating a classifier. Creating a concept or passing a workflow test does not establish semantic accuracy, benchmark approval or exhaustive negatives; unlisted labels remain unknown.

See the [implementation and validation report](../validation/ground-truth-create-and-assign-2026-10-18.md) for technical details and screenshots.
