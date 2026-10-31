# Financials in Visuals · 2026H1 Optical Supply Chain Research Edition

This is an **original, independently verifiable research-design demonstration** of [Research Skill v8](../SKILL.md), not an App Economy Insights graphic clone or proof of full-sector automation.

## Independent studies

- [22-rule editorial design manual](../research/03_VISUAL_EDITORIAL_SYSTEM.md): AEI original public methods, plus the separate Financial Times Visual Vocabulary.
- [20-stage institutional A-share forensic guide](../research/04_ASHARE_FORENSIC_DEEP_DIVE.md): CSRC half-year/annual rules, MOF CAS revenue/impairment, operating economics, separate financial-sector treatment.

## Deliverable

- Site: `/optical-2026h1.html` (standalone HTML full report, **not an iframe**).
- Three 2026H1 **user-uploaded originals**: Tianfu (185 pages, 300394), Zhongji (184 pages, 300308), Xinyisheng (134 pages, 300502).
- Six distinct visual relationships: zero-origin YoY revenue growth, 2025→2026 gross margin dumbbell, CFO/consolidated-net profit, signed cash-CapEx/FCF, dated receivables+inventory asset share, and 100% assets decomposition.
- No stock price, valuation multiple, made-up customer concentration or invented 800G/1.6T mix. Tianfu is an upstream optical parts/connection supplier and not a perfectly comparable module assembly peer.

## Reproduction

The original PDFs and normalized ledger JSONs are intentionally not committed with this example. Copy `case-map.example.json` to `case-map.json`, replace the relative paths with your own real original PDFs/ledgers (resolved relative to this mapping file), and run:

```sh
python engine/build_comparative.py --source-map case-map.json --out outputs/optical-2026h1.html --qa qa/financial-validation.json
python -m unittest discover -s tests -p 'test_comparative.py' -v
python tests/browser_qa.py
```

Tests use the exact prior local original-PDF fixtures in the authoring environment; another machine must supply them or adapt the fixture path mapping. The engine verifies hashes and exact Yuan arithmetic; it does not automatically read arbitrary PDFs. Financial-institution analysis requires separate engines.

## QA / release state

- Original 3 PDFs SHA256 inspected, exact revenue–COGS–GP checks; 13 local unittest passes.
- Chromium static article 1440/768/390: all passed locally, six SVGs, correct cash-nav anchor, no external HTTP requests, no page-body overflow.
- `INDEPENDENT_SECOND_FINANCIAL_EDITOR=NOT_CHECKED`.
- `CLOUDFLARE_PUBLIC_HTTP=NOT_CHECKED` (do not claim deployment from source commit alone).
- Distinct reports `/300394.html`, `/300308.html`, `/300502.html` must remain full-size, independent webpages.
