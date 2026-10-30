---
name: ashare-financial-storytelling
version: 3.0-preview
summary: Evidence-first visual financial storytelling from a Chinese A-share company's disclosed PDF annual, half-year, or quarterly report to one self-contained, browser-tested HTML study.
---

# A-Share Financial Storytelling · Publishing Skill (3.0 Preview)

## Purpose and non-goals

**Input:** an original A-share financial-report PDF. **Primary output:** ONE publication-quality, responsive, stand-alone **HTML** report that does not load external fonts, libraries or assets. The PDF is source material, **not** an output. No stock prices, macro dashboards, bulk market scraping, subscriptions, valuation, automatic stock picking or PDF exports unless explicitly requested. Never claim this skill reproduces or is affiliated with App Economy Insights; use its publicly described approach to business-model-first, three-statement, cash-conversion-oriented financial explanation as an editorial inspiration.

The system is not finished merely because a ledger validates, SVG renders or the GitHub commit succeeds. It is finished only after the actual published page has passed visual, semantic, source and browser tests. The present project contains a *verified single-company demonstration*, not proof of reliable zero-touch extraction for arbitrary A-share PDFs.

## Non-negotiable principles

1. **First ask what changed, not which chart to draw.** Choose one primary company-specific thesis, two or three crucial supporting observations, a plausible alternative explanation, and the remaining unanswered questions. A generic retelling of the three tables is not enough.
2. **Fact ≠ management claim ≠ calculation ≠ inference.** Label them separately in the narrative, visualization tooltip and source ledger. Never present management interpretation as independently verified causality.
3. **No fabricated segmentation.** Subtracting disclosed product revenue from total consolidated revenue gives a mathematically calculated *undisclosed residual*, not a new business segment. Label this clearly. Missing segment cost is never assumed to be zero.
4. **Consolidated vs. parent-company statements must never be mixed.** Flow statements are periods; balance sheets are dates. H1 is six months; Q3 often year-to-date nine months. Derive a single quarter only if proper comparable YTD periods and their source versions are available. Never sum point-in-time balances as if flows.
5. **Don't turn a balance sheet into cash flow.** A balance-sheet Sankey or composition graph represents stocks and accounting identity. Net income ↔ CFO uses an indirect-method reconciliation if disclosed, not guesses from balance sheet balances.
6. **True Sankey, honest geometry.** Its thick paths MUST be continuous curves/polygons with widths proportional to magnitudes. A row of bars and connecting hairlines is not a Sankey. Signed amounts and non-conserving profit adjustments require a waterfall/bridge or a *clearly separated* injection/adjustment step, never abs(negative) masquerading as a positive flow.
7. **Publication is contingent upon browser inspection.** Validate full-size desktop and mobile, labels and scroll, keyboard/tooltips, download buttons and console errors. Do not publish based on static HTML syntax alone.
8. **No cross-project actions.** Only write to the repo and branch explicitly authorized for this project. New editions go to a preview path first. Never replace a production report or homepage without the user's express approval.

## Workflow

### A. PDF intake and evidence extraction

1. Identify company, exchange/ticker, statement date, report period, accounting basis, whether audited, currencies, date/version, and source PDF SHA-256. If the report is a scan, inspect page images. Otherwise extract text AND inspect complex table images/headers manually.
2. Read *together* (a) Business model and key products, (b) MD&A and operating/market drivers, (c) consolidated income statement, (d) consolidated balance sheet, (e) cash flow statement plus indirect-method notes when disclosed, (f) business/product/geography revenue and cost segment disclosures, (g) risk factors and significant accounting notes.
3. Create a typed evidence ledger (`field`, original amount in CNY yuan Decimal, reporting period, stock/flow, consolidated/parent, source table, page, reported/calculated status, original Chinese field label, original PDF/version and extraction confidence). Keep the row's exact date and **do not** mistake unit 万元 or 千元 for 元.
4. For disclosed segments with rounding, keep raw exact amounts. If disclosed product sums differ from consolidated totals, use a labeled residual with sign and formula. If material but unexplained, block the full breakdown rather than fake a tidy third segment.

### B. Deterministic calculations and accounting gates

Before rendering, run exact-Decimal checks on whichever fields apply:

- `assets = liabilities + total equity`; current + non-current asset/liability subtotals when available.
- `revenue − COGS = gross profit` (industrial reporters only; never force this on banks/insurance).
- `operating profit = revenue − total operating costs + other gains/losses` with exact CSRC income-statement line signs, including tax/surcharges, impairment, investment, fair value, FX if present.
- `total profit − income tax = consolidated net income`; `parent net income + minority interest = consolidated net income`.
- `cash_close = cash_open + CFO + CFI + CFF + FX effect` for same period and cash-equivalents scope.
- When indirect reconciliation is disclosed, `net income + SUM(all signed adjustments) = CFO` to the yuan. **Do not** lump uncollected adjustments into an arbitrary balancing number.
- `simple FCF = CFO − cash spent acquiring/building long-term assets` is clearly an analyst-defined metric and **not** necessarily management's definition of FCF.
- Compare like periods, indicate when prior figures are restated, and keep balance-sheet YoY distinct from changes vs. prior FY end.

