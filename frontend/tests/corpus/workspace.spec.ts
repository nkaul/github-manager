import { test, expect, type Page } from "@playwright/test";
import { chooseOption } from "../helpers/chooseOption";

test.afterEach(async ({ page }) => { await page.unrouteAll({ behavior: "ignoreErrors" }); });

async function openWorkspace(page: Page) {
  await page.request.post("http://127.0.0.1:8015/api/v1/test/login");
  await page.goto("/");
  await chooseOption(page.getByLabel("Workspace collection"), "ground-truth");
  await expect(page.getByRole("heading", { name: "Public - Ground Truth", exact: true })).toBeVisible();
}
async function openRepository(page: Page, name: string) {
  await page.getByLabel("Search corpus repositories").fill(name);
  await expect(page.locator(".corpus-pagination")).toContainText("1 results");
  await page.getByRole("button", { name: `Review ${name}`, exact: true }).click();
  await expect(page.getByRole("region", { name: "Repository evidence review", exact: true }).getByRole("heading", { name, exact: true })).toBeVisible();
  await expect(page.getByLabel("Repository purpose", { exact: true })).toBeEnabled();
}
async function reviewGroups(page: Page) {
  for (const kind of ["Projects", "Topics", "Tags"]) await page.getByRole("checkbox", { name: `${kind} reviewed`, exact: true }).check();
}

// All mutations below use the disposable test identity/database on 8015.
test("adjacent review saves first, retries only navigation, persists and keeps mobile actions visible", async ({ page }) => {
  const errors: string[] = [];
  let reviewWrites = 0, failNeighbor = false;
  page.on("pageerror", error => errors.push(error.message));
  page.on("console", message => { if (message.type() === "error" && !message.text().includes("503")) errors.push(message.text()); });
  await page.route("**/api/v1/**", async route => {
    const original = new URL(route.request().url());
    if (route.request().method() === "PUT" && /\/review$/.test(original.pathname)) reviewWrites++;
    if (failNeighbor && original.pathname.endsWith("/neighbors")) {
      failNeighbor = false;
      await route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ detail: "Disposable navigation failure" }) });
      return;
    }
    original.port = "8015";
    await route.fulfill({ response: await route.fetch({ url: original.toString() }) });
  });
  await openWorkspace(page);
  await expect(page.locator(".corpus-stats")).toContainText("600");
  await expect(page.locator(".corpus-app select")).toHaveCount(0);
  await page.getByRole("button", { name: /^Filters/ }).click();
  await chooseOption(page.getByLabel("Sampling domain", { exact: true }), "science");
  const sampling = page.getByRole("combobox", { name: "Sampling domain", exact: true });
  await sampling.fill("not a known sampling domain");
  await expect(page.getByRole("listbox", { name: "Available options", exact: true })).toContainText("No matching options");
  await sampling.press("Escape");
  await expect(sampling).toHaveValue("Science · 60");
  await expect(page.getByRole("dialog", { name: "Filter corpus repositories", exact: true })).toBeVisible();
  await page.getByRole("dialog", { name: "Filter corpus repositories", exact: true }).getByRole("button", { name: "Done", exact: true }).click();
  await expect(page.locator(".corpus-pagination")).toContainText("60 results");
  await openRepository(page, "numpy/numpy");
  const review = page.getByRole("region", { name: "Repository evidence review", exact: true });
  await expect(page.getByLabel("Saved source text")).toContainText("NumPy");
  await expect(review.getByRole("button", { name: "Confirm & next", exact: true })).toBeDisabled();
  await expect(review.getByText("Original proposed labels", { exact: true })).toBeVisible();
  await review.getByText("Notes & missing concepts", { exact: false }).click();
  await review.getByLabel("Review notes", { exact: true }).fill("Disposable browser QA only; not a real human annotation.");
  await reviewGroups(page);
  await page.getByLabel("Search corpus repositories").fill("");
  await expect(page.locator(".corpus-pagination")).toContainText("60 results");
  const row = await (await page.request.get("http://127.0.0.1:8015/api/v1/corpus/repos?q=numpy/numpy")).json();
  const rid = row.items[0].repository_id;
  const neighbor = await (await page.request.get(`http://127.0.0.1:8015/api/v1/corpus/repos/${rid}/neighbors?domain=science&label_basis=proposals`)).json();
  expect(neighbor.next).toBeTruthy();
  failNeighbor = true;
  await review.getByRole("button", { name: "Confirm & next", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Review saved");
  await expect(page.getByRole("status")).toContainText("could not be loaded");
  await expect(review.getByRole("heading", { name: "numpy/numpy", exact: true })).toBeVisible();
  expect(reviewWrites).toBe(1);
  await review.getByRole("button", { name: "Next repository", exact: true }).click();
  await expect(review.getByRole("heading", { name: neighbor.next.full_name, exact: true })).toBeVisible();
  expect(reviewWrites).toBe(1);
  const saved = await (await page.request.get(`http://127.0.0.1:8015/api/v1/corpus/repos/${rid}`)).json();
  expect(saved.review.status).toBe("HUMAN_CONFIRMED");
  expect(saved.review.revision).toBe(1);
  expect(saved.draft).toBeNull();
  await page.screenshot({ path: "test-results-corpus/public-ground-truth-review-1080p.png", fullPage: false });
  await page.reload();
  await chooseOption(page.getByLabel("Workspace collection"), "ground-truth");
  await openRepository(page, "numpy/numpy");
  await review.getByText("Notes & missing concepts", { exact: false }).click();
  await expect(review.getByLabel("Review notes", { exact: true })).toHaveValue("Disposable browser QA only; not a real human annotation.");
  const exported = await (await page.request.get("http://127.0.0.1:8015/api/v1/corpus/reviews/export")).json();
  expect(exported.reviews.some((record: { repository_id: number }) => record.repository_id === rid)).toBeTruthy();
  await chooseOption(page.getByLabel("Workspace collection"), "github");
  await expect(page.getByRole("heading", { name: "My repositories", exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "numpy/numpy", exact: false })).toHaveCount(0);
  await chooseOption(page.getByLabel("Workspace collection"), "ground-truth");
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.getByRole("tab", { name: /^Review$/ })).toHaveAttribute("aria-selected", "true");
  await expect(page.locator(".corpus-decision-footer")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
  const boxes = await page.evaluate(() => ({ footer: document.querySelector(".corpus-decision-footer")!.getBoundingClientRect().bottom, height: innerHeight }));
  expect(boxes.footer).toBeLessThanOrEqual(boxes.height);
  const reviewTab = page.getByRole("tab", { name: /^Review$/ });
  await reviewTab.focus();
  await reviewTab.press("ArrowRight");
  await expect(page.getByRole("tab", { name: "Evidence", exact: true })).toBeFocused();
  await expect(reviewTab).toHaveAttribute("tabindex", "-1");
  await expect(page.getByRole("region", { name: "Saved source evidence", exact: true })).toBeVisible();
  await page.getByRole("tab", { name: "Evidence", exact: true }).press("Home");
  await expect(page.getByRole("tab", { name: /^Queue/ })).toBeFocused();
  await page.getByRole("tab", { name: /^Queue/ }).press("ArrowRight");
  await expect(reviewTab).toBeFocused();
  await expect(reviewTab).toHaveAttribute("tabindex", "0");
  await page.screenshot({ path: "test-results-corpus/public-ground-truth-mobile.png", fullPage: false });
  expect(errors).toEqual([]);
});

