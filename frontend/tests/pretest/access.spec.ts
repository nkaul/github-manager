import { test, expect } from "@playwright/test";

test("local API proxy, setup instructions and anonymous session boundary", async ({ page, request }) => {
  const config = await request.get("/api/v1/pretest/config");
  expect(config.ok()).toBeTruthy();
  const anonymous = await request.get("/api/v1/me");
  expect(anonymous.status()).toBe(401);
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Connect your GitHub account" })).toBeVisible();
  if (!(await config.json()).oauth_configured) {
    await expect(page.getByRole("heading", { name: "One-time OAuth App setup" })).toBeVisible();
    await expect(page.getByText("http://127.0.0.1:3000/api/v1/auth/github/callback", { exact: true })).toBeVisible();
    await expect(page.getByText("Continue with GitHub", { exact: false })).toHaveAttribute("aria-disabled", "true");
  }
  expect(await page.evaluate(() => ({ local: { ...localStorage }, session: { ...sessionStorage } }))).toEqual({ local: {}, session: {} });
  await page.screenshot({ path: "test-results/phase0-desktop.png", fullPage: true });
});

test("fixture identity, repository view, source limits and report action", async ({ page }) => {
  const mutations: string[] = [];
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const path = new URL(request.url());
    let value: unknown;
    if (path.pathname.endsWith("/pretest/config")) value = { oauth_configured: true };
    else if (path.pathname.endsWith("/me")) value = { user: { id: 42, login: "fixture-user", name: "Fixture User" }, scopes: ["repo"], csrf_token: "fixture-csrf" };
    else if (path.pathname.endsWith("/repos")) {
      value = { items: [{ id: 1, full_name: "fixture/repo", html_url: "https://github.com/fixture/repo", private: true, language: "Python", default_branch: "main", sources: ["OWNER"], eligible: true, favorite: false }], total: 1, next_cursor: null, coverage: [{ source: "WATCH", status: "UNAVAILABLE", count: null, note: "Permission or organization policy denied" }] };
    } else if (path.pathname.endsWith("/pretest/github/run")) {
      expect(request.method()).toBe("POST");
      expect(request.headers()["x-csrf-token"]).toBe("fixture-csrf");
      mutations.push(path.pathname);
      value = { filename: "github-fixture.md", rows: [] };
    } else throw new Error(`Unexpected fixture path ${path.pathname}`);
    await route.fulfill({ contentType: "application/json", body: JSON.stringify(value) });
  });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Fixture User" })).toBeVisible();
  await expect(page.getByText("GitHub ID 42", { exact: false })).toBeVisible();
  const repo = page.getByRole("link", { name: "fixture/repo", exact: false });
  await expect(repo).toHaveAttribute("href", "https://github.com/fixture/repo");
  await expect(page.getByText("UNAVAILABLE · unknown")).toBeVisible();
  await page.getByRole("button", { name: "Verify access & save report" }).click();
  await expect(page.getByRole("link", { name: "github-fixture.md" })).toBeVisible();
  expect(mutations).toHaveLength(1);
  await page.getByRole("button", { name: "Favorites", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Favorites", exact: true })).toBeVisible();
});

test("phone layout fits viewport and setup remains reachable", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Connect your GitHub account" })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
  await page.screenshot({ path: "test-results/phase0-phone.png", fullPage: true });
});

test("OAuth start proxy preserves nonce cookie and redirects without following GitHub", async ({ request }) => {
  const config = await request.get("/api/v1/pretest/config");
  test.skip(!(await config.json()).oauth_configured, "OAuth registration is not configured");
  const start = await request.get("/api/v1/auth/github/start", { maxRedirects: 0 });
  expect(start.status()).toBe(302);
  const location = new URL(start.headers()["location"]);
  expect(location.origin).toBe("https://github.com");
  expect(location.searchParams.get("code_challenge_method")).toBe("S256");
  expect(start.headers()["set-cookie"]).toContain("HttpOnly");
  expect(start.headers()["set-cookie"]).toContain("SameSite=lax");
  const badCallback = await request.get("/api/v1/auth/github/callback?state=invalid-test-state&code=invalid-test-code", { maxRedirects: 0 });
  expect(badCallback.status()).toBe(400);
  expect(await badCallback.text()).not.toContain("invalid-test-code");
});
