#!/usr/bin/env python3
"""Editorial FAIL vs engineering render PASS are independent.

Exact historical mobile-overflow FAIL cases are allowed only on the *identical*
old published HTML bytes, as explicit technical debt. No new issuer is allowed
to inherit horizontal finance-chart windows. Any edit to a failing old HTML
must remove the failure, not silently reset a baseline to match new bytes.

This pure contract consumes actual Chromium 1440/768/390 report data, not a
guess from "overflow-x:hidden" or number of SVGs. Human design QA stays open.
"""
from __future__ import annotations
import json,hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WIDTHS={390,768,1440}
def validate_audit(audit,debt):
    errors=[]
    old=debt["legacy_source_frozen_allowlist_for_preexisting_only"]
    if not old or set(old)=={"601628"}:errors.append("VISUAL_LEGACY_DEBT_BASELINE_INVALID")
    records=audit.get("records",[])
    bycode={}
    for row in records:bycode.setdefault(row.get("code"),[]).append(row)
    if len(bycode)!=audit.get("count_issuers") or len(records)!=audit.get("count_viewport_tests"):
        errors.append("VISUAL_AUDIT_ISSUER_VIEWPORT_COUNTS_MISMATCH")
    accepted_debt=[]
    for code,views in bycode.items():
        actual={x["viewport"][0] for x in views}
        if actual!=WIDTHS or len(views)!=3:
            errors.append(f"VISUAL_MISSING_ACTUAL_THREE_CJK_VIEWPORTS {code}")
            continue
        sha={x.get("source_html_sha256") for x in views}
        if len(sha)!=1 or len(next(iter(sha),''))!=64:
            errors.append(f"VISUAL_SOURCE_HTML_FINGERPRINT_UNSTABLE {code}")
        for row in views:
            if row.get("body")>row["viewport"][0]+2 or row.get("quality_gates",{}).get("root_document_no_overflow")!="PASS":
                errors.append(f"VISUAL_ROOT_OVERFLOW {code}/{row['viewport'][0]}")
            if row.get("iframes")!=0:
                errors.append(f"VISUAL_FORBIDDEN_IFRAME_COMPANY {code}")
            if row.get("figures",0)<6:
                errors.append(f"VISUAL_INSUFFICIENT_FINANCIAL_FIGURES {code}")
        mobile=next(x for x in views if x["viewport"][0]==390)
        internal=mobile.get("internalHorizontalScrollers",[])
        if internal:
            if old.get(code)==next(iter(sha),None):
                accepted_debt.append({"code":code,"status":"FAIL_BASELINE_ONLY","artifact_sha":next(iter(sha),None),"count":len(internal),
                                      "type":"MOBILE_FINANCIAL_EXHIBITS_HORIZONTALLY_CLIPPED"})
            else:
                errors.append(f"VISUAL_NO_NEW_OR_CHANGED_COMPANY_MAY_HAVE_390_INNER_SCROLL {code}")
        else:
            if code=="601628" and mobile.get("mobileAltFigures")!=10:
                errors.append(f"VISUAL_601628_MOBILE_MONEY_GRAMMAR_REGRESSED {code}")
        if code not in old and mobile.get("evidenceTables",0)<1:
            errors.append(f"VISUAL_NEW_ISSUER_MUST_HAVE_SOURCE_LINKED_FIGURE_TABLES {code}")
        if code not in old and sum(int(x.get("realSvgTextLabels",0)) for x in views)==0:
            errors.append(f"VISUAL_NEW_ISSUER_HAS_NO_READABLE_ACTUAL_FINANCE_SVG_TEXT {code}")
        if code in old and internal and old[code]!=next(iter(sha),None):
            errors.append(f"VISUAL_LEGACY_FAILED_VERSION_CHANGED_NO_MOBILE_FIX {code}")
    if audit.get("count_issuers",0)>len(old) and not any(x.get("code")=="601628" for x in audit.get("records",[])):
        errors.append("VISUAL_RELEASE_CATALOG_MISSING_ALREADY_PUBLISHED_601628")
    return errors,accepted_debt


