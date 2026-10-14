# GitHub Manager — public demo site on GitHub Pages

Date: October 13, 2026 (America/New_York).

Status: **APPROVED AND PUBLISHED.** The user approved execution and public release after creating and cloning the separate demo repository. The application runtime and cloud deployment remain deferred. See the [publication results](../validation/github-pages-demo-publication.md).

## 1. Agreed scope and proposed destination

The user requested a GitHub Pages site for the demo page and recordings, then specified a new GitHub repository with a local clone under `repos`. The user selected **demo site and recordings only**, accepting the proposed repository name and separate local directory.

| Item | Proposed value |
|---|---|
| GitHub owner | `nkaul` |
| New repository | `nkaul/github-manager-demo` |
| Visibility | Public, subject to release approval |
| Local clone | `/Users/nkaul/Documents/repos/github-manager-demo` |
| Expected site URL | `https://nkaul.github.io/github-manager-demo/` |
| Publishing source | `main`, repository root (`/`), with `.nojekyll` |
| Primary recording | Full Cedar · Option D, calmer delivery walkthrough |

This is a project site, so its repository name appears in the URL. The existing app repository is `nkaul/github-manager`; the new demo repository has its own URL and history. The existing local `github-manager` directory will remain the source of the approved media and historical evidence.

## 2. Findings and design alignment

- The local app checkout is on `develop`, with an initial tracked commit and substantial uncommitted/untracked application, documentation and testing work. Publishing must use the fresh sibling clone and explicitly selected files; staging the application checkout wholesale would exceed this task's scope.
- A public GitHub API read confirmed that `nkaul/github-manager` exists, is public, has default branch `main`, and has no Pages site. An unauthenticated lookup of `nkaul/github-manager-demo` returned 404. That does not rule out a private repository using the name; availability must be confirmed while signed in before creation.
- `demo/full-v2/index.html` already provides a buildless player, 32 chapter buttons, fullscreen, captions, audio-only playback and downloads. Its relative paths are suitable for adaptation to a project subpath.
- The full recording is 24:12, 1920×1080, H.264/AAC. Existing local evidence records 117 feature assertions, 390 caption cues, all 32 chapter seeks and responsive playback checks. These are historical local results; hosted playback needs a new validation report.
- The player currently links raw feature/cost audits and local recording notes. The public copy needs curated notes, minimal chapter data and a public verification summary instead of copying that directory wholesale.
- The original video is **62,568,111 bytes / 59.67 MiB** and the narration is **25,125,762 bytes / 23.96 MiB**. Captions, chapters, transcript, poster and branding add little to the roughly 84 MiB initial package.
- Git and its macOS keychain credential helper are available. The GitHub CLI was not found in the checked locations. Repository administration and authenticated Git write access have not been verified; the proposed browser-plus-Git path does not require a CLI installation.

The approved architecture uses a Next.js/FastAPI application, with a local SQLite adapter for Phase 0.9 and later DynamoDB/SQS deployment. GitHub Pages serves static content and cannot run the Python API. This site therefore demonstrates the completed local app through recordings and explanatory content. Visitors will not sign into the application or invoke GitHub/OpenAI from the site. No OAuth callback, API key, database, AWS resource or production application architecture change is needed. See [Pages static hosting](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site) and the [approved local-demo boundary](phase-0-9-functional-demo.md).

## 3. Visitor experience

1. A clear GitHub Manager introduction using the approved zen-cat branding and balanced Material purple, indigo and blue palette. State that this is a recorded walkthrough of the local MVP.
2. A prominent full-demo player with duration, Cedar narration disclosure, fullscreen and English captions.
3. The complete 32-chapter feature navigator, with shareable chapter links and responsive phone layout. Playback starts on user action; loading the page should not download the full video eagerly.
4. A concise explanation of repository discovery, four taxonomy facets, AI review, persistent analysis, manual/bulk/drag-and-drop assignments, budget controls, reanalysis, automatic organization and selective reset. Link these descriptions to the relevant chapters.
5. Download links for the 1080p video, narration, VTT/SRT and a readable transcript.
6. Public recording notes and a dated verification summary explaining real-account footage, copy-only edits/resets, bounded public-model tests and deferred cloud runtime. Local results and new hosted results remain distinguishable.

