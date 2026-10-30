---
name: ashare-financial-storytelling
description: Source-verifiable institutional-grade financial research and editorial visualization for Chinese A-share listed-company financial reports. Turn one or more issuer PDF filings into an evidence-based, analytically deep, responsive, self-contained HTML equity-research story; includes forensic accounting, industry-aware business economics, adversarial thesis review, publication QA and provenance.
version: 4.0.0
---

# A-SHARE FINANCIAL STORYTELLING — RESEARCH DESK v4

## Mission / what success means

Think like a buy-side sector analyst, an accounting-forensics reviewer, and a financial-information designer working together. Explain **how the business creates value, why financial performance changed, whether the earnings and cash are sustainable, what could invalidate the thesis**, and what the filings genuinely do not answer. An excellent report makes the reader **understand and question** the company, not simply admire an attractive graphic.

**Input:** an original issuer annual/H1/quarterly PDF. Optionally separately authorized past filings, peers, market and operating data, with each source and as-of date explicitly segregated. **Final deliverable:** one original, polished, self-contained, offline HTML report. No PDF output, bulk dashboard, simulated prices, stock rating, fabricated targets or unsourced projections. The skill is **a disciplined research workflow**, not a promise of automatic generic PDF understanding. Do not imply affiliation with, reproduce artwork from, or copy the house style of App Economy Insights. Borrow its publicly documented principles: start with business model; analyze economics, risk, profitability, balance and liquidity; show the money; use visual explanations as part of a narrative.