test("incomplete drafts restore without confirmation and invalid evidence remains editable", async ({ page }) => {
  await page.route("**/api/v1/**", async route => {
    const url = new URL(route.request().url()); url.port = "8015";
    await route.fulfill({ response: await route.fetch({ url: url.toString() }) });
  });
  await openWorkspace(page);
  await openRepository(page, "scipy/scipy");
  const summary = await (await page.request.get("http://127.0.0.1:8015/api/v1/corpus")).json();
  const rows = await (await page.request.get("http://127.0.0.1:8015/api/v1/corpus/repos?q=scipy/scipy")).json();
  const rid = rows.items[0].repository_id;
  const detail = await (await page.request.get(`http://127.0.0.1:8015/api/v1/corpus/repos/${rid}`)).json();
  const originalIds = detail.proposal.labels.filter((label: { decision?: string }) => (label.decision || "SUPPORTED") === "SUPPORTED").map((label: { id: string }) => label.id);
  const addition = summary.registry.find((concept: { id: string; kind: string }) => concept.kind === "TAG" && !originalIds.includes(concept.id));
  expect(addition).toBeTruthy();
  await chooseOption(page.getByRole("combobox", { name: "Add Tag", exact: true }), addition.id);
  await expect(page.getByRole("button", { name: "Add label", exact: true })).toHaveCount(0);
  await chooseOption(page.getByLabel(`Evidence file for ${addition.name}`, { exact: true }), detail.files[0].path);
  const quote = page.getByLabel(`Exact quote supporting ${addition.name}`, { exact: true });
  await quote.fill("This exact quote is deliberately absent from the saved source.");
  await page.getByRole("button", { name: "Save draft", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Draft saved");
  const afterDraft = await (await page.request.get("http://127.0.0.1:8015/api/v1/corpus")).json();
  expect(afterDraft.human_confirmed).toBe(summary.human_confirmed);
  expect(afterDraft.reviewed).toBe(summary.reviewed);
  await page.reload();
  await chooseOption(page.getByLabel("Workspace collection"), "ground-truth");
  await openRepository(page, "scipy/scipy");
  await page.getByText("Exact source evidence · attached", { exact: true }).click();
  await expect(quote).toBeVisible();
  await expect(quote).toHaveValue("This exact quote is deliberately absent from the saved source.");
  await reviewGroups(page);
  await page.getByRole("button", { name: "Confirm & next", exact: true }).click();
  await expect(page.locator(".corpus-error")).toContainText("Added-label evidence must match saved source text exactly");
  await expect(quote).toHaveValue("This exact quote is deliberately absent from the saved source.");
  await expect(page.getByRole("button", { name: "Save draft", exact: true })).toBeEnabled();
  await expect(page.locator(".corpus-conflict")).toHaveCount(0);
  const source = await (await page.request.get(`http://127.0.0.1:8015/api/v1/corpus/repos/${rid}/source?path=${encodeURIComponent(detail.files[0].path)}`)).json();
  await quote.fill(source.text.slice(0, 100));
  await reviewGroups(page);
  await page.getByRole("button", { name: "Confirm & next", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Review saved");
  const saved = await (await page.request.get(`http://127.0.0.1:8015/api/v1/corpus/repos/${rid}`)).json();
  expect(saved.review.status).toBe("HUMAN_CONFIRMED");
  expect(saved.draft).toBeNull();
});

test("stale final-save failure keeps the case and edits until explicit comparison and reapply", async ({ page }) => {
  let conflictOnce = true;
  await page.route("**/api/v1/**", async route => {
    const url = new URL(route.request().url());
    if (conflictOnce && route.request().method() === "PUT" && /\/review$/.test(url.pathname)) {
      conflictOnce = false;
      await route.fulfill({ status: 409, contentType: "application/json", body: JSON.stringify({ detail: "Another review was saved; compare the latest review.", code: "CORPUS_REVIEW_CONFLICT", current_review: null, current_draft: null }) });
      return;
    }
    url.port = "8015";
    await route.fulfill({ response: await route.fetch({ url: url.toString() }) });
  });
  await openWorkspace(page);
  const candidates = await (await page.request.get("http://127.0.0.1:8015/api/v1/corpus/repos?limit=25")).json();
  const candidate = candidates.items.find((row: { full_name: string; review_status: string; has_draft?: boolean }) => row.review_status === "PROPOSED" && !row.has_draft && !["numpy/numpy", "scipy/scipy"].includes(row.full_name));
  expect(candidate, "A real untouched public case is required for independent stale-save QA").toBeTruthy();
  await openRepository(page, candidate.full_name);
  const review = page.getByRole("region", { name: "Repository evidence review", exact: true });
  await review.getByText("Notes & missing concepts", { exact: false }).click();
  await review.getByLabel("Review notes").fill("Disposable stale-save test: these unsaved edits must survive.");
  await reviewGroups(page);
  await review.getByRole("button", { name: "Confirm & next", exact: true }).click();
  await expect(page.locator(".corpus-conflict")).toContainText("Your current edits are preserved");
  await expect(review.getByRole("heading", { name: candidate.full_name, exact: true })).toBeVisible();
  await expect(review.getByLabel("Review notes")).toHaveValue("Disposable stale-save test: these unsaved edits must survive.");
  await expect(review.getByRole("button", { name: "Confirm & next", exact: true })).toBeDisabled();
  await page.getByRole("button", { name: "Compare latest saved record", exact: true }).click();
  await page.getByRole("button", { name: "Reapply my edits", exact: true }).click();
  for (const kind of ["Projects", "Topics", "Tags"]) await expect(page.getByRole("checkbox", { name: `${kind} reviewed`, exact: true })).not.toBeChecked();
  await expect(review.getByLabel("Review notes")).toHaveValue("Disposable stale-save test: these unsaved edits must survive.");
  await reviewGroups(page);
  await review.getByRole("button", { name: "Confirm & next", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Review saved");
});
