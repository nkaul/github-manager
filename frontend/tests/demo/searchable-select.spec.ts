import { test, expect, type Page } from "@playwright/test";

async function authenticate(page: Page, id: number) {
  const response = await page.request.post("/api/v1/test/login", { data: { id } });
  expect(response.ok(), `Disposable fixture login ${id} failed: HTTP ${response.status()}`).toBe(true);
}

async function login(page: Page, id: number) {
  await authenticate(page, id);
  await page.goto("/");
  await expect(page.getByRole("combobox", { name: "Workspace collection", exact: true })).toHaveValue("My GitHub workspace");
}

test("searchable workspace selection commits only an enabled option; Escape and Tab discard search", async ({ page }) => {
  await login(page, 9161);
  const workspace = page.getByRole("combobox", { name: "Workspace collection", exact: true });
  await workspace.click();
  const current = page.getByRole("option", { name: "My GitHub workspace", exact: true });
  await expect(current).toHaveCSS("background-color", "rgb(57, 73, 171)");
  await expect(current).toHaveCSS("color", "rgb(255, 255, 255)");
  await workspace.fill("synthetic");
  await expect(page.getByRole("option")).toHaveCount(1);
  await expect(page.getByRole("option", { name: "Public + synthetic demo", exact: true })).toBeVisible();
  await workspace.press("Escape");
  await expect(workspace).toHaveValue("My GitHub workspace");
  await expect(page.getByRole("listbox")).toHaveCount(0);
  await workspace.click();
  await workspace.fill("does not exist");
  await expect(page.getByText("No matching options", { exact: true })).toBeVisible();
  await workspace.press("Tab");
  await expect(workspace).toHaveValue("My GitHub workspace");
  await expect(page.getByRole("listbox")).toHaveCount(0);
  await workspace.click();
  await workspace.fill("synthetic");
  await workspace.press("Enter");
  await expect(workspace).toHaveValue("Public + synthetic demo");
  await expect(workspace).toBeFocused();
  await expect(page.getByRole("listbox")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Load demo samples", exact: true }).first()).toBeVisible();
});

test("required selection rejects uncommitted text and dropdown Escape preserves its parent dialog", async ({ page }) => {
  await login(page, 9162);
  await page.getByRole("button", { name: "Content settings", exact: true }).click();
  await page.getByRole("button", { name: "+ Create concept", exact: true }).click();
  const dialog = page.getByRole("dialog");
  const type = dialog.getByRole("combobox", { name: /^Type/ });
  await type.click();
  await type.press("Home");
  await expect(dialog.getByRole("option", { name: "DOMAIN", exact: true })).toHaveClass(/is-active/);
  await type.press("End");
  await expect(dialog.getByRole("option", { name: "TAG", exact: true })).toHaveClass(/is-active/);
  await type.press("Escape");
  await expect(dialog).toBeVisible();
  await expect(type).toHaveValue("PROJECT");
  await expect(type).toBeFocused();
  await dialog.getByLabel("Name", { exact: true }).fill("Unsaved required field check");
  const domain = dialog.getByRole("combobox", { name: /^Parent domain/ });
  await domain.click();
  await domain.fill("arbitrary text is not a domain ID");
  expect(await domain.evaluate(el => (el as HTMLInputElement).validity.customError)).toBe(true);
  await domain.press("Tab");
  let writes = 0;
  page.on("request", request => { if (request.method() === "POST" && /\/taxonomy\/concepts(?:\?|$)/.test(request.url())) writes++; });
  await dialog.getByRole("button", { name: "Save concept", exact: true }).click();
  await expect(dialog).toBeVisible();
  expect(writes).toBe(0);
  expect(await domain.evaluate(el => (el as HTMLInputElement).checkValidity())).toBe(false);
  await domain.press("Escape");
  await expect(dialog).toHaveCount(0);
});

test("disabled inference choices cannot be clicked or selected by keyboard", async ({ page }) => {
  await authenticate(page, 9163);
  const snapshot = await (await page.request.get("/api/v1/workspace?collection=github")).json();
  await page.route("**/api/v1/workspace?collection=github", route => route.fulfill({ json: { ...snapshot, live_ai_enabled: false } }));
  await page.goto("/");
  await page.getByRole("button", { name: "AI Organization", exact: false }).click();
  const inference = page.getByRole("combobox", { name: "Inference mode", exact: true });
  await inference.click();
  const live = page.getByRole("option", { name: "Live AI · within approved cap", exact: true });
  await expect(live).toHaveAttribute("aria-disabled", "true");
  await live.dispatchEvent("click");
  await inference.press("Escape");
  await expect(inference).toHaveValue("Reuse validated cached AI");
  await inference.press("ArrowDown");
  await inference.press("ArrowDown");
  await inference.press("Enter");
  await expect(inference).toHaveValue("Rules only · no model calls");
});

test.describe("touch dropdown", () => {
  test.use({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  test("long options wrap inside the viewport and a tap commits within a modal", async ({ page }) => {
    await authenticate(page, 9164);
    const snapshot = await (await page.request.get("/api/v1/workspace?collection=github")).json();
    const label = "Platform engineering, delivery systems and developer experience — long example";
    snapshot.organization.concepts = { ...snapshot.organization.concepts, "searchable-domain": { id: "searchable-domain", kind: "DOMAIN", name: label, description: "Browser fixture only", aliases: [], active: true } };
    await page.route("**/api/v1/workspace?collection=github", route => route.fulfill({ json: snapshot }));
    await page.goto("/");
    await page.getByRole("button", { name: "Content settings", exact: true }).click();
    await page.getByRole("button", { name: "+ Create concept", exact: true }).click();
    const dialog = page.getByRole("dialog");
    const domain = dialog.getByRole("combobox", { name: /^Parent domain/ });
    await domain.tap();
    await domain.fill("delivery");
    const list = dialog.getByRole("listbox");
    await expect(list).toBeVisible();
    const rect = await list.boundingBox();
    expect(rect!.x).toBeGreaterThanOrEqual(8);
    expect(rect!.x + rect!.width).toBeLessThanOrEqual(390);
    expect(rect!.y).toBeGreaterThanOrEqual(0);
    expect(rect!.y + rect!.height).toBeLessThanOrEqual(844);
    const option = list.getByRole("option", { name: label, exact: true });
    expect((await option.boundingBox())!.height).toBeGreaterThanOrEqual(44);
    await option.tap();
    await expect(domain).toHaveValue(label);
    await expect(list).toHaveCount(0);
    await expect(dialog).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await dialog.getByRole("button", { name: "Cancel", exact: true }).click();
  });
});
