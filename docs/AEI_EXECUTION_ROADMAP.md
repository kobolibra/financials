# AEI × FT production reliability program

Status: implementation in progress. This is an execution contract, NOT proof of final AEI-level quality.

## Actual starting point

Eleven issuers are currently published. Four historical V10 HTML pages still fail mobile visual quality: 600036, 688111, 600519, 000333. At 390px, the publisher hides non-Sankey financial SVG diagrams and places its only surviving 850px Sankey in a narrow horizontal scroller. Historic CI once asserted that horizontal scrolling meant success. A passing ledger or HTTP 200 is not visual certification.

## Typed semantics for the four actual 2026H1 issuers

| Issuer | Required primary accounting grammar | Why |
| --- | --- | --- |
| 688111 Kingsoft Office | TYPE A: each WPS product revenue to its OWN reported cost and derived GP | Source has four separate cost items. Group COGS flow hides true product economics |
| 600519 Moutai | TYPE C: omit all-positive product GP Sankey; show signed product economics instead | Other business cost exceeds its own revenue. A negative GP ribbon cannot be disguised as positive |
| 000333 Midea | TYPE B: top-level exclusive revenues to group COGS/GP only, prominently state PRODUCT_LEVEL_GP_NOT_ESTABLISHED | No equivalent per-business reported cost for this exact grouping. Industrial child and geography axes cannot be summed twice |
| 600036 China Merchants Bank | BANK NET INCOME to credit/operating expenses and operating profit | NII already subtracts interest expense. No invented industrial gross-profit interpretation |

The source ledger and the produced HTML must satisfy the same type. Newly added scripts/audit_v10_flow_contract.py loads original yuan values, determines the actual flow type and checks the published figure 02. Its adversarial tests check real issuer facts, source-tampering, visible caveats, illegal positive flows, and source SHA changes.

Historical release debt rule: an unchanged existing HTML hash remains a disclosed FAIL but is temporarily waived by the default command; any changed report hash immediately revokes this waiver. The --strict command must remain FAIL for the old four until actually fixed. Green CI on unchanged historical files NEVER means they are certified.

## Work packages and evidence

1. **P0: render engine integration.** The publisher itself, not just the auditor, must call the typed financial flow decision before creating an SVG. A renders every source's actual COGS/GP ribbons with exact yuan geometry. B visibly discloses group-only GP. C uses signed waterfall or non-Sankey presentation. Bank follows its own net-income grammar.
2. **P0: source-specific narrow-screen design.** Replace the mobile display:none and 850px scroll. Independently lay out source-connected finance charts for 390 and 768 with real SVG money geometry, signed CFO/profit/cash bridges, and same-date balance stock identity. Keep original desktop graphics and source tables; do not substitute a generic KPI list.
3. **P0: original-source reproducibility.** Acquire actual issuer PDFs with validated SHA, regenerate all four articles byte-for-byte, check that figure source IDs and physical pages match, test every diagram under Chinese-font Chromium at 1440/768/390, and save screenshots and exact HTML SHA.
4. **P0: remove the false-positive mobile test.** Replace the historic scroller-success assertion with no-inner-scroll, per-exhibit non-hidden visibility, CJK text bounding box and actual source/path/target yuan geometry checks. Verify real Cloudflare full-response SHA after deploying, not only status 200.
5. **P1: editorial benchmark.** Link each company's hero question, business mechanism, strongest counterargument, and each figure brief to original-source facts. Compare real public AEI/FT examples to representative output using an independent finance/visual evaluation with explicit rubric and multiple repeated source reports.
6. **P1: cross-sector stability.** Run adversarial and repeated builds on independent reports in software, spirits, banks, conglomerates, semiconductors, insurance, power and optical. Track original accounting, incorrect Sankey omission rate, mobile readability, insight quality, human reviewer agreement, reproducibility, and regression.

## Release standard

All eleven issuer articles must have no unwaived source/financial-geometry/mobile P0. All financial and editorial evidence must be bound to the exact published HTML SHA. Missing genuine screenshot checks and independent human editorial review remain NOT_CHECKED; a CI PASS only certifies its explicitly executed checks. Neither source conservation nor a long Skill guarantees AEI-level quality. The project should only claim exceeding an AEI benchmark in specific, independently measured dimensions, never as an untested global assertion.

Current scope of this branch: typed original-yuan and immutable-publication contract plus CI and roadmap. No attempt is made to silently rewrite or redeploy the existing four unfinished company publications.
