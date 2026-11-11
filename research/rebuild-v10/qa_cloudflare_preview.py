#!/usr/bin/env python3
"""Independent PR Cloudflare HTML-byte + real remote mobile browser release gate.

Premerge PASS requires:
  PR branch preview exact public HTML bytes == committed PR candidate for 4 reports.
  Current production exact bytes == current MAIN source for all 4 reports.
  Previews open/fully render every one of the 36 source finance exhibits from HTTPS
  under Chromium touchscreen Android-sized, WebKit touchscreen iPhone-sized,
  Chromium tablet and desktop without body/figure horizontal clipping.

This is a real browser/HTTP test, NOT real handset hardware or human art direction.
Do not infer that PR code has reached production until main deployment byte SHA matches.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright
from decimal import Decimal as D

ROOT=Path(__file__).resolve().parents[2]
BASE_PATH="research/2026-h1-v10"
OUT=ROOT/"research/rebuild-v10/cloudflare-release-qa"
OUT.mkdir(parents=True,exist_ok=True)
PREVIEW=os.environ.get("FINANCIALS_PR_PREVIEW","https://quality-aei-sankey-source-co.financials-in-visuals.pages.dev").rstrip("/")
PRODUCTION=os.environ.get("FINANCIALS_PRODUCTION","https://financials-in-visuals.pages.dev").rstrip("/")
CODES={"688111":(9,"TYPE_A_SOURCE_OWN_COST_GP"),
       "600519":(9,"TYPE_C_SANKEY_OMITTED"),
       "000333":(10,"TYPE_A_SOURCE_OWN_COST_GP"),
       "600036":(8,"BANK_NET_INCOME_TO_OPERATING_PROFIT")}
CONTEXTS=(
    ("chromium",390,844,True,3,"Android-size Chromium touchscreen"),
    ("webkit",375,812,True,3,"iPhone-size WebKit touchscreen simulation"),
    ("chromium",768,1024,False,1,"tablet-width Chromium"),
    ("chromium",1440,960,False,1,"desktop Chromium"),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_bytes(url: str, attempts: int=4) -> tuple[bytes,int]:
    error=None
    for i in range(attempts):
        try:
            request=Request(url,headers={
                "User-Agent":"Mozilla/5.0 (compatible; FinancialsReleaseAudit/1.0)",
                "Accept":"text/html,*/*",
                "Cache-Control":"no-cache",
                "Pragma":"no-cache",
            })
            with urlopen(request,timeout=35) as resp:
                data=resp.read()
                status=resp.status
            if status!=200 or not data.lstrip().lower().startswith(b"<!doctype html"):
                raise ValueError(f"HTTP_HTML_INVALID {url} status={status} bytes={len(data)}")
            return data,status
        except (HTTPError,URLError,TimeoutError,ValueError) as err:
            error=err
            if i!=attempts-1:
                time.sleep(7)
    raise RuntimeError(f"PUBLIC_HTTP_FAILED {url} {error!r}")


def require_preview_current(url: str, expected: bytes) -> tuple[bytes,int]:
    """Wait for known Cloudflare branch deployment convergence, never accept stale."""
    last=None
    for i in range(9):
        data, status=fetch_bytes(url,attempts=2)
        if data==expected:
            return data,status
        last=sha(data)
        print("PR_PREVIEW_NOT_YET_DEPLOYED",i+1,"public_sha",last,"expected_sha",sha(expected),flush=True)
        if i<8:
            time.sleep(12)
    raise AssertionError(f"PR_PREVIEW_FULL_HTML_SHA_MISMATCH {url} {last} != {sha(expected)}")


def main():
    result={
        "schema":"financials.premerge.real_cloudflare_and_mobile.v1",
        "pr_number":35,
        "preview_domain":PREVIEW,
        "production_domain":PRODUCTION,
        "actual_device_hardware":"NOT_TESTED_USE_MOBILE_TOUCHSCREEN_BROWSER_EMULATION",
        "source_pdf_line_column_independent_review":"NOT_CHECKED",
        "independent_visual_editorial_art_direction":"NOT_CHECKED",
        "preview_exact_full_html_bytes":"NOT_CHECKED",
        "main_production_exact_full_html_bytes":"NOT_CHECKED",
        "pr_candidate_already_on_production":"NO_CLAIM_BEFORE_MERGE",
        "preview_mobile_html_full_online_render":"NOT_CHECKED",
        "pages":[],
        "browser_cases":[],
        "blockers":[],
    }
    try:
        for code,(count,expected_kind) in CODES.items():
            path=f"public/{BASE_PATH}/{code}.html"
            candidate=(ROOT/path).read_bytes()
            original=subprocess.check_output(["git","show",f"refs/remotes/origin/main:{path}"],cwd=ROOT)
            preview_url=f"{PREVIEW}/{BASE_PATH}/{code}.html"
            production_url=f"{PRODUCTION}/{BASE_PATH}/{code}.html"
            preview,status_preview=require_preview_current(preview_url,candidate)
            production,status_prod=fetch_bytes(production_url)
            matches_main=production==original
            matches_pr=production==candidate
            row={
                "issuer":code,
                "preview_url":preview_url,
                "production_url":production_url,
                "candidate_byte_count":len(candidate),
                "candidate_sha256":sha(candidate),
                "preview_http_status":status_preview,
                "preview_sha256":sha(preview),
                "preview_exact_candidate_bytes":preview==candidate,
                "production_http_status":status_prod,
                "production_sha256":sha(production),
                "main_sha256":sha(original),
                "production_exact_current_main_bytes":matches_main,
                "production_exact_pr_candidate_bytes":matches_pr,
                "publication_state":("PENDING_MAIN_MERGE_AND_DEPLOYMENT" if matches_main
                                     else "ALREADY_LIVE_CANDIDATE_OUTSIDE_MAIN" if matches_pr
                                     else "LIVE_PRODUCTION_NOT_EQUAL_MAIN_OR_CANDIDATE"),
            }
            print("PR_PREVIEW_BYTES",code,row["candidate_sha256"],"PASS",flush=True)
            print("CURRENT_PRODUCTION_BYTES",code,
                  row["production_sha256"],"vs main",row["main_sha256"],
                  "MATCH" if matches_main else "DIFFER",flush=True)
            result["pages"].append(row)
            if not matches_main:
                result["blockers"].append("PRODUCTION_NOT_CURRENT_MAIN "+code)
        result["preview_exact_full_html_bytes"]="PASS" if all(r["preview_exact_candidate_bytes"] for r in result["pages"]) else "FAIL"
        result["main_production_exact_full_html_bytes"]="PASS" if all(r["production_exact_current_main_bytes"] for r in result["pages"]) else "FAIL"
        if result["blockers"]:
            raise AssertionError("PRODUCTION_CURRENT_MAIN_HAS_SHA_DRIFT "+str(result["blockers"]))

        # The browser reads the actual HTTPS preview, not file:// output.
        with sync_playwright() as p:
            browsers={"chromium":p.chromium.launch(headless=True),
                      "webkit":p.webkit.launch(headless=True)}
            try:
                for engine,width,height,touch,dpr,label in CONTEXTS:
                    browser=browsers[engine]
                    context=browser.new_context(
                        viewport={"width":width,"height":height},
                        device_scale_factor=dpr,
                        is_mobile=touch,
                        has_touch=touch,
                        locale="zh-CN",
                    )
                    for code,(expected_count,expected_kind) in CODES.items():
                        page=context.new_page()
                        page_errors=[]
                        page.on("pageerror",lambda err:page_errors.append(str(err)))
                        link=f"{PREVIEW}/{BASE_PATH}/{code}.html"
                        response=page.goto(link,wait_until="networkidle",timeout=60000)
                        assert response and response.status==200,(engine,width,code,"HTTP_NOT_200")
                        page.evaluate("document.fonts.ready")
                        page.locator("figure.graphic").first.wait_for(timeout=15000)
                        figs=page.locator("figure.graphic")
                        assert figs.count()==expected_count,(engine,width,code,"FIGURE_COUNT",figs.count(),expected_count)
                        assert page.locator("#fig-02").get_attribute("data-flow-kind")==expected_kind
                        page_metrics=page.evaluate("""() => ({
                          width:document.documentElement.clientWidth,
                          bodyScroll:document.documentElement.scrollWidth,
                          touch:navigator.maxTouchPoints,
                          hasOverflow:[...document.querySelectorAll('.graphic-svg')].filter(e => {
                            const s=getComputedStyle(e);
                            return s.display!=='none' && e.scrollWidth>e.clientWidth+2;
                          }).length
                        })""")
                        assert page_metrics["bodyScroll"]<=width+2,(engine,width,code,"DOCUMENT_OVERFLOW",page_metrics)
                        assert page_metrics["hasOverflow"]==0,(engine,width,code,"INNER_FINANCE_OVERFLOW",page_metrics)
                        if touch and engine=="chromium":
                            # Chromium exposes navigator.maxTouchPoints in this configured
                            # touchscreen context; Linux WebKit may return zero even with
                            # has_touch=True and is_mobile=True. Do not equate platform
                            # API support with actual figure viewport correctness.
                            assert page_metrics["touch"]>0,(engine,width,code,"TOUCH_MODE_INACTIVE",page_metrics)
                        if touch and engine=="webkit":
                            assert context is not None and page_metrics["width"]==width,(engine,width,code,"WEBKIT_MOBILE_VIEWPORT_INVALID",page_metrics)
                        detail=[]
                        for idx in range(expected_count):
                            fig=figs.nth(idx)
                            fid=fig.get_attribute("id")
                            desktop=fig.locator(".desktop-finance svg")
                            mobile=fig.locator(".native-finance svg")
                            assert desktop.count()==mobile.count()==1,(engine,width,code,fid,"DUAL_FIGURES_MISSING")
                            active=mobile if width<=850 else desktop
                            inactive=desktop if width<=850 else mobile
                            geo=active.evaluate("""el => {
                              const wrap=el.parentElement;
                              const r=el.getBoundingClientRect();
                              const texts=[...el.querySelectorAll('text')].map(t=>{
                                const box=t.getBoundingClientRect();
                                return {label:t.textContent,x:box.left,right:box.right,
                                        height:box.height,width:box.width};
                              });
                              const paths=[...el.querySelectorAll('path[data-ribbon-yuan]')].map(t=>({
                                amount:t.getAttribute('data-ribbon-yuan'),
                                scale:t.getAttribute('data-scale-yuan-per-svg-unit'),
                                d:t.getAttribute('d')
                              }));
                              return {display:getComputedStyle(el).display,wrapDisplay:getComputedStyle(wrap).display,
                                      x:r.left,right:r.right,width:r.width,height:r.height,
                                      innerScroll:wrap.scrollWidth,innerClient:wrap.clientWidth,
                                      texts,paths};
                            }""")
                            assert geo["display"]!="none" and geo["wrapDisplay"]!="none",(engine,width,code,fid,"CHART_HIDDEN")
                            assert inactive.evaluate("e=>getComputedStyle(e.parentElement).display")=="none",(engine,width,code,fid,"INACTIVE_CHART_VISIBLE")
                            assert geo["width"]>195 and geo["height"]>40,(engine,width,code,fid,"CHART_NOT_READABLY_SIZED",geo)
                            assert geo["x"]>=-2 and geo["right"]<=width+3,(engine,width,code,fid,"FIGURE_SCREEN_CLIPPED",geo)
                            assert geo["innerScroll"]<=geo["innerClient"]+2,(engine,width,code,fid,"CHART_INNER_SCROLL")
                            for t in geo["texts"]:
                                if t["label"].strip():
                                    assert t["x"]>=-5 and t["right"]<=width+8,(engine,width,code,fid,"TEXT_OFFSCREEN",t)
                                    assert t["height"]>0,(engine,width,code,fid,"TEXT_INVISIBLE",t)
                            for ribbon in geo["paths"]:
                                vals=[D(z) for z in re.findall(r"-?\d+(?:\.\d+)?",ribbon["d"])]
                                assert len(vals)>=16,(engine,width,code,fid,"BAD_RIBBON_GEOMETRY")
                                thick=abs(vals[-1]-vals[1])
                                expected=D(ribbon["amount"])/D(ribbon["scale"])
                                assert abs(thick-expected)<=D(".001"),(engine,width,code,fid,"WRONG_ORIGINAL_YUAN_RIBBON",thick,expected)
                            if width<=850 and fid=="fig-02" and code in ("688111","000333","600036"):
                                # Real Cloudflare Android-size Chromium AND
                                # iPhone-size WebKit CJK measured collision proof.
                                spacing=active.evaluate("""svg=>{
                                  const n=r=>[...svg.querySelectorAll('[data-editorial-role="'+r+'"]')];
                                  const bot=r=>Math.max(...n(r).map(e=>e.getBoundingClientRect().bottom));
                                  const top=r=>Math.min(...n(r).map(e=>e.getBoundingClientRect().top));
                                  return {legend:bot('source-summary'),header:top('source-stage-header'),
                                    outcome:bot('outcome-value'),warning:top('accounting-limitation'),
                                    warningBottom:bot('accounting-limitation'),
                                    note:top('source-caveat'),noteBottom:bot('source-caveat'),
                                    svgBottom:svg.getBoundingClientRect().bottom};
                                }""")
                                assert spacing["legend"]+3<spacing["header"],(engine,width,code,"MOBILE_SOURCE_LABEL_COLLISION",spacing)
                                assert spacing["outcome"]+3<spacing["warning"],(engine,width,code,"MOBILE_AMOUNT_AND_ACCOUNTING_WARNING_COLLISION",spacing)
                                assert spacing["warningBottom"]+3<spacing["note"],(engine,width,code,"MOBILE_FINANCIAL_WARNING_AND_PDF_NOTE_COLLISION",spacing)
                                assert spacing["noteBottom"]<spacing["svgBottom"],(engine,width,code,"MOBILE_PDF_NOTE_CLIPPED",spacing)
                            detail.append({
                                "figure_id":fid,
                                "source_svg":width<=850,
                                "text_labels_checked":len(geo["texts"]),
                                "original_yuan_ribbons_geometry_checked":len(geo["paths"]),
                                "visible_without_internal_scroll":"PASS",
                            })
                            # Every original phone figure receives its own PNG.
                            if touch:
                                dest=OUT/f"preview-{code}-{engine}-{width}-{fid}.png"
                                active.screenshot(path=str(dest),timeout=30000)
                                detail[-1]["actual_preview_figure_png_sha256"]=sha(dest.read_bytes())
                        # WebKit has a hard 32767px bitmap edge limit; these
                        # long financial articles exceed it after device scale.
                        # Every exhibit is already captured independently above.
                        # Preserve an actual viewport screenshot on WebKit;
                        # Chromium still captures the entire article.
                        whole=engine!="webkit"
                        shot=OUT/f"preview-{code}-{engine}-{width}-{'full' if whole else 'viewport'}.png"
                        page.screenshot(path=str(shot),full_page=whole,timeout=45000)
                        assert not page_errors,(engine,width,code,"JS_PAGE_ERRORS",page_errors)
                        receipt={
                            "issuer":code,
                            "engine":engine,
                            "touchscreen_mobile_emulation":touch,
                            "viewport_width":width,
                            "viewport_height":height,
                            "source_url":link,
                            "exact_http_sha256":next(x["candidate_sha256"] for x in result["pages"] if x["issuer"]==code),
                            "actual_browser_response_status":response.status,
                            "browser_pageerror_count":len(page_errors),
                            "figure_count":expected_count,
                            "all_figures":detail,
                            "actual_article_or_viewport_screenshot_sha256":sha(shot.read_bytes()),
                            "screenshot_scope":"FULL_PAGE" if whole else "TOP_VIEWPORT_WEBKIT_BITMAP_LIMIT",
                            "scroll_and_original_yuan_geometry":"PASS",
                        }
                        result["browser_cases"].append(receipt)
                        print("CLOUDFLARE_LIVE_PREVIEW_BROWSER_PASS",engine,width,code,
                              "actual_figures",expected_count,"touch",touch,flush=True)
                        page.close()
                    context.close()
            finally:
                for b in browsers.values():
                    b.close()
        assert len(result["browser_cases"])==16
        result["preview_mobile_html_full_online_render"]="PASS"
        result["overall_premerge"]="PASS_PREVIEW_ONLY_PRODUCTION_CANDIDATE_NOT_YET_DEPLOYED"
        return 0
    except Exception as err:
        result["blockers"].append(f"{type(err).__name__}: {str(err)}")
        result["overall_premerge"]="FAIL_STOP_THE_LINE"
        print("CLOUDFLARE_PREMERGE_BLOCKED",repr(err),file=sys.stderr,flush=True)
        return 1
    finally:
        (OUT/"result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")


if __name__=="__main__":
    raise SystemExit(main())
