# FINANCIALS IN VISUALS / PROJECT_STATE.md

> **LATEST CHECKPOINT IS AT THE BOTTOM**: use the schema-driven publisher validation and latest Library archive; older paragraphs are retained as historical evidence.
Updated: 2026-11-02 · Working branch: `pdf-source-validation-2026h1` · **Not merged to main**

> This is the **first file** every new ChatGPT session must fetch. Next read `skills/ashare-financial-storytelling/SKILL.md` from the CURRENT branch and its four `research/01...04` dependencies. Never claim project familiarity before reading the actual latest sources and code.

## Mission / immutable requirements
Transform ORIGINAL Chinese A-share financial filings into independent, offline-capable, source-audited original editorial HTML equity research. Business/economics before the graphics, strict PRC CAS and CSRC reporting semantics, balanced bull/bear and falsification, full original page routes, not iframe, not a uniform KPI dashboard. Benchmark public App Economy Insights analysis and Financial Times visual vocabulary without copying third-party assets. Target Cloudflare project `financials-in-visuals.pages.dev`; only repo `kobolibra/financials` is in scope (never touch `quantitative_analysis`).

## Git and execution contract
- Last verified production `main` HEAD before this branch: `c42347d01325b13cea4fba8b4b45a342a9443d07`. Re-query; do not assume immutable.
- Original main Skill is v8.0.0 (blob `5e15f7df0a34f669307fb4b730a8e2a818348a47`).
- The **working branch** has an updated v8.1.0-RC1 Skill and the acquisition workflow, but this is a candidate, not a production release. Merge only after independent review and end-to-end QA.
- Validated PDF-fetch GitHub Actions: https://github.com/kobolibra/financials/actions/runs/41413522262 ; ZIP artifact `verified-original-2026h1-pdfs` ID `13127020520`, seven-day retention. Re-run the workflow after expiration or persist the exact originals to long-term storage.

## Verified issuer sources (exact bytes)
| Ticker | Issuer | Filing | Physical pages | Byte size | SHA-256 |
|---|---|---|---:|---:|---|
| 688111 | 金山办公 | 2026H1, unaudited | 199 | 1,332,059 | `ec2322dc3a4461eef43045361391c0efe5673794302e329d03c7bbb8a3ad15a4` |
| 600519 | 贵州茅台 | 2026H1, unaudited | 110 | 832,321 | `0e10aa26be46b1cf3cd03f06e834c7fb98d5dd0d661b96f8fddd4af7e846a4f6` |
| 000333 | 美的集团 | 2026H1, unaudited | 205 | 3,825,459 | `576dd80e353e53296a800b03e9889a9cbb2e8b91fa2ab3c1dace7c10159179b8` |

**Crucial:** The previous original optical-sector cases were 300394 (Tianfu), 300308 (Zhongji), 300502 (Xinyisheng). These three newly fetched sources are cross-sector stress tests, not replacement for the existing HTML pages.

## Persistent cross-chat archive (confirmed 2026-11-02)

The verified complete local artifact package has been uploaded to the user's **ChatGPT Library** folder `/Financials-in-Visuals` (not temporary conversation attachment alone):
- `/Financials-in-Visuals/2026H1-cross-sector-verified-package.zip` — original 3 PDFs, SHA manifest, source ledgers, exact-source/finance/browser QA logs, 3 HTML reports, directory, rebuild scripts and research/handoff documents; Library ID `libfile_5e4b9c46a2c0819192f683807ca874f2`.
- `/Financials-in-Visuals/2026H1-html-previews.zip` — 3 HTML reports and directory; Library ID `libfile_c89e84f6260081919db467937a996211`.

A new ChatGPT conversation should use `files__list` or `files__search` scoped to Library to locate these files, then `files__materialize` for raw ZIP bytes if rebuilding. A future session must NEVER assume `/mnt/data/...` paths persist across conversations. Re-validate SHA after extraction. This archive snapshot is **work-in-progress**, not released production.

