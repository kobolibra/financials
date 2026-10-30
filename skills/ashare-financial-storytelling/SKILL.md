---
name: ashare-financial-storytelling
version: 5.0.0
summary: A-share fundamental research, forensic accounting, sourced finance visuals and reproducible offline HTML publishing. Real cross-issuer industrial ledger renderer, PDF candidate extractor, source SHA audit and browser gate; fail-closed for missing or sector-incompatible evidence.
---

# Financials Research Desk · A-Share Financial Storytelling Skill 5

## Mission

From an **original Chinese listed issuer PDF** to an **institutionally defensible fundamental research narrative and excellent self-contained HTML**. Draw original explainers inspired by App Economy Insights' publicly described **business-model-first** inquiry, not its copyright-protected designs. The PDF is input, **not an output file**. Only publish what is supported by original disclosures, transparent calculations and explicit uncertainty. Never treat a chart as proof of a causal conclusion.

## Actual, tested capabilities

- `engine/probe_pdf.py`: scans a **searchable** PDF (any issuer or reporting period) for 14 categories of financial source *candidates*, with original nearby text, physical and printed page numbers, source SHA, and explicit `UNREVIEWED` flag. Does **not** auto-approve data, overcome scanned pages or choose consolidated vs parent columns autonomously.
- `engine/source_audit.py`: compares original source SHA and checks whether ledger numbers can be located on claimed pages. Split/damaged PDF table cells can be flagged, not silently considered verified.
- `engine/audit.py`: Decimal ledger validation (asset identity, P&L, minority/parent, cash-flow movement, indirect CFO adjustments, segment remainder, simple FCF, period & scope); **does not** validate investment thesis.
- `engine/render.py`: cross-issuer renderer for industrial/service ledgers with approved source facts, real proportional Sankey (nonnegative conserved flows), revenue/gross-profit comparison, ALL signed disclosed CFO indirect adjustments, working capital, capital structure, counter-case, falsifiable watchlist, inline financial traces, keyboard/tooltips and SVG export. Banks, insurers and brokers **fail closed** until a separate sector renderer exists.
- `tests/test_engine.py` plus `tests/browser_acceptance.py`: unit/adversarial + actual 1440/768/390 Chromium screenshot and interaction tests. Source PDF is **not shipped inside the bundle**; case sample requires the original supplied report for source checks.

## Required workflow, no shortcuts

