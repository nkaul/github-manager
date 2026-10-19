# AI system design relocation — October 19, 2026

The complete `ai-system-design/` directory moved to
[`eval/ai-system-design/`](../ai-system-design/README.md). All 259 original files
are accounted for. Internal subdirectories retain their previous layout.

Live Markdown links, repository-relative script paths, animation asset loaders,
reproduction commands, and packaged skill references use the new location.
Script root discovery accounts for the additional `eval/` level. Generated
documentation templates also use the correct relative paths.

## Preserving historical evidence

Result JSON, recorded logs, source manifests, earlier preservation archives, and
image assets retain their original bytes. Their historical `ai-system-design/`
path strings intentionally remain as provenance. They describe the location at
the time of the original run, rather than a new evaluation.

[`manifest.json`](manifest.json) records the old and new paths and before/after
SHA-256 hashes. [`originals.zip`](originals.zip) retains the pre-move bytes of
every text file edited for this relocation. It contains documentation and source
files only, with no private corpus, credentials, or application database.

[`relocation_support.py`](relocation_support.py) translates historical paths for
active reproduction tools. Historical hash checks can read archived originals
only after confirming that the current file exactly matches its recorded
post-relocation hash. A subsequent edit cannot silently pass this check. Current
content hashes remain separate from historical hashes; frozen manifests are not
rewritten to accept changed evidence.

The corpus, human labels, saved API results, application SQLite data, monetary
ledger, and finished API allowance remain at their existing private paths. This
move makes no model calls or GitHub changes.

## Verification

Run from the repository root:

```sh
backend/.venv/bin/python eval/relocation/verify.py
backend/.venv/bin/python eval/ai-system-design/evaluation/reviewed-30-v1/runner.py freeze
backend/.venv/bin/python eval/ai-system-design/evaluation/reviewed-30-v1/walkthrough/verify_walkthrough.py \
  --output eval/relocation/walkthrough-verification.json
backend/.venv/bin/python eval/ai-system-design/ground-truth-creation/scripts/verify_package.py \
  --output eval/relocation/ground-truth-verification.json
```

The existing freeze is verified in place; it is not recreated. Separate output
paths preserve the earlier verification receipts. For Promptfoo, follow the
[updated replay instructions](../ai-system-design/evaluation/reviewed-30-v1/README.md),
which generate a separate configuration with the relocated provider path.

Validation completed after the move:

- All 259 original package files accounted for; 200 retain identical bytes and
  59 have documented path, link, or reproduction-tool updates.
- 655 original files outside the relocation edits retain identical bytes,
  including the user's existing `.gitignore` changes.
- The frozen evaluation reference verifies without recreating it.
- All 22 plain-language evaluation checks and all 18 ground-truth publication
  checks pass, with their new receipts saved separately.
- 30 existing offline tests pass: 4 evaluation tests, 12 original corpus tests,
  and 14 refreshed corpus tests. Figure-renderer JavaScript syntax also passes.
- Local link scanning introduces no broken Markdown targets. Seven missing
  local targets predate the move, including media already removed from this
  repository and historical preview/report artifacts.

Concurrent edits to the root `README.md` were preserved. The relocation archive
retains its earlier bytes, while the manifest records the current version;
those owner edits are separate from mechanical path updates.

[`verification.json`](verification.json) records file preservation and link
checks. Missing local targets that already existed before the move are listed
separately from any regression. Published demo-site copies are separate and
retain their existing deployment paths.
