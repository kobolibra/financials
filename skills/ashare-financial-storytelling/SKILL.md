---
name: ashare-financial-storytelling
version: 6.0.0
summary: Evidence-gated A-share equity fundamental analysis and original financial information design, with a reproducible multi-chart industrial research HTML publisher and explicit PDF/financial/visual/browser/release QA.
---
# FINANCIALS IN VISUALS · Research & Publishing Skill v6

## Mission

Read the original A-share annual, semiannual or quarterly PDF as an analyst, **not** as a dashboard exporter. Answer in this order: (i) how the issuer earns money and where it sits in the value chain; (ii) why revenue and profit changed; (iii) how reported profit translates to operating cash; (iv) which capital commitments, balance-sheet items and financial-statement notes change the quality of profit; (v) best opposing explanation and **falsifiable follow-up indicators**; (vi) visualization that communicates these results without misrepresenting accounting.

**Output**: one responsive, independent, self-contained HTML research publication, with original plots/graphics and inline JS/CSS/SVG; no PDF output. The original PDF remains the source. Do not claim App Economy Insights affiliation or reproduce third-party diagrams. Publicly disclosed AEI work is an editorial/research **benchmark across all chart families**, not just a Sankey style reference.

## Mandatory source and research discipline

1. Register document legal name/ticker/exchange, report type, current and comparative periods, financial statement **flow vs. stock**, consolidation basis, currency and original scale, revision status, audit opinion, original PDF SHA-256, PDF page index and printed page mapping.
2. Read business model/industry/revenue policy, management report, consolidated P&L, consolidated balance sheet, consolidated CFO and note, change of equity, product/geographic revenue+cost, credit-loss allowance and AR aging, inventory composition/write-down, prepayments, other receivables, relevant associated parties, capex/constructed assets, R&D/SBC/impairment, FX/hedges, contingencies and material event notes. Do not use partial extracted text when a table is broken: inspect original rendered PDF page and record reviewer/source.
3. Exact typed **evidence ledger** in original yuan Decimal (not rounded/display units) for each used material figure. Each cell has source original label, PDF page, table, period, stock/flow, currency, reporting scope, source quality and reported/derived label. A displayed derived metric includes a formula. Do not treat missing data as 0.
4. Write a research memo **before charting**: the specific company economic model; current principal thesis; material quantified facts; competing explanation of equal sophistication; evidence that would confirm or falsify the thesis; three to five watch indicators and unresolved gaps. Distinguish `reported fact`, `management claim`, `reproducible calculation`, `analyst inference`, `unknown`.
5. For the A-share framework, check changed share counts / bonus/adjusted EPS, nonrecurring gains after taxes, parent versus consolidated profits, tax, working capital net versus gross, AR top-five vs **revenue** concentration, supplier prepayment versus purchase concentration, FX P&L versus cash FX vs foreign translation OCI. An error in denominator is a blocker.
6. Key sector routing. Generic industrial profitability is **invalid** for banks, insurers, brokers and some property developers. Fail closed, select sector-specific notes and standards. Avoid forcing positive Sankey flows for loss makers or signed items.
7. If external public sources are explicitly authorized, get dated industry/peer/market data and cite separately. Do not infer peer valuations, price history, growth estimates, shipment quantities or operating KPIs from a single filing.

## App Economy Insights benchmark: the FULL chart grammar

The AEI's publicly available *6 Charts Before You Buy*, P&L, balance-sheet, cash-flow and FCF analyses teach different graphics for different research questions. Select by available evidence, never by quota:

