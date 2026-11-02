# FINANCIALS IN VISUALS / PROJECT_STATE.md
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
