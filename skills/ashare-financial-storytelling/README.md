# FINANCIALS · Research Desk v5

> From publicly filed Chinese A-share financial reports to an evidence-backed, audited, distinctive **single-file HTML research publication**.

This package fixes two concrete gaps in prior versions: (1) the financial HTML renderer is no longer hardcoded for Tianfu; it accepts typed ledgers and curated memos from different industrial issuers, with fail-closed financial industry routing; (2) browser screenshot and interactions are actually tested on 3 viewports. It also provides a real PDF evidence **candidate extractor**. **It does not hallucinate full autonomous institutional analysis** from an unseen PDF; human approval of the accounting statement cells and analyst thesis remains part of the quality contract.

## What is included

- `SKILL.md`: full workflow contract and gatekeeping.
- `engine/probe_pdf.py`: generic searchable-PDF candidate extraction, including raw passages and page provenance.
- `engine/source_audit.py`: original PDF SHA and exact/fragmented source value presence check.
- `engine/audit.py`: source-ledger financial identities and scope.
- `engine/render.py`: industrial issuer ledger + research memo → original fully self-contained HTML.
- `examples/tianfu-ledger.json`: reviewed 59 structured financial facts, including 10 newly added working-capital concentration lines and 15 separately signed indirect-CFO adjustments.
- `examples/tianfu-memo.json`: editorial research thesis, alternative and falsifiable follow-up, manually reviewed.
- `tests/test_engine.py`: 9 unit and adversarial tests including second synthetic issuer, mismatched arithmetic, inappropriate bank template and incomplete segmentation.
- `tests/browser_acceptance.py`: actual Chromium offline browser smoke + screenshot + SVG export/interaction.
- `outputs/tianfu-2026H1-v5.html`: independently browser-rendered deliverable; the PDF itself is deliberately not included.
- `qa/`: original ledger audit, source-text cross check, viewport screenshot and acceptance JSON; separated publication states.

## Reproduce the Tianfu case

```bash
python -m pip install pymupdf playwright
# Browser QA uses installed system Chromium: /usr/bin/chromium
python engine/probe_pdf.py original_report.pdf --out outputs/candidates.json
python engine/source_audit.py --pdf original_report.pdf --ledger examples/tianfu-ledger.json --out qa/source-audit.json
python engine/audit.py examples/tianfu-ledger.json --pdf original_report.pdf --out qa/audit.json
python engine/render.py --ledger examples/tianfu-ledger.json --memo examples/tianfu-memo.json --out outputs/tianfu-2026H1-v5.html --qa qa/finance.json
python -m unittest discover -s tests -p 'test_*.py' -v
python tests/browser_acceptance.py outputs/tianfu-2026H1-v5.html qa/browser
```

If using a different report, **replace** the sample ledger and memo with a reviewed issuer-specific pair, not merely the issuer's name. Changes in source period, accounting scope or product dimensions must trigger a new audit. For a bank/insurer, do not reuse industrial charts.

## Truth-in-publishing

- `PDF_INTAKE`: source candidates, not approved data.
- `ARITHMETIC_AUDITED`: sourced figures internally reconcile, not equivalent to investment thesis verification.
- `ANALYST_REVIEWED`: reviewer has checked key original note/table lines, causal and rival arguments, and limits.
- `BROWSER_VERIFIED`: attached local Chromium tests and screenshots pass, visible layout inspected.
- `GIT_VERIFIED`: actual GitHub source blob SHA checked.
- `LIVE_VERIFIED`: independently fetched/rendered Cloudflare URL. Without it, do not assert public deployment works.

**Design provenance:** independent original design informed by publicly described App Economy Insights methodology (business anatomy, three-statement integration, earnings-to-cash and visual storytelling). No affiliation and no reused proprietary graphic.