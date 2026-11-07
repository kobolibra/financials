---
name: ashare-financial-storytelling
description: Original-PDF-grounded A-share public company research, institutional financial breakdown, AEI-informed original Sankey and signed cash-flow visuals, standalone HTML publications, real mobile/desktop QA, financial evidence gates, and zero-memory cross-session handoff. Use for kobolibra/financials research, any new issuer or reporting period, report regeneration, visual quality problems, Skill improvements, source reconciliation and PR release approval.
---

# Financials in Visuals — one production contract

Contract version: 9.0.0

**This is a decision-and-execution Skill, not a record of earlier successes.** The 125 KB append-only historical v8.8 notes are preserved in `docs/history/ASHARE_FINANCIAL_STORYTELLING_SKILL_V8_8_ARCHIVE.md`; historical claims there NEVER authorize a current release. The five research manuals below provide accounting/editorial detail, while this file decides what to execute, what can be published and what must be rejected.

## 0. Start from actual source of truth, not chat memory

Read `START_HERE.md`, `project-status.json`, `PROJECT_STATE.md`, `AGENTS.md`, `docs/HANDOFF_PROTOCOL.md`. Re-query actual GitHub main/PR HEAD, reports in `site/research_catalog.json`, their source PDF SHA, live main and Cloudflare candidate. Do not confuse unmerged PR #35 with production `main`; see `docs/ACTIVE_PR35_HANDOFF.md`, `research/quality/active-pr35.json`, `docs/AEI_RESEARCH_EDITORIAL_SCORECARD.md`.

Read these **five complete research guides** when doing report research or visualization:
- `research/01_APP_ECONOMY_INSIGHTS_RESEARCH.md`: evidence-backed public AEI benchmarks, no copying designs.
- `research/02_ASHARE_INSTITUTIONAL_RESEARCH.md`: issuer mechanism, unit economics, comparables, capital.
- `research/03_VISUAL_EDITORIAL_SYSTEM.md`: editorial hierarchy, color semantics and precise chart selection.
- `research/04_ASHARE_FORENSIC_DEEP_DIVE.md`: original note cells, reclassifications and audit traps.
- `research/05_CROSS_SECTOR_GENERALIZATION.md`: banks/insurance/industry-specific accounting; unseen samples.

## 1. Research must precede drawing

For **every** report, create five decision-bound items linked to literal source fact IDs, issuer, reporting period, original PDF SHA and physical pages:

1. One falsifiable company-specific thesis about the business model, not generic KPI growth.
2. A ledger-backed quantitative driver equation with directly disclosed vs derived vs hypothesized values separated.
3. The strongest serious alternative explanation and the specific original evidence that would distinguish it.
4. Business durability and reinvestment/working capital/credit/capital constraints, with explicit cash and profit scopes.
5. What is NOT_CHECKED: missing peer/8–12 quarter/volume-price/valuation data; never fabricate.

Each figure receives a **five-second editorial brief** (question, graphically provable answer, key comparison, contradictory evidence, exact fact IDs, scope, unit, period, disclaimer, why this graphic). Four actual v10 hero examples: `research/quality/pr35-hero-figure-briefs.json`. Figure counts and test counts are never analytical-depth scores.

## 2. Use one semantic compiler, one money-flow renderer

**Classify legal accounting before any shape**: full source bytes+physical PDF pages → exact Decimal CNY yuan facts → source exclusivity / period / consolidated basis / sign → flow type. Shared type contracts: `research/shared/editorial_financial_flow.py` and `scripts/audit_v10_flow_contract.py`.

**Canonical visual design engine for nonnegative conserved profit flows**: `research/shared/unified_income_sankey.py` with issuer adapter `research/rebuild-v10/unified_finance.py`. Never introduce another custom company Sankey, hard-coded label/width template or an 850px phone scroller. `data-design-system="FINANCIALS_UNIFIED_STORY_V1"` must be present in both independent desktop and mobile editions.

