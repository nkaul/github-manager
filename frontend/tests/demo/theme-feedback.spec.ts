import { chooseOption } from "../helpers/chooseOption";
import { test, expect, type Page } from "@playwright/test";
import { writeFileSync } from "node:fs";

async function login(page: Page, id: number) {
  await page.request.post("/api/v1/test/login", { data: { id } });
  await page.goto("/");
  await chooseOption(page.getByLabel("Workspace collection"), "samples");
}

async function workspace(page: Page) {
  return (await page.request.get("/api/v1/workspace?collection=samples")).json();
}

test("specific taxonomy conflicts, opt-in repair, undo, saved draft and explicit publication", async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 1080 });
  await login(page, 9104);
  const seeded = await (await page.request.post("/api/v1/test/review-fixture")).json();
  await page.reload();
  await chooseOption(page.getByLabel("Workspace collection"), "samples");
  await page.getByRole("button", { name: "AI Organization", exact: false }).click();
  await page.getByRole("button", { name: "Review draft", exact: true }).click();
  const dialog = page.getByRole("dialog");
  const check = page.getByRole("region", { name: "Taxonomy conflict check", exact: true });
  await expect(check).toContainText("3 conflicts need review");
  await expect(check).toContainText("AI - Atrificial Intelligence");
  await expect(check).toContainText("Archived — reservation retained");
  await expect(check).toContainText("Legacy Machine Learning");
  await expect(check).toContainText("after normalization");
  await page.screenshot({ path: "test-results/feedback-taxonomy-conflicts-1920.png" });
  await check.getByRole("button", { name: "Edit manually", exact: true }).first().click();
  await expect(page.getByLabel("Proposal 1 aliases", { exact: true })).toBeFocused();
  await check.getByRole("button", { name: "Reuse existing “Artificial Intelligence”", exact: true }).click();
  await expect(page.getByLabel("Proposal 1 name", { exact: true })).toHaveValue("Artificial Intelligence");
  await expect(page.getByLabel("Proposal 2 domain", { exact: true })).toHaveValue("Artificial Intelligence");
  await expect(check).toContainText("2 conflicts need review");
  await dialog.getByRole("button", { name: "Undo last repair", exact: true }).click();
  await expect(page.getByLabel("Proposal 1 name", { exact: true })).toHaveValue("AI - Atrificial Intelligence");
  await expect(check).toContainText("3 conflicts need review");
  await check.getByRole("button", { name: "Reuse existing “Artificial Intelligence”", exact: true }).click();
  await expect(check).toContainText("2 conflicts need review");
  await check.getByRole("button", { name: "Remove conflicting aliases", exact: true }).click();
  await expect(check).toContainText("Names and aliases are ready");
  await expect(page.getByLabel("Proposal 3 aliases", { exact: true })).toHaveValue("");
  await expect(dialog.getByText("Supporting samples: synthetic/orion-api", { exact: true })).toBeVisible();
  const before = await workspace(page);
  expect(before.organization.drafts["review-fixture"].status).toBe("DRAFT");
  expect(before.organization.drafts["review-fixture"].edited_proposals).toBeUndefined();
  expect(Object.keys(before.organization.concepts)).toHaveLength(2);
  await dialog.evaluate(el => el.scrollTop = 0);
  await page.screenshot({ path: "test-results/feedback-taxonomy-repaired-1920.png" });
  await dialog.getByRole("button", { name: "Save draft", exact: true }).click();
  await expect(dialog).toHaveCount(0);
  const saved = await workspace(page);
  expect(Object.keys(saved.organization.concepts)).toHaveLength(2);
  expect(saved.organization.drafts["review-fixture"].status).toBe("DRAFT");
  await page.getByRole("button", { name: "Review draft", exact: true }).click();
  await expect(check).toContainText("Names and aliases are ready");
  await dialog.getByRole("button", { name: "Approve & publish taxonomy", exact: true }).click();
  await expect(dialog).toHaveCount(0);
  const after = await workspace(page);
  expect(after.organization.drafts["review-fixture"].status).toBe("PUBLISHED");
  expect(after.organization.concepts[seeded.existing_id].name).toBe("Artificial Intelligence");
  expect(after.organization.concepts[seeded.archived_id].active).toBe(false);
  const project = Object.values(after.organization.concepts).find((c: unknown) => (c as { kind: string }).kind === "PROJECT") as { domain: string };
  expect(project.domain).toBe(seeded.existing_id);
});

test("balanced palette, meditating mascot and title-cased Material sync progress", async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 1080 });
  await login(page, 9105);
  await page.getByRole("button", { name: "Load demo samples", exact: true }).click();
  await expect(page.getByRole("button", { name: "Details for orion-api", exact: true })).toBeVisible();
  const snapshot = await workspace(page);
  await page.route("**/api/v1/workspace?collection=samples", route => route.fulfill({ json: {
    ...snapshot, organization: { ...snapshot.organization,
      control: { ...snapshot.organization.control, active_run: "progress-fixture" },
      runs: { ...snapshot.organization.runs, "progress-fixture": {
        id: "progress-fixture", kind: "SYNC", status: "RUNNING", total: 12, processed: 6,
        failed: 0, created_at: new Date().toISOString(), message: "FIXTURE: Reading repository access", outcomes: {},
      } },
    },
  } }));
  await expect(page.locator(".wm-progress strong")).toHaveText("GitHub Sync · Running");
  await expect(page.getByRole("progressbar", { name: "GitHub Sync progress", exact: true })).toHaveAttribute("value", "6");
  await expect(page.locator(".wm-progress")).toHaveCSS("background-color", "rgb(240, 245, 251)");
  await expect(page.locator(".wm-spinner")).toHaveCSS("border-top-color", "rgb(57, 73, 171)");
  const numbers = await page.locator(".wm-stat strong").evaluateAll(els => els.map(el => getComputedStyle(el).color));
  expect(new Set(numbers).size).toBe(1);
  await expect(page.locator(".wm-stat")).toHaveCount(5);
  await expect(page.locator(".wm-stats")).toHaveCSS("background-color", "rgb(255, 255, 255)");
  await expect(page.locator(".wm-stats")).toHaveCSS("gap", "0px");
  await page.screenshot({ path: "test-results/feedback-sync-progress-1920.png" });
  await page.emulateMedia({ reducedMotion: "reduce" });
  const logo = page.locator(".wm-header .wm-zen-cat");
  await expect.poll(() => logo.evaluate(el => (el as HTMLImageElement).currentSrc)).toContain("rays-poster.svg");
  const poster = await page.request.get(await logo.evaluate(el => (el as HTMLImageElement).currentSrc));
  writeFileSync("test-results/feedback-selected-logo.svg", await poster.text());
  await expect(logo).toBeVisible();
});