| Research question | Preferred graphic | Accounting/analytical blocker |
|---|---|---|
| How the business makes money? | **Conserved true Sankey**: disclosed product revenue → consolidated revenue → COGS/gross profit → operating core/spend; *separate signed profit bridge* to net income | Product costs must exist; no negative ribbons; no invented product classification |
| Which drivers explain profit change? | **Gross-profit delta waterfall**, comparable period bars and, if defensible, within-product vs mix decomposition | Do not label accounting revenue/cost bridge a price-volume causal explanation |
| Is growth accelerating? | 8–12 comparable **quarterly** revenue and YoY line + segment mix only if historical filings exist | H1 versus H1 is not 12-quarter trend; no interpolated missing periods |
| Are margins and returns durable? | GAAP/CAS gross, operating and FCF margin lines, ROE/ROIC with correct denominators and comparable years | No annualizing half-year ROE as a proven yearly return; SBC not free |
| Does profit convert to cash? | **Signed bridge**: consolidated NP + every disclosed indirect CFO adjustment (grouped with expandable raw 15 or actual count) → CFO | Do not conflate balance-sheet delta with indirect cash adjustments |
| Where did cash go? | Cash opening + CFO + CFI + CFF + FX → cash closing **waterfall**; FCF = CFO−cash capex separately | Cash equivalents ≠ monetary funds; financing dividend + interest differs from dividends |
| What finances operations? | **Equal-total asset stocks and funding/liabilities/equity columns**; net cash/debt maturity when available | Balance-sheet components are stocks, NOT money moving through the company |
| Working capital/concentration | Same-scope stock pair or grouped bars; concentration part-to-whole radial with **actual denominators** | AR concentration ≠ revenue concentration, prepayments ≠ total procurement |
| Peer context/valuation/price vs fundamentals | Dated comparison, valuation bands, indexed fundamentals/market price ONLY when approved external price/peer data present | Missing prices/multiples or incomparable peers → show source gap, **no pretend chart** |

Reference studies: https://www.appeconomyinsights.com/p/6-charts-before-you-buy ; https://www.appeconomyinsights.com/p/how-to-analyze-an-income-statement ; https://www.appeconomyinsights.com/p/how-to-analyze-a-cash-flow-statement ; https://www.appeconomyinsights.com/p/how-to-analyze-a-balance-sheet ; https://www.appeconomyinsights.com/p/free-cash-flow-explained ; https://www.appeconomyinsights.com/p/how-to-analyze-a-10-k . The specific issuer original PDF—not third-party screenshots—is the source for published values.

## Figure and editorial quality contract

- **No cookie-cutter KPI terminal.** A useful cover and sharp quantified claim, strong first money-flow page, then visually varied earnings, growth, cash, stock/working capital, risk and counterargument chapters. Layout has intentional whitespace, legible Chinese and numerical hierarchy. Every figure must explain one question in five seconds.
- Use an original restrained palette (ink, neutral money, green profit, coral costs/outflows). Don't copy logos, individual graphics, page composition, or trademarks from AEI.
- Every displayed number linked to source page, correct reported period, decimal formula and note; major figure titles contain explicit question/answer. Important numbers readable without hover. Tooltips reveal exact yuan/page. Enable keyboard, accessible alt/role text, SVG export.
- Do not use CDN, remotely loaded fonts, APIs, external JS/SVG, stock photos, runtime finance feeds. Offline HTML must stand alone. Browser test 1440px, 768px, 390px: zero document horizontal overflow, meaningful chart scroll affordance, hover/focus, downloads, headings, no page errors, no remote requests, screenshots visually inspected.
- Reject repetitive generic charts, vague “增长很好” captions, insufficient/too small chart labels, broken page anchors, false negative/positive area geometries and overselling of unavailable evidence.
- Use clear notes for stock vs flow, reported vs derived, segment residual, management explanation and research hypothesis.

## Reproducible implementation (what actually works)

