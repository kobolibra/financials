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
