#!/usr/bin/env python3
"""Actual current production Cloudflare optical finance release, source-byte bound.

This is NOT local set_content QA, nor an independent human editorial review.
A failing exact article SHA, 390 finance geometry, source route or CJK screenshot
means public production remains FAIL. Run only after changed main is deployed.
"""
from __future__ import annotations
import hashlib,json,os,time,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
ORIGIN="https://financials-in-visuals.pages.dev"
OUT=ROOT/"research/visual-audit/live-optical-native"
OUT.mkdir(parents=True,exist_ok=True)
CODES=("300394","300502","300308")
WIDTHS=(1440,768,390)
SHA=lambda b:hashlib.sha256(b).hexdigest()

def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Financials-in-Visuals-release-proof/1.0"}),timeout=25) as response:
        return response.read()

def expected(code):
    return (ROOT/f"public/{code}.html").read_bytes()

def wait_for_real_deploy():
    for iteration in range(12):
        try:
            home=fetch(ORIGIN+"/")
            if SHA(home)!=SHA((ROOT/"public/index.html").read_bytes()):
                raise AssertionError("PUBLIC_INDEX_MAIN_SOURCE_SHA_DIFFERENCE")
            actual={code:SHA(fetch(ORIGIN+f"/{code}")) for code in CODES}
            expected_sha={code:SHA(expected(code)) for code in CODES}
            if actual==expected_sha:
                return SHA(home),actual
            print("REAL_PUBLIC_ARTICLE_SHA_NOT_YET_SOURCE_MAIN",iteration,actual,expected_sha,flush=True)
        except Exception as error:
            print("REAL_CLOUDFLARE_HTTP_NOT_PROVEN",iteration,str(error),flush=True)
        time.sleep(8)
    raise AssertionError("REAL_CLOUDFLARE_PUBLIC_ARTICLE_SHA_NOT_MATCHED_CURRENT_MAIN")

