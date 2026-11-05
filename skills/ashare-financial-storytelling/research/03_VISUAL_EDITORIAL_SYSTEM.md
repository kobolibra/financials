# Financials in Visuals — Visual Editorial System / Research Edition 8

**Date:** 2026-11-01  
**Purpose:** independent, testable editorial information design for Chinese listed-company financial research. This is a design system derived from public analytical methods, not a reproduction of App Economy Insights' branding or proprietary templates.

## 1. What was independently researched

**App Economy Insights (AEI), primary-source benchmark:**

- [How to Analyze a Stock](https://www.appeconomyinsights.com/p/how-to-analyze-a-stock): six research questions — company, economics, opportunities, risks, financials, valuation. **Implication:** no figure until its investment-relevant question is known.
- [How to Analyze a 10-K](https://www.appeconomyinsights.com/p/how-to-analyze-a-10-k): business model, risk factors, statements, MD&A, notes, compensation and audit report examined together. **Implication:** footnote interpretation must accompany the chart; a Sankey is a reading aid, not due diligence.
- [How to Analyze an Income Statement](https://www.appeconomyinsights.com/p/how-to-analyze-an-income-statement): ordered revenue components, GP and margin structure, context and growth drivers. **Implication:** diagram data widths are audited amounts; value addition is grouping and comparison.
- [How to Analyze a Balance Sheet](https://www.appeconomyinsights.com/p/how-to-analyze-a-balance-sheet): date-specific assets = liabilities + equity; composition and solvency. **Implication:** do not call asset-composition links real transfers of cash.
- [How to Analyze a Cash Flow Statement](https://www.appeconomyinsights.com/p/how-to-analyze-a-cash-flow-statement): three cash flow sections and end-cash reconciliation. **Implication:** signed accounting adjustments must not become nonnegative flowing ribbons.
- [Free Cash Flow Explained](https://www.appeconomyinsights.com/p/free-cash-flow-explained): actual cash CapEx vs operating cash; note lumpy growth capex, working-capital swings and accounting/cash boundaries. **Implication:** disclose issuer-specific FCF definition and accounting path.
- [6 Charts Before You Buy](https://www.appeconomyinsights.com/p/6-charts-before-you-buy): 8–12Q revenue and margin histories; leverage; indexed price/fundamentals; valuation history; peer comparison. **Implication:** these are capabilities requiring separate datasets, not default charts from one PDF.
- [Get Custom Visuals](https://www.appeconomyinsights.com/p/get-custom-visuals): publicly showcased differences in revenue categories, income, balance structure and segment story. **Implication:** diagram grammar adapts to the business, never the opposite.

**Independent cross-check on design choice:** [Financial Times Visual Vocabulary](https://github.com/Financial-Times/chart-doctor/tree/main/visual-vocabulary) categorizes graphics by *deviation, correlation, ranking, distribution, change over time, magnitude, part-to-whole, spatial and flow.* This is the missing dimension in v7: **the relationship must select the form.** This FT reference is a separate methodological source, not a claim that AEI uses this taxonomy.

**Important source boundary:** The sources verify only public charts and published analysis. They cannot establish AEI's full paid archive, typography specifications, internal production software or quality-assurance process. Any instructions below are *our original editorial synthesis*, not attributed as AEI policy.

## 2. Editorial product architecture — not a dashboard

The article must have two reading speeds:

- **90-second executive pass:** one falsifiable lead, three high-signal numbers, the largest contradiction, one primary graphic, the counterargument and a 3-item watchlist.
- **20-minute analyst pass:** full industry/value chain map, comparable business and product definitions, three-statement walk-through, accounting notes, concentration, capex/ROIC, historical operating trends, stress cases, evidence ledger, primary-source page links and assumptions.

An article is a magazine-like **thesis-driven sequence**, not a 4×4 matrix of KPIs. Before choosing figure counts, draft a 1-page editorial storyboard:

1. **Question:** Why does this business matter *now*?
2. **Economic engine:** What actually creates contribution profit?
3. **Growth mechanics:** Quantity / average revenue per shipped item / product mix / FX / acquisitions, **only at valid granularity**.
4. **Accounting engine:** What flows from gross profit to consolidated and parent net income?
5. **Cash conversion:** Where did net profit turn into, or fail to turn into, CFO?
6. **Capital demand:** Inventory, receivables, CapEx, financing and reinvestment.
7. **Resilience:** Debt, liquidity, counterparty, dilution and capital allocation.
8. **Competition and price:** Peers and valuation, only if priced, dated and methodologically comparable data exist.
9. **Red-team:** What else would create these same numbers? Which future disclosure would falsify the explanation?

The story determines number of charts. It is forbidden to create an arbitrary chart quota as a release criterion.

## 3. Visual selection grammar — 22 executable recipes

| Research question / data relationship | Preferred form | Mandatory source definition / guardrail | A chart MUST be absent when |
|---|---|---|---|
| What makes up total revenue? | weighted proportional flow or ordered bars | exclusive product categories and group revenue residual | segments overlap or lack same consolidation |
| Which product drives total gross profit? | contribution bars / grouped dot plots | segment revenue **and** segment cost | gross profit cannot be allocated to categories |
| How does gross profit convert into parent profit? | two signed waterfalls / operating bridge | CAS line-item signs; consolidated NP and NCI | nonoperating/OCI mistaken for costs |
| Why did total gross profit change? | 2025→2026 delta bridge, not causal attribution | Δgross profit = Δrevenue − ΔCOGS | prior quarter/H1 scope differs |
| Did volume or realized revenue per item change? | dual-panel indexed quantity/revenue, explicitly named *aggregate average revenue per unit* | consistent product unit and definitions | models/currency/scope differ and cannot be qualified |
| How much was exact price × mix? | bridge with quantitative disaggregation | same product/SKU, ASP, quantity, mix and FX disclosed | mix, price or FX residual unsupported |
| Has quarterly growth accelerated? | Q/Y growth bars + level lines | 8–12 true comparable standalone quarters | only YTD H1 / nine-month totals available |
| Did margins expand? | 2-period dumbbell or 8–12Q lines | gross, operating, FCF denominators uniform | undefined FCF or category mix changes |
| How resilient is debt? | net cash/debt bars; debt maturity ladder | maturity schedule, restricted cash, leases; coverage correct | debt basis or liquidity undefined |
| What makes up the balance sheet? | 100% composition or double-sided balance structure | assets=liabilities+total equity at same date | stocks/flow juxtaposed as one conserved money stream |
| What changed in funding structure? | pairs by date + bridge with sign | prior stock time and current stock time | only one date exists |
| Does profit become cash? | signed indirect CFO waterfall | all disclosed adjustments exact-yuan reconciled | adjustment rows missing |
| How did end cash change? | signed CFO/CFI/CFF/FX waterfall | cash equivalents, not monetary funds | period or definition mismatched |
| How much cash was reinvested? | CFO vs cash CapEx with zero baseline; FCF divergence | exact cash-flow CapEx item and disclosed definition | CapEx incorrectly inferred from ΔPP&E |
| Where is capital tied up? | inventory + AR as % *same-date assets* stacked bars | net balance stocks with same-date total assets | mix treated as cash conversion |
| Has receivable collection deteriorated? | aging ladder and allowance trend | aging buckets, allowances, write-offs | notes don't break down aging |
| How concentrated are accounts? | ranked values and explicitly labeled denominator | top-5 AR balances / total AR+contract assets | cannot infer sales share from AR |
| Is equity being diluted? | share-base step and reported/adjusted EPS | weighted vs period-end shares, bonus issues | share denominator unclear |
| Is capital productive? | ROIC / incremental return on invested capital history | invested-capital definition and NOPAT, average stocks, long spans | only one H1 report without valid base |
| Price diverging from fundamentals? | start-indexed 100 price vs operating series | split-adjusted price and dated financial series | no market data |
| Is valuation reasonable? | multiple time-series with percentile band; scenarios | timestamped EV/shares/debt, normalized/NTM earnings | only a PDF and no market inputs |
| Are peers actually comparable? | multi-metric small multiples / growth–margin scatter with caveat | same periods, different value-chain roles clearly separated | false peers or accounting basis differences unresolved |

**Do not confuse chart types with chart count.** A page with nine SVGs can still have only three ideas. A great page uses as many *different analytical relationships* as the evidence needs.

## 4. Original visual system — enforceable design specification

- **Canvas:** warm low-chroma ivory `#F6F5F0`; **paper:** `#FFFEFC`; **ink:** `#16363B`; muted `#607875`; green `#087F68`; copper `#AC765C`; blue `#436F87`. Colors code concepts consistently, not random categories. Always include labels/sign/shape so hue is not the only carrier.
- **Typography:** Chinese heading should use an appropriate local serif fallback; body uses platform sans; financial numerals may use tabular figures. No missing glyphs. Hero maximum 2–3 lines at 1440px, no orphan Chinese characters (“用。” on its own line is a **release fail**).
- **Grid:** max content width 1100–1180px, 12-column conceptual structure, charts dominate body width; notes below charts, never far-away appendix-only sourcing. A figure's annotation density should suit its role.
- **Hierarchy:** one page headline; section statement (reader takeaway) before diagram; figure header a *research question*, direct numbers and units, footnote and counter-explanation underneath. Avoid repeating the page title in every chart card.
- **Chart semantics:** bars measuring absolute magnitude begin at zero. Dot plots/dumbbells can use a nonzero domain but must declare it. Signed movements need a visible zero. Area and ribbon widths MUST encode actual conserved quantities. Negative values are never presented as positive area flows.
- **Period clarity:** explicitly print `2026H1 vs 2025H1` on comparative *flows*; `2026-06-30 vs 2025-12-31` on *stocks*. Never call these the same “同比”.
- **Unit clarity:** `亿元人民币`, `%`, `pp`, `百万只` not mixed; signed changes may show `+`/`−`. Dates, scope and audited flag visible.
- **Sources:** source block belongs under every key graphic and should identify company/PDF page/original statement/derived formula. Displayed values can round, but backend checks exact yuan.
- **Mobile:** no complete report inside an iframe. Content must occupy the full browser page; a complex *chart only* may scroll horizontally with visible hint. Never allow body-level overflow. Test 390, 768, 1440px and browser magnification.
- **Interaction:** not necessary to explain static findings. Clickable sources and accessible titles are more important than hover animation. If interactive, keyboard focus and an accessible data-table alternative are mandatory.
- **Final screenshot critique:** editorial review of hero at 1440 and 390, then *every figure screenshot*, not merely JS errors and scroll width; title breaks, clipped axes, overlapping labels, poor contrast and chart illegibility are release blockers.
- **Publication:** each company gets its **own standalone HTML route**; homepage is a directory, never a scrollable iframe collection or document.write router. Github blob verification != Cloudflare remote serving check.

## 5. Figure brief contract, required for every significant figure

```
chart_id; analyst_question; decision-relevant answer; analytical_relationship;
source_doc_id; physical_page; original_field; date/period; issuer; scope;
source_status; calculation/formula; denominator; sign_policy; exact_reconciliation;
chart_family; encoding (x/y/size/color/shape); allowed domain; normalizations;
annotation; competing_hypothesis; mobile_render_policy; accessibility_alt;
quality_gates; chart_omission_reason_if_not_ready
```

A chart is published only when each required field has been populated and passed audit. `UNKNOWN`, `NOT_DISCLOSED`, `NOT_COMPARABLE`, `SOURCE_UNVERIFIED` are values, **not zeros**.

## 6. Three existing report design gaps, observed in rendered screenshots

1. **Hero typography failure:** the 2026H1 新易盛 desktop screenshot ends the primary headline with the single line “用。”; the current browser test did not fail because it checks horizontal overflow, not editorial line composition. A new screenshot review gate is therefore mandatory.
2. **Narrative balance:** the original Tianfu v7 full screenshot contains long sequences of similar boxed figures. A true AEI-class business explanation needs stronger alternation of diagrams, compact interpretation, opposing views, raw evidence and editorial pacing.
3. **Research depth mismatch:** one H1 PDF cannot establish 8–12Q or normalized historical valuation. Existing reports must visibly show evidence limitations rather than celebrating the number of generated charts.
4. **Website routing regression:** prior homepage iframe/anchor hacks made the reading experience inferior. Separate full-size report pages are an architectural invariant, not a cosmetic preference.

## 7. Concrete proof-of-method, not a mockup

`nextlevel/engine/build_comparative.py` uses three user-supplied **2026H1 original PDFs** to generate `/optical-2026h1.html`: six different financial relationships, including a margin dumbbell, signed FCF bars, two-date asset share, zero-baseline growth bars, CFO/NP conversion and 100% asset composition. Each chart displays source pages; three issuer roles are distinguished before comparison. Code audits original PDF SHA256 and exact gross-profit arithmetic. No external prices or made-up product mix. `nextlevel/tests/test_comparative.py` and `nextlevel/tests/browser_qa.py` are reproducible acceptance.


## 8. 2026-11-03 practical AEI-inspired design challenge: an honest diagram can still be weak

**Before (observed on ASR 688220's actual 1440px figure screenshot):** four exclusive product revenues enter one center node, then a single consolidated COGS/GP split. The center node was mathematically conserved to 0.01 yuan, yet the product-level COGS and GP rows (both actually present on PDF physical p.178) were absent from the geometry. The visual said almost nothing about WHY two business models have different margins. Group-only flow therefore failed the product-economics editorial question even when source accounting tests were green.

**After (original design specification, not AEI artwork reproduction):** for each business type, exact source revenue splits into (a) own original positive cost and (b) own derived GP; all costs feed the aggregated COGS sink, all GP feed the same GP sink. Two conservation layers must be asserted, same width scale across the entire plot. The visual unit is an accounting allocation, not a payment between counterparties. Label large flow amounts directly at their source and outcome; extremely small IP/test branches remain true subpixel-width flows with supporting numeric annotation below the plot. The actual zero margin on the test-service line is mathematically zero and must not be portrayed as a minimum visible green flow.

**Companion exhibits, independent relationships:**
- Signed P&L waterfall: GP to recurring expense pressure, other income/investments, fair-value, impairment, nonoperating/tax, GAAP net. Signed amounts preserve direction. Do not draw an all-positive GP→NP Sankey if disclosed signed terms have gross expenses larger than available GP.
- Same-date balance sheet: 2025-12 and 2026-06 assets equal liabilities plus *total* equity, shared absolute yuan width, not a liquid-cash inflow; liabilities share can change independently of earnings.
- Product margins: separate magnitude (GP yuan starts at zero) from percentage margin (labeled without putting percentages on the monetary axis). One genuinely zero GP cannot be misread as rounded-away sales.
- Net income to CFO: complete original signed 17-item bridge; the BS inventory stock delta cannot be inserted as a shortcut.

**Source-cell anti-regression:** p.87 of ASR's 2026H1 P&L has a blank current-year nonoperating expense cell and **15.30 yuan in the prior-year comparative column**. Earlier ledger classified 15.30 as 2026H1 because a number appeared on the correct page. The visual compiler must check original x-column, not only page token presence. The corrected 2026H1 contribution of zero is a derivation from the P&L subtotal and physically blank current cell, not an issuer-disclosed numeric zero. This concrete error demonstrates why self-certified source tests are insufficient.

**Reviewer actions for each figure screenshot:** 5-second research answer; label hierarchy; monetary shape conservation; true zero/sign; period/currency; real source table and alternative explanation; exact legends for micro flows; 1440/768/390 all readable; check accessible keyboard/export; repeat on real public route. No editorial completion is claimed without actual screenshot opening, and no external human independence is implied by a second automated test.

## 9. v8.8 AEI/FT 财务总编独立阻断

参照 [AEI/FT完整财经视觉标准](../../../docs/AEI_FINANCIAL_VISUAL_EDITORIAL_STANDARD.md) 区分逐业务原始成本/毛利（Type A）与只有集团毛利的守恒分配图（Type B）；只有集团成本的资金图不能回答哪个产品自身赚钱。现存V10四公司在390隐藏全部非桑基SVG，仅850px桑基横滑，因此真实结构FAIL，必须改源生成器/真实HTML/逐图CJK浏览器与本版Cloudflare SHA，不可用历史截图、源表或CI绿色冒充视觉修复。公司专属5秒研究问题/原图真实面积/中文getBBox/负数/反证是独立于会计金额PASS的质量门。
