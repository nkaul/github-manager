import { test, expect, type Page } from "@playwright/test";
import { writeFileSync } from "node:fs";

async function seed(page: Page, id: number) {
  await page.request.post("/api/v1/test/login", { data: { id } });
  await page.goto("/");
  await page.getByLabel("Workspace collection").selectOption("samples");
  if (await page.getByRole("button", { name: "Load demo samples", exact: true }).count()) await page.getByRole("button", { name: "Load demo samples", exact: true }).first().click();
  await expect(page.getByRole("button", { name: "Details for orion-api", exact: true })).toBeVisible();
}

async function mutate(page: Page, path: string, data: unknown) {
  return page.evaluate(async ({ path, data }) => {
    const me = await (await fetch("/api/v1/me")).json();
    const response = await fetch(`/api/v1${path}?collection=samples`, { method: "POST", headers: { "Content-Type": "application/json", "X-CSRF-Token": me.csrf_token }, body: JSON.stringify(data) });
    if (!response.ok) throw new Error("Fixture setup failed: " + response.status);
    return response.json();
  }, { path, data });
}

async function structure(page: Page, prefix: string, count = 1) {
  const domain = await mutate(page, "/taxonomy/concepts", { kind: "DOMAIN", name: `${prefix} Domain`, description: "UI fixture domain", aliases: [] });
  const projects = [];
  for (let i = 0; i < count; i++) projects.push(await mutate(page, "/taxonomy/concepts", { kind: "PROJECT", name: `${prefix} Project ${i + 1}`, domain: domain.id, description: "UI fixture project", aliases: [] }));
  await expect(page.locator(".wm-sidebar").getByRole("button", { name: domain.name, exact: true })).toBeVisible();
  return { domain, projects };
}

test("tree-first shell, readable compact cards and responsive/reduced-motion layout", async ({ page }) => {
  await seed(page, 9101);
  await structure(page, "Layout", 22);
  const audits = [];
  for (const [width, height] of [[1920, 1080], [1440, 900], [1280, 800], [390, 844]]) {
    await page.setViewportSize({ width, height });
    const overflow = await page.evaluate(() => ({ width: innerWidth, scroll: document.documentElement.scrollWidth, elements: [...document.querySelectorAll("body *")].filter(el => el.getBoundingClientRect().right > innerWidth + 1).slice(0, 12).map(el => ({ class: el.className, right: el.getBoundingClientRect().right })) }));
    expect(overflow.scroll, JSON.stringify(overflow)).toBeLessThanOrEqual(width);
    await expect(page.getByRole("button", { name: "AI Organization", exact: false })).toHaveCount(1);
    await expect(page.getByRole("button", { name: "Content settings", exact: true })).toHaveCount(1);
    if (width >= 1280) {
      const geometry = await page.evaluate(() => {
        const tree = document.querySelector(".wm-sidebar .wm-tree")!.getBoundingClientRect();
        const sidebar = document.querySelector(".wm-sidebar")!.getBoundingClientRect();
        const stat = document.querySelector(".wm-stat")!;
        return { ratio: tree.height / sidebar.height, cardHeight: stat.getBoundingClientRect().height, labelSize: parseFloat(getComputedStyle(stat.querySelector("span")!).fontSize) };
      });
      const colors = await page.evaluate(() => {
        function luminance(rgb: string) {
          const channels = rgb.startsWith("#") ? [1, 3, 5].map(i => parseInt(rgb.slice(i, i + 2), 16)) : rgb.match(/[\d.]+/g)!.slice(0, 3).map(Number);
          const values = channels.map(v => { const c = v / 255; return c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4; });
          return .2126 * values[0] + .7152 * values[1] + .0722 * values[2];
        }
        return [".wm-nav.is-active span", ".wm-project span", ".wm-stat>span", ".wm-stat small", ".wm-stat-selected strong", ".wm-tree-menu>summary", ".wm-header-actions>.wm-secondary", ".wm-filter-field>span", ".wm-table th", ".wm-description", ".wm-visibility", ".wm-activity", ".wm-source"].map(selector => {
          const el = document.querySelector(selector)!;
          const style = getComputedStyle(el);
          let parent: Element | null = el;
          let background = "rgb(255, 255, 255)";
          while (parent) { const computed = getComputedStyle(parent); if (computed.backgroundImage !== "none" && computed.getPropertyValue("--metric-surface").trim()) { background = computed.getPropertyValue("--metric-surface").trim(); break; } const bg = computed.backgroundColor; if (bg !== "rgba(0, 0, 0, 0)" && bg !== "transparent") { background = bg; break; } parent = parent.parentElement; }
          const a = luminance(style.color), b = luminance(background);
          return { selector, color: style.color, background, ratio: (Math.max(a, b) + .05) / (Math.min(a, b) + .05), size: parseFloat(style.fontSize) };
        });
      });
      for (const pair of colors) { expect(pair.ratio, JSON.stringify(pair)).toBeGreaterThanOrEqual(4.5); expect(pair.size, pair.selector).toBeGreaterThanOrEqual(12); }
      audits.push({ width, height, ...geometry, colors });
      expect(geometry.ratio).toBeGreaterThanOrEqual(width === 1920 ? 0.65 : 0.55);
      expect(geometry.cardHeight).toBeLessThanOrEqual(100);
      expect(geometry.labelSize).toBeGreaterThanOrEqual(12);
    } else {
      await page.getByRole("button", { name: "Open navigation", exact: true }).click();
      await expect(page.locator(".wm-sidebar").getByRole("button", { name: "Layout Domain", exact: true })).toBeVisible();
      await page.getByRole("button", { name: "Close navigation", exact: true }).click();
      await expect(page.locator(".wm-sidebar")).toHaveCSS("transform", "matrix(1, 0, 0, 1, -280, 0)");
    }
    await page.screenshot({ path: `test-results/refinement-${width}.png` });
  }
  writeFileSync("test-results/refinement-layout-audit.json", JSON.stringify(audits, null, 2));
  await page.setViewportSize({ width: 1920, height: 1080 });
  const domain = page.locator(".wm-sidebar").getByRole("button", { name: "Layout Domain", exact: true });
  await domain.focus();
  await page.keyboard.press("ArrowDown");
  await expect(page.locator(".wm-sidebar").getByRole("button", { name: "Layout Project 1", exact: true })).toBeFocused();
  await page.keyboard.press("Home");
  await expect(page.getByRole("button", { name: "Collapse Layout Domain", exact: true })).toBeFocused();
  await page.emulateMedia({ reducedMotion: "reduce" });
  await expect.poll(() => page.locator(".wm-header .wm-zen-cat").evaluate(el => (el as HTMLImageElement).currentSrc)).toContain("poster.svg");
});

