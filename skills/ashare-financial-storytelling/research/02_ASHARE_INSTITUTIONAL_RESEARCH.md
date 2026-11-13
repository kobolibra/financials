# A-Share Institutional Financial Research | Source-Based Framework

当前执行补充（2026-11-13）：完整源账核查、重点正文表达、完整对账下沉。优先遵循 `../../../docs/PROFIT_CHAIN_EDITORIAL_STANDARD.md`：合法同口径利润链贯通归母；正负调整、行业收入基准、源格和实际几何分别验收；独立详细桥仅在回答新增重要问题时留正文。下方有日期的案例是历史证据，不覆盖当前目录和本次HTML字节。

**Source hierarchy:** (1) issuer disclosure PDF and revisions; (2) applicable CSRC/PRC Accounting Standards and exchange rules; (3) independently verified industry/customer/peer filings; (4) dated market data; (5) analyst inference. Source citation and as-of date are non-negotiable. **Framework is professional analytical synthesis, not a regulation itself.**

## 1. Rules and the current regulatory signal

- [CSRC Rule No. 2: Annual Report Content & Format, 2025 edition](https://www.csrc.gov.cn/csrc/c101954/c7547588/content.shtml), effective 2025-07-01. For listed company **annual reports**, not public-fund periodic disclosures.
- [CSRC Disclosure Rule 15: general financial reporting provisions and research disclosure additions](https://www.csrc.gov.cn/shanghai/c105566/c7454684/content.shtml), amended in 2023: materiality, appropriate footnote detail including receivables and R&D; source of analytic checklist, not permission to infer missing details.
- [CSRC explanatory bulletin No. 1: nonrecurring gains/losses, 2023](https://www.csrc.gov.cn/csrc/c101954/c7451398/content.shtml): evaluate economic nature, industry and business model; do not automatically label all subsidies or SBC nonrecurring.
- [CSRC 2025 company annual financial-report supervision release, 2026-08-14](https://www.csrc.gov.cn/csrc/c100028/c7652148/content.shtml): observed misapplications/inadequate disclosures including revenue, instruments, long-term investment/business combinations, impairment and R&D. **These are examination priorities, not evidence any particular issuer committed misconduct.**
- [PRC Ministry of Finance 2025 standards implementation report, 2026-08-03](https://www.mof.gov.cn/zhengwuxinxi/caizhengxinwen/202608/t20260803_3994689.htm): accounting standards are primary for faithful records; version-specific standards matter.
- Confirm issuer exchange/sector supplementary guidelines separately for each report period. Banking, insurance and broker rules differ. Do not import US GAAP cash flow, EBITDA or asset classifications by default.

## 2. Two separate research products

**PDF-only factual report**: claims backed by given issuer document; no assertions of global market share, peers, sector growth, customer identities, share-price attractiveness or forecast without evidence. Includes caveat 'source-limited.'

**Full institutional equity research**: integrate ≥3 FY + 8–12Q where relevant; industry operating and competitor datapoints; customer/supplier and technological trends; price/volume/mix when reported; financial modeling, scenario sensitivities and valuation. Each additional data input explicitly authorized and timestamped. Without those inputs, mark `NOT_ESTABLISHED` and disable investment-price/valuation graphics.

## 3. Analyst research structure, in order

1. **Identity & provenance** — issuer, ticker, exchange, share class, report (annual/H1/Q/YTD), PDF SHA256, release/amendment date, audited or not, date vs period, reporting currency/units, consolidation, prior-period restatement, annual comparative basis.
2. **Business/value chain** — customers and demand mechanism; offerings/pricing, distribution and recognition, segments, geography and FX, supplier bottlenecks, concentration, product life cycles, margins and R&D intensity. Mark `management claim` separately from `filing fact`.
3. **Growth and unit economics** — Revenue and GP by nonoverlapping segment, gross margin pp, incremental GP, volume×price×mix×FX×M&A if quantities/price available; alternative explanations and what would discriminate. Never deduce unit ASP or yield from group revenue.
4. **P&L & recurring earnings** — CAS signed profit bridge, finance expense/FX, provision, impairment, investment and fair-value, government aid, taxes, minority interests, adjustment to parent nonrecurring profit. Include source-specific materiality, not just check a 10% change cutoff.
5. **Earnings quality** — revenue recognition, related-party sales, contract liabilities, receivable age and allowances, top-5 AR vs sales distinction, factoring/bills, inventories categories and writedowns, prepaid counterparties, supplier advances, restricted cash and deposits; accrual-based earnings vs actual CFO.
6. **Operating cash** — indirect method to yuan, all adjustments signed, CFO net-income conversion; why BS stocks != indirect adjustment rows. CFO, CFI, CFF, FX to closing cash equivalence. Cash flow FX != P&L FX != OCI translation.
7. **Reinvestment & return on capital** — cash CapEx vs PP&E/CIP, depreciation/amortization, R&D capitalization and leasing, dividends/buybacks, financing, dilution, ROIC/ROE with correct weighted bases; separate maintenance and growth CapEx only if sourced.
8. **Balance sheet & solvency** — net debt/cash with restricted-fund definitions, asset quality and liquidity, maturity/covenants, contingent guarantees, related parties and consolidation anomalies. Bank-style debt metrics not imposed on banks.
9. **Governance and incentives** — controlling shareholders, pledges, capital increases, buybacks, share-based compensation, audit opinion and emphasis of matter; adjusted per-share comparatives.
10. **Industry, peer and demand evidence** — actual market/technology/competitive positioning from dated independent sources; peers chosen by economic model/segment and accounting, NOT same index code.
11. **Valuation & scenarios** — historical/forward multiples only with authorized dated markets, share base, cash/debt and credible forecasts; scenario levers and falsifiers, not made-up probabilities or price targets.
12. **Risk and thesis disconfirmation** — strongest competing explanation, material gaps, monitoring calendar, quantitative downside drivers if real evidence permits, and what a new disclosure would make you revise.

## 4. Accounting correctness constraints

- In CNY Decimal yuan: assets = liabilities + *total* equity; current+noncurrent when disclosed.
- Income statement bridge in issuer's line structure with proper signs; GP = revenue−COGS; operating profit is not automatically GP−all total operating costs again; parent NP + minority = consolidated NP.
- Separate report flows (H1 six months; nine-month YTD) from point-in-time June vs Dec; H1 gross profit from half-year flow is not annualized ROIC.
- Profit to CFO = consolidated net profit + every original **signed** reported indirect adjustment. If missing data, status FAIL/NOT_CHECKED and no purported exact bridge.
- Cash closing = opening + CFO + CFI + CFF + cash FX effect. Monetary funds ≠ cash equivalents; restricted funds can create differences.
- Group segment columns cannot overlap across product/geography/category. Unallocated positive residual is a mathematical unknown, not a business entity.
- R&D *expense* vs R&D *investment* or capitalized development; distinguish.
- AR gross vs net, allowance, contract assets and top counterparties; number/denominator must match.
- Inventory net/gross by raw/work-in-progress/finished and provision; a supply squeeze is management commentary, not automatically evidence of a prudent build or future inventory impairment.
- Nonrecurring uses regulator's economic/business principles and issuer's disclosed tax/minority adjustments. Don't auto-adjust all subsidies or share payments.
- EPS pre/post restatement, stock splits/bonus issues, noncontrolling interests, OCI and FX income versus cash different accounting scopes.

## 5. Sector-specific workbooks

| Sector | Key economics | Financial emphasis | Common hallucination risk |
|---|---|---|---|
| Optical components/electronics | shipment, speeds, ASP, yield, mix **if provided**, supply chain, R&D | segment GP, AR, raw inventory, supply bottleneck, facilities/FX | fake 800G/1.6T mix, guessed customers, market share |
| Semiconductor | wafer/product mix, capacity/yield, input cost, outsourced fabrication | inventories, depreciation, impairments, R&D, subsidy | sector ASP != issuer ASP |
| Machinery/construction | tender/backlog and recognition period, progress, working capital | contract assets/liabilities, overdue receivables, provisions | awarded order != recognized revenue |
| Consumer | channels/SSSG, SKU mix, promotions, inventory/returns | inventory aging, channel receivables, cost structure | make up sell-through |
| Pharmaceutical/biotech | trial/pipeline stages, licensing, commercialization | capitalization, milestones, cash runway | trial probabilities fabricated |
| Software/platform | ARR/churn/GMV/take rate **if disclosed**, acquisition costs | SBC, contract liabilities, concentration | invent retention/GMV cohorts |
| Energy/commodity | selling price/volume, commodity sensitivity, cost curve | capex, reserves, hedges, leverage | assume derivative cash = P&L |
| Utilities | regulated tariff, throughput/MWh | depreciation, debt/refinance, return on capital | generalize industrial margin |
| Property | presale/contract liability, completion, funding | constrained cash, project inventory, debt maturity | presale equals GAAP sales |
| Banks | NIM, asset quality, deposits, NPL, CET1, capital and liquidity | ECL staging, loan/asset mix, risk weights | CFO/FCF industrial formulas invalid |
| Insurance | CSM/contract service, premiums, claims, solvency | underwriting vs investment income, duration | bank/industrial Sankey forced |
| Securities & asset managers | fee AUM and commission, credit & investment income | risk capital, leverage, segment commissions | consolidated AUM equals owned assets |

## 6. Research dossier data contract

Each fact: `field`, exact signed decimal yuan, display unit, current/comparable period, physical PDF page & printed page if divergent, source original Chinese line/heading, source hash/version, consolidation, stock/flow, disclosed or calculated, formula, confidence, image review state, reviewer. Qualitative claims also carry statement type (`FACT`, `MANAGEMENT`, `CALCULATION`, `HYPOTHESIS`, `UNKNOWN`), source exact page and whether contradictory evidence exists.

All claims must be falsifiable where relevant. Example: “无源收入同比+77.40%，分部毛利率 71.90%” is issuer-reported; “供应紧张是有源收入下滑的唯一原因” is *unsupported*, and must be rejected.

## 7. Publication gate

`SOURCE_CHECKED`, `ACCOUNTING_PASS`, `RESEARCH_PEER_REVIEWED`, `CHART_SEMANTICS_PASS`, `DESIGN_CRITIQUE_PASS`, `DESKTOP_MOBILE_BROWSER_PASS`, `GITHUB_BLOB_VERIFIED`, `CLOUDFLARE_HTTP_VERIFIED` are **separate** statuses. No averaging; an unresolved publication blocker cannot be hidden inside a high percentage score.

The present Tianfu 2026 H1 PDF case can verify many facts and graphs, but **not** multi-quarter trend, 5-year valuation, share-price, external peer or model-specific unit economics. Those require additional original sources and as-of dates.