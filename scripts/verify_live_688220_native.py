#!/usr/bin/env python3
"""Independent REAL Cloudflare full HTML + Chromium semiconductor mobile release.
No manual human design approval is asserted.
"""
from __future__ import annotations
import hashlib,json,os,time,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
ORG="https://financials-in-visuals.pages.dev"
OUT=ROOT/"research/issuers/688220/live-visual-qa"
OUT.mkdir(exist_ok=True,parents=True)
SHA=lambda b: hashlib.sha256(b).hexdigest()

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Financials-in-Visuals-688220-exact-release-check"})
    with urllib.request.urlopen(req,timeout=25) as r:
        return r.read()

def main():
    local=(ROOT/"public/688220.html").read_bytes()
    home=(ROOT/"public/index.html").read_bytes()
    remote=b""
    for retry in range(16):
        try:
            remote=get(ORG+"/688220.html")
            if remote==local and get(ORG+"/")==home:
                break
        except Exception as exc:
            print("PUBLIC_DEPLOY_PENDING_HTTP",retry,str(exc),flush=True)
        print("PUBLIC_DEPLOY_PENDING_FULL_SOURCE_HTML_SHA",retry,SHA(remote),SHA(local),flush=True)
        time.sleep(10)
    assert local==remote,("ACTUAL_CLOUDFLARE_688220_HTML_SHA_MISMATCH",SHA(local),SHA(remote))
    assert get(ORG+"/")==home,"PUBLIC_SITE_DIRECTORY_HTML_NOT_MAIN_SHA"
    manifest=json.loads((ROOT/"research/issuers/688220/source-manifest.json").read_text())
    ledger=json.loads((ROOT/"research/issuers/688220/source-ledger.json").read_text())
    assert ledger["issuer"]["code"]=="688220"
    pdf_sha=manifest["pdf_sha256"]
    assert pdf_sha.encode() in local and len(pdf_sha)==64
    catalog=json.loads((ROOT/"site/research_catalog.json").read_text())["issuers"]
    assert len(catalog)>=11 and any(z["code"]=="688220" for z in catalog)
    for company in catalog:
        independent=get(ORG+company["href"])
        assert b"<html" in independent.lower() or b"<!doctype" in independent.lower(),("PUBLIC_COMPANY_HTML_MISSING",company["code"])
        assert independent!=home,("COMPANY_LINK_REDIRECTS_TO_HOMEPAGE",company["code"])
    rows=[];screens=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(args=["--no-sandbox"])
        for width in (1440,768,390):
            page=browser.new_page(viewport={"width":width,"height":900},device_scale_factor=1,accept_downloads=True)
            page.goto(ORG+"/",wait_until="networkidle")
            assert page.locator("a.company").count()==len(catalog),(width,"COMPANY_DIRECTORY_COUNT")
            directory_shot=OUT/f"live_directory_{width}.png"
            page.screenshot(path=str(directory_shot),full_page=True)
            screens.append({"viewport":width,"sha256":SHA(directory_shot.read_bytes()),"bytes":directory_shot.stat().st_size,"file":directory_shot.name})
            page.locator('a.company[href="/688220.html"]').click()
            assert page.url.rstrip("/").endswith("/688220.html") or page.url.rstrip("/").endswith("/688220"),(width,page.url)
            page.wait_for_selector("#chart-flow svg",state="attached")
            facts=page.evaluate("""() => {
              const source=[...document.querySelectorAll('.native-asr-source')].map(x=>({w:+x.getAttribute('width'),amount:+x.dataset.exactYuan}));
              const sink=[...document.querySelectorAll('.native-asr-sink')].map(x=>({w:+x.getAttribute('width'),amount:+x.dataset.exactYuan}));
              const flow=[...document.querySelectorAll('.native-asr-ribbon')].map(x=>({w:+x.dataset.width,amount:+x.dataset.exactYuan}));
              const native=[...document.querySelectorAll('.native-asr')];
              const bbox=native.flatMap(n=>[...n.querySelectorAll('svg text')].map(t=>{const b=t.getBBox();return {x:b.x,right:b.x+b.width,total:t.ownerSVGElement.viewBox.baseVal.width}}));
              return {n:native.length,visible:native.filter(n=>getComputedStyle(n).display!=='none').length,
                originals:[...document.querySelectorAll('.vizscroll')].filter(n=>getComputedStyle(n).display!=='none').length,
                cropped:native.filter(n=>n.scrollWidth>n.clientWidth+2).length,root:document.documentElement.scrollWidth,
                source,sink,flow,bbox,steps:document.querySelectorAll('.native-asr-signed').length,
                tables:document.querySelectorAll('table.evidence-table').length,
                exports:document.querySelectorAll('[data-export]').length};
            }""")
            assert facts["root"]<=width+1 and facts["n"]==facts["tables"]==facts["exports"]==9
            assert len(facts["source"])==4 and len(facts["sink"])==2 and len(facts["flow"])==7 and facts["steps"]>=25
            rev=sum(x["amount"] for x in facts["source"]);scale=298/rev
            assert abs(sum(x["amount"] for x in facts["sink"])-rev)<.001
            assert abs(sum(x["amount"] for x in facts["flow"])-rev)<.001
            assert all(abs(x["w"]-x["amount"]*scale)<.000001 for x in facts["source"]+facts["sink"]+facts["flow"])
            assert all(b["x"]>=-2 and b["right"]<=b["total"]+2 for b in facts["bbox"]),("ACTUAL_CJK_SVG_TEXT_CLIPPED",width)
            if width<900:
                assert facts["visible"]==9 and facts["originals"]==0 and facts["cropped"]==0,("PUBLIC_MOBILE_FINANCE_CLIPPED",width,facts)
            else:
                assert facts["visible"]==0 and facts["originals"]==9
                with page.expect_download() as item:
                    page.locator('button[data-export="flow"]').click()
                assert item.value.suggested_filename=="688220_2026H1_flow.svg"
            shot=OUT/f"live_688220_{width}.png";page.screenshot(path=str(shot),full_page=True)
            screens.append({"viewport":width,"sha256":SHA(shot.read_bytes()),"bytes":shot.stat().st_size,"file":shot.name})
            page.locator('a.brand[href="/#companies"]').click()
            assert page.url.startswith(ORG+"/") and page.url.endswith("#companies"),(width,"PUBLIC_DIRECTORY_RETURN_BROKEN",page.url)
            rows.append({"viewport":width,"source_graph_real_yuan":"PASS","original_production_route":"PASS","CJK_label_bbox":"PASS","nine_figure_phone_no_inner_scroll":"PASS" if width<900 else "ORIGINAL_DESKTOP","evidence_tables":9})
            page.close()
        browser.close()
    receipt={"issuer":"688220","source_main_commit":os.getenv("GITHUB_SHA","NOT_CHECKED"),"source_pdf_sha256":pdf_sha,
        "public_html_sha256":SHA(remote),"home_html_sha256":SHA(home),"public_origin":ORG,
        "unified_company_count":len(catalog),"real_browser":rows,"screenshots":screens,
        "independent_second_human_finance_editor":"NOT_CHECKED",
        "independent_second_human_visual_editor":"NOT_CHECKED",
        "SSE_original_bytes_equivalence":"NOT_CHECKED",
        "AR_top5_reported_ratio_vs_derived":"FAIL_BOUNDED_DENOMINATOR_UNKNOWN"}
    (OUT/"result.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    print("ACTUAL_CLOUDFLARE_688220_FULL_HTML_SHA_AND_ORIGINAL_9_NATIVE_FINANCE_CJK_PASS",receipt["public_html_sha256"],flush=True)
if __name__=="__main__":main()