test("header tree fetches on node selection and scoped KPIs/selection/filter chips agree", async ({ page }) => {
  await seed(page, 9102);
  const { projects } = await structure(page, "Browse");
  await mutate(page, "/repos/associations", { repo_keys: ["synthetic/orion-api"], concept_ids: [projects[0].id], operation: "ADD" });
  await page.waitForTimeout(2400); // Allow the normal workspace poll and active list refresh to settle.
  const requests: string[] = [];
  page.on("request", request => { if (request.method() === "GET" && new URL(request.url()).pathname === "/api/v1/repos") requests.push(request.url()); });
  await page.locator(".wm-tree-menu > summary").click();
  await page.waitForTimeout(450);
  await page.keyboard.press("Escape");
  await expect(page.locator(".wm-tree-menu > summary")).toBeFocused();
  await page.locator(".wm-tree-menu > summary").click();
  expect(requests).toHaveLength(0);
  await page.locator(".wm-tree-menu").getByRole("button", { name: projects[0].name, exact: true }).click();
  await expect(page.getByRole("heading", { name: projects[0].name, exact: true })).toBeVisible();
  await expect.poll(() => requests.filter(url => new URL(url).searchParams.get("concept") === projects[0].id).length).toBe(1);
  await expect(page.locator(".wm-stat").filter({ has: page.locator("span", { hasText: /^In this view$/ }) }).locator("strong")).toHaveText("1");
  await page.getByLabel("Select orion-api", { exact: true }).check();
  await expect(page.locator(".wm-stat-selected strong")).toHaveText("1");
  await page.getByLabel("Search repositories").fill("orion");
  await expect(page.locator(".wm-stat-selected strong")).toHaveText("0");
  await expect(page.locator(".wm-active-filters")).toContainText("Search: orion");
  await page.getByRole("button", { name: "Clear filters", exact: true }).click();
  await expect(page.getByLabel("Search repositories")).toHaveValue("");
  await page.screenshot({ path: "test-results/refinement-filtered.png" });
  await page.getByRole("button", { name: "AI Organization", exact: false }).click();
  await page.getByRole("button", { name: "Discover taxonomy", exact: false }).click();
  const cohort = page.getByRole("region", { name: "Run preview", exact: true });
  await expect(cohort.locator(".wm-preview-numbers span").filter({ hasText: "Chosen" }).locator("strong")).toHaveText("1");
  await expect(cohort.locator(".wm-cohort-list")).toContainText("orion-api");
});

test("automatic counts, adaptive preview, reviewed execution and saved defaults", async ({ page }) => {
  await seed(page, 9103);
  await page.getByRole("button", { name: "AI Organization", exact: false }).click();
  await page.getByLabel("Inference mode").selectOption("LIVE");
  await page.getByLabel("Taxonomy sample size", { exact: true }).fill("2");
  await page.getByLabel("Classification batch size", { exact: true }).fill("1");
  await page.getByLabel("Budget mode", { exact: true }).selectOption("ADAPTIVE");
  await page.getByRole("button", { name: "Save defaults", exact: true }).click();
  await expect(page.getByText("Run defaults saved. No work was started.", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Discover taxonomy", exact: false }).click();
  const preview = page.getByRole("region", { name: "Run preview", exact: true });
  await expect(preview).toContainText("Adaptive dollars");
  await expect(preview.locator(".wm-preview-numbers span").filter({ hasText: "Chosen" }).locator("strong")).toHaveText("2");
  await expect(preview).toContainText("1 generations / 2 HTTP attempts");
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: "test-results/refinement-run-preview.png", fullPage: true });
  await page.getByRole("button", { name: "Start reviewed run", exact: true }).click();
  await page.getByRole("button", { name: "Review draft", exact: true }).click();
  await page.getByRole("button", { name: "Approve & publish taxonomy", exact: true }).click();
  await page.getByRole("button", { name: "Full classification", exact: true }).click();
  await expect(preview.locator(".wm-preview-numbers span").filter({ hasText: "Chosen" }).locator("strong")).toHaveText("1");
  await page.getByRole("button", { name: "Start reviewed run", exact: true }).click();
  await expect(page.locator(".wm-run").first()).toContainText("Completed");
  await page.reload();
  await page.getByLabel("Workspace collection").selectOption("samples");
  await page.getByRole("button", { name: "AI Organization", exact: false }).click();
  await expect(page.getByLabel("Taxonomy sample size", { exact: true })).toHaveValue("2");
  await expect(page.getByLabel("Classification batch size", { exact: true })).toHaveValue("1");
  await expect(page.getByLabel("Budget mode", { exact: true })).toHaveValue("ADAPTIVE");
});