Report every gate as `PASS`, `FAIL`, or `NOT_CHECKED`. A materially missing / incongruent source blocks its dependent chart. **10/10 arithmetic checks passed does not prove the research content or graphics are publication-ready.**

### C. Story selection by relevance, not chart quota

Identify the company's value chain, revenue concentration, margin direction, profitability drivers, working capital, capex and funding. Select **2–4 major visuals**; a fifth only if it adds independent information. Pick charts by evidence and materiality:

| Evidence | Correct graphic | Must not do |
|---|---|---|
| Product revenue and COGS verified | Product → cost / gross-profit proportional ribbons; explain margin and mix | Fake product lines, fabricated distribution, hairline-only “Sankey” |
| Other signed income statement terms | Signed profit waterfall bridge alongside flow | Negative terms as positive Sankey flows |
| CFO indirect reconciliation disclosed | Exact signed bridge from net income to CFO | Infer note-level changes only from balance sheet stocks |
| Assets, debt, equity | Two-sided components / balanced stocks graph | Suggest asset nodes are actual cash transfers |
| Operating volumes, prices, customers disclosed | Drivers visual with unit-specific denominators | Infer price-volume contributions without comparable evidence |
| Material missing financial segments | Declare limitation and select other chart | Invent values to meet a visual quota |

Write a story plan with: thesis; evidence; one counter-hypothesis; chart purpose; source pages; why alternative charts were rejected; what the source PDF cannot establish. One chart must answer one question in five seconds.

### D. Original financial visual design

- Visual hierarchy: company/period + one strong headline → 3–4 central metrics → flagship money-flow graphic → signed profit/cash explanation → capital/caveats. Not a generic investor terminal.
- Use an original editorial design system; readable Chinese fonts, controlled palette, abundant white space, direct labels, short source notes. Maintain meaningful color semantics (teal for profit, warm/coral for cost/outflow, neutral for sources, yellow for signed adjustments).
- True Sankey requires sum of bands into node = the node's displayed magnitude (at full precision). Label source groups, outcomes, raw units, scale and residuals. Use SVG `path` with real polygon/curve area, not disconnected thin connectors.
- Hover/focus must show original number/units and where it came from (PDF page); optional export of original SVG. The graph must remain readable without a hover. Support horizontal scroll where necessary on narrow screens; do not shrink a complex diagram until labels are unreadable.
- Main HTML is self-contained. `svg`, CSS, JS must be inline; no CDN, external fonts, runtime API calls, chart images or network dependency. Do not copy App Economy Insights illustrations or trademarks.
- Cite page numbers close to each chart; distinguish original reported amount from derived amount. Use numerical values in yuan and round *only at display time*. Summaries must not contradict the exact ledger.

### E. Browser and editorial quality gates

1. Inspect the rendered page with desktop viewport (1440 px) and narrow/mobile viewport (390 px); screenshots must show no overlaps, cut-off numbers, bad contrast, impossible scroll, empty charts or missing icons.
2. Browser acceptance: no JS exceptions, no requests to external assets, at least one genuine nonzero-width SVG ribbon in flagship Sankey, tooltips work, SVG export works, keyboard focus has meaningful labels, navigation targets exist.
3. Research acceptance: headline supported by facts, alternative interpretation considered, management claims attributed, at least one important source gap acknowledged, all appropriate numbers source-linked by page, and none misrepresented by the chosen graph.
4. Mathematical acceptance: all applicable invariants PASS and any NOT_CHECKED/FAIL blocking conditions respected.
5. Deployment acceptance: **first upload a new preview path under the user's authorized GitHub repository**. Verify the GitHub blob/commit. If public Pages URL cannot be independently fetched or rendered, explicitly say “GitHub 已提交，公网部署未验证”. Request approval before replacing production HTML.

## Failure responses

If extraction is incomplete, describe precisely what is missing and produce only those well-supported parts, or a labeled working draft. Never invent data or announce “已正式发布” on the strength of an HTML file alone. If no suitable true Sankey can be constructed from evidence, use the strongest truthful alternative and explain why.

## Tianfu 2026 H1 regression case

- PDF: `苏州天孚光通信股份有限公司 2026 年半年度报告`, 185 pages, consolidated, unaudited.
- Product figures: PDF p.22: passive and active product revenue/COGS/margins. Consolidated revenue/COGS: p.61. Positive unnamed residual must be labeled **calculated undisclosed difference**.
- Cash conversion: p.147–148 indirect CFO bridge with **all 15 items**, not guessed balance-sheet delta. Profit and tax: p.61–62. Cash/net cash: p.65. Balance-sheet funding: p.56–58.
- Narrative: p.14 management attributes active-product capacity constraint partly to material shortages, but never quantifies its revenue impact.
- Test the adversarial cases: change 1 cent; substitute parent data; remove a key indirect CFO line; mismatch reporting period; sum of segments > consolidated total; source page non-existent; a negative term passed to a positive Sankey path; missing font / tooltip / broken SVG export.

**Template invocation:** “阅读并审计所附 A 股财报 PDF，先建立可追溯证据账本和分析假设，再选择最有意义的 2–4 张图。严格按照 A-Share Financial Storytelling Skill 3.0 输出一个可离线运行、经过浏览器视觉验收的 HTML 财务研究页面；不要生成 PDF，不要覆盖任何已发布网站。”