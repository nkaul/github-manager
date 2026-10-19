import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/corpus", workers: 1, timeout: 60_000,
  outputDir: "./test-results-corpus",
  use: { baseURL: "http://127.0.0.1:3015", headless: true, viewport: { width: 1920, height: 1080 }, trace: "retain-on-failure" },
  reporter: [["list"]],
  webServer: [
    { command: "cd ../backend && .venv/bin/uvicorn tests.demo.corpus_server:app --host 127.0.0.1 --port 8015 --no-access-log", url: "http://127.0.0.1:8015/health", reuseExistingServer: false },
    { command: "npm run dev -- --port 3015", url: "http://127.0.0.1:3015", reuseExistingServer: false, env: { GHM_UI: "demo", NEXT_TELEMETRY_DISABLED: "1", GHM_CORPUS_UI_TEST: "1" }, timeout: 60_000 },
  ],
});
