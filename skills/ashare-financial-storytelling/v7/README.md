# Financials in Visuals · Editorial Research Edition 7

**Why v7 differs:** Research is now separated into two first-party source-based pillars. Read `research/01_APP_ECONOMY_INSIGHTS_RESEARCH.md` (business-first, complete chart grammar and art direction) and `research/02_ASHARE_INSTITUTIONAL_RESEARCH.md` (CAS/CSRC financial and forensic work) before producing an issuer report. No assumption that a beautiful Sankey equals financial insight.

**Original real-case article**: Tianfu Communications (300394.SZ), 2026H1, 185-page unaudited source PDF SHA `6f508be2da82fb7b1728e2e638b5ce721baa3cf98a64234db636358019d913f5`.

**v7 article**: 10 original analytical exhibits: (1) product revenue→GP→operating core, (2) signed income waterfall to net profit, (3) gross-profit delta bridge, (4) two-period margin profile, (5) all-adjustments net income→CFO, (6) opening-to-closing cash, (7) analyst-defined CFO/cash CapEx/FCF, (8) balanced asset & funding architecture, (9) operating stock change, (10) correctly denominated AR and supplier-prepayment concentration. Includes source pages, alternative explanations, monitoring questions, exact-yuan tables and qualitative restrictions.

**Run:**

```bash
python engine/render_v7.py --ledger engine/sample-ledger.json --memo engine/sample-memo.json --out outputs/tianfu-research-v7.html --qa qa/v7.json
python -m unittest discover -s tests -p test_v7.py -v
python tests/browser_acceptance.py
```

**Verified locally:** real-PDF source fingerprint, exact accounting identities, 12 adverse/input tests, Chromium at 1440/768/390 without page-level scroll, source trace display, keyboard tooltip and SVG export, no remote runtime requests. GitHub blob and Cloudflare HTTP checks are separate. Any unverified public deployment remains marked not verified.

**Honest generality boundary:** this renderer is generic for data-rich **industrial/services ledgers** meeting source requirements; it does not auto-approve PDF OCR or take investment decisions, and its substitute-company test is synthetic, not a second real issuer. Banks, insurers, brokers, property and multi-quarter market/valuation/peer work require specialist inputs and templates, not fabricated visuals.