- **TYPE A**: source-specific disclosed revenue AND own cost, with exact own GP; use actual source → **one total revenue node** → separate own COGS/GP paths → group cost/GP. Exact original-yuan scale, no fabricated per-business allocation. Example: 688111 WPS.
- **TYPE B**: mutually exclusive revenue sources but only group cost known; source → total revenue → group COGS/GP; in readable Chinese directly state that PRODUCT GP is unknown. Do not imply source-level GP, not even through visual color blending. Example: 000333 Midea.
- **BANK**: net interest already deducts interest expense; combine net interest, net fees, other net income → **one** bank net revenue node → disclosed operations/credit costs and operating profit. Not industrial GP. Example: 600036 CMB.
- **TYPE C / incompatible**: overlapping categories, negative segment GP, insurance premium vs CAS service, stocks mixed with flows, currencies or dates inconsistent → omit a positive Sankey, use signed waterfall, true-scale comparison, or two-date stock. Example: 600519 Moutai negative small business GP; use a **true-scale signed main chart** plus explicitly independently scaled source-backed inset. An unobservable -0.04 SVG-unit bar MUST NOT be faked into 1px.

Use consistent semantic colors: neutral blue-grey = income sources, dark charcoal = actual total, muted copper/red = costs, green = profit, separate copper sign for negative. Each path includes amount, source key, role/stage, exact conversion factor, original ledger proof. Source widths, middle node and final sink widths must each conserve the **same** original yuan, with no phantom balancing flows or zero-value minimum width.

**AEI is a structural benchmark, not an art asset**: use public Apple illustration as a test of continuous coherent P&L grammar, directly placed amounts/margins and hierarchy, but create original artwork and distinct brand typography. The original design is not a license to copy or claim endorsement. Current authoritative geometry/structure: `docs/UNIFIED_FINANCIALS_VISUAL_STANDARD.md`.

## 3. Mobile/desktop independent art direction

Every genuinely material figure needs separate responsive design at 390 / 768 / 1440. Do not hide a complex source figure on phone, stretch 1040 SVG into a 330 column, or celebrate horizontal scrolling as PASS. On both platforms: real business labels, readable font, specific period and currency, visible zero baseline/scale for signed values, no clipped text or overlapping critical nodes, source PDF table, accessible download of the **currently visible** SVG. A 12-path graph without meaningful label hierarchy is not visually certified.

**Reject by design:** raw machine sentinel visible in Chinese article, product margin inferred from corporate rate, negative cost/revenue positive ribbon, business parent and child double-addition, bank double interest, gorgeous rainbow ribbons without a readable economic insight, a single generic KPI chart substituted for the promised signed bridge.

## 4. Mandatory REAL gates; do not conflate their scopes

Run applicable tests *on current bytes*, not yesterday's Action:
`python scripts/check_handoff.py`;
`python scripts/check_pr35_quality_handoff.py`;
`python -m unittest discover -s scripts -p 'test_check_pr35_quality_handoff.py' -v`;
`python -m unittest discover -s research/rebuild-v10 -p 'test_editorial_chart_quality.py' -v`;
`python scripts/audit_v10_flow_contract.py --strict`;
`python scripts/audit_aei_editorial_delivery.py --fail-known`;
`python scripts/check_release_contract.py`.
Then execute original SHA-PDF reconstruction, actual CJK Chromium on 1440/768/390 and WebKit phone width, source geometry/label/screenshots, actual Cloudflare **complete HTML bytes**, 11 issuer routes and visible-SVG export, and verify production SHA only after authorized merge. Single candidate/issuer PASS is **not** all 11 PASS.

**Three independent approval axes**: FINANCIAL_SOURCE / ANALYTICAL_DEPTH / VISUAL_ART_DIRECTION. Source auditor, meaningful editorial blind reading, and deployment operator sign off separately. Passing geometry and browser tests does NOT imply AEI-level excellence. If independent human editor has not actually reviewed, state NOT_CHECKED. If 20–30 unseen independent reports have not been repeated across industries/periods, claim only the exact observed issuers and periods.

## 5. Zero-memory, rollback-safe handoff

After any change, regenerate actual HTML from source; bind PDF/ledger/build/HTML/SVG/CJK PNG/Cloudflare responses to real SHA. Update `project-status.json`, top of `PROJECT_STATE.md`, `docs/ACTIVE_PR35_HANDOFF.md`, regression registry, PR and Actions links. A new session must re-query latest HEAD and run gates, never inherit stale evidence or use prior chat as authority. If a prior publisher family is not yet migrated, mark **LEGACY_VISUAL_NOT_UNIFIED**, do not falsely certify 11/11.

**Release stop rule**: if any financial P0, visual P0, misattributed profit, stale PDF/screenshot bytes or unreviewed serious claim remains, keep PR draft/unmerged or explicitly record a source-limited preview. No automatic "top tier" badge or claim until double human finance/art review and genuinely unseen reproducibility benchmark.
