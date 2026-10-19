import type { NextConfig } from "next";

const config: NextConfig = {
  // Isolate corpus browser QA from the user's running local application.
  distDir: process.env.GHM_BROWSER_TEST === "main" ? ".next-main-test" : process.env.GHM_CORPUS_UI_TEST === "1" ? ".next-corpus" : ".next",
  logging: { incomingRequests: { ignore: [/\/api\/v1\/auth\/github\/callback/] }, browserToTerminal: false },
  async headers() {
    return [{ source: "/:path*", headers: [
      { key: "Referrer-Policy", value: "no-referrer" },
      { key: "X-Content-Type-Options", value: "nosniff" },
      { key: "X-Frame-Options", value: "DENY" },
    ] }];
  },
};
export default config;
