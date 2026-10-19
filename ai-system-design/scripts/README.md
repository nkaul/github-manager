# Reproduction scripts

Run from the `github-manager` repository root, using its existing tools. No installation, API key, network call, AWS action or live app mutation is required. Do not use the paid benchmark runner to reproduce article arithmetic.

```bash
backend/.venv/bin/python ai-system-design/scripts/audit_evidence.py
backend/.venv/bin/python ai-system-design/scripts/draw_figures.py
PLAYWRIGHT_BROWSERS_PATH="$PWD/.tools/playwright" \
  .tools/node/bin/node ai-system-design/scripts/render_figures.cjs
backend/.venv/bin/python ai-system-design/scripts/verify_package.py
```

- `audit_evidence.py` reads only the existing frozen `offline.local.json` and `validation-round-2.local.json` public/synthetic experiment records, plus source/report files. It emits aggregate JSON, source hashes and the evidence index. It never imports provider settings or reads `.env`. The original ignored experiment records are required locally; they are not redistributed in the article package.
- `draw_figures.py` uses Python's standard library to generate eight exact-label SVGs. No raster-generation service or additional package is needed.
- `render_figures.cjs` uses the already installed Playwright Chromium, blocks HTTP/HTTPS, checks SVG text containment, then emits 2× PNGs and a layout audit. The browser needs ordinary local process-launch permissions; a restrictive sandbox may require approving that local render command. It does not connect to the running application or a signed-in browser.
- `verify_package.py` checks relative links, heading/figure structure, data arithmetic, PNG sizes, source/benchmark preservation and obvious accidental secret/artifact inclusion. It writes `verification.json` within this folder only. It is a publication-package check, not another app-quality benchmark.

Read the [article's reproduction limits](../github-manager-ai-system-design.md#19-threats-to-validity-and-publication-boundaries) before interpreting these scripts as full historical provider reproducibility.
