> **LATEST ACTUAL PRODUCTION IS 2026-11-03 V9**, not the historical v8.2 lab below. Read the **last checkpoint** first, plus the v8.3-RC1 Skill and the v9 release audit. Old lab fixtures are not research articles.

# Financials in Visuals · Current Project State
Updated: 2026-11-03
Production branch: `main`
Current main release: seven source-backed 2026H1 cross-sector **BETA** pages, published to the Cloudflare Pages project.
Last feature release commit: `3edfddcbbfb2a5ef56ad42a446110ca213f5edbc`
Active development branch: `pdf-source-validation-2026h1`

## Production status
- Homepage: https://financials-in-visuals.pages.dev/
- Cross-sector directory: https://financials-in-visuals.pages.dev/research-lab/2026-h1/index.html
- Seven standalone pages: `600036`, `601318`, `000002`, `000333`, `600519`, `600276`, `600900` under `/research-lab/2026-h1/<ticker>.html`.
- Original three optical company HTML and optical comparative report are preserved.
- Live Cloudflare external HTTP check of homepage, lab directory, and initial two company pages passed on GitHub Actions run 41424244962. Additional all-page browser QA is added in `.github/workflows/verify-pages-release.yml`; read the LATEST run before asserting it passed.
- Production Skill: `skills/ashare-financial-storytelling/SKILL.md`, **v8.2.0-RC3**. Fifth manual `research/05_CROSS_SECTOR_GENERALIZATION.md` is also on main.
- This is an intentionally limited public beta of one source-backed accounting relation per issuer, not complete industry/stock-research reports.

## Durable source/engine archive
In ChatGPT Library: `/Financials-in-Visuals/2026H1-seven-issuer-generalization-v8.2.zip`, Library file ID `libfile_975eb3a753708191a27057ae41801389`. All seven actual original issuer PDF bytes and SHA manifests, typed figure examples, generic renderer, tests, screenshots and historical research QA are preserved there. The separate original Kingsoft 688111 file is in `2026H1-cross-sector-verified-package.zip`.
Source evidence covers 7 real issuers and 4 basic figure relationships; old prototype tests show 28/28 unit and 21/21 render-only checks. Source QA is NOT a full independent audit of each issuer.

## Remaining high-priority product backlog
P0: Build full consolidated financial statement + significant notes evidence ledgers for multiple truly different industries, beyond one figure per company.
P0: Publication-quality full narratives, valuation only with reliable dated external evidence, opposing views, precise explanations of China CAS accounting.
P1: Independent second analyst and editor plus truly distinct visual grammars beyond four basics.
P1: Make generic publisher code + figure specs Git-tracked and run reproducible tests automatically, not just a Library ZIP.
P1: Ensure live browser routes / responsive screenshots and direct investor research readability; never fall back to iframe/mini scroll.
P1: Extend regression to second issuer per domain, amendments, restatements, cash/FX/CSM and regulated financial accounting.

## Working protocol for the next ChatGPT session
First fetch this MAIN `PROJECT_STATE.md`, main `SKILL.md`, 01–05 manuals and newest CI status. Then retrieve Library archive and verify original PDF SHA before touching numbers. Run existing CI and publish small beta versions to main continually; never wait for all 12 sector adapters to be complete before shipping a scoped, honest improvement. Archive original source bytes, current branch SHAs, exact QA PASS/FAIL/NOT_CHECKED and actual Cloudflare deploy URL after every iteration. Do not silently replace live reports; preserve existing URLs and provide versioned new research paths.

## 2026-11-02 · Editorial publication correction after direct production screenshot audit

User correctly rejected the live seven one-chart beta issuer pages as unprofessional and noncompliant with the Skill. Direct source check: one live bank article had 1 SVG, 2 sections and 1 source table, no substantive credit/loan/capital/cash research. Archived real Chromium screenshots at 1440/768/390 also showed Chinese glyphs as squares because the CI machine had no CJK font. Prior 'visual pass' status was invalid in editorial terms even though responsive width checks passed.

Corrective main release commit b08d6e52a5db9ce8f5c273d10a45193c40233ac2 features actual multi-figure source-based prior work on /research/2026-h1/index.html: 688111 Kingsoft 7 figures, 600519 Moutai 6, 000333 Midea 7. Main homepage now links these 20-figure research previews rather than treating seven one-chart technology samples as full research. Old beta paths remain accessible only as a separately identified method lab. Original 3 optical reports and comparative report remain intact.

