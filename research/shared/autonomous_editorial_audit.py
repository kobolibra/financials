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
import sys

ROOT = Path(__file__).resolve().parents[2]
# Reuse the existing strict source/period/Decimal research verifier.
TOOLS_DIR = str(ROOT / "skills/ashare-financial-storytelling/tools")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)
from research_evidence import validate as validate_research_brief
from source_publication import cited, signed_bridge_checkpoints
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
    "volume_rate": ("inputs", "rows", "flow", "average_balance"),
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
BANK_TOPICS = (
    ("BANK_NET_INTEREST_BRIDGE",
     ("nii", "nii_prior", "fin_interest_income", "fin_interest_income_prior",
      "fin_interest_expense", "fin_interest_expense_prior"),
     ("signed_bridge",), "P0"),
    ("BANK_AVERAGE_EARNING_ASSETS",
     ("fin_interest_income", "average_earning_assets", "average_earning_assets_prior"),
     ("volume_rate",), "P1"),
    ("BANK_LOAN_DEPOSIT_BASIS",
     ("loans", "loans_prior", "deposits", "deposits_prior"),
     ("comparison", "stock_delta"), "P1"),
    ("BANK_FEES_CREDIT_AND_PROFIT",
     ("fee_net", "fee_net_prior", "credit_impairment", "credit_impairment_prior",
      "parent_net", "parent_net_prior"),
     ("comparison", "signed_bridge"), "P1"),
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
    if fam == "volume_rate" and all(isinstance(figure.get(key), str)
                                    for key in ("flow", "average_balance")):
        return set(cited(figure)) & known
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
        if item.get("period") and (folder / item["period"]).is_dir():
            folder = folder / item["period"]
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
    # Editorial readiness must include genuine verified research, not only figures.
    try:
        validate_research_brief(ledger, brief)
    except (ValueError, KeyError, TypeError, ArithmeticError) as exc:
        _issue(issues, "RESEARCH_EVIDENCE_INVALID", "BLOCK",
               str(exc), "Rebuild exact-PDF source-bound theses and Decimal calculations.")
    if ledger.get("issuer", {}).get("code") != code:
        _issue(issues, "REPORT_ISSUER_MISMATCH", "BLOCK",
               "Catalog issuer and source-ledger issuer disagree.",
               "Reconcile report identity against the original PDF.")
    if (record.get("period") and ledger.get("issuer", {}).get("fiscal_period")
            and record["period"] != ledger["issuer"]["fiscal_period"]):
        _issue(issues, "REPORT_PERIOD_MISMATCH", "BLOCK",
               "Release and source-ledger fiscal periods disagree.",
               "Correct the source identity before publication.")
    # A source-file edit must never be green if the old ledger, research and
    # visual receipts still describe a previous original PDF.
    source_meta = ledger.get("source", {})
    pdf_rel = source_meta.get("source_path")
    pdf_sha = source_meta.get("original_bytes_sha256")
    if not isinstance(pdf_rel, str) or not isinstance(pdf_sha, str):
        _issue(issues, "SOURCE_PDF_IDENTITY_MISSING", "BLOCK",
               "The complete original PDF path/hash is not present in the source ledger.",
               "Attach the actual original source and a SHA-bound ledger.")
    else:
        pdf = (root / pdf_rel).resolve()
        if not pdf.is_relative_to(root.resolve()) or not pdf.is_file():
            _issue(issues, "SOURCE_PDF_NOT_ARCHIVED", "BLOCK",
                   "The original PDF is missing or outside the repository.",
                   "Archive the complete source PDF before reporting a verified analysis.")
        elif sha256(pdf.read_bytes()).hexdigest() != pdf_sha:
            _issue(issues, "SOURCE_PDF_BYTES_CHANGED", "BLOCK",
                   "The actual archived PDF differs from the ledger source SHA.",
                   "Re-extract original cells, rebuild research and recapture current visual evidence.")
    if not isinstance(figures, list):
        figures = []
    source_by_id = {}
    for figure in figures:
        if not isinstance(figure, dict):
            continue
        figure_id = str(figure.get("id"))
        refs = figure_source_refs(figure, known)
        if figure.get("family") in {"signed_bridge", "income_flow_v3"} and figure.get("source_checkpoints"):
            try:
                refs.update(signed_bridge_checkpoints(ledger, figure))
            except (ArithmeticError, ValueError, KeyError, TypeError) as exc:
                _issue(issues, "SIGNED_BRIDGE_CHECKPOINT_INVALID", "BLOCK", str(exc),
                       "Reconcile the cumulative bridge against the original disclosed subtotals.")
        source_by_id[figure_id] = refs
    if _eligible_industrial_fy(record, ledger):
        from dossier_profit_chain import build
        try:
            build(ledger)
        except (ValueError, KeyError, TypeError, ArithmeticError):
            pass  # Signed full bridge retains the separate source-completeness gate.
        else:
            primary = figures[0] if figures else {}
            if primary.get("family") != "income_flow_v3":
                _issue(issues, "COMPLETE_PROFIT_SANKEY_NOT_PRIMARY", "BLOCK",
                       "The legal primary flow must continue to consolidated and parent profit.",
                       "Build the source-bound full income flow; use the gross-only Sankey as a business exhibit.")
    covered = []
    is_bank = ledger.get("issuer", {}).get("statement_format") == "bank"
    topics = [(label, required, families, required, priority)
              for label, required, families, priority in BANK_TOPICS] if is_bank else TOPICS
    for label, required, families, operands, priority in topics:
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
    # A self-described viewport list cannot substitute a matching machine
    # receipt from the *same build*. Bind existing Chromium QA to every figure.
    browser = review.get("browser_evidence", {})
    if not isinstance(browser, dict) or browser.get("current_html_sha256") != html_sha:
        _issue(issues, "BROWSER_PROOF_STALE", "BLOCK",
               "Self-review browser evidence is absent or refers to another HTML SHA.",
               "Capture the current HTML in Chromium and WebKit before release.")
        browser = {}
    declared_views = review.get("required_viewports", [])
    required_views = {("chromium", 1440), ("chromium", 768),
                      ("chromium", 390), ("webkit", 375)}
    actual_views = {(v.get("browser"), v.get("width")) for v in declared_views
                    if isinstance(v, dict)} if isinstance(declared_views, list) else set()
    if not required_views.issubset(actual_views):
        _issue(issues, "BROWSER_VIEWPORT_COVERAGE_MISSING", "BLOCK",
               "The author review omits one or more required native viewport checks.",
               "Review desktop/tablet/mobile Chromium and native WebKit at 375.")
    for engine, widths in (("chromium", {1440, 768, 390}), ("webkit", {375})):
        receipt = browser.get(engine + "_receipt")
        proof = ((root / receipt).resolve() if isinstance(receipt, str)
                 and receipt.startswith("research/issuers/") else None)
        if proof is None or not proof.is_relative_to(root.resolve()) or not proof.is_file():
            _issue(issues, "BROWSER_RECEIPT_MISSING", "BLOCK",
                   f"The {engine} receipt is missing or outside the repository.",
                   "Archive current-article figure-level QA evidence.")
            continue
        try:
            qa = _json(proof)
            if qa.get("sha256") != html_sha:
                _issue(issues, "BROWSER_RECEIPT_STALE", "BLOCK",
                       f"The {engine} receipt describes another HTML build.",
                       "Rebuild and recapture the current HTML SHA.")
            views = qa.get("viewports", [])
            observed = {view.get("width"): view for view in views}
            if qa.get("browser") != engine or len(views) != len(widths) or set(observed) != widths:
                _issue(issues, "BROWSER_RECEIPT_INVALID", "BLOCK",
                       f"Expected one {engine} measurement per width {sorted(widths)}.",
                       "Capture the native viewports again.")
            for width in sorted(widths):
                figures = observed.get(width, {}).get("figures", [])
                if ([figure.get("id") for figure in figures] != ids
                        or any(figure.get("issues") or figure.get("overlap")
                               or not figure.get("values") for figure in figures)):
                    _issue(issues, "BROWSER_FIGURES_NOT_ALL_VERIFIED", "BLOCK",
                           f"{engine} at {width}px does not show the exact reviewed figures cleanly.",
                           "Test each current chart in this native viewport.")
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            _issue(issues, "BROWSER_RECEIPT_INVALID", "BLOCK", str(exc),
                   "Recreate a readable current figure QA receipt.")
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
        else:
            texts = [(x["research_delta"].strip(), x["visual_delta"].strip())
                     for x in chosen if isinstance(x, dict)]
            if len(set(texts)) < 2:
                _issue(issues, "PEER_CALIBRATION_COPYPASTE", "REVISION",
                       "All peers have identical generic research/visual comparisons.",
                       "Describe distinct insights from each current peer's actual figures and essays.")
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
        if len(ids) >= 4:
            answers = [str(chart_reviews.get(fid, {}).get("five_second_answer", "")).strip()
                       if isinstance(chart_reviews.get(fid), dict) else "" for fid in ids]
            if len(set(answers)) < max(3, len(ids) // 2):
                _issue(issues, "CHART_REVIEW_COPYPASTE", "REVISION",
                       "Most charts share an identical generic five-second answer.",
                       "Read each specific rendering and state its distinct accounting finding.")
    if not peers:
        _issue(issues, "CALIBRATION_PEERS_UNAVAILABLE", "REVISION",
               "No directly comparable peer reports could be read from the current repository.",
               "Document the absence; do not infer a relative visual quality score.")
    bank_basis = (is_bank and record.get("sector_adapter") == "bank"
                  and _period_kind(record.get("period")) != "UNKNOWN"
                  and any(topic["topic"] == "BANK_NET_INTEREST_BRIDGE" for topic in covered))
    if not (bank_basis or _eligible_industrial_fy(record, ledger)):
        _issue(issues, "SECTOR_OR_PERIOD_COVERAGE_NOT_ESTABLISHED", "REVISION",
               "The original statement and disclosed keys do not establish a supported research basis.",
               "Use the relevant sector and period evidence, then run a separate blind test.")
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


def audit_legacy_current_full_source(root, code, issuer, catalog, *, strict=False):
    """Legacy HTML without a new-era research-brief/release-gates contract.

    The evidence is narrower than a modern full-research review: only an
    existing financially source-bound article, every visible original SVG,
    native three-viewport capture, real export and cryptographic proof may
    pass. It MUST NOT be misrepresented as a newly complete research review.
    """
    import sys
    from hashlib import sha256 as _sha
    scripts = str(root / "scripts")
    shared = str(root / "research/shared")
    for location in (scripts, shared):
        if location not in sys.path:
            sys.path.insert(0, location)
    from audit_unified_visual_corpus import verified_complete_migration
    from browser_evidence_archive import EvidenceReader
    from qa_editorial_migration import check_vector
    html = root / "public" / issuer["href"].lstrip("/")
    if not html.is_file() or issuer.get("figure_quality_contract") != "FULL_SOURCE_FIGURES_V1":
        raise ValueError("LEGACY_CHANGED_REPORT_REQUIRES_SOURCE_FIGURE_CONTRACT " + code)
    current = _sha(html.read_bytes()).hexdigest()
    profile = catalog["figure_quality_contracts"]["FULL_SOURCE_FIGURES_V1"]
    proof = (root / profile["local_migration_receipt"]).resolve()
    proof.relative_to(root.resolve())
    receipt = _json(proof)
    if not verified_complete_migration(receipt, code, current):
        raise ValueError("LEGACY_CHANGED_REPORT_CURRENT_BROWSER_PROOF_MISSING " + code)
    source = {}
    for path in profile["source_review_indices"]:
        source.update(_json(root / path).get("issuers", {}))
    source_entry = source.get(code, {})
    pdf_sha = source_entry.get("source_sha256")
    pdf_path = (root / source_entry["source_path"]).resolve()
    pdf_path.relative_to(root.resolve())
    # V10 exchange originals are restored by the independent CI rebuild.
    # All tracked research originals must match the archived PDF fingerprint.
    if (pdf_path.is_file() or not source_entry["source_path"].startswith("work/")) and (
            not pdf_path.is_file() or _sha(pdf_path.read_bytes()).hexdigest() != pdf_sha):
        raise ValueError("LEGACY_CHANGED_REPORT_ORIGINAL_PDF_BYTES_DRIFT " + code)
    if receipt["issuers"][code]["pdf_sha256"] != pdf_sha:
        raise ValueError("LEGACY_CHANGED_REPORT_PDF_SHA_MISMATCH " + code)
    evidence = EvidenceReader(root, proof)
    views = [x for x in receipt["cases"] if x["issuer"] == code]
    if len(views) != 3:
        raise ValueError("LEGACY_CHANGED_REPORT_MISSING_THREE_NATIVE_VIEWS " + code)
    for view in views:
        if len(view["figures"]) != issuer["figures"]:
            raise ValueError("LEGACY_CHANGED_REPORT_OMITTED_FINANCE_FIGURE " + code)
        for figure in view["figures"]:
            for key, digest in (("screenshot_file","screenshot_sha256"),
                                ("export_file","vector_sha256")):
                raw = evidence.read(figure[key], code)
                if _sha(raw).hexdigest() != figure[digest]:
                    raise ValueError("LEGACY_CHANGED_REPORT_BROWSER_EVIDENCE_DRIFT " + code)
                if key == "export_file":
                    check_vector(raw.decode("utf8"), code, pdf_sha)
    return {
        "schema": "financials.autonomous_editorial_audit.v1",
        "issuer": code, "period": issuer.get("period"),
        "issuer_period": code + "@" + str(issuer.get("period")),
        "original_pdf_sha256": pdf_sha, "html_sha256": current,
        "source_topics": [], "source_coverage_count": 0,
        "source_opportunities": 0, "suggested_peers": [],
        "issues": [], "blocker_count": 0, "revision_count": 0,
        "verdict": "LEGACY_ALL_FIGURES_SOURCE_VERIFIED_NOT_NEW_EDITORIAL_CERTIFIED",
        "independent_human_review": "NOT_CHECKED",
        "strict_requested": bool(strict),
        "claim_boundary": "All current-source financial SVGs, screenshots, "
                          "native device viewports and PDF identities verified. "
                          "NOT a new-source research thesis, artistic or human signoff."
    }


def audit_issuer(root, code, *, strict=False):
    catalog = _json(root / "site/research_catalog.json")
    if "@" in code:
        company, period = code.split("@", 1)
        if not re.fullmatch(r"[0-9]{6}", company) or not re.fullmatch(
                r"20[0-9]{2}(?:Q1|H1|9M|FY)", period):
            raise ValueError("INVALID_COMPANY_PERIOD " + code)
        issuer = next((i for i in catalog.get("period_reports", [])
                       if i.get("code") == company and i.get("period") == period), None)
        folder = root / "research/issuers" / company / period
    else:
        if not re.fullmatch(r"[0-9]{6}", code):
            raise ValueError("INVALID_COMPANY " + code)
        issuer = next((i for i in catalog.get("issuers", [])
                       if i.get("code") == code), None)
        folder = root / "research/issuers" / code
    if issuer is None:
        raise ValueError("UNKNOWN_ISSUER_OR_PERIOD " + code)
    if not (folder / "release-gates.json").is_file():
        return audit_legacy_current_full_source(root, code, issuer, catalog, strict=strict)
    record = _json(folder / "release-gates.json")
    if (not (folder / "research-brief.json").is_file()
            and issuer.get("figure_quality_contract") == "FULL_SOURCE_FIGURES_V1"
            and (folder / "live-release-receipt.json").is_file()
            and record.get("release_class") == "source_limited_preview"):
        return audit_legacy_current_full_source(root, code, issuer, catalog, strict=strict)
    ledger = _json(folder / "source-ledger.json")
    pub = _json(folder / "publication.json")
    brief = _json(folder / "research-brief.json")
    review_path = folder / "editorial-self-review.json"
    review = _json(review_path) if review_path.is_file() else {}
    html = root / "public" / issuer["href"].lstrip("/")
    result = audit(root, issuer, record, ledger, pub, brief, review, catalog,
                   strict=strict, html_sha=sha256(html.read_bytes()).hexdigest())
    result["issuer_period"] = record.get("code", code.split("@", 1)[0]) + "@" + str(record.get("period"))
    return result


def changed_issuers(root, since):
    """Git diff is discovery only. Every discovered issuer is independently read."""
    r = subprocess.run(["git", "diff", "--name-only", since, "HEAD"],
                       cwd=root, check=True, text=True, capture_output=True)
    found = set()
    catalog = _json(root / "site/research_catalog.json")
    routes = {"public/" + str(i.get("href", "")).lstrip("/"):
              i["code"] + ("@" + i["period"] if i in catalog.get("period_reports", []) else "")
              for i in catalog.get("issuers", []) + catalog.get("period_reports", [])}
    paths = r.stdout.splitlines()
    for path in paths:
        # Source PDFs, notes, review receipts and report assets are material too.
        m = re.match(r"^research/issuers/([0-9]{6})/"
                     r"(?:(20[0-9]{2}(?:Q1|H1|9M|FY))/)?", path)
        if m:
            found.add(m.group(1) + ("@" + m.group(2) if m.group(2) else ""))
        if path in routes:
            found.add(routes[path])
        elif re.fullmatch(r"public/(?:.*/)?[0-9]{6}(?:-[0-9]{4}(?:q[1-4]|h1|9m|fy))?\.html", path):
            raise ValueError("UNCATALOGED_PUBLISHED_ISSUER_ROUTE " + path)
    if "site/research_catalog.json" in paths:
        base = subprocess.run(["git", "show", since + ":site/research_catalog.json"],
                              cwd=root, check=True, text=True, capture_output=True)
        before = json.loads(base.stdout)
        def entries(d):
            return {x["code"] + ("@" + x["period"] if x in d.get("period_reports", []) else ""):
                    x for x in d.get("issuers", []) + d.get("period_reports", [])}
        previous, current = entries(before), entries(catalog)
        removed = set(previous) - set(current)
        if removed:
            raise ValueError("CATALOG_ISSUER_REMOVAL_NEEDS_EXPLICIT_REVIEW "
                             + ",".join(sorted(removed)))
        found.update(code for code, entry in current.items() if previous.get(code) != entry)
    return sorted(found)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code", help="Six digit issuer in current main catalog")
    parser.add_argument("--since", help="Git base ref to audit only changed issuers")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--strict", action="store_true",
                        help="Fail closed if any blocker or unfinished editor review")
    parser.add_argument("--out", type=Path, help="Write machine-readable audit JSON")
    parser.add_argument("--review-template", type=Path,
                        help="Scaffold author tasks from current facts; does NOT fill the review")
    a = parser.parse_args()
    if bool(a.code) == bool(a.since):
        parser.error("Choose exactly one of --code and --since")
    root = a.root.resolve()
    codes = [a.code] if a.code else changed_issuers(root, a.since)
    results = [audit_issuer(root, c, strict=a.strict) for c in codes]
    if a.review_template:
        if len(codes) != 1:
            parser.error("--review-template requires exactly one report")
        report = results[0]
        real = (root / "research/issuers" / codes[0].replace("@", "/")
                / "publication.json")
        figure_ids = [x["id"] for x in _json(real)["figures"]]
        template = {
            "status": "NOT_CHECKED",
            "reviewed_html_sha256": report["html_sha256"],
            "reviewed_source_pdf_sha256": report["original_pdf_sha256"],
            "peer_calibration": {"peers": [
                {"code": p["code"], "html_sha256": p["html_sha256"],
                 "research_delta": "NOT_CHECKED", "visual_delta": "NOT_CHECKED"}
                for p in report["suggested_peers"][:2]]},
            "chart_reviews": {fid: {k: "NOT_CHECKED" for k in SELF_REVIEW_FIELDS}
                              for fid in figure_ids},
            "independent_human_review": "NOT_CHECKED",
            "warning": "This is an incomplete author task list. It must not be inserted "
                       "as PASS, and no screenshot is certified by these placeholders.",
        }
        a.review_template.parent.mkdir(parents=True, exist_ok=True)
        a.review_template.write_text(json.dumps(template, ensure_ascii=False, indent=2)
                                     + "\n", encoding="utf8")
    payload = {"schema": "financials.autonomous_editorial_batch.v1",
               "count": len(results), "reports": results,
               "scope": ("CHANGED_REPORTS_AUDITED" if results
                         else "NO_REPORT_CHANGED_NOT_AN_EDITORIAL_CERTIFICATION")}
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf8")
    if not results:
        print("EDITORIAL_AUTOPILOT_SCOPE ZERO_CHANGED_REPORTS; "
              "this green step does not certify report depth or visual quality")
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
