"""Evidence-conditioned full-year report parity for source-limited new issuers.

Never equate PASS in source/geometry/browser checks with analytical depth.
This applies only to full FY/H1 *industrial general-statement* candidates
with rich audited source facts; limited quarter disclosures remain scoped.
No absolute target chart count: require all *eligible* independent economic
questions be expressed and source-evidence-backed, not decorative charts.
"""
from __future__ import annotations

from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path

SCORES = frozenset(("R1", "R2", "R3", "R4", "R5",
                    "V1", "V2", "V3", "V4", "V5", "V6"))


def eligible(record, ledger):
    issuer = ledger.get("issuer", {})
    facts = ledger.get("facts", {})
    return (record.get("release_class") == "source_limited_preview"
            and str(record.get("period", "")).endswith(("FY", "H1"))
            and issuer.get("statement_format") == "general"
            and issuer.get("sector_adapter") in {"manufacturing", "industrial"}
            and isinstance(facts, dict) and len(facts) >= 100)


def evaluate(catalog_issuer, record, ledger, publication, research_brief,
             research_bytes, review, html_sha):
    """Pure audit: all current report identity, source breadth and visual rubric."""
    errors = []
    def fail(code):
        errors.append("FULL_REPORT_EDITORIAL_" + code + " " + catalog_issuer["code"])

    figures = publication.get("figures") or []
    facts = ledger["facts"]
    families = {r.get("family") for r in figures}
    ids = [r.get("id") for r in figures]
    if not figures or len(ids) != len(set(ids)) or len(figures) != catalog_issuer.get("figures"):
        fail("FIGURE_COUNT_OR_ID")
    if not isinstance(publication.get("essays"), list) or len(publication["essays"]) < 4:
        fail("RESEARCH_NARRATIVE_COVERAGE")
    if not isinstance(publication.get("glance"), list) or len(publication["glance"]) < 4:
        fail("OPENING_DECISION_BRIEF")
    if not isinstance(research_brief.get("theses"), list) or len(research_brief["theses"]) < 4:
        fail("SOURCE_BACKED_FALSIFIABLE_THESES")
    elif any(not isinstance(t.get("next_disclosure_test"), dict)
             or not t.get("strongest_alternative") or not t.get("calculations")
             or not t.get("source_fact_keys") for t in research_brief["theses"]):
        fail("THESIS_FALSIFICATION_OR_SOURCE")
    if not all(f.get("question") and f.get("takeaway") and f.get("counter")
               and f.get("identity") for f in figures):
        fail("INDIVIDUAL_CHART_EDITORIAL_QUESTION")
    if research_brief.get("source_pdf_sha256") != ledger["source"]["original_bytes_sha256"]:
        fail("SOURCE_PDF_SHA")
    if publication.get("research_evidence_gate", {}).get("brief_sha256") != sha256(research_bytes).hexdigest():
        fail("RESEARCH_EVIDENCE_SHA")

    def contains_any(keys):
        return set(keys).issubset(facts)
    # Eligible economics are decided by ORIGINAL SOURCE DISCLOSURES, not by
    # a target graphic count. Skipping a supported dimension is a real gap.
    required = []
    if contains_any(("rev", "cogs", "net_profit")):
        required.append(("PROFIT_FORMATION", bool({"income", "signed_bridge"} & families)))
    if contains_any(("rev", "cogs", "rev_prior", "cogs_prior")):
        required.append(("MARGIN_OR_GROWTH_CHANGE",
                         bool({"ratio_dumbbell", "growth_bars"} & families)))
    if contains_any(("cfo", "cfi", "cff", "cash_open", "cash_close")):
        bridges = [f for f in figures if f.get("family") == "signed_bridge"]
        required.append(("CASH_BRIDGE", any(
            "cfo" in json.dumps(f.get("rows", []), ensure_ascii=False)
            and "cash_close" in json.dumps(f.get("rows", []), ensure_ascii=False)
            for f in bridges)))
    if contains_any(("ar", "inventory", "ar_prior", "inventory_prior")):
        required.append(("WORKING_CAPITAL_STOCK", "stock_delta" in families))
    if contains_any(("assets", "liabilities", "equity")):
        required.append(("SAME_DATE_BALANCE", "balance" in families))
    if ledger.get("segments") and ledger.get("income_partition", {}).get("completeness") == "SOURCE_EXHAUSTIVE_MUTUALLY_EXCLUSIVE":
        required.append(("DISCLOSED_BUSINESS_ECONOMICS", bool({"income", "product_economics"} & families)))
    for label, covered in required:
        if not covered:
            fail("ELIGIBLE_QUESTION_MISSING_" + label)

    if review.get("status") != "PASS_EXECUTOR_SELF_REVIEW_ONLY":
        fail("AUTHOR_SELF_REVIEW_NOT_PASS")
    if review.get("reviewed_html_sha256") != html_sha or review.get("reviewed_figures") != len(figures):
        fail("STALE_AUTHOR_REVIEW_BYTES")
    if review.get("reviewed_source_pdf_sha256") != ledger["source"]["original_bytes_sha256"]:
        fail("AUTHOR_REVIEW_PDF_SHA")
    scores = review.get("scores", {})
    if not isinstance(scores, dict) or set(scores) != SCORES:
        fail("RUBRIC_KEYS")
    else:
        values = [v.get("score") for v in scores.values() if isinstance(v, dict)]
        if len(values) != len(SCORES) or any(type(x) is not int or x < 2 or x > 3 for x in values):
            fail("RUBRIC_MINIMUM")
        elif Decimal(sum(values)) / Decimal(len(values)) < Decimal("2.5"):
            fail("RUBRIC_AVERAGE")
    if review.get("p0_findings"):
        fail("REVIEW_P0")
    if record.get("gates", {}).get("INDEPENDENT_HUMAN_REVIEW", {}).get("status") != "NOT_CHECKED":
        fail("SELF_REVIEW_MISREPRESENTS_INDEPENDENT_HUMAN")

    return errors


