import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/demo", workers: 1, timeout: 60_000,
  use: { baseURL: "http://127.0.0.1:3016", headless: true, trace: "retain-on-failure" },
  reporter: [["list"]],
  webServer: [
    { command: "cd ../backend && .venv/bin/uvicorn tests.demo.server:app --host 127.0.0.1 --port 8016 --no-access-log", url: "http://127.0.0.1:8016/health", reuseExistingServer: false, env: { APP_ORIGIN: "http://127.0.0.1:3016" } },
    { command: "npm run dev -- --port 3016", url: "http://127.0.0.1:3016", reuseExistingServer: false, env: { GHM_UI: "demo", NEXT_TELEMETRY_DISABLED: "1", GHM_BROWSER_TEST: "main" }, timeout: 60_000 },
  ],
});