Actual public Cloudflare HTTP and real Chromium page navigation, 3 issuer x 1440/768/390 = 9 live full-page research screenshots, SVG counts, no page-level overflow, original PDF links, homepage-to-directory-to-issuer-to-cash-section click sequence passed GitHub Actions run 41425735070, after installing Noto CJK and fixing Cloudflare canonical path test. A human review of those screenshots now confirms Chinese glyphs display rather than squares. This pass verifies publication functionality but NOT buy-side research quality, which remains a known unfinished objective.

P0 next work: upgrade bank, insurer, property, pharma and utility cases from single source relation to full company analyses (and remove research mislabeling); complete full statements, material notes, red-team research for existing 3, independent reviewer; more original and company-specific infographic types beyond the repeated basic chart grammar. Update tests and gate states after each production iteration.

## 2026-11-02 · 招商银行 600036 multi-figure research published

New issuer source-first edition: `public/research/2026-h1/600036.html`, 9 analytical exhibits, 9 SVG and source tables, bank-specific 5-chapter narrative. Reproducible source generator and browser QA are checked into `research/cases/600036/` without original PDF bytes in Git. Official 247p original source SHA `0194f5122575ee8576dbce941fcc10fb171e0cd17c627dd63330da952c52b57c`, physical page values checked, 10 accounting identity checks and local 1440/768/390 rendering PASS. Library case ZIP `/Financials-in-Visuals/2026H1-CMB-600036-nine-figure-research.zip`, libfile `libfile_07a2919c985c81918cb70538b77b597e`. Homepage and research directory now promote 4 2026H1 multi-figure preview studies/29 graphics. Production live route and CI browser acceptance must be verified on the latest ACTION RUN; do not confuse code commit with live. Remaining sector full research and independent financial-editor still pending.

## 2026-11-02 · VERIFIED PUBLIC RELEASE CHECKPOINT · 招商银行 full bank-native preview

Current actual first substantive new-sector report: public URL `https://financials-in-visuals.pages.dev/research/2026-h1/600036.html`, issuer bank 600036, nine financial exhibits from one audited-reproducibility workflow; homepage now features four multi-figure research previews with 29 figures, not seven one-chart experiments. Code files on GitHub main: `research/cases/600036/build_bank.py`, `research/cases/600036/check_bank.py`, `research/cases/600036/README.md`. Full 247-page original A-share issuer PDF sha256 `0194f5122575ee8576dbce941fcc10fb171e0cd17c627dd63330da952c52b57c`; stable ChatGPT Library bundle `/Financials-in-Visuals/2026H1-CMB-600036-nine-figure-research.zip` with Library ID `libfile_07a2919c985c81918cb70538b77b597e`.

