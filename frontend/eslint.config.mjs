import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";
export default defineConfig([...nextVitals, ...nextTs, globalIgnores([".next/**", ".next-corpus/**", ".next-main-test/**", "next-env.d.ts", "playwright-report/**", "test-results/**", "test-results-corpus/**"])]);
