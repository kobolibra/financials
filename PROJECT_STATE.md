# Financials in Visuals · Current Project State
Updated: 2026-11-02
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
