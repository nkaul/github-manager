# GitHub Manager: deleted-video push repair

Date: October 19, 2026. Agent: **GitHub Deployer**. Status: **resolved; normal push succeeded and the published branch was verified**.

The repaired commits are now on [GitHub Manager's `develop` branch](https://github.com/nkaul/github-manager/tree/develop), at [commit `3366671`](https://github.com/nkaul/github-manager/commit/3366671984cedf5180a2eddd0c26dc967977b639). All final committed files are identical to the original local tip. The oversized video no longer occurs anywhere in the published branch's reachable history, and the original history is backed up locally.

## What was wrong

The `develop` branch of `https://github.com/nkaul/github-manager.git` had two local commits that had not reached GitHub. The first commit added `demo/article-animation-full/complete-1080p.mp4`; the second deleted it. Deleting the current file did not remove the earlier committed copy, so Git would still send that copy when pushing both commits.

The earlier copy was **125,108,234 bytes (119.3 MiB)**, above GitHub's 100 MiB ordinary-Git file limit. This was the only outgoing blob above that limit. This diagnosis follows the actual local object inventory; an original failed-push log was not available. [GitHub documents the limit and why a later deletion alone does not fix the unpushed history.](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)

## Exactly what changed

Only the reference to that obsolete video was removed from the earlier, unpublished commit. The second commit was recreated with the same final file tree and the repaired parent. Author, committer, timestamps and commit messages were preserved byte for byte.

| Item | Before | After |
|---|---|---|
| First local commit | `b165c201e79a97d1ed149d4b38491123bf1c58e5` | `e9ccb5fb602112e2e5d9b69b7f449e27703576ed` |
| Local branch tip | `e90462fe9f3d32aa212cad231e8d35370d1e102d` | `3366671984cedf5180a2eddd0c26dc967977b639` |
| First commit's file count | 903 | 902: only the obsolete video reference removed |
| Final commit's file count | 901 | 901, every path/mode/content unchanged |
| Final file-tree ID | `b43081cd93dc62984b7371fddebdb5fa695df451` | **Identical** |
| Largest outgoing file object | 125,108,234 bytes | 37,564,225 bytes |

The smaller `overview-slower-1080p.mp4` that the user also deleted was left in the earlier history. It is within the limit; removing it from history was unnecessary. Its deletion in the final commit remains intact.

No working file was deleted by this repair. No checkout, reset, clean, stash, staging operation, force-push, or application-code edit was used. The separate `github-manager-demo` repository and its published media were not changed.

## Verification at each step

| Step | Evidence and result |
|---|---|
| Identify the intended destination | Existing upstream is `origin/develop` in `nkaul/github-manager`, not the separate demo repository. |
| Check actual published history | Remote `develop` was `3ffac3f1ed6618b80045c3ffafc050f50d102d10`. Fetched remote `main` was `44ddb8cca08cf1c6ed51f160964d4d6e3108b387`. Neither local commit was an ancestor of either remote branch tip. |
| Inventory outgoing objects | Blocking blob: `5a7d48dfe79b0162380e413ac9ac64e14fd39f53`, 125,108,234 bytes. The repaired range has 572 blobs, none above 100 MiB. |
| Back up before repair | Two local backup refs and a complete-history bundle were created. `git bundle verify` passed and reported complete history. Details below. |
| Build repair independently | New Git tree/commit objects were prepared without changing a branch, the normal Git index or any working file. |
| Compare the historical tree | Old/new first-commit tree comparison contains exactly one deletion: the obsolete video path. Every other historical path, mode and blob ID matches. |
| Compare the final tree | Old/new tip trees are identical. All 901 final committed paths, modes and contents are preserved. |
| Move the local branch safely | An atomic `git update-ref` required the old tip still to equal the expected `e90462f`. It moved only the `develop` reference. |
| Verify the real index | SHA-256 before and after the ref update: `862fc49f16e581f889a72a7b7710e1f1ad1ca59b6d4c234a10ef2692de0aa792`. Identical. |
| Verify local files | All 912 tracked/untracked files in the immediate before/after snapshots were identical. Four additional evaluation artifacts appeared after the initial 908-file baseline, all under the active evaluation subtree and produced by the concurrent documentation task; none was lost or changed by the repair. Ignored runtime/private directories were not modified by any repair operation. |
| Check for unintended credential additions | Repair creates no new file-content blobs. A basic scan of 428 outgoing text blobs for credential-shaped values found only four false positives inside `task-...` document-link anchors. `backend/.env` remains ignored; the only tracked environment file is the configuration template. This is a focused check, not a comprehensive security audit. |
| Rehearse the push | Explicit `develop`-only normal push dry-run passed: `3ffac3f..3366671`. No backup refs or tags selected. |
| Publish and verify | Normal push exited 0: `3ffac3f..3366671`, `Done`. A separate `git ls-remote --heads origin` reported remote `develop` as `3366671984cedf5180a2eddd0c26dc967977b639`; remote `main` remained `44ddb8c`. An explicit post-push fetch of `develop` returned that exact commit and the unchanged final tree `b43081c`. The blocking blob is absent from `git rev-list --objects origin/develop`. |

The separate documentation task was actively adding/editing `ai-system-design/evaluation/reviewed-30-v1/`. Those changes were neither staged nor committed nor included in this push. Their presence after the push is expected.

After the remote verification, `git status --short --branch` reported `develop...origin/develop` with no ahead/behind count. The original index hash was still unchanged. Every original file outside the active evaluation subtree still matched its baseline. The only additional file outside that subtree was this intentionally created audit report. This report is saved locally for review and was not bundled into the already approved two-commit push.

## Backups and recovery

The original commits, including the old video, remain recoverable locally:

- Original branch-tip backup: `refs/backup/github-deployer/2026-10-19/develop-before` → `e90462fe9f3d32aa212cad231e8d35370d1e102d`.
- Original remote-base backup: `refs/backup/github-deployer/2026-10-19/origin-develop-before` → `3ffac3f1ed6618b80045c3ffafc050f50d102d10`.
- Independent bundle: `/Users/nkaul/Documents/repos/.github-manager-history-backups/2026-10-19/github-manager-before.bundle`.
- Bundle size: **379,335,418 bytes**.
- Bundle SHA-256: `8c8e5f60445ff8161c9121409a19663337c5daf4451fd9a6ddc0e66f73ca494f`.
- Local audit artifacts, file-hash manifests and the object-only preparation script are beside the bundle. This backup directory is private to the local user.

The machine-readable checkpoints are `baseline.json`, `baseline-files.json`, `prepared-repair.json`, `applied-repair.json`, `after-files.json` and `published-verification.json` in that directory. Together they record the before/after refs, immutable tree IDs, file hashes, allowed concurrent documentation edits and the successful remote verification.

To inspect or recover the old history without touching the active app checkout, clone the bundle to a **new** recovery directory and inspect the old commit there:

```bash
git clone --no-checkout \
  /Users/nkaul/Documents/repos/.github-manager-history-backups/2026-10-19/github-manager-before.bundle \
  /Users/nkaul/Documents/repos/github-manager-recovery-2026-10-19
git -C /Users/nkaul/Documents/repos/github-manager-recovery-2026-10-19 \
  show --stat e90462fe9f3d32aa212cad231e8d35370d1e102d
```

These are recovery instructions, not commands executed against the user's active checkout. Do not mirror-push the backup refs: they intentionally retain the oversized historical video. Recover any needed file in a separate directory, then review its use in an ordinary new commit. Do not rewind or force-push the published branch to the unrepaired history.

## Push command

The operation targets the existing `develop` branch explicitly and uses no force flag:

```bash
git -c push.followTags=false push --porcelain origin \
  refs/heads/develop:refs/heads/develop
```

The repair retains the application, benchmarks, evaluation history, diagrams, smaller recordings and all other previously committed files. The user-deleted full video remains absent from the final application tree, while its original bytes remain in the local backup.
