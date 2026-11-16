# Peer-review and Release Protocol

## Independent gates
**G0 Intake** — issuer, version, PDF sha, page map, scope, audit status, period, restatement understood.
**G1 Evidence** — core ledger fields traced to PDF with page/label, source pages image-checked for complex tables, qualitative management claims attributed; all formulas reproducible. Any key unknown shown.
**G2 Accounting** — applicable numeric identities with Decimal, line completeness, stock/flow, period and units; failures block impacted graphics. Report PASS/FAIL/NOT_CHECKED; no score inflation by choosing only easy checks.
**G3 Research** — a business model, 1 strong thesis, rival hypothesis, real causal mechanisms or explicit lack of evidence, quantitative materiality, earned counterarguments, read AR+inventory+notes, capital returns, sector-fit analysis, specific watch indicators.
**G4 Chart geometry** — Sankey conservation for each source/destination; signed corrections use waterfall; no fabricated residual business segment, no mixing periods/scope; chart caption and source inside document.
**G5 Design** — hierarchy and typography, intentional whitespace, contrast, hover/focus and static reading, mobile no microscopic content; design critic has inspected rendered screenshots.
**G6 Browser** — offline file, no CDN requests, no JS errors, 1440/390 widths, keyboard and pointer functions, SVG export; preserve screenshots in QA artifact.
**G7 Publishing** — only authorized repo and explicit update target; stage preview; compare preview/prod; check actual live URL independently; do not assume Pages deployed because Github commit returned 200.

## Red-team checklist (mandatory in research memo)
For EACH thesis:
- What alternative business or accounting mechanism could produce same observation?
- What is the biggest data hole?
- Would product mix, FX, share base, asset capitalization, government aid or acquisitions invalidate this comparison?
- Is one large customer/supplier material? Are the disclosed shares for receivables, purchases or revenue?
- Does the conclusion need 2024/2025 data or peers not provided?
- Which next quarterly disclosure could falsify it?
- Could the visual itself overstate a causal or cash-flow connection?

## Scored editorial rubric (internal guide, not a claim of "professional grade")
Research & business model (25): 10 explanation of actual operations, 10 economics/drivers, 5 alternatives.
Accounting reliability (25): 15 correct accounting, 5 traceability, 5 uncertainties.
Judgment & useful monitoring (20): 8 materiality, 6 falsifiers, 6 sector fit.
Visual communication (20): 8 semantic, 5 layout, 4 accessibility, 3 originality.
Reproducibility & delivery (10): 5 evidence+build, 5 browser+online verification.
**Scores cannot waive hard blockers, and should not be marketed as externally validated ratings.**

## Transparency statuses
- DRAFT: source partial or unreviewed
- ARITHMETIC_VERIFIED: invariants pass for reviewed fields; report not approved
- ANALYST_REVIEWED: thesis and footnotes verified
- BROWSER_VERIFIED: HTML local interactive QA passed
- GIT_COMMITTED: reviewed blob and SHA in target repo
- LIVE_VERIFIED: deployed Pages URL tested from independent HTTP/browser
No assertion of "auto works on any PDF" without passing multi-company multi-industry evaluation. A well-verified case is a case, not generality.

## Required issue log
Every remaining issue: ID; severity BLOCKER/MAJOR/MINOR; assertion or chart; affected source/period; next correction; review status. Release report includes explicit unsupported questions and any third-party source limitations.