The initial release publishes the completed Cedar walkthrough and its companion audio. Earlier robotic narration and voice auditions remain preserved locally; they are not automatically added to the public archive. Future approved recordings can receive their own versioned folders and cards.

## 4. Public package and preservation

Proposed layout in the **new clone**:

```text
github-manager-demo/
  .nojekyll
  .gitignore
  README.md
  index.html
  assets/branding/...
  recordings/cedar-v2/
    github-manager-full-cedar-calm-1080p.mp4
    github-manager-full-cedar-calm.m4a
    poster.jpg
    chapters.json
    full-demo.vtt
    full-demo.srt
    transcript.md
    transcript.html
    recording-notes.html
    verification.json
  docs/publication-report.md
```

Copy the video, audio, poster, caption and transcript assets without regenerating or re-encoding them; record matching SHA-256 hashes. Generate the public `chapters.json` from only chapter ID, title, start and end. Generate public verification data from explicitly selected media facts and check summaries. Do not copy embedded raw assertion objects merely because they are in the original chapter JSON.

Keep the app source, `.env` files, SQLite databases, sessions, raw footage, recording tools, intermediate audio, private validation directories, detailed provider request/cost ledgers and internal timing/preservation audits in the existing workspace. They are outside the new repository and public deployment package. Public captions/transcript remain faithful to the approved recording.

The original media, demo pages, Phase 0/0.5 reports, benchmarks, readiness evidence and app state stay intact. Append a public-site entry to `demo-video.md` after successful publication; do not rewrite historical outcomes. No new model calls, AI allowance renewal, AWS operations or source-app deployment are part of this plan.

## 5. Dependency-ordered execution

### A — Release approval and account access (small)

Obtain approval for the concrete public package described here, including the existing unmasked video. Confirm an authenticated `nkaul` browser session and Git write access through an approved local credential flow. Do not extract or reuse the application's OAuth token for publishing. Never ask for credentials in chat.

Create the **public, empty** `nkaul/github-manager-demo` repository and clone it to the proposed sibling directory. Verify the remote and empty destination before copying anything. If the name is occupied or the local path exists, inspect and report that conflict without overwriting it or silently choosing another owner/name.

Acceptance: correct owner, confirmed repository permissions, new clone with the correct remote, and no modification to the original app checkout or remote.

### B — Prepare the static site locally (medium)

Adapt the existing player and approved branding in the new clone. Add the introduction, feature links, accessible transcript, public notes and minimal verification data. Fix the existing chapter-link initialization race so a direct chapter URL works whether metadata loads before or after chapter JSON. Use project-relative asset paths throughout.

Use an explicit file manifest to copy approved media and record sizes/hashes. Inspect the staged file list and scan text/config assets for credentials, local-only URLs and unintended raw account reports. The approved footage itself remains unmasked.

Acceptance: a complete local preview served under `/github-manager-demo/`, working downloads and chapter links, readable desktop/phone layout, and a manifest containing only intended public files. Record any defect before committing. Existing recording quality reports are reused honestly rather than presented as new tests.

### C — Commit, push and enable Pages (small)

Commit only the new demo repository's reviewed files and push `main`. Configure **Settings → Pages → Deploy from a branch → main → /(root)**. Include `.nojekyll`; do not add a custom workflow unless an observed requirement justifies one. GitHub's branch publishing path is sufficient for this buildless site and still uses GitHub's deployment machinery. See [publishing-source configuration](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

The video exceeds Git's 50 MiB warning threshold but is below the 100 MiB blocking threshold; upload it through Git rather than the browser's 25 MiB file-upload form. Do not use Git LFS: GitHub documents that LFS cannot be used with Pages sites. See [file limits](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github) and [LFS restrictions](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage).

Acceptance: successful Git push and Pages deployment, correct expected URL, and HTTPS availability. No custom domain or DNS work is required. Set the new repository's website field to the confirmed public URL.

### D — Verify the deployed site and document handoff (medium)

