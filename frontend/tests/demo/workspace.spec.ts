import { chooseOption } from "../helpers/chooseOption";
import { test, expect, type Page } from "@playwright/test";

async function login(page: Page) {
  await page.goto("/");
  await page.getByRole("link", { name: "Continue with GitHub" }).click();
  await page.getByLabel("Account menu", { exact: true }).click();
  await expect(page.getByText("Demo Test Fixture", { exact: true })).toBeVisible();
  await page.getByLabel("Account menu", { exact: true }).click();
}

test("operator renews and selectively updates allowance without clearing usage history", async ({ page }) => {
  await login(page);
  await page.getByRole("button", { name: "AI Organization", exact: false }).click();
  await page.getByRole("button", { name: "Manage API allowance", exact: true }).click();
  await page.getByLabel("HTTP requests in window", { exact: true }).fill("6");
  await expect(page.getByLabel("Generations in window", { exact: true })).toHaveValue("3");
  await page.getByLabel("Reason for allowance change").fill("Browser allowance renewal test");
  await page.getByRole("button", { name: "Renew allowance window", exact: true }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(page.locator(".wm-budget")).toContainText("0/6 HTTP requests");
  await expect(page.locator(".wm-budget")).toContainText("0/3 generations");
  await page.getByRole("button", { name: "Manage API allowance", exact: true }).click();
  await chooseOption(page.getByLabel("Allowance action"), "SET_LIMITS");
  await page.getByLabel("Update HTTP request limit", { exact: true }).uncheck();
  await page.getByLabel("Update generation limit", { exact: true }).check();
  await page.getByLabel("Generations in window", { exact: true }).fill("5");
  await page.getByRole("button", { name: "Save selected limits", exact: true }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(page.locator(".wm-budget")).toContainText("0/6 HTTP requests");
  await expect(page.locator(".wm-budget")).toContainText("0/5 generations");
  await page.reload();
  await page.getByRole("button", { name: "AI Organization", exact: false }).click();
  await expect(page.locator(".wm-budget")).toContainText("0/6 HTTP requests");
  await page.getByRole("button", { name: "Manage API allowance", exact: true }).click();
  await expect(page.getByRole("dialog")).toContainText("Browser allowance renewal test");
  await page.screenshot({ path: "test-results/phase09-allowance.png", fullPage: true });
});

test("real local app: OAuth fixture, sync, draft review, classification, manual control and reset", async ({ page }) => {
  await login(page);
  await page.getByRole("button", { name: "Start GitHub sync", exact: true }).click();
  await expect(page.getByRole("link", { name: "fixture/api", exact: false })).toBeVisible();
  await page.getByRole("button", { name: "Favorites", exact: true }).click();
  await expect(page.getByRole("link", { name: "fixture/api", exact: false })).toBeVisible();
  await expect(page.getByRole("link", { name: "fixture/private", exact: false })).toHaveCount(0);
  await chooseOption(page.getByLabel("Workspace collection"), "samples");
  await page.getByRole("button", { name: "Load demo samples", exact: true }).first().click();
  await expect(page.getByRole("button", { name: "Details for orion-api" })).toBeVisible();
  await page.getByRole("button", { name: "AI Organization", exact: false }).click();
  await chooseOption(page.getByLabel("Inference mode"), "LIVE");
  await page.getByRole("button", { name: "Discover taxonomy", exact: false }).click();
  await page.getByRole("button", { name: "Start reviewed run", exact: true }).click();
  await page.getByRole("button", { name: "Review draft", exact: true }).click();
  await expect(page.getByRole("dialog")).toContainText("Test fixture draft");
  await page.getByLabel("Proposal 1 name").fill("Applications");
  await page.getByRole("button", { name: "Approve & publish taxonomy" }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page.getByRole("button", { name: "Full classification", exact: true }).click();
  await page.getByRole("button", { name: "Start reviewed run", exact: true }).click();
  await expect(page.getByRole("button", { name: "Accept", exact: true })).toHaveCount(3);
  await page.getByRole("button", { name: "Accept", exact: true }).nth(1).click();
  await page.getByRole("button", { name: "Reject", exact: true }).first().click();
  await expect(page.getByRole("button", { name: "Accept", exact: true })).toHaveCount(1);
  await page.getByRole("button", { name: "Demo samples", exact: false }).click();
  await page.getByRole("button", { name: "Details for orion-api" }).click();
  await expect(page.getByRole("dialog")).toContainText("demo-rake-tfidf-v2");
  await chooseOption(page.getByRole("combobox", { name: /^Add membership/ }), { label: "Web APIs" });
  await page.getByRole("button", { name: "Save manual membership" }).click();
  await expect(page.getByRole("button", { name: "Remove Web APIs", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Close dialog" }).click();
  await page.reload();
  await chooseOption(page.getByLabel("Workspace collection"), "samples");
  await expect(page.getByRole("button", { name: "Details for orion-api" })).toBeVisible();
  await page.screenshot({ path: "test-results/phase09-desktop.png", fullPage: true });
  await page.getByRole("button", { name: "Latest Work", exact: false }).click();
  await expect(page.getByText("FIXTURE: Synthetic Orion activity", { exact: false })).toBeVisible();
  await expect(page.locator(".wm-table-note")).toContainText("Last synced");
  await expect(page.locator(".wm-table-note")).toContainText("Use Sync samples to refresh");
  await page.getByRole("button", { name: "AI Organization", exact: false }).click();
  await page.getByRole("button", { name: "Preview reset", exact: true }).click();
  await page.getByRole("button", { name: "Preview impact", exact: true }).click();
  await page.getByLabel("Type exactly DELETE").fill("DELETE ");
  await expect(page.getByRole("button", { name: "Confirm reset" })).toBeDisabled();
  await page.getByLabel("Type exactly DELETE").fill("DELETE");
  await page.getByRole("button", { name: "Confirm reset" }).click();
  await expect(page.locator(".wm-reset-card").getByText("Cleanup verified", { exact: false })).toBeVisible();
  await page.screenshot({ path: "test-results/phase09-organizer.png", fullPage: true });
  await page.getByLabel("Account menu", { exact: true }).click();
  await page.getByLabel("Sign out").click();
  await expect(page.getByRole("heading", { name: "Connect your GitHub account" })).toBeVisible();
});

test("keyboard concept editor, rule preview, mobile layout and protected private details", async ({ page }) => {
  await login(page);
  await page.getByRole("button", { name: "Content settings", exact: false }).click();
  await page.getByRole("button", { name: "+ Create concept", exact: true }).click();
  await chooseOption(page.getByRole("combobox", { name: /^Type/ }), "TAG");
  await page.getByLabel("Name", { exact: true }).fill("Python");
  await page.getByLabel("Description", { exact: true }).fill("Primary implementation language");
  await page.getByRole("button", { name: "Save concept", exact: true }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page.getByRole("button", { name: "+ Create rule", exact: true }).click();
  await page.getByLabel("Rule name").fill("Python repositories");
  await page.getByLabel("Value", { exact: true }).fill("Python");
  await chooseOption(page.getByRole("combobox", { name: /^Assign concept/ }), { label: "TAG · Python" });
  await page.getByRole("button", { name: "Preview matches", exact: true }).click();
  await expect(page.getByRole("dialog")).toContainText("2 matching repositories");
  await page.getByRole("button", { name: "Approve rule" }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page.getByRole("button", { name: "My Repos", exact: false }).click();
  await page.getByRole("button", { name: "Details for fixture/private" }).click();
  await expect(page.getByRole("dialog")).toContainText("Private README-derived evidence is excluded");
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.getByLabel("Workspace collection")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
  await page.screenshot({ path: "test-results/phase09-phone.png", fullPage: true });
  expect(await page.evaluate(() => ({ local: { ...localStorage }, session: { ...sessionStorage } }))).toEqual({ local: {}, session: {} });
});

test("bulk and drag actions add multiple project memberships", async ({ page }) => {
  await login(page);
  await chooseOption(page.getByLabel("Workspace collection"), "samples");
  await page.getByRole("button", { name: "Content settings", exact: true }).click();
  await page.getByRole("button", { name: "+ Create concept", exact: true }).click();
  await chooseOption(page.getByRole("combobox", { name: /^Type/ }), "PROJECT");
  await page.getByLabel("Name", { exact: true }).fill("Orion Operations");
  await chooseOption(page.getByRole("combobox", { name: /^Parent domain/ }), { label: "Applications" });
  await page.getByRole("button", { name: "Save concept", exact: true }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page.getByRole("button", { name: "Demo samples", exact: false }).click();
  await page.getByLabel("Select orion-api", { exact: true }).check();
  await page.getByLabel("Select orion-ui", { exact: true }).check();
  await chooseOption(page.getByLabel("Bulk assignment concept"), { label: "Orion Operations" });
  await page.getByRole("button", { name: "Add membership", exact: true }).click();
  await expect(page.getByRole("status").filter({ hasText: "Manual assignment saved." })).toBeVisible();
  await page.getByRole("button", { name: "Clear", exact: true }).click();
  const row = page.getByRole("row").filter({ has: page.getByLabel("Select orion-ui", { exact: true }) });
  await row.dragTo(page.locator(".wm-tree .wm-project").first());
  await page.getByRole("button", { name: "Details for orion-ui", exact: true }).click();
  await expect(page.getByRole("button", { name: "Remove Orion", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Remove Orion Operations", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Remove Orion", exact: true }).click();
  await expect(page.getByRole("button", { name: "Remove Orion", exact: true })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Remove Orion Operations", exact: true })).toBeVisible();
});

test("repository selection is retained for a bounded organizer run", async ({ page }) => {
  await login(page);
  await chooseOption(page.getByLabel("Workspace collection"), "samples");
  // This scenario must also run alone against the disposable empty workspace.
  const load = page.getByRole("button", { name: "Load demo samples", exact: true }).first();
  if (await load.isVisible()) await load.click();
  // A classification preview requires an existing taxonomy, independent of earlier tests.
  const seeded = await page.evaluate(async () => {
    const me = await (await fetch("/api/v1/me")).json();
    return (await fetch("/api/v1/taxonomy/concepts?collection=samples", {
      method: "POST", headers: { "Content-Type": "application/json", "X-CSRF-Token": me.csrf_token },
      body: JSON.stringify({ kind: "TAG", name: "Selection scope fixture", aliases: [], description: "Disposable selection test" }),
    })).ok;
  });
  expect(seeded).toBe(true);
  await page.getByLabel("Select orion-ui", { exact: true }).check();
  await page.getByRole("button", { name: "AI Organization", exact: false }).click();
  await expect(page.getByLabel("Repository selection mode")).toHaveValue("Manual selection (1)");
  await chooseOption(page.getByLabel("Inference mode"), "RULES");
  const responsePromise = page.waitForResponse(r => r.url().includes("/organizer/execute") && r.request().method() === "POST");
  await page.getByRole("button", { name: "Full classification", exact: true }).click();
  await page.getByRole("button", { name: "Start reviewed run", exact: true }).click();
  const response = await responsePromise;
  expect(response.status()).toBe(202);
  expect((await response.json()).total).toBe(1);
});
