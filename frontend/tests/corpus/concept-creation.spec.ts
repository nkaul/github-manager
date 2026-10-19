import { test, expect, type Page } from "@playwright/test";
import { chooseOption } from "../helpers/chooseOption";

const api = "http://127.0.0.1:8015/api/v1";
const repoName = "rasbt/LLMs-from-scratch";
test.afterEach(async ({ page }) => { await page.unrouteAll({ behavior: "ignoreErrors" }); });

async function open(page: Page, id: number) {
  await page.route("**/api/v1/**", async route => {
    const url = new URL(route.request().url()); url.port = "8015";
    await route.fulfill({ response: await route.fetch({ url: url.toString() }) });
  });
  await page.request.post(`${api}/test/login?id=${id}`);
  await page.goto("/");
  await chooseOption(page.getByLabel("Workspace collection"), "ground-truth");
  await selectRepo(page);
  return page.getByRole("region", { name: "Repository evidence review", exact: true });
}
async function selectRepo(page: Page) {
  await expect(page.getByLabel("Repository purpose", { exact: true })).toBeEnabled();
  await page.getByLabel("Search corpus repositories").fill(repoName);
  await expect(page.locator(".corpus-pagination")).toContainText("1 results");
  const queueTab = page.getByRole("tab", { name: /^Queue/ });
  if (await queueTab.isVisible()) await queueTab.click();
  await page.getByRole("button", { name: `Review ${repoName}`, exact: true }).click();
  await expect(page.getByLabel("Repository purpose", { exact: true })).toBeEnabled();
}
async function createKind(page: Page, kind: "Topic" | "Tag", name: string) {
  await chooseOption(page.getByRole("combobox", { name: `Add ${kind}`, exact: true }), `__CREATE_${kind.toUpperCase()}__`);
  const dialog = page.getByRole("dialog", { name: `Create ${kind}`, exact: true });
  await dialog.getByLabel(`New ${kind} name`, { exact: true }).fill(name);
  await dialog.getByLabel(`New ${kind} definition`, { exact: true }).fill("Synthetic workflow QA only; not a human semantic reference.");
  await dialog.getByRole("button", { name: `Create ${kind} & assign`, exact: true }).click();
  await expect(dialog).not.toBeVisible();
}
async function externalDomain(page: Page, name: string) {
  const identity = await (await page.request.get(`${api}/me`)).json();
  const registry = await (await page.request.get(`${api}/corpus/registry`)).json();
  const response = await page.request.post(`${api}/corpus/registry/concepts`, {
    headers: { Origin: "http://127.0.0.1:3015", "X-CSRF-Token": identity.csrf_token },
    data: { kind: "DOMAIN", name, description: "Disposable concurrent vocabulary edit", registry_context: registry.registry_context },
  });
  expect(response.ok(), await response.text()).toBeTruthy();
}

