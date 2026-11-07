#!/usr/bin/env python3
"""Fail-closed, ZERO-MEMORY PR #35 quality handoff.

This checks candidate HTML SHA ↔ deterministic source rebuild manifest ↔
Chromium screenshots and typed financial receipt. A passing source receipt is
not a claim of AEI-level visual quality, human review, unobserved companies,
or a deployed main branch. GitHub/current live status must be queried anew.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
CODES={"688111":(9,"TYPE_A_SOURCE_OWN_COST_GP"),
       "600519":(9,"TYPE_C_SANKEY_OMITTED"),
       "000333":(10,"TYPE_B_GROUP_ONLY_GROSS_ALLOCATION"),
       "600036":(8,"BANK_NET_INCOME_TO_OPERATING_PROFIT")}
PR=35
MANIFEST="research/quality/active-pr35.json"


def jread(root:Path,path:str)->dict:
    return json.loads((root/path).read_text(encoding="utf8"))


def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def validate_artifact_integrity(active:dict,build:dict,browser:dict,typed:dict,
                                pages:dict[str,bytes],catalog:dict)->list[str]:
    errors=[]
    if active.get("schema")!="financials.pr35.active_quality_handoff.v1":
        errors.append("CANDIDATE_HANDOFF_SCHEMA")
    if active.get("pr_number")!=35 or active.get("branch")!="quality/aei-sankey-source-contract-v1":
        errors.append("CANDIDATE_BRANCH_IDENTITY")
    if active.get("review_state")!="UNMERGED_CANDIDATE_NEEDS_INDEPENDENT_EDITORIAL_REVIEW":
        errors.append("PREMATURE_RESEARCH_OR_DEPLOYMENT_CERTIFICATION")
    if active.get("current_art_direction",{}).get("status")!="NOT_CHECKED_CURRENT_HUMAN_REVIEW_AND_UNSEEN_PERIOD_GENERALIZATION":
        errors.append("HUMAN_OR_GENERALIZATION_CERTIFICATION_NOT_PROVEN")
    codes=set(CODES)
    if set(active.get("four_issuers",{}))!=codes:
        errors.append("INCOMPLETE_CANDIDATE_ISSUER_HANDOFF")
    if active.get("source_of_truth",{}).get("original_issuer_count_source")!="site/research_catalog.json":
        errors.append("CATALOG_NOT_GROUNDED_IN_CANONICAL_FILE")
    codes_actual=[row.get("code") for row in catalog.get("issuers",[])]
    if len(set(codes_actual))!=len(codes_actual) or not set(CODES).issubset(codes_actual):
        errors.append("CANDIDATE_OR_CATALOG_ISSUER_IDENTITY_DRIFT")
    if len(catalog.get("issuers",[]))!=11:
        errors.append("ISSUER_COUNT_DIFFERS_FROM_VERIFIED_CANDIDATE_SCOPE")
    fixtures={x["issuer"]:x for x in typed.get("records",[])}
    if set(fixtures)!=codes or typed.get("conclusion")!="STATIC_SCOPE_PASS_BROWSER_GEOMETRY_AND_HUMAN_NOT_CHECKED":
        errors.append("STRICT_TYPED_FINANCE_RECEIPT_STALE_OR_FAILED")
    if typed.get("blocking_violations"):
        errors.append("STRICT_TYPED_FINANCE_BLOCKING_VIOLATIONS")
    if browser.get("all_36_issuer_exhibits_3_viewports")!="PASS":
        errors.append("REAL_CHROMIUM_CJK_RECEIPT_MISSING")
    cases=browser.get("cases",[])
    if len(cases)!=12:
        errors.append("NOT_ALL_12_ISSUER_VIEWPORT_CASES")
    observed={(x.get("code"),x.get("width")):x for x in cases}
    if set(observed)!={(code,width) for code in CODES for width in (390,768,1440)}:
        errors.append("REAL_CHROMIUM_VIEWPORT_OR_ISSUER_OMITTED")
    for code,(count,kind) in CODES.items():
        html=pages.get(code,b"")
        if not html:
            errors.append(f"MISSING_ACTUAL_PR_HTML_{code}")
            continue
        actual=sha(html)
        filename=code+".html"
        record=build.get("files",{}).get(filename,{})
        if record.get("sha256")!=actual or record.get("bytes")!=len(html) or record.get("figures")!=count:
            errors.append(f"SOURCE_REBUILD_MANIFEST_SHA_DRIFT_{code}")
        account=fixtures.get(code,{})
        if account.get("actual_html_sha256")!=actual or account.get("current_figure_semantic_status")!="PASS_STATIC_SCOPE_ONLY":
            errors.append(f"FINANCIAL_SEMANTICS_NOT_EXACT_PR_HTML_{code}")
        if account.get("expected_semantics",{}).get("kind")!=kind or account.get("published_figure_issues"):
            errors.append(f"WRONG_TYPED_SOURCE_GRAMMAR_{code}")
        source=html.decode("utf8")
        if f'data-flow-kind="{kind}"' not in source:
            errors.append(f"PUBLISHED_FLOW_KIND_MISSING_{code}")
        if source.count('<figure class="graphic"')!=count:
            errors.append(f"PUBLISHED_FINANCIAL_EXHIBITS_OMITTED_{code}")
        if '.export{display:none}' in source:
            errors.append(f"HIDDEN_MOBILE_SVG_EXPORT_{code}")
        if '.export{display:inline-flex' not in source or "figure.querySelectorAll('.graphic-svg svg')" not in source:
            errors.append(f"NO_SOURCE_BOUND_PHONE_EXPORT_{code}")
        for width in (390,768,1440):
            item=observed.get((code,width),{})
            if item.get("html_sha256")!=actual or item.get("actual_all_figures")!=count:
                errors.append(f"STALE_SOURCE_SHA_CJK_BROWSER_{code}_{width}")
            if not item.get("real_chromium") or len(item.get("figures",[]))!=count:
                errors.append(f"NOT_REAL_ALL_FIGURES_CJK_{code}_{width}")
            if item.get("full_page_screenshot_sha256") is None:
                errors.append(f"MISSING_ACTUAL_FULL_PAGE_SCREENSHOT_{code}_{width}")
        if code=="688111":
            if 'viewBox="0 0 1040' not in source or 'data-layout="desktop-editorial"' not in source:
                errors.append("WPS_NO_INDEPENDENT_THREE_STAGE_DESKTOP")
            if "集团营业毛利" not in source or "毛利率" not in source:
                errors.append("WPS_SOURCE_OWN_GP_STORY_ABSENT")
        if code=="600519":
            for needle in ('data-local-inset-source="other_rev"',
                           'data-inset-yuan-per-svg-unit',
                           '独立金额比例尺','局部放大','负毛利'):
                if needle not in source:
                    errors.append("MOUTAI_TINY_NEGATIVE_GP_EDITORIAL_MISSING_"+needle)
            if 'data-flow-omission="FINANCIAL_SANKEY_OMITTED_WITH_SOURCE_REASON"' not in source:
                errors.append("MOUTAI_SOURCE_REASONED_OMISSION_METADATA_MISSING")
            if 'viewBox="0 0 1040' not in source or 'data-layout="desktop-editorial"' not in source:
                errors.append("MOUTAI_DESKTOP_IS_ONLY_A_STRETCHED_330_PHONE_CHART")
    return errors


def validate_handoff_documents(active:dict,status:dict,
                               entry:str,state:str,agents:str,skill:str,
                               protocol:str,scorecard:str)->list[str]:
    errors=[]
    candidate=status.get("active_pr35_quality_candidate",{})
    if candidate.get("handoff_manifest")!=MANIFEST or candidate.get("pr_number")!=PR:
        errors.append("PROJECT_STATUS_DOES_NOT_SURFACE_CANDIDATE")
    if candidate.get("state")!="UNMERGED_CANDIDATE_WITH_SEPARATE_MAIN_PRODUCTION":
        errors.append("PROJECT_STATUS_PREMATURE_RELEASE")
    if candidate.get("main_at_review_start")!=active.get("source_main_sha_at_start"):
        errors.append("PROJECT_STATUS_MAIN_BASELINE_DRIFT")
    if "ACTIVE_PR35_HANDOFF.md" not in entry[:3500]:
        errors.append("START_HERE_HAS_NO_ACTIVE_PR_HANDBACK")
    if "ACTIVE_PR35_HANDOFF.md" not in state[:3500]:
        errors.append("PROJECT_STATE_HAS_NO_ACTIVE_PR_HANDBACK")
    if "ACTIVE_PR35_HANDOFF.md" not in agents[:3500]:
        errors.append("AGENTS_IGNORE_CANDIDATE_HANDOFF")
    if "ACTIVE_PR35_HANDOFF.md" not in protocol:
        errors.append("HANDOFF_PROTOCOL_MISSING_ACTIVE_CANDIDATE_LINK")
    if "ACTIVE_PR35_HANDOFF.md" not in skill[:6000]:
        errors.append("SKILL_MISSING_ACTUAL_PR35_EDITORIAL_HANDOFF")
    for phrase in ("五秒","归因","反证","原始元","局部放大","NOT_CHECKED","多期","同行"):
        if phrase not in scorecard:
            errors.append("RESEARCH_VISUAL_SCORECARD_INCOMPLETE_"+phrase)
    if status.get("production_branch")!="main":
        errors.append("IMPROPER_PRODUCTION_BRANCH_CHANGE")
    if status.get("limitations",{}).get("independent_second_human_analyst")!="NOT_CHECKED":
        errors.append("FAKE_SECOND_HUMAN_APPROVAL")
    return errors


def check_repo(root:Path=ROOT)->list[str]:
    active=jread(root,MANIFEST)
    build=jread(root,"research/rebuild-v10/build-manifest.json")
    browser=jread(root,"research/rebuild-v10/real-browser-qa/result.json")
    typed=jread(root,"research/rebuild-v10/strict-semantic-audit.json")
    catalog=jread(root,"site/research_catalog.json")
    pages={code:(root/"public/research/2026-h1-v10"/(code+".html")).read_bytes()
           for code in CODES}
    errors=validate_artifact_integrity(active,build,browser,typed,pages,catalog)
    texts=lambda path:(root/path).read_text(encoding="utf8")
    errors+=validate_handoff_documents(
        active,jread(root,"project-status.json"),
        texts("START_HERE.md"),texts("PROJECT_STATE.md"),
        texts("AGENTS.md"),texts("skills/ashare-financial-storytelling/SKILL.md"),
        texts("docs/HANDOFF_PROTOCOL.md"),
        texts("docs/AEI_RESEARCH_EDITORIAL_SCORECARD.md"))
    return errors


if __name__=="__main__":
    try:
        issues=check_repo()
    except (OSError,KeyError,ValueError) as e:
        print("CANDIDATE_HANDOFF_RUNTIME_FAILURE",repr(e),file=sys.stderr)
        sys.exit(2)
    if issues:
        for issue in issues:
            print("PR35_QUALITY_HANDOFF_FAIL",issue,file=sys.stderr)
        sys.exit(1)
    print("PR35_QUALITY_HANDOFF_PASS exact 4 HTML sha 3-source receipts 12 CJK cases 36 original images, never fake main/human/AEI")
