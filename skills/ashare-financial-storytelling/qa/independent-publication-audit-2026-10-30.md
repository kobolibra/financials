# Independent App Economy Insights Benchmark & Financials v5 Publication Audit

**Date:** 2026-10-30  
**Scope:** \`public/index.html\`, \`public/300394/2026-H1/index.html\`, \`skills/ashare-financial-storytelling/{SKILL.md,engine/render.py,engine/probe_pdf.py,engine/source_audit.py,examples/tianfu-memo.json,qa/v5-acceptance.json}\` and source PDF pages 103/112.  
**Verdict:** **FAIL — not publication-grade / not genuinely general-purpose.** The existing work is an arithmetic-reviewed source-led industrial **demonstration** with a limited product-to-COGS/GP Sankey and local browser QA. It is NOT equivalent to App Economy Insights in end-to-end P&L graphic complexity or editorial standards; no external expert publisher has endorsed it.

## App Economy Insights: what is actually being benchmarked

Official public sources:
- https://www.appeconomyinsights.com/p/how-to-analyze-a-stock — 6 questions: what business, economics, what goes right, what goes wrong, numbers, valuation.
- https://www.appeconomyinsights.com/p/how-to-analyze-a-10-k — issuer filing, risk factors, 3 statements, MD&A and notes.
- https://www.appeconomyinsights.com/p/how-to-analyze-an-income-statement — financial flow illustration, revenue/cost/profit and economics.
- https://www.appeconomyinsights.com/p/how-to-analyze-a-balance-sheet — stock identity and solvency.
- https://www.appeconomyinsights.com/p/how-to-analyze-a-cash-flow-statement — net earnings to cash and financing/investing.
- https://www.appeconomyinsights.com/p/6-charts-before-you-buy — multi-period revenue/margin, leverage, peer/valuation context.
- https://www.appeconomyinsights.com/p/how-to-analyze-an-income-statement/comments — publisher confirms diagrams are manually designed with substantial preparation.

What is good: narrative graph directly explains money flows; nodes/band widths follow economics; labels show money, YoY and margin; complete flow can continue into operating expenses/profit/tax/net income, not stop at gross profit. Contrast explicit opportunities/risks and multi-period dynamics. **Do not copy proprietary layouts, graphics, logos or claim affiliation.**

## Current product: independently verified observations

- Production HTML file exactly matches v5 preview's GitHub blob SHA \`abeeaee71e37ab1160942a7642204662e7a0e6da\`. Homepage Git blob \`d51a0189ce4821b5932a84654f8863deece2d1c0\` contains **no auto redirect** as of this audit, and links to the report. New public domain supplied by user: \`https://financials-in-visuals.pages.dev/\`. Old browser tab \`https://financials-8d4.pages.dev/\` is a **different domain**; cannot assume both Pages projects deploy the same Git commit.
- Offline HTML contains **one SVG** with **six connected paths**. Source economics: passive and active optical products plus an explicitly derived residual into COGS versus gross profit; exact grouped arithmetic has checks.
- The Sankey does NOT show downstream gross profit → R&D/other operating expense → operating profit → interest/FX/tax → net income, unlike richer App Economy Insights exemplars. No same-canvas cash-based capital allocation.
- Remaining figures are mostly horizontally scaled bars and cards. Signed cash adjustments preserve signs but are **not a proper waterfall/earnings-to-CFO bridge picture**; many repeated card layouts and full paragraphs dilute the visual-first objective.
- Local Chromium acceptance previously passed 1440 / 768 / 390 width, keyboard and hover, SVG export, no JS error. This tests function, not professional visual quality. External Cloudflare live HTTP fetch failed; NOT VERIFIED.
- 19 existing unit tests pass, including a *synthetic* second industrial issuer. This cannot prove operation on actual filings for multiple industries and business models.

## Original PDF source re-checks in this audit

Page **103** original table: Top-5 accounts receivable and contract assets balance total **¥1,287,923,163.36**, printed share **84.27%**. Not revenue share.

Page **112** original table: period-end raw inventory net **¥574,812,595.29**, prior balance **¥177,416,358.15**; aggregate inventory gross **¥981,119,698.61** and allowance **¥52,289,008.50**; supplier-1 prepayment printed share **83.40%**. Values visually checked from the PDF rendered page, not merely inferred from parsed text.

The five fields flagged NOT_LOCATED by parsed-text scanner were found on these page images. The **parsing failure remains** until table geometry / cell association is robust. Manually verified amounts do not make automatic PDF extraction universal.

## Priority defects and corrections

### P0 (publication-blocking)
1. **Generic renderer has issuer-specific literals.** \`engine/render.py\` embeds “无源和有源”, "2026 H1", "2025年末", \`p22\`, \`p61\`, \`p147–148\`, and hardcoded **15 indirect adjustments**, plus a fixed aria-label **84.27%**. These would mislead on another company; source page and period must come from ledger. Unit tests that simply use a second synthetic ticker do not detect this.
2. **Missing comparable revenue falsely shown as 0.00% YoY.** \`growth=((rev-rr)/rr*100) if rr else D(0)\` then displays "同比 0.00%". Absent data MUST render “未披露/不可比”; zero is a claim of no growth.
3. **Unreviewed source-memo label is not independently authenticated.** \`memo.review_status="ANALYST_REVIEWED"\` is trusted by renderer. There is no independent human-approval artifact tying the analyst and source versions to publication. Tool provenance and reviewer checks must be separate and release fail-closed.
4. **Report validation state was stale.** Prior QA JSON still said \`production_overwritten: false\` even though v5 was promoted. This was corrected as part of this audit, but a future release must automatically update metadata from actual Git state and public HTTP.
5. **No public deployment verification.** GitHub 200+commit is NOT equivalent to Cloudflare deployment success. Old/new Pages URLs may differ; do not claim live parity until HTTP body/hash or browser checks succeed.

### P1 (research/editorial quality)
6. **Flagship missing downstream financial logic.** Promote from 2-stage product split into defensibly conserved multi-stage income statement visualization. Use exact CAS sign handling; signed tax, fair value, FX and impairment need bridge/injection semantics, never misleading positive-flow paths. **Do not force an inaccurate Sankey**; use separate signed waterfall if needed.
7. **Lacks graphical earnings-to-cash reconciliation.** Fifteen signed rows visually crowd the page; construct distinct stages for noncash/working capital and end at CFO with exact amount. Expose expanded individual adjustments in secondary view.
8. **Historical evidence too thin.** Only 2025H1 vs 2026H1, and period-end vs prior FY end. Distinguish H1 vs 9M vs FY, note revisions. Multi-quarter and peer comparisons need additional verified PDFs/inputs; never invent external data.
9. **No robust economic attribution.** Passive growth vs active decline, better margins, inventory buildup are important but cannot be equated with verified pricing power, yield or share. Build product gross profit contribution bridge from comparable disclosed product revenue/cost and label remainder; price-volume when not disclosed remains unknown.
10. **Footnote forensics need more visual prioritization.** AR concentration, raw materials and supplier prepayments merit a concise risk transmission diagram/sensitivity rather than repetitive bars/cards. Do not conflate AR and revenue share or prepay and procurement share.

### P2 (visual/design interaction)
11. **Chart labels and nested content too small** relative to desktop canvas and especially phone-sized horizontal scroll; improve standalone static comprehension and direct annotation before hover.
12. **Repeated cards and long paragraphs** break narrative rhythm. Apply editorial pacing: large business-flow feature, one crisp transition chart, brief counterthesis/risk, then methods footnotes. One question per visual and one source per material claim.
13. **Visual originality without copying**: use system font, generous whitespace, deliberate hierarchy, color semantics, margin/YoY integrated into figure. No decorative Sankey where basic bars are more accurate. The current cards meet basic cleanliness, not App Economy Insights publication caliber.
14. **Landing version confusion**: change log must clearly show active primary domain and latest research version. Root page is a research library (confirmed in GitHub); browser currently on old domain may serve an earlier deployment.

## Required release gates before any future "top-tier" claim

- Evidence: source page + label + period/scope + reviewer for all 59 structured facts; five fragmented fields manually verified here, auto parser still needs cell geometry.
- Accounting: applicable reconciliations PASS, with NOT_CHECKED/unknown surfaced, not hidden; graph edges preserve values and proper signs.
- Research: an explicit economic story, 2-sided thesis, key operating driver uncertainty and dated watchlist; independent research/peer module only with approved data sources.
- Chart: full income flow or appropriate signed bridge; cash reconciliation graphic; mobile static clarity; all data sourced at figure level.
- Generic: real second company and at least one different sector tested; no hardcoded company name/report period/page/source inside generic renderer; missing comparable data must not become 0% growth.
- Browser: 1440/768/390 + fresh Chromium screenshots, 5-second reader test and manual design critique; not merely no console errors.
- Publish: preview first; explicit user approval to overwrite; production Git SHA verified; **actual new Cloudflare primary URL fetched and compared**, old domain behavior explained. No claim of verified public release if inaccessible.

## Release decision

**HOLD — no further claim that Skill v5 is a production-quality universal A-share research publisher.** Current official PDF-based Tianfu research is useful as a reviewed demonstration. The homepage no longer has an automatic Tianfu redirect in the Git source, but **Cloudflare live behavior is unverified**. This audit does not change production HTML or the existing homepage.
