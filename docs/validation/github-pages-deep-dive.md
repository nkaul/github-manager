# GitHub Manager — Deep dive publication

Date: October 13, 2026 (America/New_York).

**PASS — Drive-only page deployed and hosted playback verified.**

## Published page

- [Deep dive](https://nkaul.github.io/github-manager-demo/deep-dive/)
- [Demo repository](https://github.com/nkaul/github-manager-demo)
- Tested content commit: 8905a9d615747257a28316142c6ce45e33992b0f.
- Successful [Pages deployment 38500611445](https://github.com/nkaul/github-manager-demo/actions/runs/38500611445).

The new page shares the main demo’s header, zen logo, Material palette, rounded player cards, footer and motion preferences. The home page’s navigation links to Deep dive, and the new page links back to the full walkthrough.

## Recordings

1. **GitHub Manager - System Design Overview** — [original video](https://drive.google.com/file/d/1lFRi4GLv16iaH3W0ZwsYQBa_Xz60ZSHu/view?usp=drive_link), embedded with Google Drive’s video player. Observed duration: 521.822 seconds, about 8:42.
2. **GitHub Manager Architecture Deep Dive - Podcast** — [original audio](https://drive.google.com/file/d/12OINEhz3RTbcWQVZ9e-lW98J10fQWo-w/view?usp=sharing), embedded with Google Drive’s audio preview. Displayed duration: 21:23.

Both new recordings stay on Google Drive. No new video or audio payload was included in the published repository or its new commit history. Visible original Drive links provide an alternative if a browser cannot use the embedded players.

## Fresh local and hosted validation

| Check | Result |
|---|---|
| Public HTTPS route returns HTTP 200 | PASS |
| Exact requested section headings and correct Drive file IDs | PASS |
| Two correctly titled embedded players | PASS |
| Video streams in a signed-out Chromium context; playback time advances | PASS |
| Podcast streams without sign-in; elapsed time advances and play/pause works | PASS |
| Podcast play/pause controls work at 390-pixel phone width | PASS |
| Desktop 1440×1000 and phone 390×844 layouts have no horizontal overflow | PASS |
| Both original Drive links preserve the supplied URLs and safe new-tab behavior | PASS |
| Main-demo navigation works in both directions | PASS |
| Shared logo-motion preference and reduced-motion behavior | PASS |
| Main demo still loads all 32 chapters; representative chapter-17 seek | PASS |
| Internal page, script, stylesheet and branding links return HTTP 200 | PASS |
| JavaScript page errors in final local and hosted runs | 0 |
| New pushed history contains no media payload | PASS |

Google’s podcast preview has overlapping controls at narrow iframe widths. The page keeps the preview’s internal layout wide enough for its controls and scales the iframe to fit the card, without horizontal page scrolling. The original Drive link remains available. This was verified with the actual phone-width play/pause controls, not only a screenshot.

Validation covers installed Chromium, short streaming samples and responsive layouts. Full-duration subjective listening, physical mobile devices and Safari/WebKit were not tested. Google Drive supplies the player controls and media delivery.

## Preservation and maintenance

The original six published Cedar recording assets still match their recorded SHA-256 values. Earlier recordings, readiness reports, benchmarks and the live local application remain intact. No new OpenAI calls, allowance renewals, app-data operations or AWS changes were performed.

Updates use normal commits and pushes to main. The owner’s public Drive sharing permissions govern the two new recordings. The reporting-only follow-up commit adds this report and its README link; it does not change the tested players.

## Local publication decisions

Automatic approval review rejected an initial push containing a copied 41.3 MB podcast payload because the user had authorized linking/embedding but had not explicitly authorized public redistribution. That push did not execute. The user then explicitly selected **Use the Drive audio embed only**. The final implementation honors that choice.

The rejected unpublished commit was replaced locally before publication. The copied payload and its manifest were removed from the demo checkout and retained only in ignored local test storage. The outgoing commit history was checked to contain no new M4A, MP4 or WAV payload. The published source commit is 8905a9d, whose parent is the prior public release 7c6feb3; the rejected 6aa604f candidate was not pushed.

The native-player experiment and its original validation notes are retained separately under the ignored .tools/pages-publishing/native-candidate directory. It is not part of the site. Final Drive-only browser checks and snapshots are in .tools/pages-publishing/deep-dive-local-qa.json and deep-dive-hosted-qa.json, plus associated screenshots.

## Final release confirmation

Reporting commit `4db947fb1b2212e61bb0b52ab57fe56434cf550e` deployed successfully in [Pages run 38500953844](https://github.com/nkaul/github-manager-demo/actions/runs/38500953844). The final public page and completed report were rechecked. The demo repository working tree is clean, and the temporary publication preview server is stopped.