def validate_current_published_files(root, audit, debt):
    """Reject stale old screenshots as proof of NEW current HTML bytes.

    The original 11×3 baseline is permanently retained for before/after.
    When an issuer's current full HTML SHA has changed, demand independent
    source-tied real Chromium 3-view receipts with native money-flow proof.
    This does not claim external Cloudflare before a matching live run.
    """
    errors=[];fixed=[];unresolved=[]
    catalog=json.loads((root/"site/research_catalog.json").read_text(encoding="utf8"))["issuers"]
    before={}
    for r in audit["records"]:
        before.setdefault(r["code"],set()).add(r["source_html_sha256"])
    old=debt["legacy_source_frozen_allowlist_for_preexisting_only"]
    seen=set()
    for issuer in catalog:
        code=issuer["code"];seen.add(code)
        html=root/"public"/issuer["href"].lstrip("/")
        if not html.is_file():
            errors.append(f"VISUAL_CURRENT_ISSUER_REPORT_MISSING {code}")
            continue
        sha=hashlib.sha256(html.read_bytes()).hexdigest()
        baseline=before.get(code)
        if baseline=={sha}:
            if code in old:unresolved.append(code)
            continue
        # Insurer had a separately authenticated current production source
        # before this comparative audit. Its HTML SHA changed from first
        # baseline after screenshot-proven typo correction; require BOTH real
        # 1440/768/390 Cloudflare live receipt and source-linked 10 mobile
        # finance exhibitions, not the two-sector renderer's custom schema.
        if code=="601628":
            p=root/"research/issuers/601628/live-release-receipt.json"
            if not p.is_file():
                errors.append("VISUAL_601628_NEW_HTML_REQUIRES_REAL_CLOUDFLARE_SOURCE_LIVE_RECEIPT")
                continue
            q=json.loads(p.read_text(encoding="utf8"))
            vs=q.get("real_chromium_viewports",[])
            valid=(q.get("actual_full_content_sha256_equals_repository_main_601628")==sha and
                q.get("all_11_issuer_external_routes")=="PASS" and
                len(vs)==3 and {v.get("width") for v in vs}==WIDTHS and
                next((v for v in vs if v.get("width")==390),{}).get("mobile_ten_full_width_source_exact_money_exhibits")=="PASS")
            if not valid:
                errors.append("VISUAL_601628_CURRENT_CORRECTED_SOURCE_AND_REAL_CLOUDFLARE_THREE_WIDTHS_MISMATCH")
                continue
            fixed.append({"code":code,"source_html_sha256":sha,"mobile_original_money_grammar":"PASS_REAL_CLOUDFLARE_SOURCE_SHA_ALL_TEN_MOBILE_FINANCIAL_FIGURES"})
            continue
        # Shared optical original-money publisher has its OWN actual real CJK
        # 1440/768/390 screenshots. Its output is not an unrelated sector or
        # insurer receipt; require exact current HTML bytes and native money
        # plus all CAS signed mobile geometry before treating its old 390 FAIL
        # as technically repaired. This does NOT prove external production.
        if code in {"300394","300502","300308"}:
            p=(root/"optical-native-visual-qa-300308/result.json" if code=="300308"
               else root/"optical-native-visual-qa/result.json")
            if not p.is_file():
                errors.append(f"VISUAL_CHANGED_OPTICAL_ISSUER_REQUIRES_REAL_BROWSER_FINANCE_SOURCE_PROOF {code}")
                continue
            d=json.loads(p.read_text(encoding="utf8"))
            vs=[x for x in d.get("cases",[]) if x.get("issuer")==code]
            valid=(len(vs)==3 and {x.get("width") for x in vs}==WIDTHS
                and all(x.get("sha256")==sha for x in vs)
                and all(x.get("money_area")=="PASS" and x.get("signed_accounting_and_svg_geometry")=="PASS" and x.get("figures",0)>=9 for x in vs)
                and all(x.get("native_mobile_finance_no_inner_scroll")=="PASS" for x in vs if x.get("width") in {390,768})
                and all(isinstance(x.get("screenshot_sha256"),str) and len(x["screenshot_sha256"])==64 for x in vs))
            if not valid:
                errors.append(f"VISUAL_CHANGED_OPTICAL_ISSUER_ORIGINAL_MONEY_SOURCE_390_BROWSER_RECEIPT_INVALID {code}")
                continue
            fixed.append({"code":code,"source_html_sha256":sha,"mobile_original_money_grammar":"PASS_REAL_CJK_3_VIEWPORTS_SOURCE_WEIGHTED_AND_SIGNED_ACCOUNTING"})
            continue
        # Old source SHA proves only history, not an edited current page.
        # The two-industry QA is calculated from new source and full HTML bytes.
        receipt=root/"research/issuers"/code/"visual-qa/result.json"
        if not receipt.is_file():
            errors.append(f"VISUAL_CHANGED_ISSUER_REQUIRES_ACTUAL_NEW_BROWSER_CENSUS {code}")
            continue
        d=json.loads(receipt.read_text(encoding="utf8"))
        three=d.get("actual_3_viewport_checks",[])
        widths={x.get("width") for x in three}
        valid=(
            d.get("issuer")==code and d.get("html_sha256")==sha and
            len(three)==3 and widths==WIDTHS and
            all(x.get("body_no_overflow")=="PASS" for x in three) and
            any(x.get("width")==390 and x.get("actual_native_mobile_financial_figures_and_390_no_inner_scroll")=="PASS" for x in three) and
            d.get("all_eight_390px_native_money_visuals_readable_and_source_reconciled")=="PASS" and
            d.get("source_nodes_sinks_ribbons_exact_svg_geometric_proportions")=="PASS"
        )
        if not valid:
            errors.append(f"VISUAL_CHANGED_ISSUER_BROWSER_SOURCE_SHA_OR_390_NATIVE_MONEY_EVIDENCE_INVALID {code}")
            continue
        fixed.append({"code":code,"source_html_sha256":sha,"mobile_original_money_grammar":"PASS_REAL_CHROMIUM_AND_SOURCE_GEOMETRY"})
    for code in before.keys()-seen:
        errors.append(f"VISUAL_ISSUER_CATALOG_REMOVED_WITHOUT_REVIEW {code}")
    if len(catalog)!=audit["count_issuers"]:
        errors.append("VISUAL_CURRENT_CATALOG_COUNT_DIFFERS_FROM_ACTUAL_SCREENSHOT_CENSUS")
    return errors,fixed,unresolved

