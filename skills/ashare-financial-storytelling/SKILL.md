---
name: ashare-financial-storytelling
version: 7.0.0
summary: Two-track research-to-publication discipline: independently benchmark App Economy Insights financial storytelling and rigorously analyze A-share original filings under current PRC accounting/disclosure rules, then produce a source-audited, responsive original visual equity research HTML.
---

# FINANCIALS IN VISUALS · Research & Publication Skill v7

## The two independent research foundations (MANDATORY)

**Pillar A — financial visual storytelling:** read `research/01_APP_ECONOMY_INSIGHTS_RESEARCH.md` before selecting figures. It reconstructs from first-party public App Economy Insights posts the business-first research flow and **full** graphic grammar: income flows, signed P&L waterfalls, balance composition, net income→CFO, financing and cash, FCF and capital allocation, multi-quarter revenue, margins, debt, price vs fundamentals, valuation spectrum, peers. Its source links must be retained; the visuals must be original, not copied from AEI.

**Pillar B — institutional A-share fundamentals:** read `research/02_ASHARE_INSTITUTIONAL_RESEARCH.md` before conducting the company analysis. The applicable CSRC rules, Chinese accounting standards, industry and exchange disclosures determine all facts, materiality, analytical ratios and caveats. *CAS, reporting periods and consolidation scope take precedence over beautiful graphics.*

Never treat these pillars as interchangeable. A well-designed chart is not proof of an investment claim. A well-supported financial table is not yet a compelling visual publication.

## Required operating sequence

1. **Intake:** confirm exact PDF source SHA, issuer, ticker, report version/revision, report period, audited status, currency, scale, stock/flow, consolidated vs parent, comparative and restatement. Map real PDF physical pages to report printed pages. Fail closed when mismatch.
2. **PDF-to-evidence:** read business/MD&A/risk, all three consolidated statements, product/geography/segment notes, revenue policy, receivables/contract assets, inventory and provisions, cash supplement, R&D, CapEx/CIP, related parties, share incentives, nonrecurring, guarantees and audit. PDF parsers merely nominate values; a human/source-review artifact verifies fragmented tables. Record original line and page.
3. **Evidence ledger:** exact signed Decimal yuan; date or period; consolidation; source label/page/sha; calculation proof; confidence and reviewer. The only allowed estimate without source is a clearly labeled illustrative calculation, not presented as a historical fact. Missing cannot become zero.
4. **Industry route:** identify manufacturing, semiconductor, pharma, bank, insurer, broker, developer, utility, platform etc. Banks/insurance must not use industrial COGS/FCF and should fail closed until a suitable specialist template is available.
5. **Analyst memo:** economic model, three alternative thesis candidates, magnitude analysis of revenue+GP+expenses, recurring profit vs reported, cash conversion, working capital/counterparty, reinvestment/return on capital, key market/technology risk, strongest opposing hypothesis, evidence gaps, 3–5 testable follow-ups. Label every assertion as DISCLOSED / MANAGEMENT / DERIVED / HYPOTHESIS / UNKNOWN.
6. **Chart selection (NO chart quota):** select graphic by the analytic relationship. Conserved nonnegative allocation uses Sankey; signed terms use waterfalls; balance composition is a stock identity; revenue and margins trend require comparable periods; peer/valuation need independent authorized market/peer data. A single original PDF cannot justify 8–12Q trends or stock targets.
7. **Visual editorial:** publish thesis first, strong information hierarchy, large primary visual, direct amount and pp labels, compact close-to-chart sources, counterview, analytical watchlist; deliberate whitespace and typographic consistency. Avoid mass-production dashboard cards, pseudo-Sankey and decorative graphs. Mobile SVG charts may scroll **inside** the chart with an explicit hint, never overflow the whole page.
8. **Accounting gates:** exact ledger balance sheet, GP bridge, P&L signed subtotal, minority interests, net income + all individual CFO adjustments, cash close identity, reported vs derived segment residual, source count, matching periods. Any material fail blocks affected figures.
9. **Red-team:** a financial/casual mechanism that could mimic the observed data; unsourced peer claims; unreported ASP/yield; AR concentration misnamed revenue share; monetary funds vs cash equivalents; stock changes mistaken for CFO adjustments; FX P&L mistaken for cash FX; false net-zero from missing inputs.
10. **Browser and publication:** playwright Chromium 1440/768/390, no page-level horizontal overflow, no JS errors/network dependency, figures readable, accessible keyboard tooltips and SVG export, all links anchored, static screenshot inspection and 5-second graphic critique. Check GitHub blob and public Pages HTTP separately; do not claim live if only GitHub is verified. User-authorized repo only, preview before production.

## Implementation in this repository

- `engine/render_v7.py`: version 7 standalone offline HTML editorial renderer (industrial/services only) with dynamically bound source fields and validated cash/profit bridges.
- `engine/editorial_charts.py`: asset=liabilities+equity composition, analyst-defined CFO/CapEx/FCF, paired margin comparison. The charts use ledger-sourced page and period labels.
- `engine/audit.py`, `engine/probe_pdf.py`, `engine/source_audit.py`: source/candidate and accounting controls. They DO NOT mean arbitrary PDF extraction is fully autonomous.
- `engine/sample-ledger.json`, `engine/sample-memo.json`: source-reviewed Tianfu H1 real case. No price, valuation, market share or unsupported sector data.
- `tests/test_v7.py`: 12 real arithmetic, semantic and synthetic cross-issuer/adversarial tests; `tests/browser_acceptance.py`: 1440/768/390. Browser implementation uses installed Chromium when available and does not require access to the public site.
- `outputs/tianfu-research-v7.html`: actual standalone publication output.

Run from the skill v7 directory:

```bash
python engine/render_v7.py --ledger engine/sample-ledger.json --memo engine/sample-memo.json --out outputs/tianfu-research-v7.html --qa qa/v7.json
python -m unittest discover -s tests -p test_v7.py -v
python tests/browser_acceptance.py
```

## Scope and limits, never hidden

The Tianfu report uses its **185-page 2026 H1 unaudited issuer filing**; 59 normalized fields and 15 indirect CFO rows. Full market-return, peer/valuation, and 8–12Q trend research requires other original reports and timestamped market data. Visual QA of one real issuer + synthetic alternate issuer is not independent validation on every A-share sector. The skill is an institutional **methodology and implemented industrial case**, not verified autonomous multi-sector investment advice.

**Quality status cannot be inferred from the version number.** Record each separate gate: `PDF_HASH`, `SOURCE_REVIEW`, `ACCOUNTING`, `RESEARCH`, `CHART_SEMANTICS`, `BROWSER`, `GIT`, `LIVE_CLOUDFLARE`. Any missing gate shows FAIL/NOT_CHECKED. Do not self-assign externally endorsed ratings.