import type { Locator } from "@playwright/test";

/** Choose the committed value of the searchable single-select, never raw query text. */
export async function chooseOption(control: Locator, choice: string | { label: string }) {
  const input = control.and(control.page().getByRole("combobox"));
  await input.click();
  await input.fill("");
  const listId = await input.getAttribute("aria-controls");
  const list = input.page().locator(`[id=${JSON.stringify(listId)}]`);
  const option = typeof choice === "string" ? list.locator(`[role="option"][data-value=${JSON.stringify(choice)}]`) : list.getByRole("option", { name: choice.label, exact: true });
  await option.click();
}
