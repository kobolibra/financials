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
        if issuer.get('editorial_contract'):
            try:
                import sys
                sys.path.insert(0,str(root/'research/shared'))
                from audit_unified_visual_corpus import verified_complete_migration
                from browser_evidence_archive import EvidenceReader
                from qa_editorial_migration import check_vector
                catalog_full=json.loads((root/'site/research_catalog.json').read_text())
                proof=(root/catalog_full['figure_quality_contracts']['FULL_SOURCE_FIGURES_V1']['local_migration_receipt']).resolve()
                proof.relative_to(root.resolve());q=json.loads(proof.read_text());reader=EvidenceReader(root,proof)
                if not verified_complete_migration(q,code,sha):raise ValueError('CURRENT_COMPLETE_PROOF')
                bundle=json.loads((root/issuer['editorial_manifest']).read_text())
                if q['issuers'][code]['pdf_sha256']!=bundle['source_pdf']['source_sha256']:raise ValueError('CURRENT_ORIGINAL_PDF')
                for case in (c for c in q['cases'] if c['issuer']==code):
                    if case.get('editorial_main_layer')!='PASS' or len(case['figures'])!=issuer['figures']:raise ValueError('READING_LAYER_OR_MISSING_REFERENCE')
                    if sum(f['grammar']=='FULL_PROFIT_CHAIN_V1' for f in case['figures'])!=1:raise ValueError('ONE_PROFIT_CHAIN')
                    for f in case['figures']:
                        for path_key,hash_key in (('screenshot_file','screenshot_sha256'),('export_file','vector_sha256')):
                            raw=reader.read(f[path_key],code)
                            if hashlib.sha256(raw).hexdigest()!=f[hash_key]:raise ValueError('REAL_EVIDENCE_BYTES')
                            if path_key=='export_file':check_vector(raw.decode(),code,q['issuers'][code]['pdf_sha256'])
            except (OSError,ValueError,KeyError,TypeError,ImportError):
                errors.append('VISUAL_CURRENT_FULL_PROFIT_CHAIN_COMPLETE_PROOF_REQUIRED '+code)
                continue
            fixed.append({'code':code,'source_html_sha256':sha,'mobile_original_money_grammar':'PASS_CURRENT_ALL_FIGURES_AND_DOWNSTREAM_RECONCILIATION_NOT_HUMAN_CERTIFICATION'})
            continue
        if issuer.get('source_publication'):
            from audit_unified_visual_corpus import verified_complete_migration
            folder=(root/issuer['source_publication']).resolve()
            try:
                folder.relative_to(root.resolve())
                proof=folder/'visual-qa/result.json'
                q=json.loads(proof.read_text())
                valid=verified_complete_migration(q,code,sha)
                for case in q.get('cases',[]):
                    for figure in case.get('figures',[]):
                        for path_key,hash_key in (('screenshot_file','screenshot_sha256'),('export_file','vector_sha256')):
                            f=(proof.parent/figure[path_key]).resolve();f.relative_to(proof.parent.resolve())
                            valid=valid and hashlib.sha256(f.read_bytes()).hexdigest()==figure[hash_key]
                if not valid:raise ValueError('current source browser proof differs')
            except (OSError,ValueError,KeyError,TypeError):
                errors.append('VISUAL_NEW_SOURCE_DOSSIER_CURRENT_COMPLETE_PROOF_REQUIRED '+code)
                continue
            fixed.append({'code':code,'source_html_sha256':sha,'mobile_original_money_grammar':'PASS_ALL_SOURCE_FIGURES_CURRENT_BYTES_REAL_DOWNLOADS_NOT_HUMAN_CERTIFICATION'})
            continue
        # Insurer had a separately authenticated current production source
        # before this comparative audit. Its HTML SHA changed from first
        # baseline after screenshot-proven typo correction; require BOTH real
        # 1440/768/390 Cloudflare live receipt and source-linked 10 mobile
        # finance exhibitions, not the two-sector renderer's custom schema.
        # V10's renewed source-bound path uses one actual original-byte CJK
        # Chromium census for ALL independent company figures, not only the
        # hero Sankey or a generic sector's unrelated receipt schema.
        if code in {"688111","600519","000333","600036"}:
            p=root/"research/rebuild-v10/real-browser-qa/result.json"
            if not p.is_file():
                errors.append(f"VISUAL_CHANGED_V10_REQUIRES_NEW_ALL_FIGURE_CJK_SOURCE_RECEIPT {code}")
                continue
            q=json.loads(p.read_text(encoding="utf8"))
            arr=[x for x in q.get("cases",[]) if x.get("code")==code]
            counts={"688111":9,"600519":9,"000333":10,"600036":8}
            expected=counts[code]
            valid=(q.get("all_36_issuer_exhibits_3_viewports")=="PASS"
                   and len(arr)==3
                   and {x.get("width") for x in arr}==WIDTHS
                   and all(x.get("html_sha256")==sha and
                           x.get("real_chromium") is True and
                           x.get("actual_all_figures")==expected and
                           isinstance(x.get("full_page_screenshot_sha256"),str) and
                           len(x["full_page_screenshot_sha256"])==64 and
                           len(x.get("figures",[]))==expected for x in arr)
                   and all(len({f.get("figure") for f in x["figures"]})==expected
                           and all(f.get("native_source_svg")== (x["width"]<=850)
                                   and f.get("scroll_free")=="PASS"
                                   and f.get("CJK_text_inside_screen")=="PASS"
                                   and f.get("source_ribbon_actual_SVG_thickness")=="PASS"
                                   and isinstance(f.get("actual_figure_png_sha256"),str)
                                   and len(f["actual_figure_png_sha256"])==64
                                   for f in x["figures"])
                           for x in arr)
                  )
            # Every checked 390/768 page must have a genuine independent
            # mobile rendering of EVERY finance exhibit. Source SHA prevents
            # old PNGs and receipts being rebound to new HTML.
            if not valid:
                errors.append(f"VISUAL_CHANGED_V10_ORIGINAL_SOURCE_ALL_FINANCE_3_VIEWPORT_RECEIPT_INVALID {code}")
                continue
            fixed.append({"code":code,"source_html_sha256":sha,
                          "mobile_original_money_grammar":"PASS_LOCAL_REAL_CJK_3_VIEWPORTS_ALL_MATERIAL_FIGURES__CLOUDFLARE_NOT_CHECKED"})
            continue
        if code=="601628":
            # Production proof is NEVER repurposed as a PR candidate receipt.
            # A candidate can pass the local real-CJK gate only when its own
            # screenshot bytes and page SHA are independently source-bound.
            p=root/"research/issuers/601628/visual-qa/result.json"
            if not p.is_file():
                errors.append("VISUAL_601628_CANDIDATE_REQUIRES_CURRENT_REAL_CJK_RECEIPT")
                continue
            q=json.loads(p.read_text(encoding="utf8"))
            views=q.get("original_actual_3_viewport_checks",[])
            # Genuine 2026-11-09 insurer research upgrade has an additional
            # thirteenth-fact source table, not a new figure. A prior
            # 10-figure article legitimately has 10 figure tables; the
            # 11th decision table is legal ONLY with exact 13 original
            # source fact IDs and 4 independently derived CAS ratios.
            editorial=html.read_text(encoding="utf8")
            has_decision='id="quantified-decision"' in editorial
            expected_tables=11 if has_decision else 10
            if has_decision:
                decision_ok=(editorial.count('data-source-key=')==13
                             and editorial.count('data-decision-key=')==4
                             and 'data-accounting-not-causal="true"' in editorial
                             and 'data-pdf-sha256=' in editorial
                             and 'NOT_CHECKED' in editorial)
            else:
                decision_ok=True
            valid=(decision_ok and q.get("code")==code and q.get("page_1440_768_390")=="PASS"
                and q.get("source_nodes_sinks_ribbons_exact_svg_geometric_proportions")=="PASS"
                and q.get("mobile_fully_visible_financial_figures")=="PASS"
                and q.get("mobile_ledger_exact_value_and_geometry")=="PASS"
                and q.get("chart_count")==10 and q.get("source_table_count")==expected_tables
                and q.get("export_click_and_svg_download")=="PASS"
                and len(views)==3 and {v.get("width") for v in views}==WIDTHS
                and all(v.get("result")=="PASS" and v.get("body_no_overflow")=="PASS"
                        and v.get("source_sankey_actual_path_and_rect")=="PASS"
                        and v.get("svg_export")=="PASS" and v.get("figure_count")==10
                        and v.get("original_source_tables")==expected_tables and v.get("cjk_font_available") is True
                        for v in views)
                and next((v for v in views if v.get("width")==390),{}).get("figure_readability")
                    =="MOBILE_ALL_TEN_COMPLETE_NO_HORIZ_SCROLL")
            # The original QA script stores no HTML SHA. Prove it was
            # reconstructed from the CURRENT HTML through a dedicated
            # candidate-only receipt produced by the real browser workflow.
            proof=root/"research/issuers/601628/visual-qa/candidate-html-sha.json"
            if not proof.is_file():
                valid=False
            else:
                r=json.loads(proof.read_text(encoding="utf8"))
                valid=valid and r.get("candidate_html_sha256")==sha
                for w in WIDTHS:
                    fname=f"full_report_{w}.png"
                    img=root/"research/issuers/601628/visual-qa"/fname
                    record=r.get("screenshots",{}).get(fname,{})
                    valid=valid and img.is_file() and record.get("sha256")==hashlib.sha256(img.read_bytes()).hexdigest() and record.get("bytes")==img.stat().st_size
            if not valid:
                errors.append("VISUAL_601628_CURRENT_CANDIDATE_THREE_CJK_WIDTHS_OR_SHA_MISMATCH")
                continue
            fixed.append({"code":code,"source_html_sha256":sha,
                          "mobile_original_money_grammar":"PASS_LOCAL_REAL_CJK_3_VIEWPORTS_TEN_FIGURES__PRODUCTION_NOT_CHECKED"})
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
        # Semiconductor source-led release is a distinct accounting/visual
        # family: 4 product cost+GP true-weighted, signed CAS/17-row CFO and
        # balanced BS. Never apply the two-sector or optical receipt schema.
        if code=="688220":
            rootdir=root/"research/issuers/688220"
            receipt=rootdir/"visual-qa-native/result.json"
            if not receipt.is_file():
                errors.append("VISUAL_688220_CHANGED_FULL_HTML_REQUIRES_ACTUAL_NINE_NATIVE_CJK_FINANCE_RECEIPT")
                continue
            q=json.loads(receipt.read_text(encoding="utf8"))
            v=q.get("actual_3_viewport_checks",[])
            screenshots=q.get("real_CJK_screenshot_sha_bytes",{})
            manifest=json.loads((rootdir/"source-manifest.json").read_text(encoding="utf8"))
            valid=(q.get("issuer")==code and q.get("html_sha256")==sha
                and q.get("source_pdf_sha256")==manifest["pdf_sha256"]
                and len(v)==3 and {z.get("width") for z in v}==WIDTHS
                and all(z.get("body_no_overflow")=="PASS" and
                        z.get("source_conserved_source_sinks_and_Bezier_actual_width")=="PASS" and
                        z.get("original_legal_signed_CFO_and_PNL_in_same_scale")=="PASS" and
                        z.get("original_CJK_text_bbox")=="PASS" for z in v)
                and all(z.get("actual_nine_390_768_native_signed_money_figures_no_inner_scroll")=="PASS"
                        for z in v if z.get("width") in (390,768))
                and q.get("all_nine_390px_native_financial_svg_legible_and_source_reconciled")=="PASS"
                and q.get("source_nodes_sinks_ribbons_exact_svg_geometric_proportions")=="PASS"
                and len(screenshots)>=21)
            # Four curated genuine CJK screenshots are persisted in Git;
            # remaining full 9×3 matrices live in the GitHub Actions artifact.
            for name in ("flow_390.png","flow_1440.png","pnl_390.png","cfo_390.png"):
                p=rootdir/"visual-qa-native"/name
                entry=screenshots.get(name)
                valid=valid and bool(entry) and p.is_file() and (
                    entry.get("sha256")==hashlib.sha256(p.read_bytes()).hexdigest()
                    and entry.get("bytes")==p.stat().st_size)
            if not valid:
                errors.append("VISUAL_CHANGED_688220_SOURCE_AMOUNT_SIGNED_CJK_390_RECEIPT_INVALID")
                continue
            fixed.append({"code":code,"source_html_sha256":sha,
                          "mobile_original_money_grammar":"PASS_REAL_NINE_NATIVE_CJK_SOURCE_SANKKEY_SIGNED_CAS_BS"})
            continue
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
    if len(catalog)!=len(seen):
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
    print("EXACT_OLD_FINGERPRINT_OR_NEW_ACTUAL_CHROMIUM_SOURCE_ARTIFACT_PUBLISH_POLICY_PASS",len(json.loads((ROOT/"site/research_catalog.json").read_text())["issuers"]))
