import { expect, test } from "@playwright/test";

test("browser reaches the migrated database through the same-origin API", async ({ page }, testInfo) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toContainText("shared direction");
  await expect(page.getByRole("status")).toContainText("Connected");
  const response = await page.request.get("/api/health");
  expect(response.ok()).toBeTruthy();
  expect(await response.json()).toEqual({
    status: "ok", database: "ready", schema_revision: "0001_foundation",
  });
  await page.screenshot({ path: testInfo.outputPath("foundation.png"), fullPage: true });
});

test("API failure is shown without claiming storage is ready", async ({ page }) => {
  await page.route("**/api/health", route => route.fulfill({ status: 503, body: "unavailable" }));
  await page.goto("/");
  await expect(page.getByRole("status")).toContainText("Connection unavailable");
  await expect(page.getByRole("status")).not.toContainText("storage is ready");
});
