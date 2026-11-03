# 688220 2026H1 — source-conserved finance graphics and publication visual audit

**Period**: 2026H1, complete 224p mirror original PDF 1,449,510 bytes, SHA `9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc`. The exchange's static direct PDF URL returned HTML challenge, so SSE original-vs-mirror byte identity remains **NOT_CHECKED**. **Reviewer**: assistant's source/coding/screenshot review, NOT a second independent human editorial reviewer.

## Visual semantics: real checks, not eight pictures

The original first figure violated the deeper AEI/FT-derived intent: product sources were merged into one total then separated only at the group level, obscuring source-specific margins. The rebuilt Figure 01 is an *actual revenue→source-specific cost/GP network* with eight direct source/target flow paths. Each original source `revenue_i` branches to two destinations, `cost_i` and `gross_profit_i=revenue_i−cost_i`. For all four original p.178 mutually exclusive product categories:

- `Σrev_i = 2,451,275,102.27`, `ΣCOGS_i = 1,729,758,992.99`, `ΣGP_i = 721,516,109.28` CNY yuan; all exact Decimal.
- The actual SVG paths carry original `data-from`/`data-to`/`data-yuan`/`data-width`/source page/period/scope. Browser verifies **eight edges, four source nodes, two sink nodes, source and sink arithmetic and proportional widths**, not just “there is an SVG”.
- A small disclosed source of 79,769.92 yuan has a very narrow ribbon (no minimum false width). Zero GP is a zero-height path, with a separate textual explanation.
- Reusable source graph `research/shared/conserved_flow.py` rejects mixed product/region categories, parent-child duplicate facts, fabricated residuals, negative GP converted to positive-flow ribbon, stocks masquerading as period flows, currency/period/scope mismatches.
- This validates one real semiconductor reporting mode, not that every A-share sector now has an independently verified income Sankey implementation.

## Eight distinct figure briefs, assessed by original analytical question

| ID | Accounting question | Chart relation | Source physical pages | Main release check |
|---|---|---|---|---|
| flow | Product economics after cost, not merely aggregate revenue | direct source-conserved weighted 4→2 graph, 8 edges | 86,178 | actual rendered edge amounts and proportional thickness |
| segment | Segment margin rate versus actual profit contribution | zero-based GP amount + independent GM% label | 178 | margin denominator and actual figure review |
| gp | Two H1 GP changes; not ASP/cause | signed ΔRev−ΔCOGS waterfall | 86 | full original yuan arithmetic and true zero |
| pnl | Does 7.22bn-CNY-cent amount of GP cover 6.63亿 R&D? | complete GP→operating→pretax→NI signed waterfall, 9 steps | 86–87 | cost grouping declared analyst-derived, original p87 comparative column fix |
| earnings | Why positive statutory parent NI but negative deducted? | signed, same-tax-scope zero-origin profit definitions | 8–10,87 | after-tax nonrec vs GAAP parent reconciliation |
| cfo | What happened between consolidated profit and operating cash? | signed 17-item note waterfall, grouped visually | 90,187–188 | all 17 original signed adjustments close to CNY 0.00 |
| cash | How did cash equivalents close? | signed CFO, CFI, CFF, FX period cash movements | 90–92,189 | all four signs and bank/cash definition |
| capital | Are inventory, AR and contract liability cash flows? | 2025-12-31 vs 2026-06-30 paired balance stocks | 81–83,135,146–147,166 | no stock-vs-CFO semantic merge |

See `figure-briefs.json` for mandatory per-figure fact IDs, alternative explanations, provenance and mobile policies.

## Human screenshot critique of actual browser output

- Initial actual `flow_1440.png`: p.178 source groups were visually merged into a single opaque revenue trunk. **FAIL** graph economics → *reworked 8 direct edges*. 
- Subsequent `flow_1440.png`: right-hand COGS and GP labels partly clipped because 1200px inner SVG exceeded available desktop figure width, despite document-level no-overflow. **FAIL** desktop completeness → *reworked to 1060px and enforced the no-inner-desktop-scroll assertion*.
- Initial `pnl_1440.png`: 1580px diagram hid last two profit/tax items, contradicting the research thesis. **FAIL** desktop P&L completeness → *nine signed steps fit within 1060px and visible zero line*.
- Initial profit step `营业外收入 256,125.37 元` rounded to `+0.00 亿`. **FAIL** truth-preserving label → *show `+25.61 万`, no change to original amount or bar height*.
- Original mobile/nav screenshot showed sticky menu obscuring some exhibit titles; mobile source magnitudes hidden behind horizontal SVG scroll. **FAIL** graphic editorial → *static menu and first-order values above each of eight SVG figures*.
- Latest locally rendered individual `flow_1440.png`, `pnl_1440.png`, `flow_390.png`, `pnl_390.png` and full-page widths were opened for **assistant internal actual screenshot critique**. The screenshots and browser JSON artifacts are archived in the corresponding GitHub Actions build; expected current release includes 1440/768/390 width and 8 final figures with per-chart screenshots at 1440/390. No independent second human designer or analyst is claimed.

## Original source research red-team

An early extract labeled 15.30 yuan current-period nonoperating expense from p87, but the original table puts it in the 2025H1 comparator. This was corrected in the actual ledger to `nonoperating_expense_prior`, and profit bridge now has separate 2026 current-column proof. The PDF's p135 and p146 narrow tables split nine money amounts across two vertical words. Coordinate-located original cell bounds, row/column headings and dates verify those cells (`source-cells.json`), so 109 directly concatenated raw amounts plus 9 exact original source cells = **118/118 selected money source proofs**. This is neither whole-report material-note completion nor a claim that each PDF row was independently reviewed by another analyst.

A material source exception remains: p137 reports AR + contract assets top-five concentration 90.50%; summing independently reported p135 gross AR and p138 contract asset denominator yields 89.17% from original p137 numerator. No balancing category or adjusted denominator is invented. p179 future performance obligation subperiod amounts total 0.01 yuan above reported total. Both remain explicitly separated from exact-conservation figures.

## Gate assignments (must be independently kept current)

| Gate | Status | Evidence / limit |
|---|---|---|
| Full 224p mirror PDF SHA | PASS | archive and exact source SHA |
| Official SSE server byte identity | NOT_CHECKED | static SSE host returns HTML challenge |
| Selected original amount+physical-page source | PASS | 109 raw + 9 exact bounding-box cells |
| Entire material-note row/column independent completeness | NOT_CHECKED | selected case-focused review only |
| Original income and BS/CFO/accounting formulas | PASS | 2026H1 P&L/17 CFO + signed tests |
| Rendered flow semantics | PASS_TECHNICAL | actual 8 edges proportional and source-typed |
| Visual narrative / aesthetic judgement | SELF_REVIEW_PARTIAL | actual screenshots inspected; not a second external editor |
| Desktop/mobile technical | PASS_ON_MATCHING_SHA_ONLY | complete 1440,768,390, source tables and SVG export |
| Production GitHub + Cloudflare navigation | NOT_CHECKED_FOR_NEW_PR_UNTIL_MERGE | separate live QA required on final SHA |
| Independent second human financial reviewer | NOT_CHECKED | do not impersonate |
| External peers/8–12 Q market & valuation | NOT_CHECKED | single 2026H1 original filing |
