# Financials in Visuals · 2026-11-02 production editorial audit

**This is a critical review, not a certificate.** Read the current main `skills/ashare-financial-storytelling/SKILL.md` (v8.2.0-RC4) and separate full-page research pages from `/research-lab/` one-figure engineering fixtures.

## P0 observed failure and correction

The original seven-issuer beta was seven *single-chart* pages. Downloaded PDF hashes, body layout and Cloudflare HTTP 200 were real, but no article had a thesis-to-evidence, business model, earnings, balance sheet and cash, risk, competing hypothesis, and falsifiable disclosure chain. Publishing it as research was an **editorial quality failure**, regardless of honest 'beta' text. Fixed: separate `/research/2026-h1/` multi-exhibit previews, demote one-figure `/research-lab/2026-h1/` to engineering-only and insert `noindex,follow`; homepage promotes the former, not the latter.

## Existing real publication pages

| Issuer | Main full-page research article | Figures/tables | Actually checked content | Editorial release status |
|---|---|---:|---|---|
| 招商银行 600036 | `/research/2026-h1/600036.html` | 9/9 | bank NIM, rate vs volume NII attribution, bank profit, retail/wholesale, deposit funding, NPL/coverage, loan-loss provision movement, CET1/RWA, signed bank cash flows | RESEARCH_PREVIEW; independent finance reviewer and full material notes NOT_CHECKED |
| 金山办公 688111 | `/research/2026-h1/688111.html` | 7/7 | WPS product/channel distinction, contribution to GP, PRC GAAP vs CSRC deducted vs company-adjusted earnings, investment income, operating cash vs profits, CapEx, cash bridge | RESEARCH_PREVIEW; adjusted-profit tax/NCI attribution and full note coverage need second review |
| 贵州茅台 600519 | `/research/2026-h1/600519.html` | 6/6 | product revenue, channels, consolidated versus product revenue, GM, reported CFO and finance-company signs, working assets | RESEARCH_PREVIEW; financing subsidiary contribution does not prove liquor cash collection; full working capital notes NOT_CHECKED |
| 美的集团 000333 | `/research/2026-h1/000333.html` | 7/7 | nonoverlapping product/segment hierarchy, nested industrial-solutions segment, geography, gross margin, regulatory deducted vs reported profit, receivables/inventory, CFO | RESEARCH_PREVIEW; exact FX/derivative/gains after-tax and NCI, full segment eliminations NOT_CHECKED |

All published tables and figures come from dated original PDF source ledgers. The site has actual HTTP and Playwright evidence. But `PDF_PAGE_NUMBER_MATCH` does not automatically mean `PDF_ROW_COLUMN_SEMANTICS` fully reviewed, and a nine-figure page is not automatically a fully independently checked institutional note.

## Actual visual inspection finding

The bank's original figure 9 showed cash outflows as positive-length absolute bars. Even with a textual note, that figure's visual claim was misleading. It was corrected in both the source renderer `research/cases/600036/build_bank.py` and the published HTML to a **signed zero-centered chart**, with operating inflow right, investing and financing net outflows left. First correction had a text/label collision, caught by visually inspecting the PNG and fixed in a second iteration (commit `18c524b901914933b814f3c1347cecc66ef7e4dc`). The original financial units/physical pages and nine evidence tables were preserved. `python check_bank.py` on the real original 247-page PDF validated nine figures, 31 selected physical-page source numbers, zero horizontal body overflow at widths 1440/768/390, source SHA and SVG export.

The chart design remains editorially repetitive in some reports; chart count, visual similarity, small negative series, CJK line breaks and the comprehensibility of each figure must be independently screenshot-reviewed. Color/font/style similarity to public App Economy Insights is *not* equivalent to research quality.

## Release gates by evidence, not marketing

- `PASS`: original PDF 7-issuer source preservation, factual selected field checks as recorded separately; four independently routed richer HTML reports; three-viewport desktop/mobile technical screenshot tests and publicly served links (see latest CI run for authoritative status).
- `PARTIAL`: source-ledger provenance and selected exact arithmetic identities, industry-specific company narrative, figure semantic sign/scale checks, main site navigation/experimental fixture segregation.
- `NOT_CHECKED`: second independent finance/editor review; comprehensive material-note and full statement reconstructions; independently sourced full 8–12Q history; market valuation; economic causal inference; cross-issuer per-sector generalization certification; visual editorial differentiation competitive with major professional finance publications.
- `FAIL/BLOCKER for RESEARCH_RELEASE`: any preview presented as complete institutional analysis while relevant NOT_CHECKED gates remain.

## Prioritized next increments

1. Pick one real issuer's **full report** and finish legally correct three statements plus material MD&A and note-level signed reconciliation; revise the final article from the evidence graph before implementing more figures.
2. Second issuer in the same sector; verify engine portability by clean-room rebuild, not source-copy-paste.
3. Add chart-specific zero, sign, metric normalization, mobile direct labels, figure-screenshot human review and release gates; ensure a single problematic figure can block the release.
4. Maintain independently routed public company pages, preserve URLs, create new dates/versions rather than redirect or replace URLs arbitrarily. Re-run the live Cloudflare browser CI after every small release.
5. Update main `PROJECT_STATE.md` and this audit after actually verified progress; do not erase or relabel unresolved gates.

**Never claim top-tier delivery until those real gates pass.**