## Current local artifact status
During the session that authored this file, a separate local package `financials_v8_case_study/` was created, containing:
- `sources/<ticker>_2026H1_original.pdf` and `sources/source-manifest.json`;
- `research/<ticker>_2026H1_ledger.json` for 31 / 29 / 32 selected values (92 total);
- `qa/<ticker>_source_check.json`, `qa/accounting_arithmetic.json`, `qa/browser.json`, Chromium figure screenshots;
- scripts `verify_source_ledgers.py`, `financial_checks.py`, `build_reports.py`, `browser_qa.py`;
- standalone HTML `reports/index.html`, `reports/688111.html`, `reports/600519.html`, `reports/000333.html` (7 / 6 / 7 figures, **20 total**);
- `RESEARCH_AUDIT.md`, `NEXT_SESSION_START.md`.
The files are currently generated **conversation artifacts**, **not yet in main Git or on Cloudflare**. In a future chat, retrieve these from a user-saved deliverable package if present, else rebuild after retrieving the PDFs. Never invent sandbox paths from this note.

## Actual pass/fail audit
| Gate | State |
|---|---|
| Original PDF bytes, SHA, page count and issuer/period | **PASS 3/3** |
| Selected physical-page numeric matches | **PASS 92/92**, limited to selected facts |
| Targeted exact-yuan reconciliations | **PASS 11/11** |
| Source field **semantic** correctness and full 3 statements | **PARTIAL / NOT_CHECKED for comprehensive coverage** |
| 3 issuer HTML research-preview builds | **DONE in conversation workspace**, not deployed |
| Chromium `set_content` render-only at 1440/768/390: no JS errors, body overflow or remote runtime requests | **PASS 12/12** |
| Actual file/HTTP navigation | **NOT_CHECKED**: admin policy blocked both `file://` and localhost navigation; links verified structurally only |
| Per-figure independent financial editor and publication-level visual audit | **NOT_CHECKED** |
| Live Cloudflare HTTP and production identity | **NOT_CHECKED**, no production edit |
| Real cross-sector 8–12Q history, price/valuation/peers | **NOT_CHECKED**, not in filing-only scope |

## Important lessons that changed the Skill
- Download **real PDF bytes before narrative**; current container had no network/DNS but GitHub Actions ran successfully.
- Midea's graphic cover lacked machine-extractable ticker text. Don't reject PDF solely because first 2 pages do not contain ticker.
- Correct physical PDF pages vs report printed pages, and preserve Chinese units 万元 vs 千元 vs 元. Earlier ledger citations were shifted; corrected by PDF numeric page matching.
- Kingsoft's PRC GAAP parent profit, regulatory deducted parent profit and company-defined adjusted non-GAAP profit require three distinct definitions and tax/SBC/investment caveats.
- Moutai finance subsidiary affects consolidated CFO. Cash-flow table **outflow** row with negative number has POSITIVE impact on net CFO (`CFO=inflows-outflows`). Must transform sign with a visible audit note; don't make a misleading negative bar.
- Midea's business segment taxonomy has parent/children; geography is another axis. Prevent double-counting. Pretax derivative gains do not directly equal after-tax non-recurring difference.
- Long SHA strings caused 390px body overflow; fix all unbroken sources. Scrollable SVG must have a fully readable mobile summary visible without swiping.
- Browser render tests using `set_content` are NOT a substitute for route and deployed HTTP QA.

## Next work to make this more than a preview
1. Persist artifact package + primary PDFs beyond Action seven-day TTL. Save release inputs and report generator to repo or persistent Library and record their stable IDs here.
2. Expand selected 92 facts into full consolidated three statements, indirect CFO adjustment ledger and note-level accounting review; add independent dated comparables and source proof.
3. Rebuild the 20 charts against full statement and figure contracts; demand genuinely distinctive flagship charts, semantic and visual critic's screenshots, keyboard/table exports.
4. Independent red-team analyst and financial editor; acknowledge material unresolved claims.
5. Real HTTP routing test on Cloudflare preview, not just local Chromium `set_content`. Preview first, then production after passing all hard gates.
6. At every milestone update this file with exact HEAD, Skill blob, source inventory, tests and blockers. A new conversation should **not** reread the old long conversation to reconstruct the status.

## 2026-11-02 · v8.2.0-RC1 cross-sector generalization checkpoint (newer than earlier sections)

