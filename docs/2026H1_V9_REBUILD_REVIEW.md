# FINANCIALS IN VISUALS · 2026H1 complete rebuild / independent-source edition v9

**Edition:** 2026-11-03 · Four standalone original-issuer A-share research HTML articles. **Scope:** PDF-sourced institutional-style *filing research preview*, not a stock valuation or independently peer-reviewed investment recommendation.

## What was materially rebuilt

The four pages were **not** created by changing a ticker in a template. Their economic narratives and original financial exhibits are distinct:

| Code | Issuer | Central question | Real exhibits | Source-specific accounting work |
|---|---|---|---:|---|
| 600036 | 招商银行 | Why does NII rise while asset interest income falls? | 8 | Gross interest and funding costs, revenue composition, complete operating-to-parent P&L waterfall, deposits/loans, NPL/coverage/CET1 as independent metrics, balance, bank-native CFO and closing cash |
| 688111 | 金山办公 | What sits behind +236.94% parent earnings versus recurring software performance? | 9 | Revenue/product GP, separate statutory/regulatory/management earnings, consolidated balance, receivables and contract liabilities, exact signed 16-line indirect profit-to-CFO bridge, closing cash, R&D and cash capex |
| 600519 | 贵州茅台 | Does +438.84% consolidated CFO prove liquor operations improved? | 9 | Product economics and channels, GP, liability/inventory, financing subsidiary deposits and cash sign, exact signed 15-line indirect CFO reconciliation, consolidated balance and signed cash sections |
| 000333 | 美的集团 | Why does deducted parent earnings fall sharply as statutory earnings rise? | 10 | Non-overlapping parent/child industrial segments (previous erroneous 0.00 display fixed), domestic/overseas, true margin percentages, statutory vs deducted profit, receivables/inventory, financial subsidiary interest, consolidated balance, cash closure, exact signed 13-line CFO bridge |

**No invented peer/valuation/8–12Q history** from a single H1 filing. No automatic claim of price-volume-mix, economic hedging success or insurer/bank industrial cash conversion.

## Primary source inventory

| Code | Original full PDF pages | SHA256 |
|---|---:|---|
| 600036 | 247 | `0194f5122575ee8576dbce941fcc10fb171e0cd17c627dd63330da952c52b57c` |
| 688111 | 199 | `ec2322dc3a4461eef43045361391c0efe5673794302e329d03c7bbb8a3ad15a4` |
| 600519 | 110 | `0e10aa26be46b1cf3cd03f06e834c7fb98d5dd0d661b96f8fddd4af7e846a4f6` |
| 000333 | 205 | `576dd80e353e53296a800b03e9889a9cbb2e8b91fa2ab3c1dace7c10159179b8` |

## Exact evidence QA

- **191** individual selected original PDF physical-page fact positions in four disclosures; 190 original number strings and one explicitly tagged **derived** other-operating-cost group with 3 traced disclosed cost constituents. This is a **numeric-location** test, not a human second sign-off of every statement table row/column.
- Bank: exact NII (`interest income − interest expense`), fee+other=total bank revenue, full pretax/aftertax/parent attribution, original income tax and other expense components, 2025 and 2026 balance equality and full signed cash close.
- Software, liquor and manufacturer: **44** original signed indirect-CFO adjustment items verified with exact source-page numbers/sign, and each resulting original net profit → operating cash equation closes **to the yuan**. Note that the visual grouped captions only aid reading; the accompanying expandable table preserves each original item and exact source unit.
- Original and preceding balance sheets check assets = liabilities + all equity; CFO/CFI/CFF and FX check cash closure where cited. Mixed group/product hierarchies are never added as if mutually exclusive.
- **36** figures across 4 publications, each with a primary PDF link, page citations, mobile digest and expandable sourced data table. Exhibit numbering verified sequential and nonduplicated.
- Local Chromium `set_content` QA at **1440 / 768 / 390**: **12/12** page/viewport combinations passed; figure/table parity, page-wide overflow, JS errors, local anchor structure. The **actual public Cloudflare HTTP and live click navigation** are **NOT_CHECKED until GitHub Actions live validation runs**.
- Visual contact sheets and full exhibit PNG screenshots reviewed. Corrected two orphan Chinese headlines, 706.91亿 unit wrap, bad signed bar direction, unrelated risk metric scales, Midea double unit conversion, financial figure order and bank missing P&L bridge.

## Remaining non-negotiable quality gaps

- Each complete source PDF contains additional material notes, segment, governance and management discussion. They have **not** all been subjected to a second independent human reviewer. The sourced ratio proofs and 44-item CFO reconciliation do not certify all disclosures.
- Source-based 2025H1/2026H1 flow and 2025-12-31/2026-06-30 stocks do not establish a 12-quarter normalized earnings or operating history.
- External industry/peers, dated prices, valuation, target price, model forecasts, and quantified risk scenarios are not supplied. Those outputs are deliberately absent.
- This v9 iteration is markedly deeper and more honest than previous shallow pages, but **is not certified to surpass App Economy Insights**. A genuinely independent analyst/editor and a broader market evidence system remain necessary.

## Reproduction

Unzip entire package; from `v9` run:

```bash
python verify.py
python publisher.py
python qa_browser.py
python capture_all_figures.py
```

Python prerequisites: `pymupdf` (`fitz`), `playwright`, `Pillow`, and local Chromium. `qa_browser.py` uses `/usr/bin/chromium`; adjust only local executable location if required. Original reports are bundled under `work/`, never recovered from web snippet text.

## Source philosophy

Original `SKILL.md` and mandatory manuals 01–05 apply; no overuse of 1 generic infographic template. Article narrative chooses accounting question; typed original PDF fact and **signed** reconciliation gates the visual. This artifact remains inspectable offline, including its source data tables, with no external fonts, JS libraries or frame-based navigation. External source-document PDF hyperlinks are expected to require connectivity, but the analysis HTML does not.