if __name__=="__main__":
    root=ROOT/"research/visual-audit"
    audit=json.loads((root/"cross-issuer-visual-audit.json").read_text(encoding="utf8"))
    debt=json.loads((root/"quality-debt.json").read_text(encoding="utf8"))
    errors,legacy=validate_audit(audit,debt)
    assert not errors,errors
    assert len(legacy)==debt["actual_mobile_internal_horiz_scroll_fail_count"],"HISTORICAL_390PX_EXHIBIT_FAIL_BASELINE_CANNOT_BE_AUTO_MARKED_PASS"
    assert all(x["status"]=="FAIL_BASELINE_ONLY" for x in legacy)
    current_errors,fixed,still=validate_current_published_files(ROOT,audit,debt)
    assert not current_errors,current_errors
    print("ORIGINAL_SOURCE_SHA_HISTORICAL_FINANCIAL_VISUAL_FAIL_COUNT",len(legacy),[x["code"] for x in legacy])
    print("ACTUAL_CURRENT_STANDALONE_HTML_MOBILE_FIXED_BY_REAL_3_SCREEN_BROWSER_AND_ORIGINAL_MONEY_GEOMETRY",len(fixed),fixed)
    print("ACTUAL_CURRENT_390_FINANCE_INNER_SCROLL_SOURCE_UNRESOLVED_FAIL",len(still),still)
    print("EXACT_OLD_FINGERPRINT_OR_NEW_ACTUAL_CHROMIUM_SOURCE_ARTIFACT_PUBLISH_POLICY_PASS",audit["count_issuers"])
