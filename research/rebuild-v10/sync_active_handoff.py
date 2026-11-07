#!/usr/bin/env python3
"""Atomically rebind PR35 handoff to exact just-rebuilt original PDF HTML.

Must run after original PDF source rebuild, after actual CJK Chromium screenshots
and after copying four regenerated pages to public, before publication. Do
NOT move any human review or remote deployment status to PASS. Every changed
HTML revokes previously green browser/cloud receipts. Reruns idempotently.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CODES=("688111","600519","000333","600036")
HERE=ROOT/"research/rebuild-v10"
HANDOFF=ROOT/"research/quality/active-pr35.json"
STATUS=ROOT/"project-status.json"


def read(path:Path)->dict:
    return json.loads(path.read_text(encoding="utf8"))


def write(path:Path,value:dict)->None:
    content=json.dumps(value,ensure_ascii=False,indent=2)+"\n"
    if not path.exists() or path.read_text(encoding="utf8")!=content:
        path.write_text(content,encoding="utf8")


def sync():
    manifest=read(HERE/"build-manifest.json")
    browser=read(HERE/"real-browser-qa/result.json")
    assert browser["all_36_issuer_exhibits_3_viewports"]=="PASS"
    proof={}
    for code in CODES:
        page=ROOT/"public/research/2026-h1-v10"/f"{code}.html"
        data=page.read_bytes()
        actual=sha256(data).hexdigest()
        built=manifest["files"][f"{code}.html"]
        assert built["sha256"]==actual and built["bytes"]==len(data)
        matches=[x for x in browser["cases"] if x["code"]==code]
        assert len(matches)==3 and {x["width"] for x in matches}=={390,768,1440}
        assert all(x["html_sha256"]==actual and len(x["figures"])==built["figures"]
                   for x in matches)
        proof[code]=actual
    active=read(HANDOFF)
    latest=active["latest_source_sha_bound_candidate"]
    latest["four_actual_public_full_html_sha256"]=proof
    latest["gate"]="PASS_LOCAL_ORIGINAL_PDF_AND_EXACT_SHA_CJK_BROWSER__HUMAN_NOT_CHECKED"
    latest["original_pdf_full_rebuild_run"]="SEE_THIS_CURRENT_HEAD_GITHUB_ACTIONS_NO_STORED_LIVE_ID"
    latest["typed_and_editorial_handoff_pr_check_run"]="REVALIDATE_LATEST_GITHUB_HEAD"
    latest["actual_cloudflare_for_new_visual_candidate"]="PENDING_NEW_SHA_REAL_HTTPS_BROWSER"
    latest["actual_cloudflare_preview_action"]="NOT_CHECKED_THIS_HTML_SHA"
    latest["actual_cloudflare_preview_artifact"]="NOT_CHECKED_THIS_HTML_SHA"
    latest["desktop_phone_original_money_editorial_spotcheck"]="NOT_CHECKED_CURRENT_SVG_WITH_HUMAN_EDITOR"
    latest["original_browser_figures"]=36
    latest["current_main_live_new_figures"]="NOT_DEPLOYED_PR_UNMERGED"
    active["four_issuers"]["688111"]["figure_02_design"]="UNIFIED_1100_DESKTOP_AND_330_PHONE_CONNECTED_SOURCE_TO_ONE_TOTAL_TO_OWN_COST_GP"
    active["four_issuers"]["000333"]["figure_02_design"]="UNIFIED_1100_DESKTOP_AND_330_PHONE_CONNECTED_GROUP_COST_GP_NOT_OWN_MARGIN"
    active["four_issuers"]["600036"]["figure_02_design"]="UNIFIED_1100_DESKTOP_AND_330_PHONE_CONNECTED_BANK_NET_INCOME_TO_OPERATING_PROFIT"
    active["four_issuers"]["600519"]["figure_02_design"]="TYPE_C_SIGNED_1040_DESKTOP_AND_330_PHONE_NEGATIVE_WITH_INDEPENDENT_SCALE_INSET"
    active["visual_unification_status"]={
        "unified_positive_income_flow":["688111","000333","600036"],
        "lawful_signed_exception":["600519"],
        "legacy_not_unified":["300394","300308","300502","688220","600900","600276","601628"],
        "all_11_editorially_unified":"NOT_ESTABLISHED",
        "human_editorial":"NOT_CHECKED",
        "unseen_company_reporting_period_reliability":"NOT_ESTABLISHED"
    }
    write(HANDOFF,active)
    state=read(STATUS)
    candidate=state["active_pr35_quality_candidate"]
    candidate["current_new_visual_candidate_html_sha256"]=proof
    candidate["new_upgraded_figures_status"]="PASS_LOCAL_ORIGINAL_SOURCE_AND_CJK_ON_EXACT_SHA__REAL_PREVIEW_AND_HUMAN_ART_REVIEW_PENDING"
    candidate["current_local_figure_proof_action"]="REQUERY_EXACT_CURRENT_BRANCH_GITHUB_RUN"
    candidate["current_cloudflare_live_candidate_proof_action"]="NOT_VALID_UNTIL_REAL_HTTPS_SHA_MATCHES"
    candidate["candidate_source_bound_preview_validation_scope"]="NOT_CHECKED_NEW_SHA"
    candidate["latest_candidate_visual_upgrade"]=[
        "SHARED_CONNECTED_1100_330_SOURCE_TO_ONE_TOTAL_TO_EXACT_COST_OR_GP",
        "MOUTAI_INDEPENDENT_TRUE_SIGNED_SCALES"]
    candidate["legacy_unified_design_not_completed"]=active["visual_unification_status"]["legacy_not_unified"]
    write(STATUS,state)
    print("ACTIVE_PR35_SOURCE_BOUND_HANDOFF_UPDATED",json.dumps(proof,ensure_ascii=False,sort_keys=True))


if __name__=="__main__":
    sync()
