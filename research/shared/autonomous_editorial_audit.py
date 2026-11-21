#!/usr/bin/env python3
"""Autonomous editorial preflight: evidence coverage, peer calibration and review debt.

This is a production refusal / revision planner, NOT an AI art director.
It cannot judge the quality of an economic hypothesis or visual aesthetics.
Tests require that even superficially green research carries actionable debt.
No hard-coded issuer, fixed figure quota, ungrounded industry cause, or PASS by vote.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FIGURE_SOURCE_FIELDS = {
    "income": ("facts",),
    "product_economics": ("products",),
    "signed_bridge": ("rows",),
    "comparison": ("pairs",),
    "kpi_board": ("tiles",),
    "ratio_dumbbell": ("rows",),
    "growth_bars": ("pairs",),
    "stock_delta": ("items",),
    "balance": ("dates",),
    "period_columns": ("periods", "series"),
    "volume_rate": ("inputs", "rows"),
    "components": ("rows", "items"),
    "income_flow_v3": ("facts", "sources", "stages"),
}
# Full-year industrial questions are derived from actual source availability.
# "COVERED" requires a meaningful figure with its *exact source operands*,
# not merely an exhibit labelled "income", "cash" or "balance".
TOPICS = (
    ("GROSS_PROFIT_CHANGE", ("rev", "cogs", "rev_prior", "cogs_prior"),
     ("signed_bridge",), ("rev", "cogs", "rev_prior", "cogs_prior"), "P0"),
    ("PROFIT_QUALITY", ("parent_net", "adjusted_parent"),
     ("comparison", "ratio_dumbbell", "signed_bridge"),
     ("parent_net", "adjusted_parent"), "P0"),
    ("CFO_RECONCILIATION", ("net_profit", "cfo"),
     ("signed_bridge",), ("net_profit", "cfo"), "P0"),
    ("CASH_CLOSE", ("cash_open", "cash_close", "cfo", "cfi", "cff"),
     ("signed_bridge",), ("cash_open", "cash_close", "cfo", "cfi", "cff"), "P0"),
    ("CASH_REINVESTMENT", ("cfo", "cash_capex"),
     ("comparison", "signed_bridge"), ("cfo", "cash_capex"), "P0"),
    ("OPERATING_WORKING_CAPITAL", ("ar", "inventory", "ar_prior", "inventory_prior"),
     ("stock_delta",), ("ar", "inventory", "ar_prior", "inventory_prior"), "P0"),
    ("BALANCE_STRUCTURE", ("assets", "liabilities", "equity"),
     ("balance", "signed_bridge"), ("assets", "liabilities", "equity"), "P0"),
    ("PROFIT_TO_PARENT_CHAIN", ("rev", "cogs", "operating_profit", "pretax",
                                "net_profit", "parent_net"),
     ("income_flow_v3", "signed_bridge"),
     ("rev", "cogs", "operating_profit", "pretax", "net_profit", "parent_net"),
     "P1"),
)
SELF_REVIEW_FIELDS = ("five_second_answer", "source_and_grammar",
                      "visual_hierarchy", "mobile_readability",
                      "alternative_and_why_this_graph", "peer_design_delta",
                      "revision_decision")


def _json(path):
    return json.loads(path.read_text(encoding="utf8"))


def _source_refs(obj, known):
    """Only inspect value-bearing fields; question prose cannot certify a chart."""
    refs = set()
    if isinstance(obj, str):
        if obj in known:
            refs.add(obj)
    elif isinstance(obj, (list, tuple)):
        for child in obj:
            refs.update(_source_refs(child, known))
    elif isinstance(obj, dict):
        for key in ("value", "prior", "num", "den", "prior_num", "prior_den",
                    "current", "previous", "expression", "inputs", "facts",
                    "terms", "source", "revenue", "cost"):
            if key in obj:
                refs.update(_source_refs(obj[key], known))
    return refs


def figure_source_refs(figure, known):
    fam = figure.get("family")
    return _source_refs([figure.get(k) for k in FIGURE_SOURCE_FIELDS.get(fam, ())], known)


def _period_kind(s):
    for x in ("Q1", "H1", "9M", "FY"):
        if str(s).endswith(x):
            return x
    return "UNKNOWN"


def _peer_candidates(root, issuer, record, catalog, limit=3):
    choices = []
    current_sector = record.get("sector_adapter")
    current_period = _period_kind(record.get("period"))
    for item in catalog.get("issuers", []) + catalog.get("period_reports", []):
        if item.get("code") == issuer["code"] and item.get("period") == issuer.get("period"):
            continue
        page = root / "public" / str(item.get("href", "")).lstrip("/")
        folder = root / "research/issuers" / item.get("code", "")
        story = folder / "publication.json"
        release = folder / "release-gates.json"
        if not story.is_file() or not release.is_file() or not page.is_file():
            continue
        try:
            peer = _json(release)
            if peer.get("period") != item.get("period") and item.get("period"):
                continue
            pub = _json(story)
            figures = pub.get("figures") or []
            if not isinstance(figures, list) or not figures:
                continue
            same_sector = peer.get("sector_adapter") == current_sector
            same_period = _period_kind(peer.get("period")) == current_period
            choices.append({
                "code": item["code"], "period": peer.get("period"),
                "href": item.get("href"),
                "sector": peer.get("sector_adapter"),
                "same_sector": same_sector, "same_period_kind": same_period,
                "figure_count": len(figures),
                "research_paragraph_count": sum(
                    len(x.get("paragraphs", [])) for x in pub.get("essays", [])
                    if isinstance(x, dict)),
                "figure_families": sorted(set(x.get("family", "")
                                               for x in figures)),
                "html_sha256": sha256(page.read_bytes()).hexdigest(),
            })
        except (ValueError, KeyError, TypeError):
            continue
    choices.sort(key=lambda x: (not x["same_sector"], not x["same_period_kind"],
                                -x["research_paragraph_count"], -x["figure_count"], x["code"]))
    distinct = []
    seen = set()
    for item in choices:
        if item["code"] not in seen:
            distinct.append(item)
            seen.add(item["code"])
        if len(distinct) == limit:
            break
    return distinct


def _issue(issues, code, severity, detail, action):
    issues.append({"code": code, "severity": severity, "detail": detail,
                   "action": action})


def _eligible_industrial_fy(record, ledger):
    issuer = ledger.get("issuer", {})
    return (record.get("release_class") == "source_limited_preview"
            and _period_kind(record.get("period")) in {"FY", "H1"}
            and issuer.get("statement_format") == "general"
            and issuer.get("sector_adapter") in {"manufacturing", "industrial"}
            and len(ledger.get("facts", {})) >= 100)


def audit(root, issuer, record, ledger, publication, brief, review, catalog,
          *, strict=False, html_sha=None):
    code = issuer["code"]
    facts = ledger.get("facts", {})
    known = set(facts)
    figures = publication.get("figures", [])
    issues = []
    if not isinstance(figures, list):
        figures = []
    source_by_id = {
        str(f.get("id")): figure_source_refs(f, known)
        for f in figures if isinstance(f, dict)
    }
    covered = []
    for label, required, families, operands, priority in TOPICS:
        if not set(required).issubset(known):
            continue
        matching = [f.get("id") for f in figures if isinstance(f, dict)
                    and f.get("family") in families
                    and set(operands).issubset(source_by_id.get(str(f.get("id")), set()))]
        covered.append({"topic": label, "eligible": True, "status": (
            "COVERED_WITH_SOURCE_KEYS" if matching else "ELIGIBLE_BUT_NOT_DEMONSTRATED"),
            "source_keys": list(required), "figures": matching})
        if not matching:
            severity = "BLOCK" if priority == "P0" else "REVISION"
            _issue(issues, "MISSING_" + label, severity,
                   "Original source has the required accounting keys, but no chart "
                   "of the correct economic grammar cites all required operands.",
                   "Build a lawful source-verified exhibit, or document a page-bound "
                   "reason this relationship cannot be rendered; do not draw a decorative substitute.")
    if ledger.get("income_partition", {}).get("completeness") == "SOURCE_EXHAUSTIVE_MUTUALLY_EXCLUSIVE":
        segkeys = {s.get(k) for s in ledger.get("segments", [])
                   if isinstance(s, dict) for k in ("rev", "cost")}
        income = [f.get("id") for f in figures if f.get("family") == "income"
                  and {"rev", "cogs"}.issubset(source_by_id.get(str(f.get("id")), set()))
                  and segkeys.issubset(source_by_id.get(str(f.get("id")), set()))]
        covered.append({"topic": "DISCLOSED_MUTUALLY_EXCLUSIVE_INCOME",
                        "status": ("COVERED_WITH_SOURCE_KEYS" if income else
                                   "ELIGIBLE_BUT_NOT_DEMONSTRATED"),
                        "source_keys": sorted(segkeys), "figures": income})
        if not income:
            _issue(issues, "MISSING_DISCLOSED_INCOME", "BLOCK",
                   "An original mutually exclusive revenue/cost partition exists but "
                   "there is no source-backed income graph using precisely that axis.",
                   "Use one axis only; verify each source/cost and conservation in yuan.")
    ids = [f.get("id") for f in figures if isinstance(f, dict)]
    if not ids or len(ids) != len(set(ids)) or any(not x for x in ids):
        _issue(issues, "FIGURE_IDS_NOT_UNIQUE", "BLOCK",
               "Figure identity is missing or duplicated.",
               "Regenerate IDs and bind every review/screenshot to the actual figure ID.")
    questions = [re.sub(r"\s+", "", str(f.get("question", "")))
                 for f in figures if isinstance(f, dict)]
    if any(not q for q in questions):
        _issue(issues, "FIGURE_QUESTION_MISSING", "BLOCK",
               "At least one exhibit has no reader-facing research question.",
               "Decide the economic question before choosing a chart.")
    for q, n in Counter(questions).items():
        if q and n > 1:
            _issue(issues, "DUPLICATE_RESEARCH_QUESTION", "REVISION",
                   "The exact same question appears on multiple figures.",
                   "Remove one, change its analytical purpose, or put a reconciliation in the appendix.")
    if html_sha is None:
        html_sha = "NOT_CHECKED"
    if review.get("reviewed_html_sha256") != html_sha:
        _issue(issues, "REVIEW_STALE_HTML", "BLOCK",
               "Author review does not bind the exact current generated HTML.",
               "Rebuild, recapture actual browser pages, then repeat the full editorial review.")
    if review.get("reviewed_source_pdf_sha256") != ledger.get("source", {}).get("original_bytes_sha256"):
        _issue(issues, "REVIEW_STALE_PDF", "BLOCK",
               "Review is not bound to the original PDF source fingerprint.",
               "Redo review using the original archived PDF identity.")
    if record.get("gates", {}).get("INDEPENDENT_HUMAN_REVIEW", {}).get("status") == "PASS":
        _issue(issues, "HUMAN_REVIEW_UNVERIFIED", "BLOCK",
               "Automated author self-review cannot establish independent human approval.",
               "Attach real independent reviewer proof or restore NOT_CHECKED.")
    peers = _peer_candidates(root, issuer, record, catalog)
    calibration = review.get("peer_calibration", {})
    if not isinstance(calibration, dict):
        calibration = {}
    verified_peer_codes = {p["code"] for p in peers}
    chosen = calibration.get("peers", [])
    if not isinstance(chosen, list):
        chosen = []
    chosen_codes = {x.get("code") for x in chosen if isinstance(x, dict)}
    if len(chosen_codes & verified_peer_codes) < 2:
        _issue(issues, "PEER_CALIBRATION_MISSING", "REVISION",
               "No current-byte side-by-side comparison with two valid library exemplars.",
               "Use the suggested same-sector/same-period peers; compare story thesis, figures, "
               "hero hierarchy, mobile reading, and explain concrete strengths and gaps.")
    else:
        if not all(x.get("html_sha256") in {p["html_sha256"] for p in peers
                                              if p["code"] == x.get("code")}
                   and len(str(x.get("research_delta", ""))) >= 30
                   and len(str(x.get("visual_delta", ""))) >= 30
                   for x in chosen if isinstance(x, dict)):
            _issue(issues, "PEER_CALIBRATION_STALE_OR_VAGUE", "REVISION",
                   "Peer byte fingerprint or research/visual difference is unproved.",
                   "Reopen the current peer page and document specific comparative improvements.")
    chart_reviews = review.get("chart_reviews", {})
    if not isinstance(chart_reviews, dict):
        chart_reviews = {}
    missing = [fid for fid in ids if fid not in chart_reviews]
    if missing:
        _issue(issues, "CHART_BY_CHART_REVIEW_MISSING", "REVISION",
               "Figures without independent author eye-test: " + ", ".join(missing),
               "For each rendered desktop and mobile figure, record the seven review fields "
               "and a concrete revision/no-change reason with screenshot evidence.")
    else:
        for fid in ids:
            item = chart_reviews.get(fid, {})
            if not isinstance(item, dict) or any(
                len(str(item.get(k, "")).strip()) < 15 for k in SELF_REVIEW_FIELDS
            ):
                _issue(issues, "CHART_REVIEW_INCOMPLETE_" + str(fid), "REVISION",
                       "Source and visual semantics are not documented per figure.",
                       "Read the actual source/desktop/mobile exhibit and complete every test.")
    if not peers:
        _issue(issues, "CALIBRATION_PEERS_UNAVAILABLE", "REVISION",
               "No directly comparable peer reports could be read from the current repository.",
               "Document the absence; do not infer a relative visual quality score.")
    if not _eligible_industrial_fy(record, ledger):
        _issue(issues, "SECTOR_OR_PERIOD_COVERAGE_NOT_ESTABLISHED", "REVISION",
               "This automated source-topic dictionary covers rich industrial FY/H1 only.",
               "Use a sector-specific adapter and genuine new-sector/period blind test, "
               "never a manufacturing-template PASS.")
    blockers = [x for x in issues if x["severity"] == "BLOCK"]
    revisions = [x for x in issues if x["severity"] == "REVISION"]
    return {
        "schema": "financials.autonomous_editorial_audit.v1",
        "issuer": code, "period": record.get("period"),
        "original_pdf_sha256": ledger.get("source", {}).get("original_bytes_sha256"),
        "html_sha256": html_sha, "source_topics": covered,
        "source_coverage_count": sum(x["status"] == "COVERED_WITH_SOURCE_KEYS" for x in covered),
        "source_opportunities": len(covered),
        "suggested_peers": peers, "issues": issues,
        "blocker_count": len(blockers), "revision_count": len(revisions),
        "verdict": ("BLOCK" if blockers else "REVISION_REQUIRED" if revisions
                    else "READY_FOR_HUMAN_INDEPENDENT_REVIEW_NOT_CERTIFIED"),
        "independent_human_review": (
            record.get("gates", {}).get("INDEPENDENT_HUMAN_REVIEW", {}).get("status", "NOT_CHECKED")),
        "strict_requested": bool(strict),
        "claim_boundary": "Mechanical source coverage and author self-review only; "
                          "does not certify business causation, originality or aesthetic excellence.",
    }


def audit_issuer(root, code, *, strict=False):
    catalog = _json(root / "site/research_catalog.json")
    issuer = next((i for i in catalog.get("issuers", []) +
                   catalog.get("period_reports", []) if i.get("code") == code), None)
    if issuer is None:
        raise ValueError("UNKNOWN_ISSUER " + code)
    folder = root / "research/issuers" / code
    record = _json(folder / "release-gates.json")
    ledger = _json(folder / "source-ledger.json")
    pub = _json(folder / "publication.json")
    brief = _json(folder / "research-brief.json")
    review_path = folder / "editorial-self-review.json"
    review = _json(review_path) if review_path.is_file() else {}
    html = root / "public" / issuer["href"].lstrip("/")
    return audit(root, issuer, record, ledger, pub, brief, review, catalog,
                 strict=strict, html_sha=sha256(html.read_bytes()).hexdigest())


def changed_issuers(root, since):
    """Git diff is discovery only. Every discovered issuer is independently read."""
    r = subprocess.run(["git", "diff", "--name-only", since, "HEAD"],
                       cwd=root, check=True, text=True, capture_output=True)
    found = set()
    for path in r.stdout.splitlines():
        m = re.fullmatch(r"research/issuers/([0-9]{6})/(?:publication\.json|"
                         r"research-brief\.json|source-ledger\.json|editorial-self-review\.json)", path)
        if m:
            found.add(m.group(1))
        m = re.fullmatch(r"public/([0-9]{6})\.html", path)
        if m:
            found.add(m.group(1))
    return sorted(found)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code", help="Six digit issuer in current main catalog")
    parser.add_argument("--since", help="Git base ref to audit only changed issuers")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--strict", action="store_true",
                        help="Fail closed if any blocker or unfinished editor review")
    parser.add_argument("--out", type=Path, help="Write machine-readable audit JSON")
    a = parser.parse_args()
    if bool(a.code) == bool(a.since):
        parser.error("Choose exactly one of --code and --since")
    root = a.root.resolve()
    codes = [a.code] if a.code else changed_issuers(root, a.since)
    results = [audit_issuer(root, c, strict=a.strict) for c in codes]
    payload = {"schema": "financials.autonomous_editorial_batch.v1",
               "count": len(results), "reports": results}
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf8")
    for r in results:
        print("EDITORIAL_AUTOPILOT", r["issuer"], r["verdict"],
              "coverage", str(r["source_coverage_count"]) + "/" + str(r["source_opportunities"]))
        for issue in r["issues"]:
            print(" ", issue["severity"], issue["code"], issue["action"])
    # Full lack of evidence must NOT become a green CI status simply because
    # the model omitted opt-in fields or edited the peer benchmark wording.
    return 1 if a.strict and any(x["issues"] for x in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
