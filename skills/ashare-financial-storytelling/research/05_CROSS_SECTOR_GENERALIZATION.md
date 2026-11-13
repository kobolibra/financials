# Cross-Sector Financial Research Adapter Protocol · Candidate v8.2

当前执行补充（2026-11-13）：完整源账核查、重点正文表达、完整对账下沉。优先遵循 `../../../docs/PROFIT_CHAIN_EDITORIAL_STANDARD.md`：合法同口径利润链贯通归母；正负调整、行业收入基准、源格和实际几何分别验收；独立详细桥仅在回答新增重要问题时留正文。下方有日期的案例是历史证据，不覆盖当前目录和本次HTML字节。

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

## v8.5.0-RC1 · 首次正式十公司目录的两种不同原始财报完整研究样本（2026-11-04）

- **公用事业—水电 600900**：完整 2026H1 原始214页 PDF、SHA256 `738de3b36a31646f344cefaf90b4f149d653c3f68e89f4f8d14bdf02fc9c65a2`。物理发电量不是按会计合同实现的售电量或电价分母；报告内 2025H1 同控合并追溯同期才是可用同比基数。对比来源 p7/8、法定三表48–56、主营/其他业务及水资源税 p154、现金限制 p162；明确投资收益、利息、股利支付与电费现金不同。`HYD-012` 反例防止错误同期基准。
- **医药—创新药及知识产权许可 600276**：完整 2026H1 原始182页 PDF、SHA256 `ff6910663a9726acb889aa061a8bab1433f58890d81ebea013b8c637a097a7aa`。产品销售、许可收入、其他收入在 p145 披露为互斥可加收入类型；管理层创新药销售88.09亿只属销售商品内一个子集。期后才生效 BMS 合作/合同里程碑与本期销售/许可收入分离。p153 银行承兑汇票背书为非现金支付，经济再投资与现金购建资产/简单现金 FCF要分开；开发支出存量和当期研发不能相减求当期资本化。回归 `PHA-013`, `PHA-014`, `PHA-015`。
- **可再生的共同财务内核**：签名 CAS 利润/现金桥、16/17条间接 CFO 全原披露调节、原始 PDF 实际源格 x/y、各行业逐源收入→原成本/毛利真比例桑基、两时点资产＝负债＋权益、CJK 1440/768/390、源码到两独立离线 HTML逐字节 clean rebuild。主分支原件+会计+浏览器 [41736999153](https://github.com/kobolibra/financials/actions/runs/41736999153) PASS，真实 Cloudflare 十家公司/三尺寸 [41736999189](https://github.com/kobolibra/financials/actions/runs/41736999189) PASS；唯一目录 `site/research_catalog.json`→`public/index.html`，原八家 HTML 原样保留。
- **严格能力分级**：这验证两个**不同**会计/商业模式各一家公司 L1 实施，仍**未证明**任一单行业两家不同公司 L2 或银行/保险跨会计域 L3。完整所有重大附注语义/历史8–12季度外部估值/第二名独立人类编辑 `NOT_CHECKED`。不断将源 PDF 错列、分组叠加、非现金虚增、不正确量价拆解及手机裁切加进真实对抗测试，不能用统一 Dashboard 模板代替行业经营问题。

### v8.6 · Life insurer zero-context true original report stress (601628)

Do not port industrial gross-profit / accrual-working-capital / FCF / indirect-CFO assumptions into insurers. A single original annual/half-year source can contain three incompatible numbers: management legacy premium reporting (2026H1 China Life RMB million 536634), CAS recognized insurance service revenue (112525), and actual cash premiums received from issuing insurance contracts (626732). These cannot be added or drawn as a cash Sankey. Exact mutually exclusive p10 first-year regular / single / short-duration / renewal categories can form a two-stage **true geometric** premium-composition Sankey only. P&L has CAS insurer service result, fair-value +135835, investment income +112902, insurance finance -188067 and OCI -48038; full signed original account rows matter. If only original direct-CFO exists, reconcile all actual cash receipt/payment lines rather than fabricating net income→CFO. CSM stock RMB million 813253 on June 30 is an insurance obligation component and not the p87 service-period amortization 35155 nor management NBV. Run true PDF row/column anchors on physical p43–44,47–48,53–54,85/87; screenshot real 1440/768/390; check original weighted SVG path coordinates and every source table. This one-insurer test is **L1**, not insurance-sector L2 or all-industry L3. See `research/issuers/601628`, `skills/ashare-financial-storytelling/quality-regressions.json` INS-021–VIS-027, original SHA b094bf337309e30564dda86ff4b3c4d66aeeb37ce0357a3568e246569f0e2943. Independent second human review NOT_CHECKED.