def validate_source_limited_full_research(root: Path, catalog_issuer: dict,
                                          record: dict):
    source = record.get("ledger_file")
    if not isinstance(source, str) or not source.startswith("research/issuers/"):
        return ["FULL_REPORT_EDITORIAL_MISSING_LEDGER " + catalog_issuer["code"]]
    folder = (root / source).resolve().parent
    try:
        folder.relative_to(root.resolve())
    except ValueError:
        return ["FULL_REPORT_EDITORIAL_UNTRUSTED_PATH " + catalog_issuer["code"]]
    if not (folder / "source-ledger.json").is_file():
        return ["FULL_REPORT_EDITORIAL_MISSING_LEDGER " + catalog_issuer["code"]]
    ledger = json.loads((folder / "source-ledger.json").read_text(encoding="utf8"))
    if not eligible(record, ledger):
        return []
    paths = ("publication.json", "research-brief.json", "editorial-self-review.json")
    if any(not (folder / name).is_file() for name in paths):
        return ["FULL_REPORT_EDITORIAL_NO_CURRENT_RUBRIC " + catalog_issuer["code"]]
    pub = json.loads((folder / paths[0]).read_text(encoding="utf8"))
    brief_raw = (folder / paths[1]).read_bytes()
    brief = json.loads(brief_raw)
    review = json.loads((folder / paths[2]).read_text(encoding="utf8"))
    html = root / "public" / catalog_issuer["href"].lstrip("/")
    if not html.is_file():
        return ["FULL_REPORT_EDITORIAL_MISSING_HTML " + catalog_issuer["code"]]
    return evaluate(catalog_issuer, record, ledger, pub, brief, brief_raw,
                    review, sha256(html.read_bytes()).hexdigest())
