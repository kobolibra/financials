# Financials in Visuals · Dual-Track Research & Publication System v7

The skill is no longer a one-chart Sankey imitation. It has **two independent research foundations** and one source-audited original visual reporting implementation.

## Read the two research pillars separately

1. [App Economy Insights complete visual research analysis](research/01_APP_ECONOMY_INSIGHTS_RESEARCH.md) — original first-party research, business-first framing, full P&L / balance / cash / FCF visual grammar, 6 pre-investment charts and their evidence requirements.
2. [Professional A-share institutional financial research framework](research/02_ASHARE_INSTITUTIONAL_RESEARCH.md) — PRC accounting and CSRC disclosure, material financial-note interrogation, industry-specific ratios, cash-quality/valuation/risks, counter-hypotheses and provenance.

[Execution Skill v7](SKILL.md) binds these two independently researched pillars to the publication gates.

## Working v7 issuer case

- **Published GitHub path:** `public/300394/2026-H1/index.html` (the Pages project must independently deploy this Git commit).
- **Sources:** Tianfu Communications 2026 H1 unaudited PDF, 185 pages, SHA-256 `6f508be2da82fb7b1728e2e638b5ce721baa3cf98a64234db636358019d913f5`, 59 structured source facts, 15 original signed indirect CFO adjustments.
- **Editorial output:** 10 original exhibits: product economics / income allocation, complete P&L bridge, gross-profit change bridge, two-period margins, net earnings→CFO, opening→closing cash, analyst-defined FCF, balance-sheet anatomy, working-capital comparisons and properly denominated concentration.
- **Reproducible v7 package:** [v7](v7/) with `engine/render_v7.py`, ledger, research memo, chart primitives, tests, local-browser QA, HTML build and instructions.
- **Verification:** 12 regression tests PASS; local Chromium at 1440/768/390 PASS, keyboard, SVG export, no JS exception or page overflow. GitHub content SHA re-read matches preview and production.

## The unresolved professional boundary

The user-facing site is `https://financials-in-visuals.pages.dev/`. The GitHub production HTML has been updated and verified; **its Cloudflare live HTTP body has not been independently verified in this execution environment.** Neither a GitHub commit nor a screenshot of a local HTML file can substitute for a public site verification.

The second issuer regression is synthetic; cross-sector automatic PDF research, historical price/valuation/peer research and 8–12Q comparisons need their own verified inputs. The system deliberately refuses banking/insurance/real-estate industrial-style accounting rather than hallucinate universal support.

**Publication quality has several independent gates. No self-awarded 'top-tier' labels from code tests alone.**