1. **PDF intake:** source fingerprint, legal issuer identity, market board, printed page map, first-party disclosure vintage, reporting period, audit, units, currency, consolidation scope, restatements, annual vs H1/YTD. Run `probe_pdf.py` and check the table images for important candidates. If scanned/no text, clearly request manual/OCR source inspection before approval. Distinguish PDF page index from the printed page number.
2. **Research question:** before charting, explain the value chain, who pays whom, segment economics, pricing/volume/mix/currency supply constraints, geography and business risks. Start from the biggest **financially material** change, not a fixed chart list. Compare MD&A with notes and statements; check audited opinions if annual.
3. **Typed evidence:** build `examples/*-ledger.json` with original yuan Decimal strings, reporting period, stock/flow, consolidated/parent, source page, original Chinese field label, status and verification level. Critical qualitative explanations must be tagged `management_claim`, `reported_fact`, `derived` or `analyst_hypothesis` in the research memo. Need explicit company name and source SHA.
4. **Analytical accounting:** run `audit.py` against the approved ledger with exact original values. Important mandatory reading: revenue/cost product margins, weighted ROE and share-adjusted EPS, recurring vs nonrecurring parent profit, net profit→CFO, cash movements, inventory composition and provision, AR aging and counterparty concentration, prepayments, tax, subsidies, R&D and FX distinctions, equity and capital allocation. Period labels and CAS identities are not optional.
5. **Adversarial thesis:** describe what changed, strongest cause that is **supported**, most credible alternative, information that cannot be established from the PDF, and 3–5 measurable next-disclosure falsifiers. Do not infer unit/volume/price, client identities or peer advantage without appropriate evidence. AR concentration cannot be called revenue concentration; prepayment concentration cannot be called purchases concentration.
6. **Sector routing:** industrial/service renderer only with valid consolidated revenue and COGS. Banks/insurers/securities/property need their own appropriate validated renderers; no generic gross-profit/FCF Sankey. If material chart inputs missing, omit chart instead of drawing false values.
7. **Rendering:** author/review `examples/*-memo.json`; run `render.py`. Memo without `review_status: ANALYST_REVIEWED` is visibly marked as a draft. A valid memo remains a record of an analyst review, not an autonomous AI truth guarantee. Never claim independent verification of management's explanations.
8. **Math QA:** exact Decimal at source (yuan), rounded only at display; signed CFO adjustments positive/negative, flow conservation per node, ratio comparison basis, residual disclosure. Hard block when a source is missing, period mixed, or core identities fail.
9. **Editorial QA:** original high-quality research publication: one incisive thesis, editorial typography, meaningful palette, proportional flows, negative-value waterfall/bridge, readable original source captions, evidence and rival view near claims. No decorative dashboards or chart quotas. No unconsented copied publisher visual.
10. **Browser QA:** build HTML as single offline file with *no* remote assets/CDNs/fonts/scripts. Inspect 1440 desktop, 768 tablet, 390 mobile *and* chart horizontal scroll. Confirm tooltips on hover/focus, navigation, export, no JS errors or requests; keep screenshots and machine-readable QA JSON. Visual review is human, not replaceable by tests alone.
11. **Release:** stage new version at `public/preview/` in the expressly authorized GitHub repo, verify blob SHA. Only replace production report/homepage with user's explicit release authorization. Distinguish **locally rendered**, **browser-tested**, **Git committed**, **Cloudflare live URL independently tested**. Never equate these.

## One-company acceptance and honest generalization

The 2026 H1 Tianfu 185-page filing is a source-matched, audited **regression case**. Automated PDF candidate discovery and cross-issuer *ledger-to-HTML* rendering now run, including a second synthetic industrial fixture. This is NOT the same as zero-touch report-grade analysis of every A-share filing. Banks/insurance are intentionally blocked. Full annual/hybrid/OCR inputs require manual source review and sector-specific adapters. Do not call the entire platform universally automatic.

## Usage

```bash
python engine/probe_pdf.py company.pdf --out output/candidates.json
# MANUALLY inspect source candidate pages and approve a normalized ledger + memo
python engine/source_audit.py --pdf company.pdf --ledger examples/company-ledger.json --out qa/source.json
python engine/audit.py examples/company-ledger.json --pdf company.pdf --out qa/accounting.json
python engine/render.py --ledger examples/company-ledger.json --memo examples/company-memo.json --out output/research.html --qa qa/finance.json
python -m unittest discover -s tests -p 'test_*.py' -v
python tests/browser_acceptance.py output/research.html qa/browser
```

Read detailed domain research from the existing `references/research-method.md`, `references/ashare-accounting.md`, `references/sector-playbooks.md`, `references/visual-editorial.md`, `references/quality-gates.md` and `references/tianfu-research-case.md` in the `financials` repo. The above commands assume this bundle's root directory and installed `PyMuPDF` + `Playwright/Chromium` for analysis/QA (the HTML output itself requires no Python/Node/CDN).

## Conditions that block 'publication-ready'

- Source PDF SHA mismatch, misread unit/period/reporting scope, critical reconciliation failure, unsigned or fabricated financial segment, any invented causal assertion or misleading graphic.
- Unresolved major source image/text issue, inappropriate sector renderer, inability to establish actual figure data or broken browser interactions.
- Public Pages address not independently verified, even when GitHub push succeeded; cite link as *expected* rather than proven until measured.

## Regulatory/version awareness

Follow issuer's actual accounting rules **as of report period**, not today's future-effective CAS changes. CSRC 2025 annual report format revisions effective July 2025; MOF CAS30 issued Aug 2026 with future staggered effective dates (some listed firms 2027, other mainland issuers 2029 unless early adoption). New regulator guidance is not automatically applicable retroactively. See official regulator links in `references/ashare-accounting.md`.