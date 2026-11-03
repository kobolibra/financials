# Independent Visual Research Benchmark | App Economy Insights

**Research scope**: publicly accessible App Economy Insights articles; not a reconstruction of its proprietary templates, paid archives or source code. **Benchmark is a workflow and visual grammar, not a brand to copy.** Research date 2026-10-30. First party links below.

## 1. What was actually read

| Original publication | What it concretely teaches | What our A-share publisher must implement |
|---|---|---|
| [How to Analyze a Stock](https://www.appeconomyinsights.com/p/how-to-analyze-a-stock) | Six analytical questions: business, business economics, opportunity, risk, financials, price/value; business comes before stock chart | An actual thesis, competitor/counter-case, operating economics, decision-relevant uncertainties, valuation only with dated inputs |
| [How to Analyze a 10-K](https://www.appeconomyinsights.com/p/how-to-analyze-a-10-k) | Read business, risk, three statements, management discussion and notes jointly | A-share MD&A ↔ notes cross-checks; source-linked qualitative and quantitative evidence |
| [How to Analyze an Income Statement](https://www.appeconomyinsights.com/p/how-to-analyze-an-income-statement) | Multi-stage revenue categories, COGS, GP, expenses, profit; annotate margin and growth; emphasize unit economics and standards | Proportional flows for nonnegative conserved allocations AND signed P&L bridges for CAS-specific gains/losses |
| [How to Analyze a Balance Sheet](https://www.appeconomyinsights.com/p/how-to-analyze-a-balance-sheet) | Assets, liabilities and equity: stocks and composition at a date, financial resilience only in context | Equal-total stock composition with asset breakdown; never suggest balance sheet is literal cash movement; dates required |
| [How to Analyze a Cash Flow Statement](https://www.appeconomyinsights.com/p/how-to-analyze-a-cash-flow-statement) | Indirect CFO adjustments, investing, financing, cash balance movement; profit does not mean cash | Net income → ALL signed adjustments → CFO, then CFO+CFI+CFF+FX → closing cash, with each equation verified |
| [6 Charts Before You Buy](https://www.appeconomyinsights.com/p/6-charts-before-you-buy) | Revenue growth 8–12 quarters; margins; net debt/leverage; indexed share price vs business; valuation history; peers | Six *separate* chart capabilities, only activate if comparative periods, prices and peer basis are genuinely available |
| [Stock Buybacks & Dividends Explained](https://www.appeconomyinsights.com/p/stock-buybacks-and-dividends-explained) | Reconcile earning capacity, capital allocation, distributions, liquidity, optionality | Separate dividend/repurchase/financing bridge and capital allocation; never label interest+distribution cash wholly dividends |

## 2. Information design, based on the public original figures

- **Diagram logic first:** money amounts define node conservation and ribbon widths, NOT aesthetics. The plot tells a complete accounting story for the scope selected. No hairline pseudo-Sankey.
- **A meaningful visual family:** income-source/Sankey, fully signed waterfall, equal-total balance composition, cash conversion bridge, profitability dumbbell/line, market-indexed trend, historical valuation distribution, peer multiples, concentration ranked bands, small multiples. Do not force one type into all problems.
- **Hierarchical reading:** one-line conclusion, direct number/units and labels, comparison or margin callout near the data, subtle supporting context. The reader must understand the question and answer without opening a tooltip.
- **Context and caveats are also designed:** clarify reported-vs-derived, A-share accounting differences, data boundary and alternative causes. Avoid disembodied figures that can visually imply certainty unsupported by filings.
- **Narrative pacing:** standout first visual; compact analytical comparison; contrasting cash or capital visual; counter-hypothesis; clear watchlist and footnotes. Not a uniform grid of repetitive mini-cards.
- **Reader utility:** a browser article with navigable chapter anchors, figure focus/hover, source trace, accessible data table, mobile scroll controls, SVG export if useful.
- **Originality:** use original design, colors, type hierarchy and custom geometry. No copying copyrighted figures or graphic assets.

## 3. The complete chart grammar (not 1–2 figures)

| Module | Best graphic | Enabling evidence | Honest fallback/absence |
|---|---|---|---|
| Revenue contribution | weighted flow or ordered bars | non-overlapping product/region sales and sources | if categories overlap, separate views |
| Product economics | contribution/margin lollipop | comparable product revenues+COGS | product sales-only figure with cost unknown |
| Full income engine | nonnegative revenue→COGS/GP→Opex/Core; separate signed bridge to net | consolidated CAS P&L line items | signed waterfall only where negative core invalidates flows |
| Gross-profit change | Δrevenue, ΔCOGS bridge | comparable income statements | two bars if data missing |
| Price-volume-mix | decomposed change waterfall | exact volume/ASP, consistent product definitions | 'not established', no fabricated breakdown |
| Margin evolution | 8–12Q chart or 2-period dumbbell | proper time series | explicit 2 periods ≠ trend |
| Balance / leverage | asset and funding equal-total stocks; maturity ladders | balance and debt notes | balance-only, no invented maturity |
| Net income to cash | signed indirect CFO waterfall | note and 100% adjustments | no forced approximate cash reconciliation |
| Cash movement | opening balance → CFO/CFI/CFF/FX → close | cash flow statement | omit if any scope incongruent |
| Reinvestment/FCF | CFO−cash CapEx signed bridge | verified cash spend | label analyst-defined FCF, not literal use of CFO |
| Working capital | paired period composition and receivables/inventory ageing | consistent gross/net stocks and note breakdowns | category-level note, not inferred aging |
| Credit concentration | ranked table/bars and named denominator | AR and contract assets, or revenue explicitly | NEVER label AR share as revenue concentration |
| Equity/dilution | share-base changes and adjusted EPS | share movements, bonus issues, incentives | note adjusted prior denominator |
| Price vs fundamentals | indexed 0/100 series | historical market prices, split adjustments, quarterly fundamentals | ABSENT unless authorized data available |
| Valuation history | P/E, EV/FCF, P/B percentile band | historical prices, enterprise values, earnings expectations as-of | no invented multiple, forward estimate, target price |
| Peers | comparable scatter or small multiples | business/segment comparability, common FY, sources | no arbitrary rival list |

## 4. Editorial tests

1. Can a 5-second reader explain the company-specific result for **each** major visual?
2. Are central numbers visibly labeled with financial unit, period and basis?
3. Is width/area meaningful, and does each money-flow node conserve the stated amount?
4. Are positive/negative, stock/flow and net/gross distinctions correct?
5. Is one major alternative explanation visible alongside the favored account?
6. Are footnotes and sources placed close to the exhibit rather than buried at the end?
7. Does mobile render remain readable without scaling detailed 1400px diagrams down to 320px?
8. Is every unsupported market/multi-quarter/valuation module omitted rather than padded?
9. Is this *an original finance publication*, not an imitation or scraped asset from App Economy Insights?

## 5. Important boundary

The cited first-party public pages are sufficient to examine the public analytical framework and representative financial diagrams. They do NOT establish access to every paid subscriber-only chart, proprietary design system or internal editorial process. Do not claim to have exhaustively inspected them. Some visual techniques are a synthesis of good information design, not direct quotes from the publisher.

## 2026-11-03 · Tested failure mode: accounting total conserved, yet diagram omits segment economics

A first-pass A-share chart had four sources merge to consolidated income, followed by a single consolidated COGS/GP split. That diagram balanced *aggregate* revenue but did **not** trace segment-specific cost and margin. Under the source-first income-statement treatment described by App Economy Insights' public article (above), distinguish total-income reconciliation from actual product economics. When original segment revenue AND segment costs are available at the same consolidation/period, prefer segment-to-COGS and segment-to-GP edges, each sourced independently. Test edges in the browser DOM, not only a standalone ledger equation. For 688220, four mutually exclusive original p.178 product categories yield eight original-amount routes; the tiny testing service category is not artificially widened. This test is our original chart implementation, not a reproduction of the publisher's proprietary visuals. The exact reusable contract and counterexamples are at `research/shared/conserved_flow.py` and `research/issuers/688220/test_accounting.py`.
