import { expect, test } from "@playwright/test";

test("Markdown upload preserves reviewed text and feeds extraction", async ({ page }, testInfo) => {
  await page.goto("/");
  await page.getByLabel("Login name").fill("student1");
  await page.getByLabel("Password", { exact: true }).fill("browser-test-password-1");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  const importer = page.getByRole("form", { name: "Import a Markdown document" });
  const templateResponse = await page.request.get("/templates/idea-template.md");
  expect(templateResponse.ok()).toBeTruthy();
  expect(await templateResponse.text()).toContain("## Personal requirements");
  const download = page.waitForEvent("download");
  await importer.getByRole("link", { name: "Download Markdown template" }).click();
  expect((await download).suggestedFilename()).toBe("feedbackform-idea-template.md");
  const markdown = "# Offline decision workspace\r\n\r\n## Preferences\r\n- I want a web app, not a mobile app. 🦊\r\n\r\n## Personal requirements\r\n- Only if it works offline.\r\n\r\n## References\r\n<img src=x onerror=window.markdownExecuted=true>\r\n";
  await importer.getByLabel("Markdown file", { exact: true }).setInputFiles({
    name: "ai-brief.md", mimeType: "text/markdown", buffer: Buffer.from(markdown),
  });
  await expect(importer.getByLabel("Document title")).toHaveValue("Offline decision workspace");
  const preview = importer.getByLabel("Markdown preview");
  await expect(preview).toHaveValue(markdown.replaceAll("\r\n", "\n"));
  const save = importer.getByRole("button", { name: "Import reviewed Markdown" });
  await expect(save).toBeDisabled();
  await importer.getByRole("checkbox").check();
  // Failed saves retain the preview and review state, so the participant can retry.
  await page.route("**/api/workspaces/*/ideas", async route => {
    if (route.request().method() === "POST") await route.fulfill({ status: 503,
      json: { detail: "Import temporarily unavailable" } });
    else await route.continue();
  });
  await save.click();
  await expect(importer.getByRole("alert")).toContainText("Import temporarily unavailable");
  await expect(preview).toHaveValue(markdown.replaceAll("\r\n", "\n"));
  await page.unroute("**/api/workspaces/*/ideas");
  await save.click();
  await expect(importer.getByRole("status")).toContainText("Markdown imported");
  const idea = page.locator("article[data-idea-id]").filter({ hasText: "Offline decision workspace" });
  await expect(idea).toHaveCount(1);
  await expect(idea.locator(".markdown-body").getByRole("heading", { name: "Preferences", exact: true })).toBeVisible();
  await expect(idea.locator(".markdown-body ul")).toHaveCount(2);
  await expect(idea.locator(".idea-meta")).toContainText("Student 1");
  expect(await page.evaluate(() => "markdownExecuted" in window)).toBe(false);
  await expect(idea.locator("img")).toHaveCount(0);
  await page.reload();
  const workspaces = await (await page.request.get("/api/workspaces")).json();
  const ideas = await (await page.request.get(`/api/workspaces/${workspaces[0].id}/ideas`)).json();
  expect(ideas.find((row: { title: string }) => row.title === "Offline decision workspace").body).toBe(markdown);
  const board = page.getByRole("region", { name: "Understand everyone’s priorities" });
  await board.getByRole("button", { name: "Extract preferences from new feedback" }).click();
  await expect(board.getByText("Extraction completed.", { exact: false })).toBeVisible();
  const extracted = board.locator(".preference-card").filter({ hasText: "## Personal requirements" });
  await expect(extracted).toHaveCount(1);
  await extracted.getByText("Inspect original evidence", { exact: true }).click();
  await expect(extracted.getByText("Original idea", { exact: true })).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath("markdown-import.png"), fullPage: true });
});

