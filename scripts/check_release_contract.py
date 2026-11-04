#!/usr/bin/env python3
"""Fail-closed, issuer-independent publication-evidence and feedback regression contract.

New issuers must present a release-gates.json rather than inheriting the eight
historical pages' QA status. This checks data/proof consistency, NOT browser/live
service truth or the professional merits of source interpretation.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from decimal import Decimal, InvalidOperation

ROOT = Path(__file__).resolve().parents[1]
LEGACY_PRE_CONTRACT = frozenset({
    "300394", "300308", "300502", "600036", "688111", "600519", "000333"
})
GATES = frozenset({
    "PDF_BYTES", "SOURCE_ROW_COLUMN", "ACCOUNTING_CORE",
    "RESEARCH_COUNTERCASE", "CHART_SEMANTICS", "VISUAL_EDITORIAL_SELF",
    "BROWSER_LOCAL", "OFFLINE_REBUILD", "MAJOR_NOTES_COMPLETE",
    "REPORTED_NOTE_TIES", "OFFICIAL_PDF_BYTE_EQUIVALENCE",
    "HISTORICAL_PEERS_VALUATION", "INDEPENDENT_HUMAN_REVIEW",
    "CLOUDFLARE_LIVE"
})
PREVIEW_BLOCKERS = frozenset({
    "PDF_BYTES", "SOURCE_ROW_COLUMN", "ACCOUNTING_CORE",
    "RESEARCH_COUNTERCASE", "CHART_SEMANTICS", "VISUAL_EDITORIAL_SELF",
    "BROWSER_LOCAL", "OFFLINE_REBUILD"
})
STATUSES = frozenset({"PASS", "FAIL", "NOT_CHECKED"})
RELEASE_CLASSES = frozenset({"source_limited_preview", "verified_research"})
SECTOR_ADAPTERS = frozenset({
    "optical", "semiconductor", "manufacturing", "software", "consumer",
    "bank", "insurance", "insurance_group", "property", "broker",
    "pharma", "utility", "energy", "construction", "holding_mixed",
    "other_sector_specific"
})
REGRESSION_STATUSES = frozenset({
    "TESTED_ISSUER_ONLY", "TESTED_GENERIC_MECHANISM",
    "FAIL_LIVE_STILL_OPEN", "NEW_CONTRACT"
})
GITHUB_ACTION = re.compile(r"^https://github[.]com/kobolibra/financials/actions/runs/[0-9]+$")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def checked_path(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or value.startswith("/"):
        raise ValueError(f"INVALID_RELATIVE_PATH {value}")
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"OUTSIDE_REPOSITORY_PATH {value}") from exc
    return candidate


def validate_proof(root: Path, key: str, gate: dict) -> list[str]:
    errors: list[str] = []
    status, proof = gate.get("status"), gate.get("proof")
    if status not in STATUSES:
        return [f"INVALID_GATE_STATUS {key}: {status}"]
    if status != "NOT_CHECKED":
        if not isinstance(proof, str) or not proof:
            errors.append(f"UNSUPPORTED_GATE {key}: PASS/FAIL without proof")
        elif not GITHUB_ACTION.fullmatch(proof):
            try:
                if not checked_path(root, proof).is_file():
                    errors.append(f"MISSING_GATE_PROOF {key}: {proof}")
            except ValueError as exc:
                errors.append(str(exc))
    if not isinstance(gate.get("scope"), str) or len(gate["scope"].strip()) < 15:
        errors.append(f"AMBIGUOUS_GATE_SCOPE {key}")
    return errors


def validate_release(root: Path, catalog_issuer: dict, record: dict,
                     *, check_bytes: bool = True) -> list[str]:
    errors: list[str] = []
    code = catalog_issuer["code"]
    if record.get("schema_version") != 1 or record.get("code") != code:
        errors.append(f"ISSUER_RECORD_IDENTITY {code}")
    if record.get("report_route") != catalog_issuer["href"]:
        errors.append(f"ISSUER_ROUTE_MISMATCH {code}")
    route = catalog_issuer["href"]
    expected = "public/" + route.lstrip("/")
    if record.get("report_file") != expected or not (root / expected).is_file():
        errors.append(f"ISSUER_HTML_NOT_CANONICAL {code}")
    # Optional issuer-owned canonical offline HTML byte fingerprint. This is
    # mandatory once a new issuer opts into published_html_sha256; missing
    # the updated value after regenerating one sentence must fail release.
    # Historic company receipts without this field are not retroactively faked.
    declared_html_sha = record.get("published_html_sha256")
    if declared_html_sha is not None and declared_html_sha not in {"NOT_CHECKED", "NOT_CHECKED_PENDING_MAIN_DEPLOY"}:
        if not isinstance(declared_html_sha, str) or not re.fullmatch("[a-f0-9]{64}", declared_html_sha):
            errors.append(f"PUBLISHED_REPORT_SHA_INVALID {code}")
        elif (root / expected).is_file() and hashlib.sha256((root / expected).read_bytes()).hexdigest() != declared_html_sha:
            errors.append(f"PUBLISHED_REPORT_SHA_MISMATCH {code}")
    if not record.get("period") or record.get("release_class") not in RELEASE_CLASSES:
        errors.append(f"ISSUER_PERIOD_OR_CLASS_MISSING {code}")
    if record.get("release_class") == "verified_research" and catalog_issuer.get("stage") == "source-review":
        errors.append(f"FULL_RESEARCH_BUT_CATALOG_SOURCE_REVIEW {code}")

    pdf = record.get("source_pdf", {})
    path = pdf.get("path")
    sha = pdf.get("sha256")
    if not isinstance(sha, str) or not re.fullmatch("[a-f0-9]{64}", sha):
        errors.append(f"PDF_SHA_NOT_GROUNDED {code}")
    if pdf.get("official_original_byte_equivalence") not in STATUSES:
        errors.append(f"PDF_OFFICIAL_BYTE_GATE_MISSING {code}")
    if not isinstance(pdf.get("bytes"), int) or pdf["bytes"] < 10000:
        errors.append(f"PDF_BYTE_SIZE_INVALID {code}")
    if not isinstance(pdf.get("physical_pages"), int) or pdf["physical_pages"] < 2:
        errors.append(f"PDF_PAGE_CLAIM_INVALID {code}")
    try:
        original = checked_path(root, path)
        if original.suffix.lower() != ".pdf" or not original.is_file():
            errors.append(f"PDF_NOT_ARCHIVED {code}")
        elif check_bytes:
            data = original.read_bytes()
            if (not data.startswith(b"%PDF") or len(data) != pdf.get("bytes")
                    or hashlib.sha256(data).hexdigest() != sha):
                errors.append(f"PDF_BYTE_HASH_MISMATCH {code}")
    except ValueError as exc:
        errors.append(str(exc))

    # A release JSON alone can describe a correct PDF while a stale source
    # ledger or nine attractive charts still point to a different report.
    # Demand issuer, period, original bytes identity and figure citations
    # across the actual checked-in artifacts, not only release metadata.
    sector = record.get("sector_adapter")
    accounting_basis = record.get("accounting_basis")
    if sector not in SECTOR_ADAPTERS or not isinstance(accounting_basis, str) or len(accounting_basis) < 20:
        errors.append(f"ISSUER_SECTOR_MODEL_MISSING {code}")
    else:
        forbidden = {
            "bank": ("industrial_", "industrial_fcf", "revenue_cogs"),
            "insurance": ("industrial_", "revenue_cogs", "premium_as_recognized_revenue"),
            "insurance_group": ("industrial_", "revenue_cogs", "premium_as_recognized_revenue"),
            "property": ("presales_as_revenue", "restricted_cash_equals_free_cash"),
        }
        if any(x in accounting_basis.lower() for x in forbidden.get(sector, ())):
            errors.append(f"WRONG_INDUSTRY_ACCOUNTING_GRAMMAR {code}/{sector}")
        if sector == "other_sector_specific" and len(accounting_basis) < 80:
            errors.append(f"UNKNOWN_SECTOR_REQUIRES_DOCUMENTED_MODEL {code}")

    ledger_data = None
    try:
        ledger_file = checked_path(root, record.get("ledger_file"))
        if not ledger_file.is_file():
            errors.append(f"ISSUER_SOURCE_LEDGER_MISSING {code}")
        else:
            ledger_data = read_json(ledger_file)
            identity = ledger_data.get("issuer", {})
            source = ledger_data.get("source", {})
            if identity.get("code") != code or identity.get("fiscal_period") != record.get("period"):
                errors.append(f"LEDGER_ISSUER_PERIOD_MISMATCH {code}")
            if source.get("original_bytes_sha256") != sha or (
                "SHA_PASS" not in str(source.get("original_bytes_gate", ""))
            ):
                errors.append(f"LEDGER_PDF_PROVENANCE_STALE {code}")
            if source.get("physical_pages_observed") != pdf.get("physical_pages"):
                errors.append(f"LEDGER_PDF_PHYSICAL_PAGE_DRIFT {code}")
            for key, fact in ledger_data.get("facts", {}).items():
                if fact.get("classification") not in ("DISCLOSED", "DISCLOSED_RESTATED"):
                    continue  # Derived claims still require separate source semantic review.
                amount = str(fact.get("yuan", ""))
                try:
                    parsed = Decimal(amount)
                    if not parsed.is_finite() or parsed.as_tuple().exponent < -2:
                        raise InvalidOperation("original precision exceeds cents")
                except (InvalidOperation, ValueError, TypeError):
                    errors.append(f"LEDGER_DISCLOSED_VALUE_INVALID {code}/{key}")
                if not isinstance(fact.get("page"), int) or not 1 <= fact["page"] <= pdf.get("physical_pages", 0):
                    errors.append(f"LEDGER_FACT_SOURCE_PAGE_INVALID {code}/{key}")
                if not isinstance(fact.get("period"), str) or not fact["period"]:
                    errors.append(f"LEDGER_FACT_PERIOD_MISSING {code}/{key}")
                # Insurance regulatory capital is issuer-level C-ROSS eligible/minimum
                # capital: it is NOT CAS consolidated shareholder equity. Allow
                # this third scope exclusively for a documented insurer adapter.
                accepted_scopes = {"consolidated", "parent"}
                if record.get("sector_adapter") in {"insurance", "insurance_group"}:
                    accepted_scopes.add("issuer_regulatory")
                if fact.get("scope") not in accepted_scopes:
                    errors.append(f"LEDGER_FACT_SCOPE_INVALID {code}/{key}")
                if len(str(fact.get("label") or "")) < 3:
                    errors.append(f"LEDGER_FACT_ROW_LABEL_MISSING {code}/{key}")
                kind = fact.get("type")
                if kind in ("stock", "flow"):
                    if fact.get("unit") != "元" or fact.get("currency") != "CNY":
                        errors.append(f"LEDGER_MONEY_UNIT_NOT_YUAN {code}/{key}")
                elif kind == "ratio":
                    if fact.get("unit") not in ("%", "pp"):
                        errors.append(f"LEDGER_RATIO_WRONGLY_MONEY {code}/{key}")
                else:
                    errors.append(f"LEDGER_FACT_TEMPORAL_KIND_INVALID {code}/{key}")
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        errors.append(f"ISSUER_SOURCE_LEDGER_INVALID {code}: {exc}")

    try:
        briefs_file = checked_path(root, record.get("figure_briefs_file"))
        if not briefs_file.is_file():
            errors.append(f"ISSUER_FIGURE_BRIEFS_MISSING {code}")
        else:
            briefs = read_json(briefs_file)
            if (briefs.get("issuer") != code or briefs.get("report") != record.get("period")
                    or briefs.get("source_sha256") != sha):
                errors.append(f"FIGURE_BRIEFS_PDF_IDENTITY_MISMATCH {code}")
            figures = briefs.get("figure_briefs", [])
            if not isinstance(figures, list) or len(figures) < 2:
                errors.append(f"COMPLETE_RESEARCH_NOT_A_SINGLE_CHART {code}")
            else:
                unique_families = set()
                figure_ids = set()
                for item in figures:
                    fid = item.get("id")
                    if not fid or fid in figure_ids:
                        errors.append(f"FIGURE_ID_DUPLICATE_OR_MISSING {code}/{fid}")
                    figure_ids.add(fid)
                    unique_families.add(item.get("family"))
                    for required in ("question", "takeaway", "identity", "counter", "mobile"):
                        if len(str(item.get(required) or "")) < 10:
                            errors.append(f"FIGURE_RESEARCH_BRIEF_MISSING {code}/{fid}/{required}")
                    pages = item.get("source_pages", [])
                    if not pages or any(not isinstance(x, int) or x < 1 or x > pdf.get("physical_pages", 0) for x in pages):
                        errors.append(f"FIGURE_SOURCE_PAGE_INVALID {code}/{fid}")
                    cited = item.get("facts", [])
                    if not cited or (ledger_data and any(x not in ledger_data.get("facts", {}) for x in cited)):
                        errors.append(f"FIGURE_UNGROUNDED_FACT_ID {code}/{fid}")
                if len(unique_families) < 2:
                    errors.append(f"GENERIC_REPEATED_FIGURE_GRAMMAR {code}")
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        errors.append(f"ISSUER_FIGURE_BRIEFS_INVALID {code}: {exc}")

    # The published offline file is itself a financial dataset. When an issuer
    # embeds a machine-readable source ledger, it must match the checked-in
    # source file, even for narrative provenance fields. The ASR clean rebuild
    # caught this: updating source.reason without regenerating the published
    # HTML changed one huge JSON line while all accounting/geometry passed.
    if ledger_data is not None:
        try:
            html = (root / expected).read_text(encoding="utf-8")
            match = re.search(
                r'<script\s+id="ledger-data"\s+type="application/json">([\s\S]*?)</script>',
                html,
            )
            if match:
                rendered = json.loads(match.group(1))
                for field in ("issuer", "source", "facts", "segments"):
                    if rendered.get(field) != ledger_data.get(field):
                        errors.append(f"PUBLISHED_LEDGER_FIELD_DRIFT {code}/{field}")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"PUBLISHED_LEDGER_EMBED_INVALID {code}: {exc}")

    sankey = record.get("sankey", {})
    if sankey.get("decision") not in {"USED_CONSERVED", "OMITTED_WITH_SOURCE_REASON"}:
        errors.append(f"SANKEY_RESEARCH_DECISION_MISSING {code}")
    if (sankey.get("decision") == "OMITTED_WITH_SOURCE_REASON"
            and len(str(sankey.get("omission_reason") or "")) < 25):
        errors.append(f"SANKEY_OMISSION_NOT_SOURCE_GROUNDED {code}")

    gates = record.get("gates")
    if not isinstance(gates, dict):
        return errors + [f"ISSUER_GATES_MISSING {code}"]
    for key in sorted(GATES - gates.keys()):
        errors.append(f"REQUIRED_GATE_MISSING {code}/{key}")
    for key in sorted(gates.keys() - GATES):
        errors.append(f"UNKNOWN_GATE {code}/{key}")
    for key in sorted(GATES & gates.keys()):
        errors += validate_proof(root, f"{code}/{key}", gates[key])
    if record.get("release_class") == "source_limited_preview":
        for key in sorted(PREVIEW_BLOCKERS & gates.keys()):
            if gates[key].get("status") != "PASS":
                errors.append(f"PREVIEW_P0_BLOCKED {code}/{key}")
        # Bounded exceptions cannot vanish from a preview merely because the
        # main accounting equation passes.
        for key, gate in gates.items():
            if gate.get("status") == "FAIL" and not any(
                b.get("kind") in {"SOURCE_NOTE", "RELEASE", "RESEARCH"}
                for b in record.get("blockers", [])
            ):
                errors.append(f"FAIL_WITHOUT_DISCLOSED_BLOCKER {code}/{key}")
    else:
        for key in sorted(GATES & gates.keys()):
            if gates[key].get("status") != "PASS":
                errors.append(f"VERIFIED_RESEARCH_HAS_OPEN_GATE {code}/{key}")
    # Never silently convert older Cloudflare browser green to new live PASS:
    # a source receipt is not the same thing as deployed production bytes.
    if gates.get("CLOUDFLARE_LIVE", {}).get("status") == "PASS":
        live_fp=record.get("live_release_fingerprint")
        if not live_fp:
            errors.append(f"LIVE_PASS_WITHOUT_DEPLOYED_FINGERPRINT {code}")
        # A new issuer with a cryptographic FULL HTML SHA is not allowed to
        # claim an unrelated 'green' live proof or just the PDF source SHA.
        # Older source-limited issuer records with explicit NOT_CHECKED HTML
        # fingerprint retain their historical partial-proof classification.
        if isinstance(declared_html_sha,str) and re.fullmatch("[a-f0-9]{64}",declared_html_sha):
            if live_fp!=declared_html_sha:
                errors.append(f"LIVE_FINGERPRINT_HTML_DRIFT {code}")
            commit=record.get("actual_main_release_commit")
            if not isinstance(commit,str) or not re.fullmatch("[a-f0-9]{40}",commit):
                errors.append(f"LIVE_PROOF_MAIN_COMMIT_INVALID {code}")
            # Generic new-issuer evidence must reference an original ACTUAL
            # public-browser receipt, not a green provider badge or a bare
            # Github Actions number. Historical issuers with explicitly
            # NOT_CHECKED publication HTML SHA are deliberately excluded.
            live_path=record.get("live_receipt_file")
            if not live_path:
                errors.append(f"LIVE_CAPTURE_RECEIPT_MISSING {code}")
            else:
                try:
                    receipt=read_json(checked_path(root,live_path))
                    if receipt.get("schema_version")!=1 or receipt.get("issuer")!=code:
                        errors.append(f"LIVE_CAPTURE_ISSUER_MISMATCH {code}")
                    if receipt.get("status")!="PASS":
                        errors.append(f"LIVE_CAPTURE_NOT_PASS {code}")
                    if receipt.get("verified_git_commit")!=commit:
                        errors.append(f"LIVE_CAPTURE_MAIN_SHA_MISMATCH {code}")
                    if receipt.get("actual_publication_action")!=gates["CLOUDFLARE_LIVE"].get("proof"):
                        errors.append(f"LIVE_CAPTURE_ACTION_MISMATCH {code}")
                    if receipt.get("actual_full_content_sha256_equals_repository_main_"+code)!=declared_html_sha:
                        errors.append(f"LIVE_CAPTURE_HTML_SHA_MISMATCH {code}")
                    if receipt.get("pdf_sha256")!=record.get("source_pdf",{}).get("sha256"):
                        errors.append(f"LIVE_CAPTURE_ORIGINAL_SOURCE_SHA_MISMATCH {code}")
                    home_sha=receipt.get("actual_full_content_sha256_equals_repository_main_index")
                    if not isinstance(home_sha,str) or not re.fullmatch("[a-f0-9]{64}",home_sha):
                        errors.append(f"LIVE_CAPTURE_HOME_SHA_INVALID {code}")
                    expected_historical_home=record.get("actual_directory_fingerprint")
                    # Compare to the homepage fingerprint AS OF THIS release:
                    # later company additions legitimately change today's root,
                    # but cannot retroactively falsify old captured release data.
                    if expected_historical_home and home_sha!=expected_historical_home:
                        errors.append(f"LIVE_CAPTURE_HOMEPAGE_SHA_MISMATCH {code}")
                    screens=receipt.get("screenshots",[])
                    expected_screens={f"live_{code}_{w}.png" for w in (1440,768,390)}
                    expected_screens|={f"live_directory_{w}.png" for w in (1440,768,390)}
                    if not isinstance(screens,list) or {x.get("name") for x in screens if isinstance(x,dict)}!=expected_screens:
                        errors.append(f"LIVE_CAPTURE_SCREENSHOT_SET_INVALID {code}")
                    elif any(not isinstance(x.get("sha256"),str) or not re.fullmatch("[a-f0-9]{64}",x["sha256"]) or not isinstance(x.get("bytes"),int) or x["bytes"]<10000 for x in screens):
                        errors.append(f"LIVE_CAPTURE_SCREENSHOT_HASH_INVALID {code}")
                    views=receipt.get("real_chromium_viewports",[])
                    if not isinstance(views,list) or {x.get("width") for x in views if isinstance(x,dict)}!={1440,768,390}:
                        errors.append(f"LIVE_CAPTURE_REAL_VIEWPORTS_INVALID {code}")
                    else:
                        site=record.get("live_site_origin","https://financials-in-visuals.pages.dev")
                        good_articles={site+f"/{code}",site+f"/{code}.html"}
                        for view in views:
                            if view.get("actual_dedicated_article_final_url") not in good_articles or view.get("actual_return_to_library_url")!=site+"/#companies":
                                errors.append(f"LIVE_CAPTURE_COMPANY_VS_HOME_ROUTE_INVALID {code}")
                                break
                            if any(view.get(z)!="PASS" for z in ("new_601628_main_route" if code=="601628" else "back_to_same_home","no_page_horizontal_overflow","real_live_screenshots")):
                                errors.append(f"LIVE_CAPTURE_VIEWPORT_PROOF_INVALID {code}")
                                break
                        if receipt.get("all_11_issuer_external_routes")!="PASS" and code=="601628":
                            errors.append(f"LIVE_CAPTURE_ELEVEN_ISSUER_ROUTE_INVALID {code}")
                        if code=="601628" and next(x for x in views if x["width"]==390).get("mobile_ten_full_width_source_exact_money_exhibits")!="PASS":
                            errors.append(f"LIVE_CAPTURE_PHONE_FINANCE_FIGURES_INVALID {code}")
                except (OSError,ValueError,KeyError,TypeError,AttributeError,json.JSONDecodeError) as exc:
                    errors.append(f"LIVE_CAPTURE_RECEIPT_UNREADABLE {code}: {type(exc).__name__}")
    return errors


def validate_registry(root: Path) -> list[str]:
    errors = []
    path = root / "skills/ashare-financial-storytelling/quality-regressions.json"
    data = read_json(path)
    if data.get("schema_version") != 1:
        errors.append("REGRESSION_SCHEMA_UNSUPPORTED")
    cases = data.get("cases", [])
    if not cases:
        errors.append("REGRESSION_CASES_EMPTY")
    ids = [x.get("id") for x in cases]
    if len(set(ids)) != len(ids):
        errors.append("REGRESSION_DUPLICATE_ID")
    for case in cases:
        id_ = case.get("id")
        if not re.fullmatch(r"[A-Z]{3}-[0-9]{3}", str(id_)):
            errors.append(f"REGRESSION_ID_INVALID {id_}")
        if case.get("status") not in REGRESSION_STATUSES:
            errors.append(f"REGRESSION_STATUS_INVALID {id_}")
        if case.get("transfer_gate") not in (GATES | {"HANDOFF_SOURCE_OF_TRUTH"}):
            errors.append(f"REGRESSION_WRONG_GATE {id_}")
        if case.get("scope") not in {"single_issuer", "cross_issuer_mechanism", "cross_issuer_process"}:
            errors.append(f"REGRESSION_SCOPE_INVALID {id_}")
        for field in ("root_cause", "correction", "assertion_marker", "proof_file"):
            if not isinstance(case.get(field), str) or len(case[field]) < 3:
                errors.append(f"REGRESSION_MISSING_{field} {id_}")
        try:
            test_path = checked_path(root, case.get("proof_file"))
            if not test_path.is_file():
                errors.append(f"REGRESSION_PROOF_FILE_MISSING {id_}")
            elif case.get("assertion_marker") not in test_path.read_text(encoding="utf-8"):
                errors.append(f"REGRESSION_MARKER_MISSING {id_}")
        except (ValueError, UnicodeError) as exc:
            errors.append(f"REGRESSION_PROOF_INVALID {id_}: {exc}")
    return errors


def validate_repository(root: Path = ROOT, *, check_bytes: bool = True) -> list[str]:
    errors = validate_registry(root)
    issuers = read_json(root / "site/research_catalog.json")["issuers"]
    codes = [x["code"] for x in issuers]
    if len(set(codes)) != len(codes):
        errors.append("DUPLICATE_CATALOG_CODE")
    if not LEGACY_PRE_CONTRACT.issubset(codes):
        errors.append("HISTORIC_SEVEN_REMOVED")
    for issuer in issuers:
        code = issuer["code"]
        if code in LEGACY_PRE_CONTRACT:
            continue  # explicit historical review debt, not retroactive certification
        record_path = root / "research" / "issuers" / code / "release-gates.json"
        if not record_path.is_file():
            errors.append(f"UNREGISTERED_NEW_ISSUER {code}")
            continue
        errors += validate_release(root, issuer, read_json(record_path),
                                   check_bytes=check_bytes)
    return errors


if __name__ == "__main__":
    try:
        problems = validate_repository()
    except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print("RELEASE_CONTRACT_CRASH", type(exc).__name__, str(exc), file=sys.stderr)
        raise SystemExit(2)
    if problems:
        for problem in problems:
            print("RELEASE_CONTRACT_FAIL", problem, file=sys.stderr)
        raise SystemExit(1)
    print("ISSUER_RELEASE_CONTRACT_PASS: existing seven legacy-review debt explicit; all new issuer records source-hashed and independently gated; regression inventory structurally verified")
