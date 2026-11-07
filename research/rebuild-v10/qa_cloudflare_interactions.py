#!/usr/bin/env python3
"""Independent real Cloudflare PR reader interaction and export QA.

Strictly HTTP GET preview report bytes and all 11 route HTML bytes, then
use real Chromium 390/1440 and WebKit 375 to verify all 36 figure SVG
downloads match the VISIBLE rendition byte-for-byte. Exercise keyboard
source-table disclosure, PDF page anchors and navigation. No remote writes.
Not human visual review, native device or full PDF-cell certification.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import sys
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"research/rebuild-v10/cloudflare-interaction-qa"
OUT.mkdir(parents=True,exist_ok=True)
DOMAIN=os.environ.get("FINANCIALS_PR_PREVIEW","https://quality-aei-sankey-source-co.financials-in-visuals.pages.dev").rstrip("/")
CODES={"688111":9,"600519":9,"000333":10,"600036":8}
ENGINES=(("chromium",390,844,True),("webkit",375,812,True),("chromium",1440,960,False))


def sha(data: bytes) -> str:
    return sha256(data).hexdigest()


def fetch(url: str) -> bytes:
    request=Request(url,headers={
        "User-Agent":"Mozilla/5.0 (compatible; OriginalFinancePreviewReleaseQA/1.0)",
        "Cache-Control":"no-cache",
        "Accept":"text/html,*/*",
    })
    with urlopen(request,timeout=35) as response:
        assert response.status==200,(url,response.status)
        data=response.read()
    assert data.lstrip().lower().startswith(b"<!doctype html"),(url,"NOT_REAL_HTML",len(data))
    return data


def main() -> int:
    result={
        "schema":"financials.v10.pr35.actual_online_reader_interaction.v1",
        "source":"Cloudflare PR branch HTTPS, not file://",
        "candidate_commit":os.environ.get("GITHUB_SHA","NOT_BOUND_TO_GITHUB_SHA_USE_ACTUAL_CONTENT_SHA"),
        "actual_hardware":"NOT_CHECKED",
        "independent_financial_editorial_review":"NOT_CHECKED",
        "company_routes":[],
        "browser_cases":[],
        "blocking_issues":[],
    }
    try:
        catalog=json.loads((ROOT/"site/research_catalog.json").read_text(encoding="utf8"))
        issuers=catalog["issuers"]
        assert catalog["published_issuer_count"]==len(issuers)==11,(len(issuers),catalog["published_issuer_count"])
        index=fetch(DOMAIN+"/")
        expected_index=(ROOT/"public/index.html").read_bytes()
        assert index==expected_index,("PREVIEW_HOME_NOT_CURRENT_REPO",sha(index),sha(expected_index))
        assert b'id="companies"' in index,("MAIN_DIRECTORY_ANCHOR_MISSING")
        for issuer in issuers:
            code=issuer["code"]
            href=issuer["href"]
            assert href.startswith("/") and href.endswith(".html"),(code,href)
            actual=fetch(DOMAIN+href)
            source=(ROOT/"public"/href.lstrip("/")).read_bytes()
            assert actual==source,("PREVIEW_ISSUER_HTML_NOT_REPOSITORY",code,sha(actual),sha(source))
            assert href.encode() in index,("UNIFIED_HOME_ISSUER_LINK_MISSING",code,href)
            assert code.encode() in actual,("ISSUER_HTML_CODE_MISSING",code)
            result["company_routes"].append({"code":code,"route":href,
                "actual_online_full_html_sha256":sha(actual),
                "full_online_html_byte_equal":"PASS",
                "main_directory_link":"PASS"})
            print("CLOUDFLARE_11_ISSUER_ROUTE_EXACT_SHA_PASS",code,href,flush=True)
        assert {x["code"] for x in result["company_routes"]}=={x["code"] for x in issuers}
        result["unified_home_sha256"]=sha(index)
        result["unified_11_issuer_organic_routes"]="PASS"

        with sync_playwright() as p:
            chrome=p.chromium.launch(headless=True)
            webkit=p.webkit.launch(headless=True)
            try:
                for engine,width,height,mobile in ENGINES:
                    context=(chrome if engine=="chromium" else webkit).new_context(
                        viewport={"width":width,"height":height},
                        device_scale_factor=2 if mobile else 1,
                        is_mobile=mobile,has_touch=mobile,locale="zh-CN",
                        accept_downloads=True,
                    )
                    for code,count in CODES.items():
                        page=context.new_page()
                        faults=[]
                        page.on("pageerror",lambda exc:faults.append(str(exc)))
                        url=f"{DOMAIN}/research/2026-h1-v10/{code}.html"
                        response=page.goto(url,wait_until="networkidle",timeout=60000)
                        assert response and response.status==200,(engine,width,code,"REAL_HTML_LOAD_FAILURE")
                        page.evaluate("document.fonts.ready")
                        assert page.title().strip(),(code,"MISSING_DOCUMENT_TITLE")
                        assert page.locator("html").get_attribute("lang")=="zh-CN",(code,"DOCUMENT_LANG")
                        assert page.locator('nav[aria-label="研究章节导航"] a').count()==7,(code,"LOST_EDITORIAL_NAVIGATION")
                        assert page.locator('a[href="/#companies"]').count()>=2,(code,"NO_HOME_RETURN_ROUTE")
                        assert page.locator("header .mast-links").inner_text().find("全部公司")>=0,(code,"STALE_SEVEN_COMPANY_NAV")
                        figs=page.locator("figure.graphic")
                        assert figs.count()==count,(code,"FIGURE_COUNT",figs.count(),count)
                        tested=[]
                        for idx in range(count):
                            fig=figs.nth(idx)
                            fid=fig.get_attribute("id")
                            assert fid==f"fig-{idx+1:02d}",(code,width,fid,"FIGURE_ID_UNEXPECTED")
                            desktop=fig.locator(".desktop-finance svg")
                            native=fig.locator(".native-finance svg")
                            assert desktop.count()==native.count()==1,(code,width,fid,"ORIGINAL_DUAL_RENDER_MISSING")
                            active=native if width<=850 else desktop
                            expected=active.evaluate("e=>new XMLSerializer().serializeToString(e)")
                            assert expected.startswith("<svg"),(code,width,fid,"NOT_SOURCE_SVG")
                            assert active.get_attribute("role")=="img",(code,width,fid,"MISSING_SVG_IMAGE_ROLE")
                            assert active.get_attribute("aria-label") or active.locator("title").count()==1,(code,width,fid,"SOURCE_SVG_UNLABELED")
                            assert active.is_visible(),(code,width,fid,"ACTIVE_SVG_HIDDEN")
                            assert not (desktop if width<=850 else native).is_visible(),(code,width,fid,"HIDDEN_EDITON_VISIBLE")
                            button=fig.locator("button.export")
                            assert button.count()==1,(code,width,fid,"EXPORT_BUTTON_MISSING")
                            assert button.is_enabled(),(code,width,fid,"EXPORT_DISABLED")
                            with page.expect_download(timeout=15000) as info:
                                button.click(timeout=18000)
                            download=info.value
                            assert download.suggested_filename==fid+".svg",(code,width,fid,"EXPORT_FILE_NAME",download.suggested_filename)
                            exported=Path(download.path()).read_bytes()
                            assert exported.decode("utf8")==expected,(code,width,fid,
                                "DOWNLOADED_SVG_NOT_SAME_AS_VISIBLE_ORIGINAL_MONEY_ART",
                                sha(exported),sha(expected.encode()))
                            # Source evidence must open by keyboard and link to
                            # specific original PDF physical pages.
                            summary=fig.locator("details.details summary")
                            assert summary.count()==1,(code,width,fid,"SOURCE_TABLE_DETAILS_MISSING")
                            assert fig.locator("details.details").get_attribute("open") is None,(code,width,fid,"SOURCE_PANEL_SHOULD_START_COLLAPSED")
                            if idx==0:
                                summary.focus()
                                page.keyboard.press("Enter")
                                assert fig.locator("details.details").evaluate("e=>e.open"),(code,width,fid,"KEYBOARD_ENTER_NO_DISCLOSURE")
                            else:
                                summary.click(timeout=15000)
                                assert fig.locator("details.details").evaluate("e=>e.open"),(code,width,fid,"SOURCE_PANEL_CANNOT_OPEN")
                            evidence=fig.locator("details.details table tbody tr")
                            assert evidence.count()>=2,(code,width,fid,"SOURCE_TABLE_NO_DATA",evidence.count())
                            links=fig.locator('details.details a[href*=".PDF"],details.details a[href*=".pdf"]')
                            assert links.count()>=2,(code,width,fid,"SOURCE_PDF_LINKS_MISSING")
                            for href in links.evaluate_all("nodes=>nodes.map(a=>a.href)"):
                                assert href.startswith("https://"),(code,width,fid,"PDF_URL_NOT_HTTPS",href)
                                assert "#page=" in href,(code,width,fid,"PDF_PHYSICAL_PAGE_FRAGMENT_MISSING",href)
                            summary.click()
                            assert not fig.locator("details.details").evaluate("e=>e.open"),(code,width,fid,"SOURCE_PANEL_CANNOT_CLOSE")
                            tested.append({
                                "figure":fid,
                                "active_source_original_edition":"native_mobile" if width<=850 else "desktop",
                                "downloaded_exact_currently_visible_svg_sha256":sha(exported),
                                "actual_original_svg_download_matches_visible_renderer":"PASS",
                                "source_disclosure_mouse_and_keyboard":"PASS",
                                "source_pdf_page_links":"PASS",
                            })
                        # Test one actual in-page navigation jump after all
                        # downloads, plus the real unified directory link.
                        overview=page.locator('nav[aria-label="研究章节导航"] a[href="#overview"]')
                        overview.click()
                        assert page.evaluate("location.hash")=="#overview",(code,width,"ANCHOR_NAV_FAILED")
                        await_home=page.locator('a[href="/#companies"]').first
                        assert await_home.get_attribute("href")=="/#companies"
                        assert not faults,(code,width,"PAGE_JAVASCRIPT_ERRORS",faults)
                        result["browser_cases"].append({
                            "issuer":code,"engine":engine,"viewport_width":width,
                            "real_https_source_url":url,
                            "source_html_sha256":next(r["actual_online_full_html_sha256"] for r in result["company_routes"] if r["code"]==code),
                            "original_finance_exhibits":count,
                            "tested_original_source_svg_downloads":len(tested),
                            "interactive_figure_receipts":tested,
                            "keyboard_enter_source_table":"PASS",
                            "original_source_pdf_physical_page_anchor":"PASS",
                            "visible_SVG_matches_exported_exact_XML":"PASS",
                            "page_native_issuer_nav":"PASS",
                            "page_js_exceptions":faults,
                        })
                        print("ONLINE_READER_EXPORT_SOURCE_AND_ACCESSIBILITY_PASS",
                            engine,width,code,count,flush=True)
                        page.close()
                    context.close()
            finally:
                chrome.close()
                webkit.close()
        assert len(result["browser_cases"])==12,len(result["browser_cases"])
        assert sum(z["tested_original_source_svg_downloads"] for z in result["browser_cases"])==108
        result["all_108_exact_edition_svg_exports"]="PASS"
        result["real_online_reader_interaction"]="PASS"
        result["overall"]="PASS_PREVIEW_ONLY_INDEPENDENT_HUMAN_AND_PHYSICAL_DEVICES_NOT_CHECKED"
        return 0
    except Exception as exc:
        result["blocking_issues"].append(f"{type(exc).__name__}: {exc}")
        result["overall"]="FAIL_NO_PREMERGE_SIGNOFF"
        print("ONLINE_READER_INTERACTION_BLOCKED",repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        (OUT/"result.json").write_text(
            json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")


if __name__=="__main__":
    raise SystemExit(main())
