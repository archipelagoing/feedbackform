import { defineConfig } from "@playwright/test";
import { randomUUID } from "node:crypto";

const databaseUrl = `sqlite:///./data/e2e-${randomUUID()}.db`;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  retries: 0,
  projects: [
    { name: "setup", testMatch: /onboarding\.setup\.ts/ },
    { name: "chromium", testMatch: /.*\.spec\.ts/, testIgnore: /preferences\.spec\.ts/, dependencies: ["setup"] },
    { name: "preferences", testMatch: /preferences\.spec\.ts/, dependencies: ["chromium"] },
  ],
  use: { baseURL: "http://127.0.0.1:3100", browserName: "chromium" },
  webServer: [
    {
      command: "cd ../backend && .venv/bin/alembic upgrade head && .venv/bin/uvicorn tests.e2e_app:app --host 127.0.0.1 --port 18080",
      env: { FEEDBACKFORM_DATABASE_URL: databaseUrl, FEEDBACKFORM_ALLOWED_ORIGINS: "http://127.0.0.1:3100", FEEDBACKFORM_SECURE_COOKIES: "0" },
      url: "http://127.0.0.1:18080/api/health",
      reuseExistingServer: false,
      timeout: 60_000,
    },
    {
      command: "npm run build && npm run start -- --port 3100",
      env: { FEEDBACKFORM_API_ORIGIN: "http://127.0.0.1:18080", NEXT_TELEMETRY_DISABLED: "1" },
      url: "http://127.0.0.1:3100",
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});
