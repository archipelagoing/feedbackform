import { expect, test, type Page } from "@playwright/test";

async function enter(page: Page, person: number) {
  await page.goto("/");
  await page.getByLabel("Login name").fill(`student${person}`);
  await page.getByLabel("Password", { exact: true }).fill(`browser-test-password-${person}`);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Our project", exact: true })).toBeVisible();
}

test("mouse passage and whole-idea comments persist with attribution after edits", async ({ page, browser }, testInfo) => {
  await enter(page, 1);
  const original = `Comment pilot ${Date.now()}: 😀 repeat and repeat\nKeep this final line.`;
  await page.getByLabel("Your idea", { exact: true }).fill(original);
  await page.getByRole("button", { name: "Share idea", exact: true }).click();
  const card = page.getByRole("article").filter({ hasText: original });
  const id = await card.getAttribute("data-idea-id");
  const stable = page.locator(`article[data-idea-id="${id}"]`);
  await stable.locator(".discussion > .idea-body").scrollIntoViewIfNeeded();
  // Use a real mouse drag over a DOM Range's measured word bounds.
  const box = await stable.locator(".discussion > .idea-body").evaluate(node => {
    const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
    let text: Text | null = null;
    let start = -1;
    while (walker.nextNode()) {
      const candidate = walker.currentNode as Text;
      const index = candidate.data.lastIndexOf("repeat");
      if (index !== -1) { text = candidate; start = index; }
    }
    if (!text) throw new Error("Passage not found");
    const range = document.createRange(); range.setStart(text, start); range.setEnd(text, start + 6);
    const box = range.getBoundingClientRect();
    return { x: box.x, y: box.y, width: box.width, height: box.height };
  });
  await page.mouse.move(box.x + 1, box.y + box.height / 2);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width - 1, box.y + box.height / 2, { steps: 12 });
  await page.mouse.up();
  await expect.poll(() => page.evaluate(() => window.getSelection()?.toString())).toBe("repeat");
  await stable.getByRole("button", { name: "Comment on selected passage", exact: true }).click();
  await stable.getByLabel("Your comment").fill("Preserve the second repeat.");
  await stable.getByRole("button", { name: "Save comment", exact: true }).click();
  await expect(stable.getByText("Your comment was saved.", { exact: true })).toBeVisible();
  await expect(stable.locator(".discussion > .idea-body mark")).toHaveText("repeat");
  await page.reload();
  await expect(stable.locator(".discussion > .idea-body mark")).toHaveText("repeat");
  await stable.getByRole("button", { name: "Comments", exact: true }).click();
  await expect(stable.locator(".comment")).toContainText("Preserve the second repeat.");
  await expect(stable.locator(".comment")).toContainText("Student 1");
  await stable.getByRole("button", { name: "Edit idea", exact: true }).click();
  await stable.getByLabel("Edit idea", { exact: true }).fill("A completely changed proposal");
  await stable.getByRole("button", { name: "Save new version" }).click();
  await stable.getByRole("button", { name: "Comments", exact: true }).click();
  await expect(stable.locator(".comment")).toContainText("On version 1 · earlier version");
  await stable.getByText("View version 1 context", { exact: true }).click();
  await expect(stable.locator("details")).toContainText(original);
  await expect(stable.locator(".discussion > .idea-body mark")).toHaveCount(0);
  const context = await browser.newContext();
  try {
    const other = await context.newPage(); await enter(other, 2);
    const otherCard = other.locator(`article[data-idea-id="${id}"]`);
    await otherCard.getByRole("button", { name: "Comment on idea", exact: true }).click();
    await otherCard.getByLabel("Your comment").fill("I have an overall concern.");
    await otherCard.getByRole("button", { name: "Save comment", exact: true }).click();
    await expect(otherCard.locator(".comment").filter({ hasText: "overall concern" })).toContainText("Student 2");
    await otherCard.screenshot({ path: testInfo.outputPath("comments.png") });
  } finally { await context.close(); }
});

test("keyboard passage search anchors text after emoji and a CRLF", async ({ page }) => {
  await enter(page, 3);
  const source = `Keyboard ${Date.now()} 😀\r\nTarget phrase`;
  // Persist CRLF through the real API because an editable textarea normalizes line endings.
  const me = await page.request.get("/api/auth/me");
  const workspaces = await (await page.request.get("/api/workspaces")).json();
  const created = await page.request.post(`/api/workspaces/${workspaces[0].id}/ideas`, {
    headers: { Origin: "http://127.0.0.1:3100", "X-FeedbackForm-Request": "1", "X-CSRF-Token": (await me.json()).csrf_token },
    data: { body: source },
  });
  expect(created.ok()).toBeTruthy();
  const idea = await created.json(); await page.reload();
  const card = page.locator(`article[data-idea-id="${idea.id}"]`);
  await card.getByRole("button", { name: "Choose a passage with keyboard" }).focus();
  await page.keyboard.press("Enter");
  const picker = card.getByLabel("Find passage text", { exact: true });
  await expect(picker).toBeFocused();
  await page.keyboard.type("Target phrase");
  await page.keyboard.press("Tab");
  await expect(card.getByRole("button", { name: "Comment on this passage", exact: true })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(card.getByLabel("Your comment")).toBeFocused();
  await page.keyboard.type("This is essential.");
  await page.keyboard.press("Tab"); await page.keyboard.press("Enter");
  await expect(card.locator(".comment")).toContainText("This is essential.");
  await expect(card.locator(".comment blockquote")).toHaveText("Target phrase");
});