**Public live acceptance SUCCESS**: GitHub Actions run `41428626353` (https://github.com/kobolibra/financials/actions/runs/41428626353) on commit `11ba278d43c041033ffa728d4000ff82aec85e83`; external Cloudflare live HTTP and actual Chromium navigation PASS, 12 research cases × viewport widths 1440/768/390 PASS, bank 9 figures + 9 data tables and source page links confirmed, no page overflow. Chinese CJK font installed, actual live desktop/mobile screenshots extracted and inspected. Screenshot artifact ID `13133926177`, name `live-cloudflare-beta-browser-qa`, uploaded by success job, retention 30 days. Earlier first run failed due CI wrongly requiring industrial `#cash` section on bank; changed to allow bank native capital/cash `#capital`, then retested SUCCESS. Current source scripts and content can be re-run with archived original PDF in Library. Prepublication selected 31 exact original numeric PDF page locations and 10 accounting identities PASS. **Still NOT independently certified:** all PDF important notes and full three-statement reconciliation, second bank case, independent finance peer/editor, eight-to-twelve quarter history, full product visual system. The report is RESEARCH_PREVIEW; no valuation or target price.

**Critical next active work:** Upgrade insurance and property from one-figure prototypes to native statement/solvency and cash/contract-liability/full-risk reviews, and iterate the existing four multi-figure reports with independently rechecked notes and editorial critique. Keep a direct public route and verify every incremental main release, not just GitHub commit.

## 2026-11-02 · P0 live article editorial correction checkpoint (latest)

- Full critical audit: `docs/FINANCIAL_REPORT_RELEASE_AUDIT_2026-11-02.md` (do not confuse technical PASS with finance/research PASS).
- `main` Skill is now v8.2.0-RC4 with publication classes and signed cash chart hard gate. Other six one-figure prototypes are engineering fixtures and `noindex`, NOT completed research.
- The bank full 9-exhibit preview signed cash-flow Figure 09 corrected, reviewed in the produced SVG screenshot, labels repositioned after first overlap. Generator and published page updated together (commit `18c524b901914933b814f3c1347cecc66ef7e4dc`); original PDF SHA, 31 page-located source numbers, multiwidth/figures/tables and SVG export tests passed locally. Real-site deployment checked through GitHub Actions, inspect most recent CI before reporting its final result.
- Public research pages are `/research/2026-h1/{600036,688111,600519,000333}.html`; 9/7/6/7 figures. All remain `RESEARCH_PREVIEW`, not institutionally fully independently reviewed.

## 2026-11-03 · LATEST: v9 REBUILT SOURCE-LIMITED RESEARCH RELEASE

Production index: `https://financials-in-visuals.pages.dev/research/2026-h1-v9/`, company URLs `.../600036.html`, `.../688111.html`, `.../600519.html`, `.../000333.html`. The old `/research/2026-h1/` pages are retained as archive; seven single-figure `/research-lab/` routes are engineering fixtures and not evidence of research publication.

**What actually changed:** Four complete original PDFs download & SHA match; restored consolidated current/prior balance sheets, cash closure, major income/segment identities; for Kingsoft, Moutai and Midea every original 16/15/13 signed indirect net-profit-to-CFO adjustment (44 total) was checked against exact PDF physical pages and reconciled to the yuan. The bank's entire statutory income-to-parent profit including tax/credit/NCI was rebuilt as a signed bridge. The Midea hierarchy unit bug, misleading signs and small nonzero commission rounded to zero were corrected. Four different industry-led article scripts yield **8+9+9+10=36** distinct sourced figures/data tables.

**Public browser:** GitHub Actions `41576887193` https://github.com/kobolibra/financials/actions/runs/41576887193 **PASS**: 12 real company/viewport checks at 1440/768/390, 36 source graph screenshots, CJK font availability, no body horizontal overflow or JavaScript errors, actual index→report→#cash→index navigation, SVG export. CI artifact `financials-v9-live-browser-evidence`, 30-day retention. Initial QA run failed because it falsely demanded ticker inside editorial title, fixed to inspect issuer metadata. Another browser run showed tofu Chinese glyphs without CJK fonts, fixed by installing font and rechecking actual screenshot. The final screenshot was opened and visually reviewed.

**Current Skill:** `skills/ashare-financial-storytelling/SKILL.md` version **8.3.0-RC1** in main, adding source-to-story and font/nonzero/sign/metric-type release gates. Native evidence scripts and source ledgers in `research/rebuild-v9/`. Source bytes and executable clean-room kit in the persistent ChatGPT Library `/Financials-in-Visuals/2026H1-v9.1-rebuilt-complete.zip` (Library ID `libfile_07d0b8f629688191a38dd1a3f733e96d`). Full code/doc screenshot archive is saved there; exact ZIP SHA from local current artifact `589e6b8ac944073fcda4a0ff2034f94987a17aabe74ae6c9a7c068b5aff4ad14`. Verified clean-unzip `python verify.py && python publisher.py` both PASS. HTML-only zip also saved in same Library folder.

**Publication classification:** `SOURCE_BASED_RESEARCH_PREVIEW` with strong accounting proof, NOT independent investment-rating equity research. **Still not complete**: all material notes independently reviewed by a second financial analyst, 8–12Q history and dated peer/valuation data, other sectors validated at full depth, real reproducible browser QA on non-CJK platforms, controlled quantitative scenario model. Do NOT infer full generalization from 4 examples.

**Next substantive increments:** (1) source-complete two more companies per material sector; (2) full appendix semantic verification of every figure row and relevant MD&A; (3) independent expert financial/editor review & true visual comparison to first-party AEI methods; (4) richer 8–12 quarter chart and peer valuation ONLY from original dated external evidence; (5) revisit four distinct issuer reports with new insight rather than increasing chart counts. Always retain URLs and run GitHub real Cloudflare CI after each release. Never fabricate tests or manual reviewer signoff.

## 2026-11-03 · VERIFIED homepage promotion and V9 live public acceptance

The **current main homepage** now features V9 at the top of the actual research catalog and hero CTA. Release homepage/Skill/PROJECT_STATE commit: `1980735109911e92568fce9535dbd2064d0daac0`. The latest live-acceptance workflow improvement commit `f9faf15806ae3364503a8585988e220816f8e079` additionally verifies the real public **homepage → V9 directory → bank report → #cash → directory** click path, not just direct report URL access. Both public homepage and full V9 are now proven through real Chromium.

**Latest confirmed CI run: https://github.com/kobolibra/financials/actions/runs/41577490124**, result SUCCESS, on 2026-11-03. This included four 2026H1 original-source article counts 8+9+9+10=36, actual CJK fonts available, all four company routes served by Cloudflare, 12/12 real responsive-width pages (1440/768/390), 36 per-exhibit browser screenshots at 1440, actual homepage navigation, #cash anchor, SVG export, no observed page-level horizontal overflow/JS errors. This CI verifies **technical/editorial rendering** but is not an independent expert-finance review.

**Canonical URL:** https://financials-in-visuals.pages.dev/research/2026-h1-v9/
**Persistent original-source + clean-room rebuild archive:** `/Financials-in-Visuals/2026H1-v9.1-rebuilt-complete.zip` Library ID `libfile_07d0b8f629688191a38dd1a3f733e96d`, exact SHA256 `589e6b8ac944073fcda4a0ff2034f94987a17aabe74ae6c9a7c068b5aff4ad14`, contains four full original PDFs, 5 standalone HTMLs, source data/QA/scripts. Opened ZIP in this run: archive passed integrity check, 35 entries, 4 original PDFs, 5 HTML files. HTML-only snapshot `/Financials-in-Visuals/2026H1-v9.1-html-only.zip` Library ID `libfile_0e2da349469481918c25da10c4c1763f`.

**Still blocked for independently certified institution-grade research:** a second financial editor's full source-row and material-note audit, external multi-quarter market/peers/valuation data, and per-sector replicability beyond four first-pass issuers. Never self-label “exceeds App Economy Insights”; continue actual source-driven improvements to the published V9 version. Old V8 and one-chart engineering lab remain archived with preserved routes and clear classification.

## 2026-11-03 · V10 source-conserved visual-storytelling correction (LATEST)

**Release trigger:** The user's original AEI-inspired Skill already required *real weighted financial flows*; public V9 included no Sankey. This was a serious documented execution failure, not a gap in the user's instructions. The new V10 reuses actual V9 source data, full four-company narratives and original PDFs rather than creating new shallow single-chart prototypes.

**Production link:** https://financials-in-visuals.pages.dev/research/2026-h1-v10/ — separately versioned from V9; homepage hero and primary featured card now point to V10, V9 and older routes preserved.

**Exact model:** 688111 four WPS/other product revenue lines→operating revenue→COGS/GP; 600519 three product revenue lines→operating revenue→COGS/GP, financial-subsidiary interest excluded; 000333 three *exclusive* top-level segments→industrial operating revenue→COGS/GP with finance interest/fees excluded; 600036 NII + net fees + other net→bank operating revenue→bank administration/credit/other cost + operating profit. Ribbons have one shared yuan-derived scale, exact signed Decimal conservation and no forced 'other' balancing node. Four financial Sankey SVGs are new **within** the existing 8/9/9/10-figure real company articles, not replacements for statements, cash and risk.

**Actual release evidence:** https://github.com/kobolibra/financials/actions/runs/41588330309 success: all four original PDF downloads, exact SHA256 and issuer/year/pages, source-to-financial invariant tests (7/7), clean rebuilt source-to-tracked HTML byte match all 5 files, real Cloudflare browser 12/12 company×viewport 1440/768/390, mobile figure-only Sankey scrolling, figure annotations, SVG export, index→bank→cash→index actual navigation, screenshots artifacts. Source and developer scripts under `research/rebuild-v10/` GitHub main; automated CI `.github/workflows/verify-v10-sankey-research.yml`.

**Cross-chat original source archive:** persistent ChatGPT Library path `/Financials-in-Visuals/2026H1-v10-sankey-source-rebuild.zip`, stable Library ID `libfile_2872106bfc8c8191a0575cea194478bb`, exact ZIP SHA256 `d08b92fa7afaad427589181966b903130cfbffad12f692a1c4872d9e072bcca9`. Contains full four original issuer PDFs (SHA individually tested), existing ledgers, source builder, evidence-based HTML, adversarial unit tests, local responsive QA and documentation. HTML-only snapshot in Library at `/Financials-in-Visuals/2026H1-v10-sankey-html.zip`, ID `libfile_5897be56f2c88191a5c7e514f2ab2f6a`.

**Current main Skill:** v8.3.1-RC1, with an enforceable mandatory AEI finance-flow decision gate and explicit valid omission for signed/incompatible financial amounts. Not yet passed: independent second finance analyst's full PDF row/column and note review, multi-quarter market/peers/valuation, comprehensive visual-quality comparison beyond the flow diagrams, every issuer sector adapter. Never claim 'exceeded App Economy Insights' solely from four legitimate Sankeys and test counts. Verify the latest homepage deployment CI after any changes.

