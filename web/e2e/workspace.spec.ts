import { expect, test, type Page } from "@playwright/test";

async function login(page: Page, number: number) {
  await page.goto("/");
  await page.getByLabel("Login name").fill(`student${number}`);
  await page.getByLabel("Password", { exact: true }).fill(`browser-test-password-${number}`);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Our project", exact: true })).toBeVisible();
}

test("four people share ideas, reload, and preserve editing ownership", async ({ browser }, testInfo) => {
  const contexts = await Promise.all([1, 2, 3, 4].map(() => browser.newContext()));
  const pages = await Promise.all(contexts.map(context => context.newPage()));
  const marker = `Pilot ${Date.now()}`;
  try {
    for (let i = 0; i < 4; i++) {
      const page = pages[i];
      await login(page, i + 1);
      await expect(page.getByRole("list", { name: "Workspace participants" }).getByRole("listitem")).toHaveCount(4);
      await page.getByLabel("Your idea", { exact: true }).fill(`${marker}: student ${i + 1} contribution 😀`);
      await page.getByRole("button", { name: "Share idea", exact: true }).click();
      await expect(page.getByText("Your idea was saved.", { exact: true })).toBeVisible();
    }
    const page = pages[0];
    await page.reload();
    for (let i = 1; i <= 4; i++) {
      await expect(page.getByRole("article").filter({ hasText: `${marker}: student ${i} contribution` })).toHaveCount(1);
    }
    const original = page.getByRole("article").filter({ hasText: `${marker}: student 1 contribution` });
    const ideaId = await original.getAttribute("data-idea-id");
    const own = page.locator(`article[data-idea-id="${ideaId}"]`);
    await own.getByRole("button", { name: "Edit idea", exact: true }).click();
    await own.getByLabel("Edit idea", { exact: true }).fill(`${marker}: student 1 revised`);
    await own.getByRole("button", { name: "Save new version" }).click();
    const revised = page.getByRole("article").filter({ hasText: `${marker}: student 1 revised` });
    await expect(revised.getByText("Version 2", { exact: true })).toBeVisible();
    await revised.getByRole("button", { name: "View history" }).click();
    await expect(revised.getByText(`${marker}: student 1 contribution 😀`, { exact: true })).toBeVisible();
    const other = page.getByRole("article").filter({ hasText: `${marker}: student 2 contribution` });
    await expect(other.getByRole("button", { name: "Edit idea", exact: true })).toHaveCount(0);
    await page.screenshot({ path: testInfo.outputPath("workspace.png"), fullPage: true });
    await page.getByRole("button", { name: "Sign out" }).click();
    await expect(page.getByRole("button", { name: "Sign in", exact: true })).toBeVisible();
    await page.reload();
    await expect(page.getByRole("button", { name: "Sign in", exact: true })).toBeVisible();
    await expect(page.getByRole("article")).toHaveCount(0);
  } finally { await Promise.allSettled(contexts.map(context => context.close())); }
});

test("a failed save preserves the idea draft", async ({ page }) => {
  await login(page, 1);
  const draft = "Keep my draft if the server is unavailable";
  await page.getByLabel("Your idea", { exact: true }).fill(draft);
  await page.route("**/api/workspaces/*/ideas", async route => {
    if (route.request().method() === "POST") await route.fulfill({ status: 503,
      contentType: "application/json", body: JSON.stringify({ detail: "Try again shortly" }) });
    else await route.continue();
  });
  await page.getByRole("button", { name: "Share idea", exact: true }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Try again shortly");
  await expect(page.getByLabel("Your idea", { exact: true })).toHaveValue(draft);
});

test("an expired session returns to sign-in", async ({ page }) => {
  await login(page, 1);
  await page.route("**/api/workspaces/*/ideas", route => route.fulfill({ status: 401,
    contentType: "application/json", body: JSON.stringify({ detail: "Session expired" }) }));
  await page.getByRole("button", { name: "Refresh ideas" }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Your session expired");
  await expect(page.getByRole("button", { name: "Sign in", exact: true })).toBeVisible();
});