**Latest candidate Skill:** `skills/ashare-financial-storytelling/SKILL.md` on the working branch, version `8.2.0-rc1`, blob SHA `4deb260c34185b94211544a3f170987e8ecc8756`. Required additional reference: `skills/ashare-financial-storytelling/research/05_CROSS_SECTOR_GENERALIZATION.md`. Both files committed on working branch; `main` remains unchanged. Recheck branch and blobs before using.

**Three new real original issuer reports validated via GitHub Actions:** successful run https://github.com/kobolibra/financials/actions/runs/41417826429 (first access-blocked source run failed). The stable document identities and checks:
| Ticker | Sector | Pages | PDF SHA256 | Original canonical PDF |
|---|---|---:|---|---|
| `600036` 招商银行 | Commercial bank | 247 | `0194f5122575ee8576dbce941fcc10fb171e0cd17c627dd63330da952c52b57c` | https://static.cninfo.com.cn/finalpage/2026-08-28/1225531453.PDF |
| `601318` 中国平安 | Insurance/bank/AM holding | 176 | `f42140b5ad6ca7577d746dad57fd43a7bbc11ee0e360f61c2ed52bd7a4f4a54b` | https://static.cninfo.com.cn/finalpage/2026-08-21/1225487480.PDF |
| `000002` 万科 | Property developer | 234 | `50813d4f08f812bab70d14fc257638b46d1b5ae138b91db7d11b1845f31c649a` | https://disc.static.szse.cn/disc/disk03/finalpage/2026-08-28/f8d56d6e-4a78-464f-8f31-79d70275b258.PDF |

**Persistent cross-conversation archive (Library upload SUCCESS):**
`/Financials-in-Visuals/2026H1-universal-validation-v8.2.zip`, Library ID `libfile_50a95412f6a88191a8693c52834019f6`, ZIP SHA256 `d81340ee80bebcdde3a58a07f07de7d1c1cdb33d39e3a66204aa00943b4b1f9d`. Contains five original PDFs (3 new bank/insurance/property + prior Midea/Moutai required for mixed-revenue tests); prior Kingsoft original PDF is in the **earlier** archive in the same Library folder. Also contains:
- `sector_profiles.json` (12 distinct economic/accounting routing contracts),
- `engine.py` (typed fact and period/scope validation, sector routing, diagram restrictions, sign and taxonomy checks),
- `test_engine.py` 18 synthetic adversarial tests,
- `test_hybrid_revenue.py` original PDF economic/finance-overlay test for Midea p98 (RMB thousands) and Moutai p30 (RMB yuan),
- `real_corpus.py`, `qa_real_sources.json` (44 selected PDF-page numbers and 7 targeted identities),
- `render_sector_cases.py`, `reports/index.html` + `reports/600036.html`, `601318.html`, `000002.html`,
- `browser_verify.py`, `qa_browser.json`, 1440/390 screenshots of 3 companies and each flagship chart,
- `GENERALIZATION_AUDIT.md`, `README_REPRODUCE.md`.
Python experimental code is in this **Library ZIP**, not yet Git-tracked. DO NOT assume scripts live in the repo.

**Current actual gates:**
- PDF original bytes/identity/pages/SHA new sectors: `PASS 3/3` (six original issuers across two archived packages including prior cases).
- Selected literal PDF physical-page numerical string matches: `PASS 44/44` **new sectors only**; earlier cases 92 selected matches. **NOT** full semantic three-statement verification.
- Bank/insurer/property targeted accounting identity and Vanke review emphasis tests: `PASS 7/7`.
- Hybrid ordinary-revenue vs total-revenue identity from Midea and Moutai physical original PDF pages: `PASS 1/1` test with two real source cases. Midea 260,042,490+1,009,683+206=261,052,379 (RMB thousand); Moutai 90,703,260,964.48+1,574,811,118.73=92,278,072,083.21 (RMB yuan).
- Sector routing and unsafe chart tests: `PASS 18/18` synthetic; including hybrid overlays, signed cash, stock vs flow and additivity.
- Standalone three new evidence-driven HTML previews (3 research relationship exhibits each) with self-contained SVG and accessible values: `DONE` **in persistent Library only**, not main Git or Cloudflare.
- Chromium **render-only** at 1440, 768 and 390: `PASS 9/9`, checked text orphan/overflow and SVG export; first-figure screenshots reviewed. **Actual file/HTTP site navigation NOT_CHECKED** due environment policy.
- Complete all-three-statement semantic and note-level review for all industries, proper independent equity-research multi-period analyses, second real issuer per industry, second financial editor and publication-level figure critique: `NOT_CHECKED`.
- Cloudflare preview/production live serving & identity: `NOT_CHECKED`. Do not claim deployed or institutional-production-ready.

