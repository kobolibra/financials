# Financials in Visuals — v10 audited financial Sankey increment

Edition: 2026-11-03 v10. This **extends** the existing v9 research generator, not a new project or a replacement for the requirements of `skills/ashare-financial-storytelling/SKILL.md` and research manuals 01–05.

## Reproduction

From the archive root, with Python 3, `pymupdf`, `playwright`, `pytest`, and Chromium installed:

```bash
cd v9
python verify.py
python publisher.py
pytest -q test_sankey.py
python qa_browser.py
```

The original full issuer PDF bytes are under `work/` and checked by SHA256 before source facts are used. Each generated company page is entirely standalone HTML with inline SVG, styles and accessible original-data evidence table. `site/index.html` links to company pages.

## Exact flow diagrams

* `688111`: WPS business lines -> recognized revenue -> reported COGS + derived gross profit.
* `600519`: product categories -> recognized operating revenue -> reported COGS + derived gross profit. Financial-subsidiary interest revenue is not included in wine product revenue.
* `000333`: exclusive company top-level segments -> industrial operating revenue -> reported COGS + derived gross profit. Consolidated total revenue also includes finance subsidiary's interest and commission; that extra revenue is intentionally not mixed in the industrial COGS diagram. Industrial child categories are excluded from the top-level sum (otherwise double-counted).
* `600036`: net interest income, net fee/commission, other net -> consolidated operating revenue -> operating/admin + credit impairment + other expenses, and operating profit. Interest expense is already netted inside net interest income and must not be deducted again.

These diagrams are **area-conserving proportional flows**, not colored connectors. Sankey construction rejects negative or mismatched sums and source/target valence. Sources keep exact original yuan amounts for accounting identities; visible amounts use 亿元 rounding. The physical source pages remain cited in the figure's table and include access to each original PDF. Mobile keeps the actual visual in a figure-only horizontally scrollable area with a nearby independent accessible summary and original data.

## Publication boundaries

This work addresses a serious omitted requirement: the AEI-informed visual grammar. It does not certify full peer/valuation analysis, independent financial editor, complete material-note semantic audit, every industry of A-share or a claim to exceed AEI. Those gates remain separate. Do not claim completion based only on 4 valid Sankey diagrams or 7 test passes. Keep other v9 exhibits; a Sankey is warranted only when sources and uses truly conserve money.