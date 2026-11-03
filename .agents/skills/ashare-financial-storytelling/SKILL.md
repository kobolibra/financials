---
name: ashare-financial-storytelling
description: Use for reading, auditing, researching, visualizing and publishing A-share listed-company financial reports and original PDF filings in Financials in Visuals, including App Economy Insights-level financial storytelling, exact source-checked Sankey diagrams, cash flow and balance sheet for any issuer, and adding new companies to the single growing issuer website. Also trigger for restoring or continuing kobolibra/financials work across sessions.
---

# A-share Financial Storytelling · Discoverable Codex repository skill

**This is a small discovery entry, not another competing skill or template.** Canonical full Skill lives at: `../../../skills/ashare-financial-storytelling/SKILL.md` relative to this file (or repository-root `skills/ashare-financial-storytelling/SKILL.md`).

## On activation — required full reads

1. Repo root `START_HERE.md`, `project-status.json`, `PROJECT_STATE.md`, and `AGENTS.md`.
2. Canonical **complete** `skills/ashare-financial-storytelling/SKILL.md`, not just summary or this wrapper.
3. ALL five canonical manuals in `skills/ashare-financial-storytelling/research/`: `01_APP_ECONOMY_INSIGHTS_RESEARCH.md`, `02_ASHARE_INSTITUTIONAL_RESEARCH.md`, `03_VISUAL_EDITORIAL_SYSTEM.md`, `04_ASHARE_FORENSIC_DEEP_DIVE.md`, `05_CROSS_SECTOR_GENERALIZATION.md`.
4. `docs/REPORT_RELEASE_CHECKLIST.md` and `docs/HANDOFF_PROTOCOL.md`.
5. `docs/SKILL_EVOLUTION_PROTOCOL.md`, `skills/ashare-financial-storytelling/quality-regressions.json`, and for each post-legacy company `research/issuers/<code>/release-gates.json`.
6. Relevant actual issuer report, source ledger, sector renderer, current GitHub CI and genuine Cloudflare public page.

## Mandatory output

Execute the two independent Skill tracks — institutional Chinese statement/notes research AND original AEI/FT-inspired source-true finance storytelling. Do not replace source-conserving income Sankey with a decorative generic chart, invent balancing categories, apply industrial CFO/FCF rules to banks, or confuse tested web behavior with finance/editorial certification. Keep full independent offline-capable HTML company reports on the **one** root library, preserving old URLs.

Before finishing record actual source PDF / accounting / figure / editorial / browser / GitHub / live QA gates and update current handoff. **Human independent second-review remains NOT_CHECKED** unless evidence exists.

**Discovery scope:** Codex operating **inside this repository** can discover this `.agents/skills/` entry; ordinary ChatGPT conversations do not necessarily search GitHub and will not auto-load this without Project instructions or explicit startup prompt. Do not claim this is installed in global ChatGPT skills.

**v8.4 non-negotiable:** Run `python scripts/check_release_contract.py`, its hostile test suite and `python scripts/check_handoff.py`; each material failure must update the actual source, a reusable test, the canonical Skill and the zero-memory handoff. Historic seven issuer pages are review debt, not automatically fully certified. Do not misrepresent old live Cloudflare PASS as the latest deployed commit.
