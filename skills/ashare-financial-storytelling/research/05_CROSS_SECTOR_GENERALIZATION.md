# Cross-Sector Financial Research Adapter Protocol · Candidate v8.2

This document is an original engineering specification. It does not certify that every industry is production-ready.

## Core design

Separate six layers: (1) original PDF provenance, SHA256, filing version and page; (2) typed facts with original unit, signed value, date/period and consolidation; (3) verified business-model routing; (4) sector-specific accounting reconciliations and material risk notes; (5) question-led chart selection; (6) financial, mobile and actual website publication gates.

Never equate operating revenue with total revenue without examining financial subsidiaries. Do not mix industry statement flows, point-in-time asset/liability balances, product/geography/channel cuts, parent and consolidated reporting, or disclosed and inferred figures.

## Industry adapters (not fixed chart templates)

- Industrial manufacturing: comparable product economics, inventory, CapEx and audited cash conversion. Reject unsourced SKU ASP and causal mix effects.
- Software: recognized subscriptions vs ARR/billings, contract liabilities, R&D, SBC and distinct GAAP/non-GAAP definitions.
- Consumer and retail: product, channel and geography as separate categorical axes; returns and inventory.
- Banking: net interest income and margin, funding mix, loan impairment stages, NPL, provisions, CET1/RWA. Reject industrial margins and industrial free cash flow.
- Insurance: insurance service and finance result, CSM roll-forward, NBV methodology, claims/combined ratio and regulatory solvency; CSM is a stock, premiums are not always recognized insurance-service revenue.
- Insurance/bank holding group: subgroup accounting, intra-group eliminations, parent-vs-NCI bridge and distinct operating-vs-GAAP earnings; reject direct addition without consolidation.
- Property: recognized delivery revenue versus presales, contract liabilities, impairments, restricted cash, maturing debt and going-concern paragraph; reject 'cash > debt' simplifications.
- Broker/asset manager: fees, trading/market-value swings, net capital and client assets versus company assets.
- Pharma: product, milestone, R&D capitalization, clinical and regulatory risk; no pipeline revenue fiction.
- Engineering/construction: backlog and contract assets/liabilities versus recognized revenue; performance obligations.
- Utilities: regulated tariff, physical volumes, fuel costs, maintenance/growth CapEx and regulatory returns.
- Mixed conglomerate: primary sectors plus material finance/insurance overlays, segment hierarchy and eliminations.

## Proof of genuine applicability

A model is LEVEL 0 if only described; LEVEL 1 after one original-filing real-company proof; LEVEL 2 after two real companies, full statements/core notes and reproducible browser-tested research; LEVEL 3 after cross-sector adversarial regression, independent editors and tested deployment. Do not claim universal capability for a LEVEL 0 model.

2026H1 real-source tests: 招商银行 600036 247 pages; 中国平安 601318 176 pages; 万科 000002 234 pages. Original bytes, SHA, full report identities passed. 44 selected original-page numbers and 7 accounting/semantic identities passed. These are not complete financial statement audits. 18 synthetic routing/adversarial unit tests passed. Three standalone sector pages were rendered at 1440/768/390, but actual-file route and Cloudflare HTTP remain NOT_CHECKED.

New mandatory checks from real filings: interest revenue identity instead of industrial gross-margin proxy; insurer segment eliminations and consolidated operating-to-GAAP net-profit bridge; Deloitte's going-concern material uncertainty in Vanke; source-link servers returning HTML rather than PDF; and Chinese hero orphan / wide SVG responsive defects.

Candidate branch: pdf-source-validation-2026h1. Preserve old reports and live main unchanged; record source artifact location, exact tests and next steps in PROJECT_STATE.md.

## Implemented cross-issuer publication boundary (v8.2.0-RC2)

An actual generic engine must consume issuer-independent figure-spec JSON; do not hardcode company identifiers into render logic. The reproducible first prototype uses: issuer original PDF SHA and page count; figure family; exact source page, decimal text and original accounting unit for each node; accounting scopes and time bases; additional explanatory claim and caveat. Each source amount is checked against the original page before the figure is rendered. All math is performed with exact Decimal normalized yuan and displayed rounded in 亿元.

Five companies were regenerated without any issuer-specific condition in the publisher: bank revenue composition (招商银行), insurer operating-to-GAAP earnings bridge (中国平安), dated liquidity-stock comparison (万科), industrial group revenue including finance subsidiary (美的集团), and consumer-finance group total versus operating revenue (贵州茅台). These are 5 verified **figure** cases, not full-report industry certifications. In a clean extracted archive, generator and all 26 current adversarial tests passed. 15/15 Chromium viewport **render-only** tests passed. The code and exact PDF bytes live in the Library archive described by `PROJECT_STATE.md`, not yet committed in this repository.

Editorial failure observed and corrected: original insurer earnings bridge made comparatively small signed adjustments into near-invisible thin strips. New design separates earnings-level and adjustment charts with their own **clearly declared independent zero-origin scales**, which must not be visually compared as the same height scale. Users see the exact signed numbers, explanation and source data table. This issue was missed by browser tests that only measured page overflow.

**Prohibited overclaim:** successful five-issuer single-relationship output does not establish original-PDF full analysis, autonomous table understanding, all 22 figure grammars in code, 12 sectors implemented or a fully reviewed publication. Future versions need full statement/note reconciliation, at least two issuer test cases per domain, dated multi-period histories, external financial editor, actual HTTP route and full visual scrutiny.

## Original pharma and hydropower tests, and fourth chart relationship (2026-11-02)

**Pharma** (恒瑞医药 600276 2026H1 PDF 182p, SHA `ff6910663a9726acb889aa061a8bab1433f58890d81ebea013b8c637a097a7aa`): original p.6 2025H1 CFO 4,300,453,251.40 yuan and 2026H1 1,987,003,872.34 yuan. A sharp cash decline cannot be attributed automatically to R&D, contracts or licensing without signed CFO and cash-recognition notes. MD&A p.20–22 distinguishes product sales, innovative medicine sales, licensing 14.22亿, R&D and period-specific events. A high headline innovation growth rate alone does not establish recurring underlying profitability.

**Utility** (长江电力 600900 2026H1 PDF 214p, SHA `738de3b36a31646f344cefaf90b4f149d653c3f68e89f4f8d14bdf02fc9c65a2`): original p.6 2025H1 revenue 36,697,614,066.72 yuan vs 2026H1 37,929,268,927.18 yuan; p.8 notes management-reported generation volume. Neither overall reported revenue growth nor gross generating volume independently identifies regulated tariffs, billed electricity price, sold-electricity composition or rainfall causal contribution.

The source-driven publisher now implements a fourth figure grammar, `period_comparison`, only when two correctly identified comparable H1 cumulative flows and original numbers are supplied. The renderer still contains no issuer-specific branches. A real clean-unzip rebuilt seven source-backed issuer figure pages and passed **28/28** unit/adversarial and **21/21** 1440/768/390 Chromium *render-only* checks. This remains a Level-1 first-company sector test, NOT a complete professional research engine, with remaining semantic restatement, full 3-statement, true HTTP navigation and editorial reviewer gates unpassed.
