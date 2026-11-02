# Cross-Sector Financial Research Adapter Protocol · Candidate v8.2

This document is an original engineering specification. It does not certify that every industry is production-ready.

## Core design

Separate six layers: (1) original PDF provenance, SHA256, filing version and page; (2) typed facts with original unit, signed value, date/period and consolidation; (3) verified business-model routing; (4) sector-specific accounting reconciliations and material risk notes; (5) question-led chart selection; (6) financial, mobile and actual website publication gates.

Never equate operating revenue with total revenue without examining financial subsidiaries. Do not mix industry statement flows, point-in-time asset/liability balances, product/geography/channel cuts, parent and consolidated reporting, or disclosed and inferred figures.

## Industry adapters (not fixed chart templates)

- Industrial manufacturing: comparable product economics, inventory, CapEx and audited cash conversion. Reject unsourced SKU ASP and causal mix effects.
- Software: recognized subscriptions vs ARR/billings, contract liabilities, R&D, SBC and distinct GAAP/non-GAAP definitions.
- Consumer and retail: product, channel and geography as separate categorical axes; returns and inventory.
- Banking: net interest income and margin, funding mix, loan impairment stages, NPL, provisions, CET1/RWA. Reject industrial margins and industrial free cash flow.
- Insurance: insurance service and finance result, CSM roll-forward, NBV methodology, claims/combined ratio and regulatory solvency; CSM is a stock, premiums are not always recognized insurance-service revenue.
- Insurance/bank holding group: subgroup accounting, intra-group eliminations, parent-vs-NCI bridge and distinct operating-vs-GAAP earnings; reject direct addition without consolidation.
- Property: recognized delivery revenue versus presales, contract liabilities, impairments, restricted cash, maturing debt and going-concern paragraph; reject 'cash > debt' simplifications.
- Broker/asset manager: fees, trading/market-value swings, net capital and client assets versus company assets.
- Pharma: product, milestone, R&D capitalization, clinical and regulatory risk; no pipeline revenue fiction.
- Engineering/construction: backlog and contract assets/liabilities versus recognized revenue; performance obligations.
- Utilities: regulated tariff, physical volumes, fuel costs, maintenance/growth CapEx and regulatory returns.
- Mixed conglomerate: primary sectors plus material finance/insurance overlays, segment hierarchy and eliminations.

## Proof of genuine applicability

A model is LEVEL 0 if only described; LEVEL 1 after one original-filing real-company proof; LEVEL 2 after two real companies, full statements/core notes and reproducible browser-tested research; LEVEL 3 after cross-sector adversarial regression, independent editors and tested deployment. Do not claim universal capability for a LEVEL 0 model.

2026H1 real-source tests: 招商银行 600036 247 pages; 中国平安 601318 176 pages; 万科 000002 234 pages. Original bytes, SHA, full report identities passed. 44 selected original-page numbers and 7 accounting/semantic identities passed. These are not complete financial statement audits. 18 synthetic routing/adversarial unit tests passed. Three standalone sector pages were rendered at 1440/768/390, but actual-file route and Cloudflare HTTP remain NOT_CHECKED.

New mandatory checks from real filings: interest revenue identity instead of industrial gross-margin proxy; insurer segment eliminations and consolidated operating-to-GAAP net-profit bridge; Deloitte's going-concern material uncertainty in Vanke; source-link servers returning HTML rather than PDF; and Chinese hero orphan / wide SVG responsive defects.

Candidate branch: pdf-source-validation-2026h1. Preserve old reports and live main unchanged; record source artifact location, exact tests and next steps in PROJECT_STATE.md.
