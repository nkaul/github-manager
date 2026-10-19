import { test, expect, type Page } from "@playwright/test";
import { apiFetch, ApiError } from "../../src/lib/api";
import { chooseOption } from "../helpers/chooseOption";

test.afterEach(async ({ page }) => { await page.unrouteAll({ behavior: "ignoreErrors" }); });
async function login(page: Page, id: number) {
  await page.request.post("/api/v1/test/login", { data: { id } });
  await page.goto("/");
}

test("request deadline covers a stalled response body and distinguishes timeout from sign-in expiry", async () => {
  const original = globalThis.fetch;
  globalThis.fetch = async (_input, init) => new Response(new ReadableStream({ start(controller) {
    init?.signal?.addEventListener("abort", () => controller.error(new DOMException("Aborted", "AbortError")));
  } }));
  try {
    await expect(apiFetch("https://example.invalid/no-network", {}, 20)).rejects.toMatchObject({ status: 504, code: "REQUEST_TIMEOUT" } satisfies Partial<ApiError>);
  } finally { globalThis.fetch = original; }
});

test("session warning extends explicitly and logo returns settings and samples to GitHub home", async ({ page }) => {
  let shortened = true, extensions = 0;
  await page.route("**/api/v1/me", async route => {
    const response = await route.fetch(); const value = await response.json();
    if (shortened) value.session.expires_in_seconds = 45;
    await route.fulfill({ response, json: value });
  });
  await page.route("**/api/v1/auth/session/extend", async route => { extensions++; shortened = false; await route.fulfill({ response: await route.fetch() }); });
  await login(page, 9171);
  const warning = page.getByRole("dialog", { name: "Your session is about to expire", exact: true });
  await expect(warning).toBeVisible();
  const geometry = await warning.boundingBox(); expect(geometry!.width).toBeLessThanOrEqual(460);
  await page.screenshot({ path: "../docs/design/workspace-refinement/session-recovery/session-warning.png" });
  await warning.getByRole("button", { name: "Extend session", exact: true }).click();
  await expect(warning).not.toBeVisible(); expect(extensions).toBe(1);
  await page.getByRole("button", { name: "Content settings", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Content settings", exact: true })).toBeVisible();
  await page.getByRole("link", { name: "GitHub Manager home", exact: true }).click();
  await expect(page.getByRole("heading", { name: "My repositories", exact: true })).toBeVisible();
  await chooseOption(page.getByLabel("Workspace collection", { exact: true }), "samples");
  await page.getByRole("link", { name: "GitHub Manager home", exact: true }).click();
  await expect(page.getByRole("combobox", { name: "Workspace collection", exact: true })).toHaveValue("My GitHub workspace");
  await expect(page.getByRole("heading", { name: "My repositories", exact: true })).toBeVisible();
  await expect(page.locator("body")).not.toContainText(/works locally|runs locally|local workspace/i);
});

test("expired authenticated polling returns to sign-in and clears disabled workspace controls", async ({ page }) => {
  let expired = false;
  await page.route("**/api/v1/workspace?**", async route => {
    if (expired) await route.fulfill({ status: 401, json: { detail: "Sign in to GitHub", code: "SESSION_EXPIRED" } });
    else await route.fulfill({ response: await route.fetch() });
  });
  await login(page, 9172);
  await expect(page.getByRole("heading", { name: "My repositories", exact: true })).toBeVisible();
  expired = true;
  await expect(page.getByRole("heading", { name: "Connect your GitHub account", exact: true })).toBeVisible();
  await expect(page.getByRole("status")).toContainText("Your session expired");
  await expect(page.getByRole("link", { name: "Continue with GitHub", exact: false })).toBeEnabled();
  await expect(page.locator(".wm-header")).toHaveCount(0);
  await expect(page.locator("body")).not.toContainText(/works locally|runs locally|local workspace/i);
});

test("slow Sync warns before its deadline and terminal failure offers an explicit retry", async ({ page }) => {
  let phase: "running" | "failed" | "done" = "running", retries = 0;
  const started = new Date(Date.now() - 275_000).toISOString();
  await page.route("**/api/v1/workspace?**", async route => {
    const response = await route.fetch(); const value = await response.json();
    value.organization.runs["ui-timeout"] = { id: "ui-timeout", kind: "SYNC", status: phase === "running" ? "RUNNING" : phase === "failed" ? "FAILED" : "COMPLETED", created_at: started, started_at: started, timeout_seconds: 300, processed: 0, total: 0, failed: 0, outcomes: {}, stage: "INVENTORY", message: phase === "failed" ? "GitHub Sync reached its time limit. Retry explicitly." : "Reading repository sources", error_code: phase === "failed" ? "GITHUB_SYNC_TIMEOUT" : undefined, retryable: phase === "failed" };
    value.organization.control.active_run = phase === "running" ? "ui-timeout" : null;
    await route.fulfill({ response, json: value });
  });
  await page.route("**/api/v1/sync?**", async route => { retries++; phase = "done"; await route.fulfill({ status: 202, json: { id: "explicit-retry" } }); });
  await login(page, 9173);
  const slow = page.getByRole("dialog", { name: "GitHub Sync is taking longer than expected", exact: true });
  await expect(slow).toBeVisible(); await slow.getByRole("button", { name: "Keep browsing", exact: true }).click();
  phase = "failed";
  const failure = page.getByRole("dialog", { name: "GitHub Sync timed out", exact: true });
  await expect(failure).toBeVisible(); expect(retries).toBe(0);
  await expect(page.locator(".wm-error")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Sync GitHub", exact: true })).toBeEnabled();
  await page.screenshot({ path: "../docs/design/workspace-refinement/session-recovery/sync-timeout.png" });
  await failure.getByRole("button", { name: "Close", exact: true }).click();
  await expect(page.locator(".wm-sync-summary")).toContainText("GitHub Sync did not finish");
  await page.getByRole("button", { name: "View recovery options", exact: true }).click();
  await failure.getByRole("button", { name: "Retry sync", exact: true }).click();
  await expect(failure).not.toBeVisible(); expect(retries).toBe(1);
});

test("another tab changing accounts clears the previous workspace and a delayed check cannot undo sign-out", async ({ page }) => {
  await login(page, 9171);
  await chooseOption(page.getByLabel("Workspace collection", { exact: true }), "samples");
  await page.request.post("/api/v1/test/login", { data: { id: 9172 } });
  await page.evaluate(() => window.dispatchEvent(new Event("focus")));
  await expect(page.getByRole("combobox", { name: "Workspace collection", exact: true })).toHaveValue("My GitHub workspace");
  await page.getByLabel("Account menu", { exact: true }).click();
  await expect(page.getByText("@ui-fixture-9172", { exact: false })).toBeVisible();
  await page.getByLabel("Account menu", { exact: true }).click();
  let release: (() => void) | undefined;
  await page.route("**/api/v1/me", async route => {
    const response = await route.fetch();
    await new Promise<void>(resolve => { release = resolve; });
    await route.fulfill({ response }).catch(() => {});
  });
  await page.evaluate(() => window.dispatchEvent(new Event("focus")));
  await expect.poll(() => Boolean(release)).toBe(true);
  await page.getByLabel("Account menu", { exact: true }).click();
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Connect your GitHub account", exact: true })).toBeVisible();
  const completed = page.waitForResponse(response => new URL(response.url()).pathname === "/api/v1/me");
  release?.();
  await (await completed).finished();
  await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));
  await expect(page.locator(".wm-header")).toHaveCount(0);
});