- Source examples: `examples/tianfu-ledger.json` and `examples/tianfu-memo.json` contain the manually reviewed case.
- `engine/audit.py`: exact yuan, accounting scope, sign, reporting period and evidence gates.
- `engine/probe_pdf.py` and `engine/source_audit.py`: **candidate-only** PDF extraction and page checking, not autonomous evidence approval. Broken cell extraction must be manually reviewed.
- `engine/build.py` + `template.html`: **data-driven**, self-contained editorial engine for industrial and manufacturing sources meeting required fields. It must not embed any issuer, old date, product class or PDF source page from the original demo; new issuer changes are injected only via ledger/memo. Financial-institution cases fail closed.
- `tests/test_engine.py`: arithmetic, source conservation, missing-period, corruption, changed-issuer and sector-safety tests.
- `tests/browser_v6.py`: local Chromium browser and responsive acceptance; screenshots in QA.

Example (from skill root):

```bash
python engine/audit.py examples/tianfu-ledger.json --out qa/ledger-check.json
python -m unittest discover -s tests -p 'test_engine.py' -v
python engine/build.py --ledger examples/tianfu-ledger.json --memo examples/tianfu-memo.json --atlas --out outputs/tianfu-h1-v6-atlas.html --qa qa/v6-atlas.json
python tests/browser_v6.py
```

The renderer **does not automatically perform full independent research or parse an arbitrary PDF perfectly**. A human-reviewed memo and evidence ledger are prerequisites. This is a multi-chart **industrial** engine, not a guaranteed universal A-share PDF-to-institutional-report model. Cross-sector full automation requires separate design, real multi-company regression and specialist sector templates.

## Release gates and authorization

Mandatory outcomes: `SOURCE_CHECKED`, `FINANCIAL_PASS`, `RESEARCH_REVIEWED`, `CHART_SEMANTICS_PASS`, `BROWSER_PASS`, `GIT_BLOB_VERIFIED`, `LIVE_HTTP_VERIFIED`. Any missing gate appears explicitly in QA JSON/readme; never silently label fully released. Verify fingerprint and unchanged source pages, exact cash/gross-profit reconciliations, all visual geometry, static chart sizes, the final live web page, and whether Cloudflare Git-to-Pages corresponds to the intended repository/branch and public domain.

Only write to expressly authorized repository; stage preview before replacing production. Production replacement requires explicit authorization in this conversation. Do not touch unrelated repos, Cloudflare settings or origin PDF. **Best practices mean demonstrated quality and truthful limits, not the version number or a self-assigned 'top-tier' label.**

## Full App Economy Insights benchmark (not merely one Sankey)

Read [the complete, source-linked visual research atlas](references/app-economy-visual-atlas.md) BEFORE selecting any financial figures. It documents publicly verifiable: income statement diagrams, balance-sheet compositions, complete cash-statement bridges, FCF/CapEx charts, growth and margin trends, leverage, indexed price/fundamentals, valuation history and peer comparisons, along with MD&A/risk analysis and original publishing craftsmanship. Do not claim to have examined paid images not publicly available.

Required selection sequence: company value-chain and full issuer income story → financial structure and debt/liquidity → earnings/working-capital cash bridge → reinvestment/FCF and dilution → multiyear trend or peer/valuation analyses **only if comparable historical filings and dated outside inputs exist**. Use proper independent visualization grammar; no imposed Sankey quota, no made-up peers or prices.

The original open-source, Decimal-ledger financial exhibits are implemented in `engine/visual_exhibits.py`; see `/preview/300394/2026-H1-visual-atlas/` for two added, tested case exhibits (capital anatomy and two-tier signed cash waterfall). The preview demonstrates an extension, **not** full arbitrary-PDF multi-sector production validation. The additional assets/earnings-to-cash exhibits have now been **promoted to the authorized production GitHub path**, with an exact blob SHA match to the reviewed preview. Cloudflare's actual public response remains unverified; do not describe that last gate as passed.

Before publication: verify every source label/period and amount, no issuer-specific page or date literals in shared drawing code, three viewport tests (1440/768/390), zero JS errors/overflow, actual production HTTP body and manual visual-editor critique. A Git commit or passing arithmetic alone does not establish editorial quality.
