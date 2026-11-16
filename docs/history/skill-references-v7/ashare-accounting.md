# A-share & China Accounting — robust analyst controls

## Rules and authority
Check applicable reporting-year version and actual issuer board: CSRC Annual report content & format (2025 effective July 1), 2023 Finance-report format rule 15 and nonrecurring gains explanation rule 1, Chinese CAS (especially CAS31 cash flow), exchange listing & industry disclosure rules (e.g. SZSE ChiNext communication industry requirements). An annual rule is not interchangeable with a fund's periodic report rule. Verify newest rules if future date changes.
Official links:
- https://www.csrc.gov.cn/csrc/c101954/c7547588/content.shtml
- https://www.csrc.gov.cn/csrc/c101954/c7451379/content.shtml
- https://www.csrc.gov.cn/csrc/c101954/c7451398/content.shtml
- https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46250.htm
- https://www.csrc.gov.cn/csrc/c100028/c7652148/content.shtml

## Exact identity checks, Decimal in original CNY
- Asset total − (liabilities + total equity) = 0; beware "equity attributable to parent" versus all shareholders.
- Consolidated income: P&L's explicit signed line structure. Operating profit = sales less total cost plus other income, investment/fair value returns, signed asset disposal, credit and asset impairments; profit before tax = operating profit + nonoperating income − nonoperating expense. Net income = pretax − income tax. Parent net = consolidated net − minority.
- Correct flow bridge: cash_close = cash_open + CFO + CFI + CFF + FX cash effect. Not equivalence of "monetary funds" and cash equivalents; restricted deposits/term deposits often differ.
- Net-profit-to-CFO: reported consolidated net income plus every **original signed** disclosed adjustment (depreciation/amortization, impairments, gains, FX/financial expense adjustment, changes in inventory/operating receivables/payables, tax and "other") = CFO. Empty cells are not always 0; consult report. Balance-sheet deltas and indirect movements are **not interchangeable** due to FX, scope, classification and noncash movements.
- CFO−cash paid to construct/acquire long-term assets = analyst "simple FCF"; not universal. Net CFO after dividend is NOT FCF.
- Segment revenue/cost/corresponding GP: guard product vs industry vs geographic categories; do not sum overlapping dimensions. Reconcile to consolidated and keep "reported residual" distinct from a proven third product. Rounding cannot be treated as exact YoY growth.
- Nonrecurring: follow company's disclosed item definition and regulator principles, not simply subtract all government grants, fair-value gains or all share compensation. Report consolidated vs parent and tax/minority effects. Cite exact list.
- ROE: weighted average net assets, don't recreate from closing equity. EPS: check bonuses/splits and adjusted comparatives. Annualized H1/9M ROE without assumptions is misleading.
- Subsequent-event, retroactive adjustment, audit and emphasis of matter: never mix document versions.
- Current/long-term inventory and receivables require gross vs net, aging, allowance, pledged/restricted and source detail.

## Change analysis heuristics (not automatic misconduct detection)
For any material >10% movement or strategically decisive small amount, read at least one original footnote:
- Gross-margin change by product (within-product versus mix versus unallocated), capacity utilization, inventory cost and FX. Claims about "pricing power" require price/customer supporting evidence.
- AR and contract assets growth relative to revenue; aging, ECL allowance, top customer exposure. A concentration in **receivable balance** is NOT a concentration in **revenue**.
- Inventory absolute and raw/WIP/finished breakdown, slow-moving/write-down changes. Inventory reserves reducing while gross raw inventory jumps is an examination cue, not proof of underprovision.
- Prepayments and suppliers: top prepayment share does not prove overall supplier concentration.
- Other receivables, contract liabilities, bills receivable, factoring, restricted funds; cash management / structured deposits.
- Income tax, finance cost from FX, other comprehensive income from foreign subsidiary translation: distinct P&L, OCI and cash FX effects; **must not add them as a single FX loss**.
- Capital projects: fixed assets/CIP/other noncurrent assets and cash CapEx need not reconcile one-to-one due to transfers, depreciation and noncash items.
- Equity incentive cost, issued shares, capital transfers, effect on EPS; bonus transfer ≠ real cash equity financing.
- Related-party, connected sales, guarantee, group entities and off-balance obligations; negative audit opinions / critical audit matters if annual audited.

## Period traps
2026H1 current flow vs 2025H1 flow; June 30 stock vs Dec 31 stock. Q3 cumulative 9M vs year-to-date 9M prior. Standalone Q3 = current 9M − same-year H1 **only if reports aligned, adjusted/revised and same consolidation scope**. Financial quarter length and seasonal comparability require precise dates. "同比" vs "环比" never swapped.
- Comparatives may show "调整前/调整后"; prefer adjusted figures with a restatement note and disclose effect.
- Published GM and YoY % have rounding. For exact bridge, source original revenues and costs, not the printed percentage alone.
- Any source that uses 亿 / 万 / 千 must be normalized to CNY yuan with stored original scale.

## Figure grammar / blocking
Sankey: nonnegative conserved magnitudes only; **do not** force money to flow between unrelated stocks; signed changes use waterfalls; capital return and profit use different bases. Chart validators require source ledger, equation, time key, source-page, derived-label provenance and sign checking. FAIL blocks deployment for affected chart.
