import { defineConfig } from "@playwright/test";
import previous from "./playwright.config";

export default defineConfig({
  ...previous,
  webServer: [
    { command: "cd ../backend && .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log", url: "http://127.0.0.1:8000/health", reuseExistingServer: false },
    { command: "npm run dev", url: "http://127.0.0.1:3000", reuseExistingServer: false,
      env: { NEXT_TELEMETRY_DISABLED: "1", GHM_UI: "preflight" }, timeout: 60_000 },
  ],
});