**Crucial quality lesson / generalization gate:** A list of 12 sector profiles is **not** 12 production adapters. At most first-case Level-1 prototypes are supported for new bank, insurance-group and property examples. An actual supported industry needs independent real-source tests on 2 issuers and full relevant statement/research/editorial/browser gates. The user expects excellence; maintain visible failing tests and gaps rather than hiding them under version numbers.

**Next uncompleted work:** (1) move Library source code into source-controlled `nextlevel` or a dedicated universal engine (do not disturb existing company HTML), (2) two or more real issuers per significant accounting sector and a restatement example, (3) exact full consolidated statements and material notes plus independent second-pass source review, (4) financial figure data schema and tests for impossible economic claims, (5) accessible real-served URL navigation with screenshot review of every diagram, (6) compare editorial quality against public AEI research without copying, (7) Cloudflare preview followed by intentional promotion only after evidence-backed acceptance. Always update this state file after further verified changes.


## 2026-11-02 · LATEST shared-publisher generalization checkpoint

**The hardcoding gap was partially fixed and proven on 5 real companies.** Earlier `render_sector_cases.py` had issuer-specific branching. The newer `generic_publisher.py` takes `generic_case_specs.json` and selects figures *only* from three generic accounting relationship families (`additive_composition`, `signed_bridge`, `stock_comparison`). The renderer has no company-name or ticker-specific branches; per-company fact mapping remains human curated. Five original verified reports were used: 招商银行 600036, 中国平安 601318, 万科 000002, 美的集团 000333, 贵州茅台 600519; 17 original PDF-bound graph source fields verified. This is a bounded technical success **NOT a general arbitrary-PDF to institutional full-research system**.

**Latest persistent reproducible archive:**
`/Financials-in-Visuals/2026H1-generalization-v8.2-verified.zip`
Library ID `libfile_3198bde6d9b48191a09cdcc2768fac8e`.
Exact ZIP SHA256 `18de1a39afdb9f733587c6891ebe0744ff4e39fdd4d4aa37b6014bdaa9e600da`.
Contains all five original PDFs necessary for the demonstrated generic examples, industry type rules, previous 3 sector-specific webpages, 5 NEW schema-driven webpages plus index, screenshots, source ledgers, 26 unit tests, browser QA and reproduction instructions. **A clean extraction of the ZIP in a new directory regenerated all five HTML files and ran all 26 tests successfully.**

Small HTML-only archive:
`/Financials-in-Visuals/2026H1-five-sector-html.zip`, Library ID `libfile_3a49c80e945c8191bb4ec6e4b817d3f9`.

**New gates:** `PASS 5/5` cases through the same schema-driven renderer; `PASS 17/17` identified original PDF page values and identity formulas; `PASS 26/26` local unit/adversarial tests (18 sector, 7 generic, 1 hybrid covering two prior real PDFs); `PASS 15/15` 5 issuer × 1440/768/390 Chromium render-only checks. Visual human critique detected that original insurer GAAP/operating profit adjustments were almost invisible because of ratio compression; fixed by separating zero-start profit scale and an EXPLICIT independently labeled adjustment scale. The final screenshot was visually inspected. **Actual served-URL/browser navigation, independent financial-editor, full 3-statement material-note analyses, all-sector source extraction, year/quarter history, and deployed Cloudflare status remain NOT_CHECKED.**

**Original repo state:** As of this checkpoint candidate `Skill v8.2.0-rc1` (blob `4deb260c34185b94211544a3f170987e8ecc8756`) and fifth research manual are on working branch only. Experimental five-sector Python publisher and assets are stored in this Library archive, not Git. Do not claim the user has a complete v8.2 production release. Never merge code or deploy without verifying real independent production routes. For future session: read this `PROJECT_STATE.md`, branch Skill, manuals 01–05, materialize this latest archive with `files__materialize`, run documented exact tests, and follow unresolved checkpoints.
