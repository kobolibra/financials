---
name: ashare-financial-storytelling
version: 8.0.0
summary: Two-track research-to-publication discipline: independently benchmark App Economy Insights financial storytelling and rigorously analyze A-share original filings under current PRC accounting/disclosure rules, then produce a source-audited, responsive original visual equity research HTML.
---

# FINANCIALS IN VISUALS · Research & Publication Skill v8

## The two independent research foundations (MANDATORY)

**Pillar A — financial visual storytelling:** read `research/01_APP_ECONOMY_INSIGHTS_RESEARCH.md` before selecting figures. It reconstructs from first-party public App Economy Insights posts the business-first research flow and **full** graphic grammar: income flows, signed P&L waterfalls, balance composition, net income→CFO, financing and cash, FCF and capital allocation, multi-quarter revenue, margins, debt, price vs fundamentals, valuation spectrum, peers. Its source links must be retained; the visuals must be original, not copied from AEI.

**Pillar B — institutional A-share fundamentals:** read `research/02_ASHARE_INSTITUTIONAL_RESEARCH.md` before conducting the company analysis. The applicable CSRC rules, Chinese accounting standards, industry and exchange disclosures determine all facts, materiality, analytical ratios and caveats. *CAS, reporting periods and consolidation scope take precedence over beautiful graphics.*

Never treat these pillars as interchangeable. A well-designed chart is not proof of an investment claim. A well-supported financial table is not yet a compelling visual publication.

## Mandatory next-level research and editorial system (2026-11-01)

The **independent research foundations** are now implemented in two additional first-party source-based manuals:

- **Graphic / presentation research**: [03_VISUAL_EDITORIAL_SYSTEM.md](research/03_VISUAL_EDITORIAL_SYSTEM.md). This separately researches public App Economy Insights methods and the Financial Times Visual Vocabulary (distinct source) and specifies 22 accounting-aware chart recipes, two-speed reading, layout and typography, zero baselines, signed bridges, mobile and per-figure screenshot review.
- **Institutional A-share fundamentals / forensic work**: [04_ASHARE_FORENSIC_DEEP_DIVE.md](research/04_ASHARE_FORENSIC_DEEP_DIVE.md). This separately researches CSRC 2025 **annual AND half-year** disclosure requirements, MOF CAS-14 and 2025 annual-report accounting guidance, 2026 regulatory accounting failure themes and Shenzhen GEM communication disclosures. It defines 20 analyst examination stages and exact reconciliation rules.

**Mandatory analytical split**: Public company filing-only note vs fully funded multi-period institutional equity research. The latter requires external dated 8–12Q history, industry/customer/peer evidence, market prices and valuation inputs. One H1 PDF cannot honestly support them. Do not claim AEI-affiliated or paywalled templates were inspected. Use original visual composition, not copied branded graphics.

**Story-level editorial contract before figures**: (1) company role/value chain; (2) investment-relevant question; (3) accounting mechanism; (4) relative comparison and explicit reporting periods; (5) balance-sheet/cash rebuttal; (6) strongest alternative cause; (7) what next disclosure would falsify the lead. A chart **must** map to one question and one data relationship. No mandatory number of charts, no auto-approval for 6, 9, 11 or 20 images.

**Mandatory figure brief**: `chart_id; analytical_question; take_away; fact_ids; issuer; report_version; physical_pdf_page; period_or_date; consolidation; units; original_vs_derived; numerator; denominator; formula; reconciliation; graphic_family; domain_and_zero; color_encoding; source_caption; alternative_hypothesis; accessibility; mobile_policy; reviewer; publication_gate`.

**Figure selection**: 22 documented recipes cover growth, segment mix, GP contributors, signed P&L, ΔGP, quantity-ASP-mix only with reported inputs, revenue and margin timelines, debt, cash and credit ladders, indirect CFO, cash movements, FCF, asset composition, AR+inventory stocks, concentration, capital return, ROIC, price/fundamental indexing, valuation and genuine peers. Chart families are selected by *change-over-time, magnitude, deviation, stock composition, part-to-whole, ranking, flow and correlation*, not the author's favorite diagram. A large Sankey can be the lead figure but never substitutes for the rest of the analysis.