test("create Domain, Project, Topic and Tag; stage evidence, persist draft and export a confirmed version", async ({ page }) => {
  test.setTimeout(90_000);
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  const review = await open(page, 9201);
  const rows = await (await page.request.get(`${api}/corpus/repos?q=${repoName}`)).json();
  const rid = rows.items[0].repository_id;
  const before = await (await page.request.get(`${api}/corpus/repos/${rid}`)).json();
  const source = await (await page.request.get(`${api}/corpus/repos/${rid}/source?path=${encodeURIComponent(before.files[0].path)}`)).json();
  const projectPicker = review.getByRole("combobox", { name: "Add Project", exact: true });
  await projectPicker.fill("QA Learning Program");
  await page.getByRole("option", { name: "+ Create Project…", exact: true }).click();
  const project = page.getByRole("dialog", { name: "Create Project", exact: true });
  await expect(project.getByLabel("New Project name", { exact: true })).toHaveValue("QA Learning Program");
  await project.getByLabel("New Project definition", { exact: true }).fill("Synthetic QA initiative for checking reference creation and persistence.");
  await project.getByLabel("New Project aliases", { exact: true }).fill("QA Learning");
  await project.getByRole("button", { name: "Create a missing Domain", exact: true }).click();
  await project.getByLabel("New parent Domain name", { exact: true }).fill("QA Knowledge Systems");
  await project.getByLabel("New parent Domain definition", { exact: true }).fill("Synthetic parent for UI contract verification.");
  await page.screenshot({ path: "../docs/design/workspace-refinement/create-and-assign-2026-10-18/create-parent-domain-1920.png" });
  await project.getByRole("button", { name: "Create Domain & select", exact: true }).click();
  await expect(project.getByLabel("New Project name", { exact: true })).toHaveValue("QA Learning Program");
  await expect(project.getByLabel("New Project aliases", { exact: true })).toHaveValue("QA Learning");
  await expect(project.getByRole("combobox", { name: "New Project parent Domain", exact: true })).toHaveValue("QA Knowledge Systems");
  await project.getByRole("button", { name: "Create Project & assign", exact: true }).click();
  await expect(project).not.toBeVisible();
  await expect(review.getByRole("group", { name: "Derived Domains", exact: true })).toContainText("QA Knowledge Systems");
  await createKind(page, "Topic", "QA Evidence Review");
  await createKind(page, "Tag", "QA Workflow Marker");
  for (const kind of ["Projects", "Topics", "Tags"]) await expect(review.getByRole("checkbox", { name: `${kind} reviewed`, exact: true })).not.toBeChecked();
  await expect(review.getByRole("button", { name: "Confirm & next", exact: true })).toBeDisabled();
  for (const [kind, name] of [["Project", "QA Learning Program"], ["Topic", "QA Evidence Review"], ["Tag", "QA Workflow Marker"]]) {
    const group = review.getByRole("region", { name: `${kind} labels`, exact: true });
    const quote = group.getByLabel(`Exact quote supporting ${name}`, { exact: true });
    if (!(await quote.isVisible())) await group.getByText("Exact source evidence · required", { exact: true }).click();
    await chooseOption(group.getByRole("combobox", { name: `Evidence file for ${name}`, exact: true }), source.path);
    await quote.fill(source.text.slice(0, 120));
  }
  await review.getByRole("button", { name: "Save draft", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Draft saved");
  const draft = await (await page.request.get(`${api}/corpus/repos/${rid}`)).json();
  expect(draft.draft.registry_context.revision).toBe(4);
  expect(draft.review).toBeNull();
  expect(draft.proposal).toEqual(before.proposal);
  expect(draft.annotation_pilot).toEqual(before.annotation_pilot);
  await page.reload();
  await chooseOption(page.getByLabel("Workspace collection"), "ground-truth");
  await selectRepo(page);
  for (const name of ["QA Learning Program", "QA Evidence Review", "QA Workflow Marker"]) await expect(review.getByText(name, { exact: true })).toBeVisible();
  for (const kind of ["Projects", "Topics", "Tags"]) await review.getByRole("checkbox", { name: `${kind} reviewed`, exact: true }).check();
  await page.screenshot({ path: "../docs/design/workspace-refinement/create-and-assign-2026-10-18/staged-review-1920.png" });
  await review.getByRole("button", { name: "Confirm & next", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Review saved");
  const exported = await (await page.request.get(`${api}/corpus/reviews/export`)).json();
  const saved = exported.reviews.find((value: { repository_id: number }) => value.repository_id === rid);
  expect(saved.registry_context.revision).toBe(4);
  expect(exported.reference_registry.versions.map((v: { registry_context: { revision: number } }) => v.registry_context.revision)).toEqual([0, 1, 2, 3, 4]);
  expect(exported.reference_registry.versions[0].extensions).toEqual([]);
  const createdProject = exported.reference_registry.registry.find((concept: { name: string }) => concept.name === "QA Learning Program");
  await page.getByRole("button", { name: /^Filters/ }).click();
  await chooseOption(page.getByRole("combobox", { name: "Label filter basis", exact: true }), "reviewed");
  await chooseOption(page.getByRole("combobox", { name: "Filter by project", exact: true }), createdProject.id);
  await page.getByRole("dialog", { name: "Filter corpus repositories", exact: true }).getByRole("button", { name: "Done", exact: true }).click();
  await expect(page.locator(".corpus-pagination")).toContainText("1 results");
  await expect(page.getByRole("button", { name: `Review ${repoName}`, exact: true })).toBeVisible();
  expect(errors).toEqual([]);
});

test("duplicate aliases identify the reserved concept and allow reuse; cancellation keeps unsaved edits", async ({ page }) => {
  const review = await open(page, 9202);
  const purpose = review.getByLabel("Repository purpose", { exact: true });
  await purpose.fill("Unsaved source review remains after cancelling concept creation.");
  await chooseOption(review.getByRole("combobox", { name: "Add Topic", exact: true }), "__CREATE_TOPIC__");
  const dialog = page.getByRole("dialog", { name: "Create Topic", exact: true });
  await dialog.getByLabel("New Topic name", { exact: true }).fill("QA Predictive Workflows");
  await dialog.getByLabel("New Topic definition", { exact: true }).fill("Duplicate alias handling only.");
  await dialog.getByLabel("New Topic aliases", { exact: true }).fill("ML");
  await dialog.getByRole("button", { name: "Create Topic & assign", exact: true }).click();
  await expect(dialog.getByRole("alert")).toContainText("Machine Learning");
  await expect(dialog.getByRole("alert")).toContainText("ML");
  await expect(dialog.getByLabel("New Topic name", { exact: true })).toHaveValue("QA Predictive Workflows");
  await page.screenshot({ path: "../docs/design/workspace-refinement/create-and-assign-2026-10-18/alias-conflict-1920.png" });
  await dialog.getByRole("button", { name: "Use existing Topic Machine Learning", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await expect(review.getByRole("region", { name: "Topic labels", exact: true }).getByText("Machine Learning", { exact: true })).toBeVisible();
  const registry = await (await page.request.get(`${api}/corpus/registry`)).json();
  expect(registry.registry_context.revision).toBe(0);
  await review.getByRole("button", { name: "+ Create missing Project", exact: true }).click();
  await page.getByLabel("New Project name", { exact: true }).fill("Cancelled QA Project");
  await page.getByLabel("New Project name", { exact: true }).press("Escape");
  await expect(page.getByRole("dialog", { name: "Create Project", exact: true })).not.toBeVisible();
  await expect(purpose).toHaveValue("Unsaved source review remains after cancelling concept creation.");
  expect((await (await page.request.get(`${api}/corpus/registry`)).json()).extension_count).toBe(0);
});

test("concurrent vocabulary changes retain creation fields and require explicit refresh before saving", async ({ page }) => {
  const review = await open(page, 9203);
  await review.getByLabel("Repository purpose", { exact: true }).fill("Unsaved concurrency QA purpose.");
  await chooseOption(review.getByRole("combobox", { name: "Add Tag", exact: true }), "__CREATE_TAG__");
  const dialog = page.getByRole("dialog", { name: "Create Tag", exact: true });
  await dialog.getByLabel("New Tag name", { exact: true }).fill("QA Concurrent Marker");
  await dialog.getByLabel("New Tag definition", { exact: true }).fill("Disposable concurrency contract.");
  await externalDomain(page, "QA External Domain One");
  await dialog.getByRole("button", { name: "Create Tag & assign", exact: true }).click();
  await expect(dialog.getByRole("alert")).toContainText("Reference vocabulary changed");
  await dialog.getByRole("button", { name: "Refresh vocabulary", exact: true }).click();
  await expect(dialog.getByLabel("New Tag name", { exact: true })).toHaveValue("QA Concurrent Marker");
  await dialog.getByRole("button", { name: "Create Tag & assign", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await externalDomain(page, "QA External Domain Two");
  await review.getByRole("button", { name: "Save draft", exact: true }).click();
  await expect(review.getByRole("alert")).toContainText("Reference vocabulary changed");
  await expect(review.getByLabel("Repository purpose", { exact: true })).toHaveValue("Unsaved concurrency QA purpose.");
  await review.getByRole("button", { name: "Refresh review vocabulary", exact: true }).click();
  await review.getByRole("button", { name: "Save draft", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Draft saved");
});

test.describe("mobile concept creation", () => {
  test.use({ viewport: { width: 390, height: 844 }, hasTouch: true });
  test("standalone Domain stays unassigned until its Project is selected; forms and actions fit", async ({ page }) => {
    const review = await open(page, 9204);
    await review.getByRole("button", { name: "Create Domain", exact: true }).tap();
    const domain = page.getByRole("dialog", { name: "Create Domain", exact: true });
    await domain.getByLabel("New Domain name", { exact: true }).fill("QA Mobile Systems");
    await domain.getByLabel("New Domain definition", { exact: true }).fill("Synthetic mobile workflow group.");
    await domain.getByRole("button", { name: "Create Domain", exact: true }).tap();
    await expect(domain).not.toBeVisible();
    await expect(review.getByRole("group", { name: "Derived Domains", exact: true })).toContainText("None");
    await review.getByRole("button", { name: "+ Create missing Project", exact: true }).tap();
    const project = page.getByRole("dialog", { name: "Create Project", exact: true });
    await project.getByLabel("New Project name", { exact: true }).fill("QA Mobile Program");
    await project.getByLabel("New Project definition", { exact: true }).fill("Synthetic QA Project under a newly created Domain.");
    await chooseOption(project.getByRole("combobox", { name: "New Project parent Domain", exact: true }), { label: "QA Mobile Systems" });
    const save = project.getByRole("button", { name: "Create Project & assign", exact: true });
    await expect(save).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
    const bounds = await save.boundingBox();
    expect(bounds!.y + bounds!.height).toBeLessThanOrEqual(844);
    await page.screenshot({ path: "../docs/design/workspace-refinement/create-and-assign-2026-10-18/create-project-390.png" });
    await save.tap();
    await expect(project).not.toBeVisible();
    await expect(review.getByRole("group", { name: "Derived Domains", exact: true })).toContainText("QA Mobile Systems");
  });
});
