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
