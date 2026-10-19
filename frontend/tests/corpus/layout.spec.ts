import { test, expect } from "@playwright/test";
import { writeFileSync } from "node:fs";
import { chooseOption } from "../helpers/chooseOption";

test("live three-pane review stays compact, selected Indigo, keyboard reachable and responsive", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.route("**/api/v1/**", async route => {
    const url = new URL(route.request().url());
    url.port = "8015";
    const response = await route.fetch({ url: url.toString() });
    await route.fulfill({ response });
  });
  await page.request.post("http://127.0.0.1:8015/api/v1/test/login");
  await page.goto("/");
  await chooseOption(page.getByLabel("Workspace collection"), "ground-truth");
  const review = page.getByRole("region", { name: "Repository evidence review" });
  await expect(review.getByLabel("Repository purpose", { exact: true })).toBeVisible();
  await page.getByLabel("Search corpus repositories").fill("numpy/numpy");
  await expect(page.getByRole("button", { name: "Review numpy/numpy", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Review numpy/numpy", exact: true }).click();
  await expect(review.getByRole("heading", { name: "numpy/numpy", exact: true })).toBeVisible();
  await expect(review.getByRole("checkbox", { name: "Projects reviewed", exact: true })).not.toBeChecked();
  await expect(review.getByRole("button", { name: "Confirm & next", exact: true })).toBeDisabled();
  const audit = [];
  for (const [width, height] of [[1920, 1080], [1440, 900], [1280, 800], [390, 844]]) {
    await page.setViewportSize({ width, height });
    await expect(page.locator(".corpus-header")).toHaveCSS("height", "56px");
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    if (width > 780) {
      const layout = await page.evaluate(() => {
        const rect = (selector: string) => document.querySelector(selector)!.getBoundingClientRect().toJSON();
        return { header: rect(".corpus-header"), workspace: rect(".corpus-layout"), queue: rect(".corpus-queue"), review: rect(".corpus-review"), footer: rect(".corpus-decision-footer"), source: rect(".corpus-source-pane") };
      });
      expect(layout.workspace.y).toBeLessThanOrEqual(200);
      expect(layout.footer.bottom).toBeLessThanOrEqual(height);
      expect(layout.footer.x).toBeGreaterThanOrEqual(layout.review.x);
      expect(layout.queue.width).toBe(280);
      if (width >= 1400) expect(layout.source.width).toBeGreaterThanOrEqual(340);
      const active = page.locator('.corpus-queue-item[aria-current="true"]');
      await expect(active).toHaveCSS("background-color", "rgb(57, 73, 171)");
      await expect(active.locator("strong")).toHaveCSS("color", "rgb(255, 255, 255)");
      await expect(page.getByLabel("Search corpus repositories")).toHaveCSS("font-size", "14px");
      const lastCheck = review.getByRole("checkbox", { name: "Tags reviewed", exact: true });
      await review.getByRole("checkbox", { name: "Projects reviewed", exact: true }).focus();
      await lastCheck.focus();
      const box = await lastCheck.boundingBox();
      expect(box!.y + box!.height).toBeLessThanOrEqual(layout.footer.top);
      audit.push({ width, height, ...layout });
    } else {
      await page.getByRole("tab", { name: "Review", exact: true }).click();
      await expect(page.getByRole("tab", { name: "Review", exact: true })).toHaveCSS("background-color", "rgb(57, 73, 171)");
      const lastCheck = review.getByRole("checkbox", { name: "Tags reviewed", exact: true });
      await review.getByRole("checkbox", { name: "Projects reviewed", exact: true }).focus();
      await lastCheck.focus();
      const footer = await page.locator(".corpus-decision-footer").boundingBox();
      const box = await lastCheck.boundingBox();
      expect(footer!.y + footer!.height).toBeLessThanOrEqual(height);
      expect(box!.y + box!.height).toBeLessThanOrEqual(footer!.y);
      await expect(page.getByLabel("Repository purpose", { exact: true })).toHaveCSS("font-size", "16px");
    }
    await page.screenshot({ path: `test-results-corpus/redesign-${width}.png` });
    if (width === 1280) {
      const evidence = review.getByRole("button", { name: "Evidence for NumPy", exact: true });
      await evidence.click();
      const sheet = page.getByRole("dialog", { name: "Saved source evidence", exact: true });
      await expect(sheet).toBeVisible();
      await expect(review).toHaveAttribute("inert", "");
      const sourceChoice = sheet.getByRole("combobox", { name: "Source document", exact: true });
      await sourceChoice.click();
      await sourceChoice.press("Escape");
      await expect(sheet).toBeVisible();
      const provenance = sheet.locator("summary").filter({ hasText: /^Source provenance$/ });
      await provenance.focus();
      await provenance.press("Enter");
      await expect(sheet.getByText("Manifest SHA-256", { exact: true })).toBeVisible();
      await page.screenshot({ path: "test-results-corpus/redesign-evidence-sheet-1280.png" });
      await page.keyboard.press("Escape");
      await expect(sheet).toHaveCount(0);
      await expect(evidence).toBeFocused();
    }
  }
  writeFileSync("test-results-corpus/redesign-layout-audit.json", JSON.stringify(audit, null, 2));
  expect(errors).toEqual([]);
});