**Adversarial accounting checks**: earnings vs CFO uses consolidated NP; balance stocks vs signed CFO movements are not interchangeable; restricted cash vs cash equivalents differ; product revenue divided by total shipped units is an aggregate realization proxy, NOT same-SKU ASP; prior adjusted EPS can differ after bonus stock; M&A/restatement comparables must be documented; FX P&L != cash flow FX != OCI. Missing data are not zero and not a forced `other` bucket.

**Design and UX blocking tests**: per-chart complete screenshot critique (1440/768/390), semantic zero-baseline checks, visible axes and precise direct labels, balanced Chinese hero line breaking (no one-character final line), accessible static narrative, annotations close to graphics, no report in homepage iframe or `document.write`. Every company has its **own real independent HTML route**.

**Real-world proof of method**: standalone industry-chain report `/optical-2026h1.html` uses three separate user-uploaded original 2026H1 PDFs. It does **not** rank suppliers with module makers as same economics. Six distinct charts: zero-origin revenue growth, margin dumbbells, CFO/consolidated-NP conversion, signed zero-origin simple FCF, changes in working asset share of total assets, 100%-asset composition. Reproducible inputs must supply original PDFs and normalized ledgers to [nextlevel engine](nextlevel/engine/build_comparative.py). A GitHub commit does not prove Cloudflare live response.

**Separate pass/fail gates**: `PDF_HASH`, `PRIMARY_PAGE_TRACE`, `ACCOUNTING_EXACT`, `CAUSAL_LANGUAGE_REVIEW`, `RED_TEAM`, `CHART_SEMANTICS`, `TYPOGRAPHY_AND_FIGURE_VISUAL`, `BROWSER_NAV`, `GITHUB_BLOB`, `LIVE_HTTP`, `INDEPENDENT_FINANCIAL_REVIEWER`. Unknown is `NOT_CHECKED`, never success. These gates cannot be averaged into a '98% ready' claim.

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

- `v7/engine/render_v7.py`: version 7 standalone offline HTML editorial renderer (industrial/services only) with dynamically bound source fields and validated cash/profit bridges.
- `v7/engine/editorial_charts.py`: asset=liabilities+equity composition, analyst-defined CFO/CapEx/FCF, paired margin comparison. The charts use ledger-sourced page and period labels.
- `v7/engine/audit.py`, `engine/probe_pdf.py`, `engine/source_audit.py`: source/candidate and accounting controls. They DO NOT mean arbitrary PDF extraction is fully autonomous.
- `v7/engine/sample-ledger.json`, `v7/engine/sample-memo.json`: source-reviewed Tianfu H1 real case. No price, valuation, market share or unsupported sector data.
- `v7/tests/test_v7.py`: 12 real arithmetic, semantic and synthetic cross-issuer/adversarial tests; `v7/tests/browser_acceptance.py`: 1440/768/390. Browser implementation uses installed Chromium when available and does not require access to the public site.
- `v7/outputs/tianfu-research-v7.html`: actual standalone publication output.

Run from `skills/ashare-financial-storytelling/v7/` (the following paths are relative to v7):

```bash
python engine/render_v7.py --ledger engine/sample-ledger.json --memo engine/sample-memo.json --out outputs/tianfu-research-v7.html --qa qa/v7.json
python -m unittest discover -s tests -p test_v7.py -v
python tests/browser_acceptance.py
```

## Scope and limits, never hidden

The Tianfu report uses its **185-page 2026 H1 unaudited issuer filing**; 59 normalized fields and 15 indirect CFO rows. Full market-return, peer/valuation, and 8–12Q trend research requires other original reports and timestamped market data. Visual QA of one real issuer + synthetic alternate issuer is not independent validation on every A-share sector. The skill is an institutional **methodology and implemented industrial case**, not verified autonomous multi-sector investment advice.

**Quality status cannot be inferred from the version number.** Record each separate gate: `PDF_HASH`, `SOURCE_REVIEW`, `ACCOUNTING`, `RESEARCH`, `CHART_SEMANTICS`, `BROWSER`, `GIT`, `LIVE_CLOUDFLARE`. Any missing gate shows FAIL/NOT_CHECKED. Do not self-assign externally endorsed ratings.