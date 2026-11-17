# Unmapped statement-row coverage review

This protocol governs `scripts/generalization_probe.py --coverage-queue ...`. It is a **manual evidence-review lane**, not an automatic completeness certificate.

## 1. Generate the full queue

```bash
python scripts/generalization_probe.py --coverage-queue /tmp/financials-unmapped-review.json
```

No company-specific extraction hints are supplied. All archived complete report PDFs are processed. The standard source/audit tests regenerate this queue in CI, and the `Verify financial research Skill and new-chat handoff` workflow uploads it as the `financials-unmapped-coverage-review` artifact.

The queue carries the source PDF SHA, issuer and reporting period, statement type, **physical PDF page**, vertical location, printed label, both current and comparative printed amounts, preceding canonical key (diagnostic only), and an ID anchored to the immutable source bytes. The ID intentionally does not depend on which canonical key preceded the item: reordering the extraction rules must not hide a previously unreviewed monetary row.

## 2. Review every item before a coverage claim

Each queue item starts with `classification: NOT_CHECKED`, `materiality: NOT_CHECKED`, `review_evidence: null`. Do **not** automatically relabel all residual rows as insignificant just because the three-statement identities close.

Review against the original physical PDF page and independent ledger keys. Record one of the following outcomes in a **separate, signed review record**; these are *proposed human-review categories*, not automatically approved states or currently implemented parser outputs.

- **Already represented**: identify the exact canonical key and source cell or prove why this is a repeated subtotal/header rather than a missing independent fact.
- **Not a monetary line item**: show the page evidence that makes the table row inapplicable.
- **Nonmaterial after review**: document size and qualitative relevance in the issuer's accounting context; monetary magnitude alone is insufficient, especially in regulated financial firms.
- **Material omission / unknown**: block the affected analysis, graph, and complete-coverage claim; extend a **general** mapping rule or document a source limitation; rerun the complete 30-PDF regression.

Include reviewer identity, review date, source page/cell, reason, affected report/metrics, and remediation PR where applicable. Review decisions cannot be inherited across a changed PDF SHA, changed amount, changed source label or physical page.

## 3. Release-gate semantics

A `generalization_probe` PASS means the explicitly tested stages passed, **not** all material disclosures were mapped. The review queue is never a PASS just because it was generated or archived.

Publication quality also requires sector-specific disclosures, analytical thesis and counter-evidence, exact-Yuan accounting checks, valid chart grammar, desktop/mobile browser screenshots, and independent human editorial/aesthetic review. They remain `NOT_CHECKED` without their own evidence.

For any company or period not covered by original PDFs and independent release receipts, state the omission. Never use a synthetic report or a closed arithmetic identity to claim comprehensive cross-sector generalization.