test("formatted Markdown preserves source offsets and rejects active content", async ({ page }, testInfo) => {
  await page.goto("/");
  await page.getByLabel("Login name").fill("student1");
  await page.getByLabel("Password", { exact: true }).fill("browser-test-password-1");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  const title = `Formatted idea ${Date.now()}`;
  await expect(page.getByRole("heading", { name: "Our project", exact: true })).toBeVisible();
  const source = `# ${title}\r\n\r\n## Priorities\r\n- 😀 First **repeat**; second **repeat**.\r\n- *Emphasis* and \`inline code\`.\r\n\r\n| Option | Priority |\r\n| --- | --- |\r\n| Web | High |\r\n\r\n~~~js\r\nconst ready = true;\r\n~~~\r\n\r\n[Reference](https://example.com) [Unsafe](javascript:alert(1))\r\n\r\n<img src=x onerror=window.markdownExecuted=true>\r\n`;
  const auth = await (await page.request.get("/api/auth/me")).json();
  const workspaces = await (await page.request.get("/api/workspaces")).json();
  const result = await page.request.post(`/api/workspaces/${workspaces[0].id}/ideas`, {
    headers: { Origin: "http://127.0.0.1:3100", "X-FeedbackForm-Request": "1", "X-CSRF-Token": auth.csrf_token },
    data: { title, body: source },
  });
  expect(result.status()).toBe(201);
  const idea = await result.json();
  await page.reload();
  const card = page.locator(`article[data-idea-id="${idea.id}"]`);
  const rendered = card.locator(".markdown-body");
  await expect(rendered.getByRole("heading", { name: "Priorities", exact: true })).toBeVisible();
  await expect(rendered.locator("strong")).toHaveCount(2);
  await expect(rendered.locator("em")).toHaveText("Emphasis");
  await expect(rendered.getByRole("table")).toContainText("High");
  await expect(rendered.locator("pre code")).toHaveText("const ready = true;");
  await expect(rendered.getByRole("link", { name: "Reference" })).toHaveAttribute("href", "https://example.com/");
  await expect(rendered.getByRole("link", { name: "Unsafe" })).toHaveCount(0);
  await expect(rendered.locator("img, script")).toHaveCount(0);
  expect(await page.evaluate(() => "markdownExecuted" in window)).toBe(false);
  await rendered.locator("strong").last().evaluate(element => {
    const text = element.querySelector("span")!.firstChild!;
    const range = document.createRange(); range.selectNodeContents(text);
    const selection = window.getSelection()!; selection.removeAllRanges(); selection.addRange(range);
    element.dispatchEvent(new MouseEvent("mouseup", { bubbles: true }));
  });
  await card.getByRole("button", { name: "Comment on selected passage", exact: true }).click();
  await card.getByLabel("Your comment").fill("Review this formatted passage.");
  await card.getByRole("button", { name: "Save comment", exact: true }).click();
  await expect(card.getByText("Your comment was saved.", { exact: true })).toBeVisible();
  const comments = await (await page.request.get(`/api/workspaces/${workspaces[0].id}/ideas/${idea.id}/annotations`)).json();
  expect(comments[0].span.quote).toBe("repeat");
  expect(comments[0].span.start_utf16).toBe(source.lastIndexOf("repeat"));
  await page.reload();
  await expect(rendered.locator("strong mark")).toHaveText("repeat");
  await card.getByRole("button", { name: "Show Markdown source", exact: true }).click();
  await expect(card.locator(".markdown-source")).toHaveText(source);
  await card.getByRole("button", { name: "Show formatted Markdown", exact: true }).click();
  await expect(rendered.getByRole("heading", { name: "Priorities", exact: true })).toBeVisible();
  await card.screenshot({ path: testInfo.outputPath("formatted-markdown.png") });
});

