#!/usr/bin/env python3
"""Local rendered-document QA; passing does NOT mean subjective visual or financial editorial PASS."""
from __future__ import annotations
import argparse,json,pathlib
from playwright.sync_api import sync_playwright
P=argparse.ArgumentParser();P.add_argument("--html",default="public/688220.html");P.add_argument("--out",default="research/issuers/688220/visual-qa");a=P.parse_args()
html=pathlib.Path(a.html).resolve();out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
assert html.exists() and html.stat().st_size>20000,html
bad=[];statuses=[];screenshot_count=0
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    for width,height in [(1440,960),(768,1024),(390,844)]:
        page=browser.new_page(viewport={"width":width,"height":height},accept_downloads=True)
        page.on("pageerror",lambda e:bad.append("PAGE_ERROR "+str(e)))
        page.on("console",lambda m:bad.append("CONSOLE_ERROR "+m.text) if m.type=="error" else None)
        page.goto(html.as_uri(),wait_until="load")
        page.wait_for_selector("#chart-flow svg",timeout=15000)
        info=page.evaluate("""() => ({
          scrollWidth:document.documentElement.scrollWidth,
          clientWidth:document.documentElement.clientWidth,
          svg:document.querySelectorAll('.vizscroll svg').length,
          exportButtons:document.querySelectorAll('[data-export]').length,
          evidenceTables:document.querySelectorAll('table.evidence-table').length,
          figures:document.querySelectorAll('figure.figure').length,
          amounts:Array.from(document.querySelectorAll('.vizscroll svg text')).filter(x=>/亿/.test(x.textContent)).length,
          title:document.title,
          mobileFactPanels:document.querySelectorAll('.mobile-facts').length,
          mobileFactsVisible:Array.from(document.querySelectorAll('.mobile-facts')).filter(e=>getComputedStyle(e).display!=='none').length,
          images:document.images.length,
          externalScripts:document.querySelectorAll('script[src]').length,
          tofu:document.body.textContent.includes('□')?document.body.textContent.match(/□/g).length:0
        })""")
        assert info["scrollWidth"]<=width+1,(width,"page overflow",info)
        assert info["figures"]==7 and info["svg"]==7 and info["evidenceTables"]==7,(width,info)
        assert info["exportButtons"]==7 and info["externalScripts"]==0 and info["amounts"]>=10
        assert info["mobileFactPanels"]==7,(width,"each graphic requires independent first-order values on mobile",info)
        assert info["mobileFactsVisible"]==(0 if width==1440 else 7),(width,"missing visible amount headlines for mobile/tablet",info)
        assert page.locator('a.brand[href="/#companies"]').count()==1
        assert page.locator('a[href="#cash"]').count()>=1
        page.screenshot(path=str(out/f"full_{width}.png"),full_page=True)
        screenshot_count+=1
        if width in (1440,390):
            for figure in ("flow","segment","gp","earnings","cfo","cash","capital"):
                page.locator("#fig-"+figure).screenshot(path=str(out/f"{figure}_{width}.png"))
                screenshot_count+=1
        page.locator('a[href="#cash"]').first.click()
        assert page.url.endswith("#cash"),page.url
        if width==1440:
            with page.expect_download(timeout=10000) as download:
                page.locator('button[data-export="flow"]').click()
            assert download.value.suggested_filename=="688220_2026H1_flow.svg"
        statuses.append({"viewport":width,"scroll_width":info["scrollWidth"],"figures":info["figures"],"svg":info["svg"],"source_tables":info["evidenceTables"],"result":"PASS","editorial_human_view":"NOT_CHECKED"})
        page.close()
    browser.close()
assert not bad,bad
(out/"result.json").write_text(json.dumps({"technical_browser":"PASS","source_pdf_manual_review":"NOT_CHECKED","full_design_editorial":"NOT_CHECKED","production_route":"NOT_CHECKED","viewport":statuses,"errors":bad,"screenshots":screenshot_count},ensure_ascii=False,indent=2)+"\n")
print("ASR_LOCAL_RENDER_QA_PASS",statuses,"screenshots",screenshot_count,flush=True)