- Check the project URL, every linked asset and media MIME type over HTTPS; ensure no localhost dependencies or browser errors.
- Check HTTP byte-range behavior and seeking on the hosted MP4, then exercise all 32 chapter buttons and direct chapter links. A local HTTP 206 result does not establish hosted range support.
- Verify captions, fullscreen, video/audio exclusivity, downloads and transcript links.
- Check responsive desktop and phone layouts, keyboard operation, visible focus, text contrast and reduced-motion branding.
- Use the installed Chromium browser for automation and inspect Safari/WebKit playback if the existing environment supports it; otherwise record that browser coverage limit.
- Save commit/deployment identifiers, tested URL, package hashes/sizes, actual results and limitations in Markdown: `docs/publication-report.md` in the demo repository, plus `docs/validation/github-pages-demo-publication.md` in the app workspace.

If media seeking or delivery fails, record the failure and resolve it before calling the site complete. GitHub Releases or external video/CDN hosting is a possible follow-up, requiring agreement on that changed delivery approach; it is not silently introduced. Acceptance: the public page is usable from a signed-out browser and the hosted validation report accurately records what passed.

After approval, A–D form one publishing task. Routine local fixes and checks continue within that scope. A required GitHub sign-in is the only expected user-operated step.

## 6. Capacity and future updates

The initial package is comfortably below the 1 GB published-site limit. GitHub Pages has a soft 100 GB monthly bandwidth limit, so this is appropriate for initial MVP review, with delivery reassessed if traffic grows. Avoid retaining many large revisions in the active site without checking cumulative size and Git history growth. See [Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).

The public repository works with GitHub Free; no paid plan is required for this proposed setup. A private source repository would have different plan requirements and would not itself make the Pages site private. See [repository and site visibility](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

Updates use normal new commits and the same publishing branch. For rollback, revert the site change and republish the previous working version; keep original local artifacts and reports. Removing a public site later cannot retract copies already downloaded by others.

## 7. Permissions and user actions

**Approval requested:** create the new public repository under `nkaul`, clone it to the specified local path, prepare and push the demo-only files, enable Pages, set its website URL, and publicly release the existing unmasked Cedar video plus companion audio, captions, transcript and poster.

The recording shows the real account and private-repository names/metadata. The previous instruction allowing unmasked recording covered demo creation; this request asks separately for internet publication of that concrete recording. Review it in the [current local player](http://127.0.0.1:8123) or [original guide](../../demo-video.md).

**Possible user step:** sign into GitHub in the publishing browser if needed. If the macOS Git credential does not permit pushes, complete a browser/device-based Git authentication flow. A tool installation or different credential method will be proposed only if actually needed. No API key, OAuth App registration, AWS credentials, domain purchase or DNS change is required.

Repository creation and Pages configuration need the owning account or suitable repository administration permission. If the account cannot perform those actions, the exact missing role/action will be reported; signing into the local GitHub Manager application is not proof of publishing permission.

## 8. Plan readiness

| Gate | State |
|---|---|
| Demo-only scope, new repository and sibling clone | Confirmed by user |
| Existing static player/media and preservation strategy | Ready |
| GitHub Pages/static compatibility and initial size | Ready, based on current official documentation |
| Target name availability and authenticated Git writes | PASS — user-created clone and push/admin permissions verified |
| Public release of unmasked account footage | Approved with the publishing plan |
| Hosted playback, range requests and deployed report | PASS — 32 seeks, HTTP 206, 1080p, captions, downloads and responsive layouts |

At the original planning checkpoint, this document was the only new deliverable and nothing had been created, pushed or published. The user subsequently created/cloned the new repository and approved this publishing plan.

## 9. Execution record

Published at **https://nkaul.github.io/github-manager-demo/** from the user-created sibling clone. Content commit 2217dbccf83815447ece9f1976b8e2a9c90f2b6f deployed successfully; a subsequent reporting-only commit records fresh hosted checks. Original demo media and readiness evidence are preserved. No additional sign-in, OpenAI calls or AWS work was required. Detailed results and limitations are in the linked publication report.
