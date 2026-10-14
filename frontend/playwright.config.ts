import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/pretest",
  fullyParallel: true,
  use: { baseURL: "http://127.0.0.1:3000", headless: true },
  reporter: [["list"]],
  webServer: {
    command: "npm run dev", url: "http://127.0.0.1:3000", reuseExistingServer: !process.env.CI,
    env: { NEXT_TELEMETRY_DISABLED: "1", GHM_UI: "preflight" }, timeout: 60_000,
  },
});
