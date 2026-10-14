# Animated Deep dive header link

Date: October 13, 2026 (America/New_York).

**PASS — published and verified locally and on GitHub Pages.**

Site: https://nkaul.github.io/github-manager-demo/

Commit: d500b27f15050980c013d3348c537509c1a23c61. Successful [Pages run 38501738983](https://github.com/nkaul/github-manager-demo/actions/runs/38501738983).

The main header’s Deep dive link now has a rounded blue/indigo treatment, a decorative architecture icon, a continuous four-second soft glow and a small arrow movement. Hover or keyboard focus pauses the motion. The footer’s Pause animations control stops both logo and header animation and preserves that preference; reduced-motion users receive the static highlighted link. Updated CSS/JS URLs refresh cached assets.

Fresh Chromium checks passed at 1440, 768, 650, 390 and 320 pixels without horizontal overflow. The visible header link opens Deep dive through keyboard navigation. Hover/focus pause, persistent motion controls and reduced-motion behavior passed. The main demo still loads its 32 chapter entries. No JavaScript page errors were recorded.

Only header styling, link markup and animation-control wording changed. Both Drive embeds, existing recordings and app/readiness work remain unchanged. No media payload or new model call was introduced. Browser checks/screenshots are retained in the ignored .tools/pages-publishing/header-cta-* files. Safari/WebKit was not tested for this refinement.
