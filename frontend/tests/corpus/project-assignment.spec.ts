import { test, expect } from "@playwright/test";
import { chooseOption } from "../helpers/chooseOption";

test("Project assignment is visible in its group, derives Domains and persists evidence in a draft", async ({ page }) => {
  await page.route("**/api/v1/**", async route => {
    const url = new URL(route.request().url()); url.port = "8015";
    await route.fulfill({ response: await route.fetch({ url: url.toString() }) });
  });
  await page.request.post("http://127.0.0.1:8015/api/v1/test/login");
  const summary = await (await page.request.get("http://127.0.0.1:8015/api/v1/corpus")).json();
  const rows = await (await page.request.get("http://127.0.0.1:8015/api/v1/corpus/repos?q=fluxcd/flux2")).json();
  const rid = rows.items[0].repository_id;
  const detail = await (await page.request.get(`http://127.0.0.1:8015/api/v1/corpus/repos/${rid}`)).json();
  expect(detail.proposal.labels.filter((label: { kind: string; decision?: string }) => label.kind === "PROJECT" && (label.decision || "SUPPORTED") === "SUPPORTED")).toEqual([]);
  const project = summary.registry.find((concept: { name: string; kind: string }) => concept.kind === "PROJECT" && concept.name === "Kubernetes");
  const domain = summary.registry.find((concept: { id: string }) => concept.id === project.domain);
  // Reuse an actual validated agent suggestion as disposable UI data, not a human verdict.
  const suggestion = detail.annotation_pilot.record.annotations.a.labels.find((label: { id: string }) => label.id === project.id);
  const proof = suggestion.evidence.find((evidence: { path: string }) => detail.files.some((file: { path: string }) => file.path === evidence.path));
  expect(proof).toBeTruthy();
  await page.goto("/");
  await chooseOption(page.getByLabel("Workspace collection"), "ground-truth");
  await page.getByLabel("Search corpus repositories").fill("fluxcd/flux2");
  await expect(page.locator(".corpus-pagination")).toContainText("1 results");
  await page.getByRole("button", { name: "Review fluxcd/flux2", exact: true }).click();
  const review = page.getByRole("region", { name: "Repository evidence review", exact: true });
  const projects = review.getByRole("region", { name: "Project labels", exact: true });
  const domains = review.getByRole("group", { name: "Derived Domains", exact: true });
  await expect(projects.getByRole("combobox", { name: "Add Project", exact: true })).toBeVisible();
  await expect(projects).toContainText("No Project selected");
  await expect(domains).toContainText("None");
  await expect(review.getByRole("combobox", { name: "Add Domain", exact: true })).toHaveCount(0);
  await projects.scrollIntoViewIfNeeded();
  await page.screenshot({ path: "../docs/design/workspace-refinement/assignment-controls-2026-10-18/empty-projects-1920.png" });

  await projects.getByRole("checkbox", { name: "Projects reviewed", exact: true }).check();
  await chooseOption(projects.getByRole("combobox", { name: "Add Project", exact: true }), project.id);
  await expect(projects.getByRole("checkbox", { name: "Projects reviewed", exact: true })).not.toBeChecked();
  await expect(projects.getByText(project.name, { exact: true })).toBeVisible();
  await expect(domains).toContainText(domain.name);
  await chooseOption(review.getByRole("combobox", { name: `Evidence file for ${project.name}`, exact: true }), proof.path);
  await review.getByLabel(`Exact quote supporting ${project.name}`, { exact: true }).fill(proof.quote);
  await review.getByRole("button", { name: "Save draft", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Draft saved");
  const saved = await (await page.request.get(`http://127.0.0.1:8015/api/v1/corpus/repos/${rid}`)).json();
  expect(saved.draft.label_ids).toContain(project.id);
  expect(saved.draft.additional_evidence[project.id]).toEqual({ path: proof.path, quote: proof.quote });
  expect(saved.review).toBeNull();

  await page.reload();
  await chooseOption(page.getByLabel("Workspace collection"), "ground-truth");
  await page.getByLabel("Search corpus repositories").fill("fluxcd/flux2");
  await expect(page.locator(".corpus-pagination")).toContainText("1 results");
  await page.getByRole("button", { name: "Review fluxcd/flux2", exact: true }).click();
  await expect(projects.getByText(project.name, { exact: true })).toBeVisible();
  await expect(domains).toContainText(domain.name);
  // Search accepts a registry alias without adding it as a new concept.
  const topics = review.getByRole("combobox", { name: "Add Topic", exact: true });
  await topics.fill("ML");
  await expect(page.getByRole("option", { name: "Machine Learning", exact: true })).toBeVisible();
  await topics.press("Escape");

  for (const width of [1920, 1440, 1280, 390]) {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 1080 });
    await projects.getByRole("combobox", { name: "Add Project", exact: true }).scrollIntoViewIfNeeded();
    await expect(projects.getByRole("combobox", { name: "Add Project", exact: true })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
    await page.screenshot({ path: `../docs/design/workspace-refinement/assignment-controls-2026-10-18/assigned-project-${width}.png` });
  }
  await projects.getByRole("button", { name: `Remove project ${project.name}`, exact: true }).click();
  await expect(domains).toContainText("None");
  await projects.getByRole("button", { name: "+ Create missing Project", exact: true }).click();
  await expect(page.getByRole("dialog", { name: "Create Project", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Close concept creation", exact: true }).click();
  await page.unrouteAll({ behavior: "ignoreErrors" });
});