def run():
    home_sha,article_shas=wait_for_real_deploy()
    catalog=json.loads((ROOT/"site/research_catalog.json").read_text())["issuers"]
    assert len(catalog)>=11 and {code for code in CODES}<={x["code"] for x in catalog}
    results=[];screens=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(args=["--no-sandbox"])
        for width in WIDTHS:
            page=browser.new_page(viewport={"width":width,"height":900},device_scale_factor=1)
            page.goto(ORIGIN+"/",wait_until="networkidle")
            assert page.locator("a.company").count()==len(catalog),("REAL_UNIFIED_INDEX_COUNT",width)
            screenshot=OUT/f"live_directory_{width}.png"
            page.screenshot(path=str(screenshot),full_page=True)
            screens.append({"name":screenshot.name,"sha256":SHA(screenshot.read_bytes()),"bytes":screenshot.stat().st_size})
            page.close()
        for company in catalog:
            path=company["href"]
            content=fetch(ORIGIN+path)
            assert b"<html" in content.lower() or b"<!doctype" in content.lower(),("MISSING_INDEPENDENT_COMPANY_ROUTE",company["code"])
        for code in CODES:
            # Independent signed ledger identity is embedded in full HTML.
            ledgers={
                "300394":ROOT/"skills/ashare-financial-storytelling/v7/engine/sample-ledger.json",
                "300502":ROOT/"skills/ashare-financial-storytelling/v7/examples/xinyisheng-2026H1-ledger.json",
                "300308":ROOT/"skills/ashare-financial-storytelling/v7/examples/zhongji-2026H1-ledger.json",
            }
            ledgerpath=ledgers[code]
            ledger=json.loads(ledgerpath.read_text())
            pdf_sha=ledger["document"]["source_sha256"]
            assert len(pdf_sha)==64
            assert pdf_sha.encode() in expected(code),(code,"PUBLISHED_PDF_ORIGINAL_SHA_MISSING")
            for width in WIDTHS:
                page=browser.new_page(viewport={"width":width,"height":900},device_scale_factor=1,accept_downloads=True)
                page.goto(ORIGIN+"/",wait_until="networkidle")
                page.locator(f'a.company[href="/{code}.html"]').click()
                page.wait_for_load_state("networkidle")
                article_url=page.url
                assert article_url in (ORIGIN+f"/{code}",ORIGIN+f"/{code}.html"),(code,width,"ARTICLE_REDIRECTED_TO_DIRECTORY",article_url)
                assert page.locator("figure.exhibit.has-native-finance").count()>=9
                assert pdf_sha in page.content()
                if code=="300308":
                    assert pdf_sha=="e0ecd7c365c65e90b1fa4b4616ba3f4649449d64451e0ba0b1b78ba9ce3170bf"
                    proof=json.loads((ROOT/"research/issuers/300308/source-verification.json").read_text(encoding="utf8"))
                    assert proof["source_page_amount_checks"]==63 and proof["indirect_CFO_all_original_signed_adjustments"]==15
                    assert "422,649,612.97" in page.locator(".disclosure-conflict").inner_text()
                    assert "422,649,613.97" in page.locator(".disclosure-conflict").inner_text()
                    assert "独立第二名人类研究分析师" in page.content()

                assert page.evaluate("document.documentElement.scrollWidth")<=width+2,(code,width,"FULL_HTML_BODY_HORIZONTAL_OVERFLOW")
                state=page.evaluate("""() => {
                  const figures=[...document.querySelectorAll('figure.has-native-finance')];
                  const f=figures[0],native=f.querySelector('.native-finance'),
                        desktop=f.querySelector('.chart-shell'),svg=native.querySelector('.native-money-svg');
                  const a=[...svg.querySelectorAll('.native-money-source')].map(x=>[+x.dataset.exactYuan,+x.getAttribute('width')]),
                        b=[...svg.querySelectorAll('.native-money-sink')].map(x=>[+x.dataset.exactYuan,+x.getAttribute('width')]),
                        edges=[...svg.querySelectorAll('.native-money-ribbon')].map(x=>+x.dataset.exactYuan);
                  return {figures:figures.length, nativeVisible:getComputedStyle(native).display!=='none',
                    desktopVisible:getComputedStyle(desktop).display!=='none', inner:native.scrollWidth,client:native.clientWidth,
                    source:a,sink:b,ribbons:edges, signed:[...document.querySelectorAll('.native-signed-svg')].length,
                    exportedSourceRibbons:document.querySelectorAll('.hero-svg path.money-ribbon').length,
                    bodyOverflow:document.documentElement.scrollWidth-window.innerWidth};
                }""")
                n=sum(x[0] for x in state["source"])
                assert n>0 and abs(sum(x[0] for x in state["sink"])-n)<.001
                assert abs(sum(state["ribbons"])-n)<.001
                assert state["signed"]>=5 and state["exportedSourceRibbons"]>=6
                assert all(abs(w-v/n*302)<1e-7 for v,w in state["source"]+state["sink"]),(code,width,"REAL_CLOUDFLARE_SVG_MONEY_SHAPES_NOT_SOURCE_WEIGHTED")
                if width<900:
                    assert state["nativeVisible"] and not state["desktopVisible"] and state["inner"]<=state["client"]+2,(code,width,"PUBLIC_NATIVE_MONEY_HIDDEN_OR_CROPPED",state)
                    figures=page.evaluate("""() => [...document.querySelectorAll('figure.has-native-finance')].map(f=>{
                      const n=f.querySelector('.native-finance');
                      return {inner:n.scrollWidth,visible:n.clientWidth,display:getComputedStyle(n).display};
                    })""")
                    assert all(z["inner"]<=z["visible"]+2 and z["display"]!="none" for z in figures),(code,width,"PUBLIC_OTHER_FINANCE_FIGURE_INTERNAL_SCROLL")
                else:
                    assert not state["nativeVisible"] and state["desktopVisible"]
                    with page.expect_download() as export:
                        page.locator("figure.exhibit .svg-save").first.click()
                    assert export.value.suggested_filename.endswith(".svg"),(code,"LIVE_EDITABLE_FINANCIAL_SVG_EXPORT_MISSING")
                if width==390:
                    first=page.locator("button.native-source-row").first
                    first.click()
                    assert page.locator("path.native-money-ribbon.is-selected").count()==2,(code,"NO_SOURCE_SPECIFIC_PHONE_MONEY_HIGHLIGHT")
                    first.click()
                    assert page.locator("path.native-money-ribbon.is-muted").count()==0,(code,"SOURCE_SELECTION_CANNOT_RESET")
                screenshot=OUT/f"live_{code}_{width}.png"
                page.screenshot(path=str(screenshot),full_page=True)
                screens.append({"name":screenshot.name,"sha256":SHA(screenshot.read_bytes()),"bytes":screenshot.stat().st_size})
                page.locator('a.site-library-link[href="/#companies"]').first.click()
                assert page.url==ORIGIN+"/#companies",(code,width,"RETURN_TO_SINGLE_COMPANY_DIRECTORY_FAILED",page.url)
                results.append({"code":code,"width":width,"real_article_url":article_url,"article_html_sha256":article_shas[code],"pdf_source_sha":pdf_sha,
                    "real_return_to_library":"PASS","source_weighted_cost_gp":"PASS","native_390_unclipped":"PASS" if width==390 else "NOT_PHONE"})
                page.close()
        browser.close()
    receipt={"source_main_commit":os.environ.get("GITHUB_SHA","NOT_CHECKED"),"company_directory_issuer_count":len(catalog),
        "actual_public_site":ORIGIN,"actual_home_complete_html_sha256":home_sha,"real_public_company_complete_html_sha256":article_shas,
        "real_CJK_1440_768_390_financial_editorial":results,"real_screenshots":screens,
        "independent_human_financial_editor":"NOT_CHECKED","independent_human_art_director":"NOT_CHECKED",
        "exhaustive_material_notes":"NOT_CHECKED"}
    (OUT/"result.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    assert len(results)==len(CODES)*len(WIDTHS) and len(screens)==(len(CODES)+1)*len(WIDTHS)
    print("ACTUAL_REAL_CLOUDFLARE_OPTICAL_SOURCE_THREE_ARTICLES_THREE_CHINESE_WIDTHS_EXACT_HTML_SOURCE_SHA_PASS",json.dumps({"commit":receipt["source_main_commit"],"articles":article_shas,"screenshots":len(screens)},ensure_ascii=False),flush=True)

if __name__=="__main__":run()
