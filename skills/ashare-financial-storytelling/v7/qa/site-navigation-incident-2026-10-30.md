# Company Report Routing Incident — 2026-10-30

## Symptom and official Cloudflare explanation
Users click a company card on the Pages homepage and are shown the homepage rather than a company's report. Cloudflare Pages documents that when no top-level `404.html` exists, unmatched static routes are treated as SPA routes and the root HTML is served. Reference: https://developers.cloudflare.com/pages/configuration/serving-pages/

**Root cause status: plausible / not fully confirmed.** Nested report files exist on GitHub but the live Cloudflare Pages deployment cannot be fetched in the current environment; therefore it is not yet possible to determine whether the deployment omits nested assets, the project points at the wrong repository/branch/output directory, or whether there are Cloudflare redirects.

## Source verified
- `public/index.html` is the independent website homepage.
- `public/300394/2026-H1/index.html` exists.
- `public/preview/300308/2026-H1-research-v7/index.html` exists.
- `public/300502/2026-H1/index.html` exists.
- No top-level `public/404.html`, `public/_redirects`, `wrangler.*` or checked GitHub Actions cloudflare workflow was found. These absences alone do not prove Cloudflare project setup.

## Corrective action, deployed to GitHub main
Commit `ace31e2ec1fc00063bad0cfbd478a9b8cbe418a2` added **FINANCIALS_EMBEDDED_ROUTE_V1** directly to the homepage and changed three card links to:
- `/?company=300394`
- `/?company=300308`
- `/?company=300502`

The homepage now bundles verified complete HTML for all three reports as JSON-safe inline strings, and client-side navigation renders the selected report immediately with `document.open()/document.write()/document.close()`. It also detects a deep URL of the form `/300502/2026-H1/` if Cloudflare served its root SPA fallback without changing `location.pathname`. This is a deliberate temporary resilience measure for a small three-report research library, **not** the final scalable architecture. The original standalone report files remain at their exact GitHub paths. This avoids relying on nested path availability when following homepage links, at the cost of shipping all report HTML with the homepage (229105 JS characters).

## Local testing
- GitHub homepage was fetched after the update and compared character-for-character with the submitted content.
- Counted 3 company link anchors with `?company=`.
- Using the same JSON-escaped inline HTML approach, a local Chromium `page.set_content` test rendered the Eoptolink report for desktop width 1440px and mobile width 390px with 9 SVG charts, correct report title and zero page errors.
- Live navigation on the actual Pages domain was **not testable** in this environment. `web` could not fetch it and `curl` had DNS/network restrictions. GitHub status API returned no CI statuses.

## Final site-side QA still needed
Open the actual deployed site and click each card. The report must appear and browser URL should be `/?company=300394`, `/?company=300308`, or `/?company=300502`; it must not show the research library again.
On Cloudflare **Workers & Pages → financials-in-visuals → Deployments**, verify production commit `ace31e2` or later; confirm source repository `kobolibra/financials`, branch `main`, and build output directory `public`. If the project is manually deployed or connected to a different repository, GitHub commits will not update it automatically. This cannot be corrected via GitHub alone.

## Unresolved / release distinction
- GitHub source correction: VERIFIED.
- Local client route rendering in equivalent fixture: VERIFIED.
- Cloudflare live route: NOT VERIFIED.
- Permanent scalable fix: audit deployment configuration; once deep assets are served correctly, restore clean deep links and remove all-report inline router bundle to avoid large home HTML.


---

## Corrective update: native fragment navigation (current state, supersedes earlier document.write approach)

**User-visible regression:** the earlier `?company=...` router used `document.open()/document.write()`, replacing the root document and resetting the scroll to the top. The user reported clicking a company still led to the homepage top. This proves the earlier workaround was not acceptable.

**Actual code correction:** GitHub commit `a5fae8cdf52fc312dc2f0c7bcc559caed61e214f`.
- Completely remove the old large `FINANCIALS_EMBEDDED_ROUTE_V1` + `document.write` replacement.
- Replace home card links with native hash anchors `#company-300502`, `#company-300394`, `#company-300308`.
- Append three distinct anchored company sections to the home HTML, each with a true full-company report embedded in an iframe `srcdoc`; no external asset request is needed to load the report content.
- Add a minimal compatibility handler for previously shared `/?company=300502` etc. and a Cloudflare SPA fallback deep path; it locates the precise company section and scrolls there, rather than replacing the document. This is backward compatibility only; new card links work without JS.
- Add `public/404.html` in commit `b5b4989c4719455e6b2ed93197075f93422aaaab`. For known old report paths which hit 404, automatically redirect to the exact root anchor, never the generic homepage.

**Local Chromium click test** (`/mnt/data/financials_navigation_smoke.py`, six real content frames): 3 companies × 2 widths (1440 and 390). Every clicked card reached hash `#company-XXXXXX`, landed the matching company section at approximately y=20px, showed correct report in the nested document, with 0 JS errors. GitHub source fetch independently confirmed exact match between each `iframe.srcdoc`-decoded report and the standalone GitHub company report.

**Publication caveat:** Cloudflare pages.dev production HTTP response and latest deployment commit remain UNVERIFIED in this environment because domain retrieval fails; if the user does not see this behavior, first verify the Cloudflare Pages project deploy source, branch and latest commit. This document records working GitHub code and local browser validation, not a live-site pass.

**Scalability:** `srcdoc` copies all three report HTMLs into the home page (~250k characters). It is deliberately a temporary robust navigation workaround; at a larger research-library size, prefer verified multi-page static deployment or a tested router with correct asset paths.
