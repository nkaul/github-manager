import { test, expect } from "@playwright/test";
import { chooseOption } from "../helpers/chooseOption";

test.afterEach(async ({ page }) => { await page.unrouteAll({ behavior: "ignoreErrors" }); });

test("switching workspaces does not restart the session countdown", async ({ page }) => {
  await page.clock.install();
  await page.route("**/api/v1/**", async route => {
    const url = new URL(route.request().url()); url.port = "8015";
    const response = await route.fetch({ url: url.toString() });
    if (url.pathname === "/api/v1/me") {
      const value = await response.json(); value.session.expires_in_seconds = 160;
      await route.fulfill({ response, json: value });
    } else await route.fulfill({ response });
  });
  await page.request.post("http://127.0.0.1:8015/api/v1/test/login");
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "My repositories", exact: true })).toBeVisible();
  await page.clock.fastForward(50_000);
  const warning = page.getByRole("dialog", { name: "Your session is about to expire", exact: true });
  await expect(warning).toBeVisible();
  await warning.getByRole("button", { name: "Save work first", exact: true }).click();
  await chooseOption(page.getByLabel("Workspace collection", { exact: true }), "ground-truth");
  await expect(warning).toBeVisible();
  const countdown = (await warning.locator("p").first().innerText()).match(/(\d+):(\d+)/);
  expect(countdown).not.toBeNull();
  expect(Number(countdown![1]) * 60 + Number(countdown![2])).toBeLessThanOrEqual(115);
});

test("Ground Truth Home guards edits, final warning permits draft saving, and expired API returns to sign-in", async ({ page }) => {
  let shortSession = false, expired = false, finalWrites = 0;
  await page.route("**/api/v1/**", async route => {
    const url = new URL(route.request().url()); url.port = "8015";
    if (route.request().method() === "PUT" && /\/review$/.test(url.pathname)) finalWrites++;
    if (expired && url.pathname.startsWith("/api/v1/corpus")) { await route.fulfill({ status: 401, json: { detail: "Sign in to GitHub", code: "SESSION_EXPIRED" } }); return; }
    const response = await route.fetch({ url: url.toString() });
    if (url.pathname === "/api/v1/me" && shortSession) {
      const value = await response.json(); value.session.expires_in_seconds = 8;
      await route.fulfill({ response, json: value });
    } else await route.fulfill({ response });
  });
  await page.request.post("http://127.0.0.1:8015/api/v1/test/login");
  await page.goto("/");
  await chooseOption(page.getByLabel("Workspace collection", { exact: true }), "ground-truth");
  await page.getByLabel("Search corpus repositories", { exact: true }).fill("numpy/numpy");
  await expect(page.locator(".corpus-pagination")).toContainText("1 results");
  await page.getByRole("button", { name: "Review numpy/numpy", exact: true }).click();
  const purpose = page.getByLabel("Repository purpose", { exact: true });
  await expect(purpose).toBeEnabled();
  const text = `${await purpose.inputValue()} Draft-only session recovery QA.`;
  await purpose.fill(text);
  await page.getByRole("link", { name: "GitHub Manager home", exact: true }).click();
  const leave = page.getByRole("dialog", { name: "Save your changes?", exact: true });
  await expect(leave).toBeVisible();
  await leave.getByRole("button", { name: "Stay", exact: true }).click();
  await expect(purpose).toHaveValue(text);
  shortSession = true;
  await page.evaluate(() => window.dispatchEvent(new Event("focus")));
  const warning = page.getByRole("dialog", { name: "Your session is about to expire", exact: true });
  await expect(warning).toBeVisible();
  await warning.getByRole("button", { name: "Save work first", exact: true }).click();
  await expect(warning).not.toBeVisible();
  shortSession = false;
  await page.getByRole("button", { name: "Save draft", exact: true }).click();
  await expect(page.locator(".corpus-save-state")).toContainText("Draft saved");
  const row = await (await page.request.get("http://127.0.0.1:8015/api/v1/corpus/repos?q=numpy/numpy")).json();
  const rid = row.items[0].repository_id;
  expired = true;
  await page.getByLabel("Search corpus repositories", { exact: true }).fill("fastapi/fastapi");
  await expect(page.getByRole("heading", { name: "Connect your GitHub account", exact: true })).toBeVisible();
  await expect(page.getByRole("status")).toContainText("Your session expired");
  const draft = await (await page.request.get(`http://127.0.0.1:8015/api/v1/corpus/repos/${rid}/draft`)).json();
  expect(draft.purpose).toBe(text); expect(finalWrites).toBe(0);
});