test("Markdown preview rejects invalid files and requires review after changes", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Login name").fill("student1");
  await page.getByLabel("Password", { exact: true }).fill("browser-test-password-1");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  const importer = page.getByRole("form", { name: "Import a Markdown document" });
  const file = importer.getByLabel("Markdown file", { exact: true });
  for (const [name, bytes, error] of [
    ["brief.pdf", Buffer.from("not markdown"), "ending in .md"],
    ["empty.md", Buffer.from(" \n"), "empty"],
    ["invalid.md", Buffer.from([0xff, 0xfe]), "UTF-8"],
    ["large.md", Buffer.from("a".repeat(20_001)), "20,000"],
    ["huge.md", Buffer.from("a".repeat(80_001)), "too large"],
  ] as const) {
    await file.setInputFiles({ name, mimeType: "text/plain", buffer: bytes });
    await expect(importer.getByRole("alert")).toContainText(error);
    await expect(importer.getByLabel("Markdown preview")).toHaveCount(0);
  }
  await file.setInputFiles({ name: "notes.markdown", mimeType: "text/plain", buffer: Buffer.from("I want offline support.") });
  await expect(importer.getByLabel("Document title")).toHaveValue("notes");
  await importer.getByRole("checkbox").check();
  await importer.getByLabel("Markdown preview").fill("I want offline support, if feasible.");
  await expect(importer.getByRole("checkbox")).not.toBeChecked();
  await expect(importer.getByRole("button", { name: "Import reviewed Markdown" })).toBeDisabled();
  await importer.getByRole("button", { name: "Cancel import" }).click();
  await expect(importer.getByLabel("Markdown preview")).toHaveCount(0);
});

test("extract, inspect, correct, and withdraw an interpretation through the real API", async ({ page }, testInfo) => {
  await page.goto("/");
  await page.getByLabel("Login name").fill("student1");
  await page.getByLabel("Password", { exact: true }).fill("browser-test-password-1");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  const board = page.getByRole("region", { name: "Understand everyone’s priorities" });
  await expect(board).toBeVisible();
  const source = `Vision ${Date.now()}: I want a web app, not a mobile-only project.`;
  await page.getByLabel("Your idea", { exact: true }).fill(source);
  await page.getByRole("button", { name: "Share idea", exact: true }).click();
  await expect(page.getByText("Your idea was saved.", { exact: true })).toBeVisible();
  await board.getByRole("button", { name: "Extract preferences from new feedback" }).click();
  await expect(board.getByText("Extraction completed.", { exact: false })).toBeVisible();
  const card = board.locator(".preference-card").filter({ hasText: source });
  await expect(card).toHaveCount(1);
  await card.getByText("Inspect original evidence", { exact: true }).click();
  await expect(card.getByText(source, { exact: true }).first()).toBeVisible();
  await card.getByLabel("What you mean").fill("I want a web app with offline support.");
  await card.getByLabel("Personal priority").selectOption("important");
  await card.getByRole("button", { name: "Save correction" }).click();
  await expect(card.locator(".preference-meta")).toContainText("corrected");
  await page.reload();
  await expect(card.getByLabel("What you mean")).toHaveValue("I want a web app with offline support.");
  await card.getByRole("button", { name: "View interpretation history" }).click();
  await expect(card.locator(".history")).toContainText("I prefer a mobile-only project.");
  await expect(card.locator(".history")).toContainText("I want a web app with offline support.");
  const other = board.locator(".preference-card").filter({ hasText: "Student 2" }).first();
  await expect(other).toBeVisible();
  await expect(other.getByRole("button", { name: "Save correction" })).toHaveCount(0);
  await page.screenshot({ path: testInfo.outputPath("preference-review.png"), fullPage: true });
  await card.getByRole("button", { name: "Withdraw interpretation" }).click();
  await expect(card.locator(".preference-meta")).toContainText("withdrawn");
  await expect(card.getByLabel("What you mean")).toHaveCount(0);
  await expect(page.locator("article[data-idea-id]").filter({ hasText: source })).toHaveCount(1);
});

test("missing OpenAI configuration is visible in the workspace", async ({ page }) => {
  await page.route("**/api/workspaces/*/preferences", async route => {
    const response = await route.fetch();
    const body = await response.json();
    await route.fulfill({ response, json: { ...body, configured: false } });
  });
  await page.goto("/");
  await page.getByLabel("Login name").fill("student1");
  await page.getByLabel("Password", { exact: true }).fill("browser-test-password-1");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  const board = page.getByRole("region", { name: "Understand everyone’s priorities" });
  await expect(board.getByText("OpenAI connection needed.", { exact: false })).toBeVisible();
  await expect(board.getByRole("button", { name: "Extract preferences from new feedback" })).toBeDisabled();
});