Read these references before execution:
- \`references/research-method.md\`: investment-research architecture, working hypotheses, disconfirmation, memo contract.
- \`references/ashare-accounting.md\`: Chinese accounting, period, disclosure and forensic checks.
- \`references/sector-playbooks.md\`: select an appropriate industry model and KPIs.
- \`references/visual-editorial.md\`: original visual language and chart semantics.
- \`references/quality-gates.md\`: objective QA, red-team review and release decision.
- \`references/tianfu-research-case.md\`: known single-company regression and its evidence limitations.

## Operating modes: source integrity first

**PDF-only** (default): company filings only, with strictly source-dependent conclusions. No outside company- or industry-specific factual claim unless verified and separately cited. Market share, TAM, competitive rank, peers and valuations usually remain "not established by supplied filing."

**Expanded institutional research** (only if requested / authorized and sources available): append dated independent regulator, supplier/customer, peer, policy, industry, exchange and market evidence. Separate company-reported numbers from independent evidence and mark source date, market-data currency and confidence. Perform peer matching on business model and financial definitions, not just ticker or sector.

**No invented precision.** Use Decimal in yuan for underlying amounts and only round at display time. Never infer customer names from anonymized tables, order backlog from unsatisfied performance obligations, or unit economics from consolidated data. \`未披露\` is not zero.

## Seven mandatory analytic questions (run BEFORE chart selection)

1. **Business:** What exactly is sold, to whom and through what value-chain position? Revenue recognition, sales model, contracting, pricing mechanism, product mix, geographic/currency exposure, working capital needs, fixed-cost intensity.
2. **Differentiation & durability:** What evidence indicates a moat, switching costs, cost advantage, patents, scale, quality or customer integration? Separate management's claims from demonstrated margins/retention/returns. What can erode it?
3. **Growth decomposition:** For revenue, differentiate **volume × price × mix × FX × M&A × accounting** ONLY where data permit. Study product-level revenue and gross profit contributions, market demand vs capacity/supply bottlenecks; never attribute a change to a cause without identifiable evidence. Compare same periods with restatement and share-base adjustments.
4. **Profitability:** Revenue → gross profit → operating profit → pretax → total/parent net profit → reported and扣非; decompose margins, S&M, G&A, R&D, financial FX, credit/asset impairment, government aid, investment/fair-value gains, deferred tax and unusual items. Prefer economic drivers to ratio catalogues.
5. **Cash and working capital:** Reconcile net profit → CFO using **all reported signed indirect adjustments**, CFO+CFI+CFF+FX → cash equivalents, simple analyst FCF = CFO−cash CapEx with limitations. Read receivables, prepayments, bills, contract assets/liabilities, payables, inventory categories/ages and provisions, restricted cash; ask whether cash generation is funded by counterparties or inventory changes. Never assume balance-sheet changes equal indirect-CFO adjustments.
6. **Capital allocation and risk:** Growth/maintenance CapEx distinction only if disclosed; PP&E, CIP, overseas capacity, dividends, buybacks, financing, dilution, pledges, related parties, shareholder alignment, currency/commodity/tech/regulatory/customer concentration, audit qualifications and contingencies. Judge returns on incremental capital only with comparable denominator and asset scope; avoid mechanically annualizing H1 ROIC.
7. **What matters next:** Form **1 principal thesis + 2–4 observations + 1 serious alternative explanation + 3–5 falsifiable monitoring indicators**. State observations that would change the conclusion and exact unavailable disclosures necessary to resolve material uncertainty. If valuation is not supported by authorized price/forecast inputs, exclude "price is right" and state out-of-scope.

## Required source-reading route

A. Intake: original PDF fingerprint SHA-256; issuer legal name, ticker/exchange, reporting period/date, currency, units, audited status, consolidated/parent and publication/version/revisions; make a PDF physical-page ↔ printed-page map. Read risk notice and the restatement note before comparisons.

B. Read in pairs, not isolated snippets: management discussion **against** business and risk paragraphs; P&L **against** segment revenue/cost; balance **against** AR aging/inventory categorization and provisions; CFO **against** indirect reconciliation and investment/financing detail; EPS/ROE **against** share movements and equity changes; management strategy **against** actual CapEx and R&D. Check notes for related parties, revenue policies, share payments, government grants, FX, overseas subsidiaries, audit and subsequent events.

C. Build a *machine-readable evidence ledger* with fields:
\`id, amount_decimal_yuan, currency, printed_page, pdf_page, page_anchor/quote, document_sha, table, current/comparative_period, flow_or_stock, consolidated_or_parent, disclosed_or_derived, formula, source_quality, confidence, reviewer, notes\`. Also store qualitative statements as separately attributed assertions with page anchors. Preserve exact original labels. Every material sentence and figure must link to one or several ledger facts.

D. Elicit competing explanations: not merely "growth strong" but "mix shift vs underlying unit economics"; not merely "CFO improved" but "CFO improved while inventory and AR absorb cash"; not merely "high cash" but "cash equivalents versus monetary assets and restricted balances." Label management explanations as **management statement**, not proof.

E. Select thesis-centric visuals AFTER all calculations: typically 1 signature money-flow/chart, 1 growth/mix profitability diagnostic, 1 earnings-to-cash/working capital chart, 1 capital/risk chart. For companies where Sankey is ill-suited, omit Sankey. No minimum chart quota. Small multiples and short tables can be better.

F. Draft an **analyst memo**, then build visual narrative, then red-team the memo, then run financial + visual + browser gates. Never write charts first and attach boilerplate explanation later.

## Financial invariants & materiality

Use all appropriate tests in \`references/ashare-accounting.md\`, each reported PASS / FAIL / NOT_CHECKED with numbers, source and tolerance. Checks include:
- Assets = liabilities + equity; line-subtotals and scope consistency.
- P&L reconciliation incl tax, minority interests, signed other gains/impairments; use CAS labels, not a generic US GAAP schema.
- Consolidated CFO, CFI, CFF and FX → cash equivalents.
- Net income + **each signed disclosed** indirect adjustment → CFO, with omission audit.
- Segment/subsegment revenue + residual → consolidated; related COGS **only** if segment COGS reported; no arbitrary zero gap.
- Cash equity/dividend/share changes (do not mix CFF dividend payment with total financing).
- For comparatives, restated values and stock vs flow time basis, EPS adjusted for stock split/bonus, weighted equity in ROE.
- Reporting annualized / half-year / YTD scopes never conflated.
- Reasonable scale and materiality thresholds: investigate any material change (>10% relative or financially thesis-material) and note when percentage is misleading near zero; **threshold is a heuristic, not a regulator-mandated threshold**.

Hard blocker: source mismatch or critical reconciliation FAIL, material unsigned negative flow, fabricated segment/cause, unrecoverable source amount, or unverified accounting scope. A successful sum **does not validate an economic inference**.

## Forensic review is mandatory, not optional

Score evidence on recurring profit quality and concentration without alleging wrongdoing from a red flag. Require direct review of: receivables balance/age, top counterparty concentration, inventory raw/WIP/finished and provisions, contract liabilities and prepayments, restricted funds, revenue recognition, FX/hedges, capitalized development, related-party transactions, government subsidies, impairment, tax, share compensation and dilution. Explain what the pattern could mean, what it cannot establish, and what future disclosure would validate it. Prioritize anomalous changes, not rote line-item coverage.

## Industry routing

Before ratios/plots, classify business into non-financial industrial/services, financial bank, insurer, securities/asset manager, property, utilities, platform, commodity or other. Choose the industry-specific accounting template from sector playbooks. **Never impose manufacturing COGS/EBITDA/CFO/FCF charts on banks/insurers.** For company-specific operations only use KPIs actually disclosed (e.g. optical component shipments/production, yield, customer concentration, geographic collections) and do not substitute general market assumptions.

## Deliverable HTML contract

At desktop width 1360–1440px, first screen must deliver a **sharp, evidence-supported one-sentence thesis**, a 2–3 sentence executive verdict, key results and the anchor figure. Structure:
1. Executive synthesis: verdict with uncertainty, not a rating.
2. Business/value-chain anatomy: who pays and for what, with explicit confidence.
3. Growth/margin engine: revenue and GP contributions, bridge where feasible, counter-case.
4. Earnings quality / CFO / working capital: include relevant notes and cash identities.
5. Capital allocation, capacity and financial risks, scoped to source.
6. Watchlist: leading indicators, scenarios **conditional, not fabricated probability forecasts**.
7. Sources & methods, company statements versus independent facts, calculations, non-coverage.

Every visual: question-form title, one-line interpretive answer, explicit unit/period, data provenance and materiality of residuals. Hover/focus reveals exact values/formulas/source pages, but key figures **always** appear without hover. No externally loaded JS/fonts/images/CDN; accessible fallback. Charts have correct geometric semantics; Sankey conservation + nonnegative flows, waterfalls for signed P&L adjustments, trend for time series, not a "flow" between unrelated balance stocks. Apply responsive typography and editorial review before release. Consult \`references/visual-editorial.md\`.

## Release gates and consent

1. **Evidence gate:** every material quantitative statement source or formula traceable; if chart source lacks enough data, downgrade/no-plot.
2. **Accounting gate:** applicable equations PASS and intentionally unavailable checks explicitly NOT_CHECKED; no unjustified "10/10" blanket claim.
3. **Reasoning gate:** critique major inference; strongest rival explanation; evidence needed to discriminate; sector logic defensible.
4. **Editorial gate:** 5-second takeaway per exhibit, hierarchy, original aesthetics, chart count by insight not quota; hand-check mobile text.
5. **Browser gate:** HTML at 1440px and 390px; JS errors, network calls, keyboard focus, tooltips, export, headings, anchor links, screenshots inspected.
6. **Deployment gate:** only user's authorized repository; preview first; verify actual GitHub blob; **independently** verify production URL (not GitHub commit alone). Never overwrite production/homepage without user's approval for the specific release.
7. **Honesty gate:** distinguish (a) local calculations validated, (b) local browser tests passed, (c) GitHub commit verified, (d) public Cloudflare deployment verified, and (e) general-PDF robustness proven. These are independent.

Return a **publication-readiness status** and list all remaining blockers. Do not claim "institutional-grade" on the basis of SVG rendering or one case. **One HTML output, not a PDF.**

## Demonstration and current technical boundary

The Tianfu 2026H1 example in this repository is a verified single-company dataset and reproducible HTML renderer, NOT a universal arbitrary-PDF engine. Existing production output is not automatically replaced by installing this new skill. Full autonomous extraction and multi-sector regression require separate implementation/verification. See \`references/tianfu-research-case.md\`.
