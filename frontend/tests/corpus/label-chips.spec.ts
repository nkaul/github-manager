import { test, expect, type Page } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { LABEL_CHIP_PALETTE, labelChipProps } from "../../src/components/workspace/LabelChip";
import { chooseOption } from "../helpers/chooseOption";

function luminance(hex: string) {
  const [r, g, b] = [1, 3, 5].map(i => {
    const value = parseInt(hex.slice(i, i + 2), 16) / 255;
    return value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4;
  });
  return .2126 * r + .7152 * g + .0722 * b;
}

test("label identity palette is deterministic and all small text pairs exceed 4.5:1", () => {
  for (const [background, ink] of LABEL_CHIP_PALETTE) {
    expect((luminance(background) + .05) / (luminance(ink) + .05), `${ink} on ${background}`).toBeGreaterThanOrEqual(4.5);
  }
  expect(labelChipProps("tag:python")).toEqual(labelChipProps("tag:python"));
  expect(labelChipProps("tag:python").style).not.toEqual(labelChipProps("tag:typescript").style);
  expect(labelChipProps("tag:python")["data-label-id"]).toBe("tag:python");
});

test.afterEach(async ({ page }) => { await page.unrouteAll({ behavior: "ignoreErrors" }); });

async function openIsolatedApp(page: Page) {
  await page.setViewportSize({ width: 1440, height: 900 });
  mkdirSync("../docs/design/workspace-refinement/tag-colors", { recursive: true });
  await page.route("**/api/v1/**", async route => {
    const url = new URL(route.request().url()); url.port = "8015";
    await route.fulfill({ response: await route.fetch({ url: url.toString() }) });
  });
  await page.request.post("http://127.0.0.1:8015/api/v1/test/login");
  await page.goto("/");
}

test("main label chips retain identity across list, details and reload; selection remains Indigo-white", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await openIsolatedApp(page);
  await chooseOption(page.getByLabel("Workspace collection"), "samples");
  const ids = await page.evaluate(async () => {
    const identity = await (await fetch("/api/v1/me")).json();
    async function post(path: string, data?: unknown) {
      const response = await fetch(`/api/v1${path}?collection=samples`, { method: "POST", headers: { "Content-Type": "application/json", "X-CSRF-Token": identity.csrf_token }, body: data === undefined ? undefined : JSON.stringify(data) });
      if (!response.ok) throw new Error(`Disposable chip setup failed: ${response.status}`);
      return response.json();
    }
    await post("/samples/load");
    const ids: string[] = [];
    for (const name of ["Chip Python", "Chip TypeScript", "Chip Rust"]) {
      const tag = await post("/taxonomy/concepts", { kind: "TAG", name, aliases: [], description: "Disposable browser color check" });
      ids.push(tag.id);
    }
    await post("/repos/associations", { repo_keys: ["synthetic/orion-api"], concept_ids: ids, operation: "ADD" });
    return ids;
  });
  await page.reload();
  await chooseOption(page.getByLabel("Workspace collection"), "samples");
  const row = page.locator(".wm-table tbody tr").filter({ has: page.getByRole("button", { name: "Details for orion-api", exact: true }) });
  for (const id of ids) await expect(row.locator(`[data-label-id="${id}"]`)).toBeVisible();
  const before = await row.locator(".wm-label-chip").evaluateAll(els => els.map(el => ({ id: el.getAttribute("data-label-id"), background: getComputedStyle(el).backgroundColor, color: getComputedStyle(el).color })));
  for (const chip of before) {
    expect(chip.background).not.toBe("rgb(242, 244, 247)");
    expect(chip.color).not.toBe("rgb(82, 96, 120)");
  }
  await page.screenshot({ path: "../docs/design/workspace-refinement/tag-colors/main-1440.png" });
  await row.getByRole("checkbox", { name: "Select orion-api", exact: true }).check();
  await expect(row).toHaveCSS("background-color", "rgb(57, 73, 171)");
  for (const id of ids) await expect(row.locator(`[data-label-id="${id}"]`)).toHaveCSS("color", "rgb(255, 255, 255)");
  await row.getByRole("checkbox", { name: "Select orion-api", exact: true }).uncheck();
  await row.getByRole("button", { name: "Details for orion-api", exact: true }).click();
  const detail = page.getByRole("dialog", { name: "orion-api", exact: true });
  for (const chip of before) await expect(detail.locator(`[data-label-id="${chip.id}"]`)).toHaveCSS("background-color", chip.background);
  await page.getByRole("button", { name: "Close dialog", exact: true }).click();
  await page.reload();
  await chooseOption(page.getByLabel("Workspace collection"), "samples");
  for (const chip of before) await expect(row.locator(`[data-label-id="${chip.id}"]`)).toHaveCSS("background-color", chip.background);
  await row.locator(`[data-label-id="${ids[0]}"]`).click();
  await expect(row.locator(`[data-label-id="${ids[0]}"]`)).toHaveCSS("background-color", "rgb(57, 73, 171)");
  await expect(row.locator(`[data-label-id="${ids[0]}"]`)).toHaveCSS("color", "rgb(255, 255, 255)");
});

