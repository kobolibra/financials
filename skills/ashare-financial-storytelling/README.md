# FINANCIALS IN VISUALS · Skill v6 & Tianfu case

This directory contains a **reproducible** offline HTML research article generator for A-share industrial issuers. It is an original design drawing on the *complete* App Economy Insights research/chart framework, not an App Economy Insights graphic clone.

## Actual delivered charts (Tianfu 2026 H1)
1. True conserved product → consolidated revenue → cost/gross profit → operating-core flow diagram.
2. Gross profit → net income signed P&L waterfall, including operating expense, signed other operating gains, nonoperating losses and income tax.
3. Prior/current revenue, COGS, GP, CFO comparative proportional bar panel.
4. GP-change signed bridge separating revenue growth from cost change (not causal price-volume attribution).
5. Net income → CFO signed indirect-method bridge, with all 15 original lines expanded below.
6. Opening → closing cash equivalents bridge across CFO, CFI, CFF and FX.
7. Strictly equal-total consolidated assets vs liabilities/equity stock diagram.
8. Operating asset trends on correct year-end vs half-year-end dates.
9. Top-five AR+contract assets and largest-supplier prepayment concentration (correct denominators).

Three of AEI's six pre-investment chart lenses **cannot be defensibly implemented** with the provided single half-year PDF alone: multi-quarter trends, share price vs fundamentals and valuation/peer comparisons. Their absence is intentional, not an unfinished placeholder to fill with invented data.

## Build and test

```bash
python engine/build.py --ledger examples/tianfu-ledger.json --memo examples/tianfu-memo.json --out outputs/tianfu-h1-v6.html --qa qa/v6.json
python -m unittest discover -s tests -p test_engine.py -v
python tests/browser_v6.py
```

The renderer uses only Python standard library. Local browser acceptance uses installed Playwright/Chromium. The HTML needs no dependencies or external URLs when opened.

## Important limits

- Original source: user's 185-page Tianfu 2026 H1 issuer report (unaudited) with SHA-256 `6f508be2da82fb7b1728e2e638b5ce721baa3cf98a64234db636358019d913f5`.
- Financial checks are Decimal/yuan reconciliation. A PDF table scanner produces candidates only; manual cell/page review remains mandatory.
- 13 regression checks (including a deliberately *synthetic* alternate issuer and missing comparisons) and desktop/tablet/mobile browser tests show this **industrial report generator** works for the tested cases; they cannot establish the quality of independent fundamental research for arbitrary A-share issuers, nor that financial sector companies are supported.
- Data extraction for another genuine issuer and second-industry acceptance are **not** yet established. Banks/insurers/brokers fail closed. No market prices/valuation/peer estimates are invented.
- Only a verified GitHub commit and live Cloudflare fetched HTML would establish public website publication. A commit by itself is not a live test.

## Publishing layout

The HTML is published at `/300394/2026-H1/`. Preserve `public/index.html` as the independent **research library homepage**, without forced redirects to any company. Do not create duplicate v6 preview/production versions without a release record.