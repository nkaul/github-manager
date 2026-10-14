import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/demo", workers: 1, timeout: 60_000,
  use: { baseURL: "http://127.0.0.1:3000", headless: true, trace: "retain-on-failure" },
  reporter: [["list"]],
  webServer: [
    { command: "cd ../backend && .venv/bin/uvicorn tests.demo.server:app --host 127.0.0.1 --port 8000 --no-access-log", url: "http://127.0.0.1:8000/health", reuseExistingServer: false },
    { command: "npm run dev", url: "http://127.0.0.1:3000", reuseExistingServer: false, env: { GHM_UI: "demo", NEXT_TELEMETRY_DISABLED: "1" }, timeout: 60_000 },
  ],
});