test("Ground Truth retained, original and independent labels share colors without a review write", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  let reviewWrites = 0;
  page.on("request", request => { if (request.method() === "PUT" && /\/corpus\/repos\/\d+\/(review|draft)/.test(request.url())) reviewWrites++; });
  await openIsolatedApp(page);
  await chooseOption(page.getByLabel("Workspace collection"), "ground-truth");
  const summary = await (await page.request.get("http://127.0.0.1:8015/api/v1/corpus")).json();
  const name = summary.annotation_pilot.queue[0].full_name;
  await page.getByLabel("Search corpus repositories").fill(name);
  await page.getByRole("button", { name: `Review ${name}`, exact: true }).click();
  const review = page.getByRole("region", { name: "Repository evidence review", exact: true });
  const chips = review.locator(".corpus-label-row .wm-label-chip");
  await expect(chips.first()).toBeVisible();
  const identities = await chips.evaluateAll(els => els.map(el => ({ id: el.getAttribute("data-label-id"), background: getComputedStyle(el).backgroundColor })));
  expect(new Set(identities.map(chip => chip.background)).size).toBeGreaterThan(1);
  await review.getByText("Original proposed labels", { exact: true }).click();
  for (const chip of identities) await expect(review.locator(`.corpus-original-label [data-label-id="${chip.id}"]`)).toHaveCSS("background-color", chip.background);
  await review.getByText("Original proposed labels", { exact: true }).click();
  await expect(page.getByLabel("Saved source text", { exact: true })).toBeVisible();
  await expect(page.locator(".corpus-queue-list")).toHaveAttribute("aria-busy", "false");
  await expect(review).toHaveAttribute("aria-busy", "false");
  await expect(page.getByText("Loading saved source…", { exact: true })).toHaveCount(0);
  await page.locator(".corpus-review-scroll").evaluate(el => { el.scrollTop = 0; });
  await page.screenshot({ path: "../docs/design/workspace-refinement/tag-colors/ground-truth-1440.png" });
  await review.getByRole("button", { name: "Compare independent annotations", exact: true }).click();
  const comparison = page.getByRole("region", { name: "Independent agent annotations", exact: true });
  await expect(comparison.locator(".wm-label-chip").first()).toBeVisible();
  for (const chip of identities) {
    const compared = comparison.locator(`[data-label-id="${chip.id}"]`);
    if (await compared.count()) await expect(compared.first()).toHaveCSS("background-color", chip.background);
  }
  await page.getByRole("button", { name: "Close comparison", exact: true }).click();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole("tab", { name: "Review", exact: true }).click();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await expect(chips.first()).toBeVisible();
  expect(reviewWrites).toBe(0);
});
