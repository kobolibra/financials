# Financials in Visuals — Institutional A-share Financial Forensics & Investment Research

**Date:** 2026-11-01  
**Product:** Source-limited PDF review **and** full institutional public-equity note. Never merge the two without data. This document is an independent analyst procedure derived from Chinese rules and accounting practice; it is **not** the text of a law.

## 1. Primary regulatory and conceptual sources

- [CSRC 2025 annual report content and format](https://www.csrc.gov.cn/csrc/c101954/c7547588/content.shtml) — **annual**, effective 2025-07-01.
- [CSRC 2025 half-year report content and format](https://www.csrc.gov.cn/csrc/c101954/c7547590/content.shtml) — **half-year**, effective 2025-07-01. Never cite the annual format as the only rule for H1.
- [MOF enterprise accounting standard No. 14: Revenue](https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201709/t20170907_2694006.htm) — distinct performance obligations, timing, revenue breakdown and receivable/contract liabilities disclosures.
- [MOF guidance for 2025 annual financial reporting](https://kjs.mof.gov.cn/gongzuotongzhi/202512/t20251224_3980024.htm) — revenue timing and other error risks. A change in recognition method with unchanged economics may indicate a prior error; cannot assume management used the wrong policy merely from aggregate revenue growth.
- [CSRC 2025 annual financial-report supervision release, August 2026](https://www.investor.org.cn/zczx/qwzx/zjhfb/202608/t20260817_927998.shtml) — actual regulatory errors found in revenue, financial instruments, business combinations, impairment and R&D. **Screening dimensions, not allegations about these three issuers.**
- [SZSE GEM industry disclosure guideline No. 4, communications](https://docs.static.szse.cn/www/lawrules/rule/stock/supervision/W020230210725777711333.pdf) — business models, communication product technology, capacity, output, sales, unit economic factors and major risks. Verify subsequent applicable versions on each issuer's report date.
- [CSRC explanatory bulletin on non-recurring gains and losses](https://www.csrc.gov.cn/csrc/c101954/c7451398/content.shtml) — economic nature of item and after-tax/after-NCI adjustments must be respected.

The rule hierarchy must be explicit in every case: **original company filing & amendments → applicable CAS and disclosure rules → dated independent industry/peer filings → dated market data → analyst inference.** Never treat management's industry market-size charts as independently validated economic data.

## 2. Twenty-stage institutional research checklist

Each stage has a research question, a source, a formula if applicable, a competing explanation and a publication gate.

| Stage | Analytical task | Essential disclosure / comparative | Common critical error |
|---|---|---|---|
| 01 Provenance | Who, when, which version and scope? | original PDF SHA, report physical/printed pages, issuer, period, audit flag, amendments, parent/consolidated | quote pre-restatement or wrong issuer |
| 02 Equity/share base | Is earnings-per-share comparable? | weighted average shares, bonus issue, repurchase, convertible, diluted EPS, restatements | compare unadjusted pre-bonus EPS |
| 03 Commercial model | How does company make money? | business/segment product definitions, channel, customer segment | confuse company marketing with facts |
| 04 Industry chain | Where are scale, supply bottleneck and pricing power? | company MD&A, independently dated industry sources | imply direct supplier/customer relationships |
| 05 Revenue bridge | Why did reported revenue move? | same-period comparatives, product/geography, gross/net method, M&A | count overlapping geography + product streams |
| 06 Volume/ASP/mix | More units, richer mix or price? | matching SKU/segment revenue, volume and FX | aggregate revenue / all units called price |
| 07 GP & cost driver | What caused incremental gross profit? | revenue, COGS, segment COGS, inventory pricing | ΔGP bridge presented as causal price/mix attribution |
| 08 Operating profit | Where did GP go? | selling, administration, R&D, finance, impairment, other operating gains | signed gains shown as operating costs |
| 09 Parent vs consolidated | Who owns accounting earnings? | net profit, attributable NP, noncontrolling interests, OCI | consolidated NI used as parent earnings |
| 10 Recurring earnings | How much depends on mark-to-market/one-offs? | nonrecurring table with tax and NCI, government subsidy, fair value | subtract a pre-tax gain from after-tax NP |
| 11 Revenue recognition | Was control transferred? | shipment/acceptance, FOB/FCA/DDP/DAP, consignment, contract assets/liabilities | sales before consignment withdrawals |
| 12 Receivables/credit | Is the cash collectible? | gross/net AR, ECL allowance, aging, acceptance bills, top counterparties | AR customer share called sales share |
| 13 Inventory | Is stock growth healthy or obsolete? | raw/WIP/finished, provision, lead time, advance purchases | all growing inventory deemed fraudulent |
| 14 Operating cash | Do adjustments reconcile? | all indirect CFO rows, signed with yuan precision | BS balance changes substituted for CFO note |
| 15 Cash close | What cash is actually accessible? | CFO+CFI+CFF+FX, monetary funds, restricted deposits | net cash balance equated with cash equivalents |
| 16 CapEx/returns | Is spending creating future value? | cash long-term asset purchases, PP&E/CIP, depreciation, R&D cap | H1 cash purchases inferred from fixed assets delta |
| 17 Working capital | Is balance growing faster than economics? | average AR/inventory/AP, 2025-12 and 2026-06 stocks, 2025H1/2026H1 flows | H1 revenue against year-end stock as annual DSO |
| 18 Solvency & commitments | Can financing bridge a downturn? | short/long borrowings, maturities, lease, guarantees, restricted cash | cash-rich headline ignores blocked balances |
| 19 Governance/capital returns | Are incentives aligned? | share awards, pledges, buybacks, dividends, auditor opinion | unrealized awards treated as cash paid out |
| 20 Investment thesis | What makes conclusion falsifiable? | best bull and bear, scenario equations, precise future indicators | subjective conclusion marketed as fact |

## 3. Quantitative reconciliation engines — mandatory rules

Let `D` be decimal yuan amounts from original statements, never binary floats:

```
gross_profit = revenue - cost_of_revenue
operating_profit = signed sum of every CAS P&L operating line item
net_profit = pretax_profit - income_tax_expense
net_profit = parent_attributable + noncontrolling_interests
assets = liabilities + total_equity
cash_from_operations = consolidated_net_profit + SUM(all originally signed indirect adjustments)
closing_cash_equivalents = opening_cash_equivalents + CFO + CFI + CFF + cash_FX_effect
simple_FCF = CFO - cash_paid_to_acquire_PP&E_intangibles_and_other_long_term_assets
cash_conversion = CFO / consolidated_net_profit (undefined if NI zero; dangerous when negative)
reported_AR+inventory_asset_share = (net_AR+net_inventory) / same_date_total_assets
```

**Do not** force unresolved differences into an `other` bar. Every residual needs a named accounting definition. A reported non-recurring gain may be before tax and NCI; avoid naive parent-NP adjustment. Do not put earnings EPS/dividends/DCF multiple and book value from different share bases on one chart. Proper note disclosure and judgment are needed for provisions and valuations.

## 4. Period comparability and quarterly decomposition

- Q1 is a genuine standalone quarter. H1 is six-month YTD; quarter Q2 = H1 − Q1 **only if restatement, changes in scope and accounting classifications have been reconciled**. Q3 = 9M YTD − H1; Q4 = FY − 9M, similarly guarded.
- Do **not** label mid-year stock changes YoY when comparing June 30 to prior December 31. Identify them as *year-end-to-half-year change*.
- When computing working-capital ratios such as DSO/DIO, disclose use of average stocks and annualization. For rapidly growing companies, exact trailing-four-quarter revenue may be more appropriate than simply doubling H1.
- A 2026 H1 disclosure may restate 2025H1 EPS due to a bonus issue even if reported earnings are unchanged; preserve adjusted and as-original comparisons.
- Product output/sales quantities from disclosure may be million units and cover differing models. Aggregated `revenue/units` is an **average realization proxy**, not an exact like-for-like ASP or causally identified mix change.

## 5. Deep inspection: optical interconnect case, actual three PDFs

Documents independently held and SHA-256 checked on 2026-11-01:

| Company | Ticker | Actual PDF | SHA256 | Pages |
|---|---|---|---|---:|
| 苏州天孚光通信 | 300394.SZ | 2026 H1 unaudited | `6f508be2da82fb7b1728e2e638b5ce721baa3cf98a64234db636358019d913f5` | 185 |
| 中际旭创 | 300308.SZ | 2026 H1 unaudited | `e0ecd7c365c65e90b1fa4b4616ba3f4649449d64451e0ba0b1b78ba9ce3170bf` | 184 |
| 成都新易盛 | 300502.SZ | 2026 H1 unaudited | `bc164fb2026947ef377e0f242cb80566b30afcb06d202e47b20222fd45c93d3e` | 134 |

The original Zhongji ledger's `source_sha256=NOT_VERIFIED_REMOTE_PDF` is **stale metadata** from an earlier no-bytes workflow, not a reason to claim the user's uploaded PDF is missing. The new comparative validation computes SHA from the actual attachment and records it; keep source ledger amendment history transparent rather than silently overwriting it.

**Financial insight to investigate, not a fabricated causality story:** 2026H1 CFO / consolidated NI is substantially different across these issuers, and they differ by value-chain role. Analyze whether working-capital absorption, customer terms, inventory buildup, cash purchases of long-term assets or accounting adjustments explain this. A cross-company ratio alone cannot establish fraud, solvency or durable advantage. The 3-issuer case is *one industry ecosystem*, not evidence that the engine supports banks or property developers.

## 6. Industry-specific routing and alternate metrics

| Business type | Primary drivers | Key liabilities/assets | Critical differences |
|---|---|---|---|
| Optical communications | sold units if matching disclosure, generation 400G/800G/1.6T, mix, R&D, yield if disclosed | imported components, raw/WIP, AR, CapEx | no fabricated high-speed product share; separate upstream/assembled modules |
| Integrated circuits | process node, product yield and demand cycle if reported | WIP, obsolescence, R&D capitalization, depreciation | do not infer wafer ASP from industry data |
| Construction/engineering | backlog, certified progress, signed contracts | contract assets/liabilities, guarantees, advances | contract amount != recognized revenue |
| Consumer retail | stores, comparable sales if disclosed, inventory turns | leases, loyalty and returns | channel sales != retail sell-through |
| Software/platform | recognized ARR/GMV/take rate if reported | contract liabilities, SBC, licensing | source-specific non-GAAP reconciliation |
| Biopharma | regulatory milestones and licensing terms | capitalized R&D and clinical assets | clinical trial success probability unsupported |
| Property | presales, delivered area, project cash | restricted pre-sales funds, funding wall | contracted presales != revenue |
| Bank | net interest income, NIM, deposits, NPL, credit costs, CET1 | loan ECL, RWA, capital adequacy | industrial CFO/FCF not a performance proxy |
| Insurer | underwriting, CSM, claims, solvency, investment spread | insurance contract liabilities | do not draw premiums as industrial revenue |
| Broker | trading, investment banking, asset management and spread | margin funding, trading inventory | NAV or client assets not owned company assets |

An industry-specific research model can be recorded as `NOT_IMPLEMENTED` until both **true accounting statement logic and at least two real issuer acceptance cases** exist. Generic industrial rendering should reject banks and insurers.

## 7. Red-team: 12 adversarial accounting questions

- Are consolidated and parent-company statements being mixed?
- Was a comparison restated? Was share count adjusted without revenue restatement?
- Is a split between products, geography or industries overlapping rather than additive?
- Can apparent margin improvement be explained by FX/classification, not pricing power?
- Does “revenue doubled while volume rose 61%” imply a genuine price change? Not without consistent unit mix.
- Is gross AR concentration disguised as customer revenue concentration?
- Is a rise in inventory a stock number while CFO inventory adjustment includes consolidation, translation and impairments?
- Are large prepayments classified as current or long-term, supplier advances or capital equipment?
- Does the CFO bridge reconcile all 15 original disclosed rows with the proper signs?
- Are monetary funds conflated with cash equivalents? Are restricted funds deducted?
- Is negative simple FCF due to growth CapEx, or driven by an unrepeatable working-capital deficit?
- What next-quarter disclosure would *disprove* rather than just confirm the investment thesis?

## 8. Research publication states

Each gate is separately recorded as `PASS`, `FAIL` or `NOT_CHECKED`:

`PRIMARY_PDF_SHA` → `SOURCE_PAGE_MATCH` → `ACCOUNTING_RECONCILIATION` → `CAUSE_NOT_CORRELATION` → `ALTERNATIVE_HYPOTHESIS` → `CHART_SEMANTICS` → `EDITORIAL_DESIGN` → `BROWSER_3_VIEWPORTS` → `INDEPENDENT_FINANCIAL_EDITOR` → `GITHUB_BLOB` → `CLOUDFLARE_PUBLIC_HTTP`.

The report may be a *transparent research preview* with a missing external reviewer, but it MUST NOT be labelled independently peer-reviewed or live-deployed without evidence of the corresponding gate. Avoid numerically averaging away one P0 failure.

## 2026-11-03 · Original-source column / narrow-table adversarial 688220 case

On physical PDF p.87, a CNY 15.30 yuan “营业外支出” occurs **only in the 2025H1 comparative column**. An earlier raw-ledger extraction mis-tagged it as 2026H1 because the table had two period columns. The correction requires: keep the 2025H1 fact tagged to the comparative period; do not invent current-year zero as a reported number; enforce exact `operating_profit_2026H1 + nonoperating_income_2026H1 = pretax_profit_2026H1`, then `pretax_profit − income_tax_expense = consolidated_NP`. Signed 2026H1 P&L derives GP from 2026H1 revenue and COGS, separately subtracts R&D and other operating expenses, adds investment and fair-value P&L effects, deducts impairment/disposal and identifies negative income tax expense as tax benefit, not operating cash.

The same 224-page PDF p.135 and p.146 splits nine original table monetary values across two vertically wrapped words. A page-level 109/118 raw numeric text search must NOT be called 118 complete semantic checks. `research/issuers/688220/source-cells.json` records source row, original column, date, p135/p146 physical rectangles and original word fragments. `verify_pages.py` reconstructs exact cell amount from the **original SHA-verified PDF bytes**, checks the heading and ledger period and re-renders source-page evidence, resulting in 109 original contiguous literals plus 9 reconciled physical table cells (subject to test). This is focused source-cell review, not exhaustive financial-note or external audit sign-off. One materially inconsistent reported AR concentration denominator is still explicitly unresolved; never force a percentage to balance by fabricating a new denominator.
