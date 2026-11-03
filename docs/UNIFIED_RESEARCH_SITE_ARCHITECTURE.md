# Financials in Visuals — Unified research library (2026-11-03)

## The corrected product model

**One website, one seven-company research library, one topical-research section.** The user already had three original optical reports: 300394 天孚通信, 300308 中际旭创, and 300502 新易盛. Each already contains an amount-weighted financial flow and financial statements/cash/capital work. Later work on 600036 招商银行, 688111 金山办公, 600519 贵州茅台 and 000333 美的集团 was incorrectly presented as an unrelated “four company” featured edition. That was an information-architecture and project-context failure. It also destroyed visibility for earlier output.

The root homepage **is the canonical research catalogue** of all seven distinct independent articles. Company report URLs remain stable; do not redirect or rewrite report route content. All company articles navigate directly back to `/#companies`. One separate topical article `/optical-2026h1.html` compares optical value-chain economics; it is not an eighth issuer. Archived four-company indexes and one-chart engineering fixtures remain accessible only from a low-key archive disclosure and are not primary research entries.

This is a site-architecture improvement, not a new version-specific four-company report engine. No new `/research/2026-h1-v11/` edition catalogue. No iframe, no miniature nested document scroll, no arbitrarily duplicated company.

## User-facing source of truth

- `site/research_catalog.json`: seven records, unique ticker/name/URL, industry, original/first-pass provenance and report status. Distinguish `research-preview` from `source-review`; do not claim independent certification.
- `site/portal_builder.py`: one dependency-free static original HTML generator for root `public/index.html`, accessible filter/search, 7 issuer routes, separate industry special, and subtle archive references. No issuer-specific article rendering or invented investor facts.
- `site/test_portal.py`: clean-rebuild, 7 URL identities, legacy 3 inclusion, additional 4 inclusion, topic separation, no four-company featured CTA, accessibility semantics, and no remote assets.
- Seven source report pages: original three `/300394.html`, `/300308.html`, `/300502.html`; newer four `/research/2026-h1-v10/{600036,688111,600519,000333}.html`.
- Preserve original v7 and v10 sector-specific report renderers, their figures, references and source accounting QA. Only shared catalogue links and navigation wording change in this site release.

## App Economy Insights / Skill acceptance — separated, not conflated

- **Original issuer analysis**: industrial vs bank vs software vs consumer vs manufacturing may use different accounting definitions. Do not homogenize them for a common gallery.
- **Real money flows**: all three optical articles already had proportional ribbons as their first analytical exhibit; later four have verified financial Sankeys. They must be assessed for semantically valid additive partitions and accounted residuals. A present ribbon is NOT automatically independently source-reviewed.
- **Period, scope, signs, notes**: original full-file SHA / literal numeric matching and accounting bridge are necessary but do not establish exhaustive row-column semantics. Old 300308 notes are explicitly retained as needing independent source review. Do not falsely label the entire library as institutional second-reviewed.
- **Visual system**: unified editorial typography, no image imitation, strong hierarchy, readable cards, meaningful amount labels, per-figure sources, real full-page navigation and 390px mobile. The homepage index is one stable entry, not another company-specific research story.
- **Independent editorial signoff**: NOT_CHECKED for seven full reports; external 8–12Q peer/valuation work remains not complete. No unsupported pricing, forecasts, market shares or claims of superiority to AEI.

## Release gates

1. Source catalogue precisely identifies **seven**, routes exist; source generator rebuild equals committed HTML; all 9 portal tests pass.
2. Real Cloudflare public homepage serves seven articles and one topic, with meaningful difference between research and experimental archive.
3. Real Chromium at 1440, 768 and 390 has no body-level horizontal scroll or JS errors; filter/search/back links work, and original plus new articles remain independent pages.
4. Main and separately deployed full company reports are unchanged financially; only navigation and shared access. Existing v10 `verify-v10-sankey-research.yml` still downloads four original PDF bytes and regenerates exact full HTML.
5. Evaluate Skill financial and visual editorial mandates independently before ever calling a company article institutionally publication-complete. A technically clean central catalogue cannot close missing independent finance-review gates.

**Next substantive P0 work**: seven-issuer semantic source/audit matrix with independent original PDF row and column verification, back to company-specific questions and notes; optical financial-flow residual sources deserve particular scrutiny. Full qualitative/quantitative AEI-level report narrative review across all seven remains pending.