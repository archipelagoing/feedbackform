import { expect, test } from "@playwright/test";

test("create the workspace and all four accounts through the frontend", async ({ page }, testInfo) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Create your team’s workspace." })).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath("setup.png"), fullPage: true });
  await page.getByLabel("Workspace name", { exact: true }).fill("Our project");
  await page.getByLabel("Decision question", { exact: true }).fill("What should we build?");
  await page.getByRole("button", { name: "Continue", exact: true }).click();
  for (let i = 1; i <= 4; i++) {
    await expect(page.getByRole("heading", { name: `Set up participant ${i}.`, exact: true })).toBeVisible();
    await page.getByLabel("Display name", { exact: true }).fill(`Student ${i}`);
    await page.getByLabel("Login name", { exact: true }).fill(i === 2 ? "student1" : `student${i}`);
    await page.getByLabel("Password", { exact: true }).fill(`browser-test-password-${i}`);
    await page.getByLabel("Confirm password", { exact: true }).fill(i === 1 ? "mismatched-password" : `browser-test-password-${i}`);
    const submit = page.getByRole("button", { name: i < 4 ? "Continue" : "Create workspace", exact: true });
    if (i === 1) {
      await submit.click();
      await expect(page.getByRole("main").getByRole("alert")).toContainText("passwords do not match");
      await page.getByLabel("Confirm password", { exact: true }).fill(`browser-test-password-${i}`);
    }
    if (i === 2) {
      await submit.click();
      await expect(page.getByRole("main").getByRole("alert")).toContainText("different login name");
      await page.getByLabel("Login name", { exact: true }).fill("student2");
    }
    await submit.click();
  }
  await expect(page.getByRole("heading", { name: "Our project", exact: true })).toBeVisible();
  await expect(page.getByRole("list", { name: "Workspace participants" }).getByRole("listitem")).toHaveCount(4);
  await page.reload();
  await expect(page.getByRole("heading", { name: "Our project", exact: true })).toBeVisible();
  expect(await (await page.request.get("/api/setup/status")).json()).toEqual({ needed: false });
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(page.getByRole("button", { name: "Sign in", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Create your team’s workspace." })).toHaveCount(0);
});
