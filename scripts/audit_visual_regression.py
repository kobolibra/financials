#!/usr/bin/env python3
"""Actual visual-drift census across the ONE existing eleven-issuer site.

Runs all currently published standalone HTML with real CJK Chromium at 1440,
768 and 390, from actual repository bytes. This is a SCREENSHOT AUDIT, not
financial/source confirmation or human second-editor certification.

Produce dated, SHA-scoped JSON, genuine figure screenshots and cross-company
visual comparisons. Detect the old trap: zero document overflow but a 1250px
chart trapped in a 390px horizontally scrolled window.
"""
from __future__ import annotations
import hashlib, json, os, re, subprocess
from pathlib import Path
from io import BytesIO
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
CATALOG=json.loads((ROOT/"site/research_catalog.json").read_text())
OUT=ROOT/"research/visual-audit"
OUT.mkdir(parents=True,exist_ok=True)
SRC_COMMIT=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
assert len(CATALOG["issuers"])>=11 and CATALOG["unified_directory"]
THEME={
"initial_editorial_optical":["300394","300308","300502"],
"v10_other_models":["600036","688111","600519","000333"],
"source_first_industrial":["688220","600900","600276"],
"insurance":["601628"]}
SAMPLE={"300394","300308","300502","600036","688111","688220","600900","600276","601628"}
def as_webp(raw,path,max_width=1400):
    im=Image.open(BytesIO(raw)).convert("RGB")
    if im.width>max_width:
        h=round(im.height*max_width/im.width)
        im=im.resize((max_width,h),Image.Resampling.LANCZOS)
    im.save(path,"WEBP",quality=82,method=5)
    assert path.stat().st_size>7000 and path.stat().st_size<5500000,(path,path.stat().st_size)
    return {"file":str(path.relative_to(ROOT)),"bytes":path.stat().st_size,
            "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"pixel_dims":[im.width,im.height]}

records=[];screens=[];errors=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    for entry in CATALOG["issuers"]:
        code,path=entry["code"],ROOT/"public"/entry["href"].lstrip("/")
        assert path.is_file(),(code,"MISSING_EXISTING_INDEPENDENT_HTML",str(path))
        htmlsha=hashlib.sha256(path.read_bytes()).hexdigest()
        for width,height in [(1440,900),(768,1024),(390,844)]:
            page=browser.new_page(viewport={"width":width,"height":height},device_scale_factor=1)
            page_errors=[]
            page.on("pageerror",lambda e:page_errors.append(str(e)))
            page.goto(path.as_uri(),wait_until="load",timeout=40000)
            page.wait_for_timeout(180)
            m=page.evaluate("""() => {
                const vis=el=>{const c=getComputedStyle(el);return c.display!=='none'&&c.visibility!=='hidden'&&el.getBoundingClientRect().width>1};
                const r=el=>{const b=el.getBoundingClientRect();return {x:Math.round(b.x),y:Math.round(b.y),width:Math.round(b.width),height:Math.round(b.height)}};
                const styles=[...document.querySelectorAll('style')].map(x=>x.textContent||'');
                const figures=[...document.querySelectorAll('figure')],charts=[...document.querySelectorAll('figure .chart,figure .chart-shell,figure .vizscroll,figure .plot,figure .sankey-svg')].filter(vis);
                const inner=charts.map(el=>({klass:el.className,client:el.clientWidth,scroll:el.scrollWidth,overflow:getComputedStyle(el).overflowX,
                   actualSvgWidth:Math.round(el.querySelector('svg')?.getBoundingClientRect().width||0)}));
                const money=[...document.querySelectorAll('figure path.money-ribbon')];
                const labels=[...document.querySelectorAll('figure svg text')];
                const headings=[...document.querySelectorAll('h1,h2,h3')].map(x=>x.textContent.trim().slice(0,95));
                const iframes=[...document.querySelectorAll('iframe')];
                const firstFigure=figures.find(x=>vis(x));
                const firstSvg=firstFigure?.querySelector('svg');
                const font=getComputedStyle(document.querySelector('h1')||document.body).fontFamily;
                return {body:document.documentElement.scrollWidth,figures:figures.length,visibleFigures:figures.filter(vis).length,
                    svgs:document.querySelectorAll('figure svg').length,visibleSvgCharts:charts.filter(x=>x.querySelector('svg')).length,
                    moneyRibbons:money.length,realSvgTextLabels:labels.length,
                    evidenceTables:document.querySelectorAll('figure table').length,details:document.querySelectorAll('figure details').length,
                    inlineFigureCount:figures.filter(x=>x.querySelector('svg')).length,
                    internalHorizontalScrollers:inner.filter(z=>z.scroll>z.client+6),
                    scrollInfo:inner,firstFigure: firstFigure?r(firstFigure):null,firstSvg:firstSvg?r(firstSvg):null,
                    bodyFont:getComputedStyle(document.body).fontFamily,headlineFont:font,
                    h1:headings[0]||'',headings:headings.slice(0,10),
                    firstFigureTitle:firstFigure?.querySelector('h2,h3')?.textContent.trim().slice(0,100)||'',
                    iframes:iframes.length,sourceWordCount:(document.body.textContent.match(/来源|源注|原始财报|会计关系/g)||[]).length,
                    mobileAltFigures:[...document.querySelectorAll('.mobile-chart')].filter(vis).length,
                    hasRealMoneyRect:!!document.querySelector('rect.money-source'),
                    firstFigureHasMoneyRibbon:!!firstFigure?.querySelector('path.money-ribbon'),
                    suspiciousGenericCards:[...document.querySelectorAll('.card,.metric')].length,
                    maxSvgViewbox:firstSvg?.getAttribute('viewBox')||'',
                    rootBackdrop:getComputedStyle(document.body).backgroundColor,
                    firstHero:r(document.querySelector('header .hero,.hero')||document.body),
                    design_css_sha:styles.join(' ').length,
                    linkToOnlyOneDirectory:!!document.querySelector('a[href="/#companies"]'),
                };
            }""")
            assert m["figures"]>=1,(code,width,"NO_FIGURES")
            assert not page_errors,(code,width,"JS_ERRORS",page_errors)
            assert m["body"]<=width+2,(code,width,"PAGE_OVERSCROLL",m["body"])
            group=next((k for k,v in THEME.items() if code in v),"other")
            rec={"code":code,"name":entry["name"],"report_route":entry["href"],"source_html_sha256":htmlsha,
                 "source_git_commit":SRC_COMMIT,"group":group,"viewport":[width,height],
                 **m}
            rec["quality_gates"]={
                "actual_local_browser_render":"PASS",
                "one_single_standalone_article":"PASS" if m["iframes"]==0 else "FAIL",
                "root_document_no_overflow":"PASS",
                "entire_primary_money_diagram_readable_without_figure_internal_horizontal_scroller":
                    "PASS" if not m["internalHorizontalScrollers"] else "FAIL",
                "independent_human_visual_editor":"NOT_CHECKED",
                "real_remote_cloudflare_current_sha":"NOT_CHECKED_BY_THIS_LOCAL_AUDIT",
                "current_page_offline_source_row_and_financial_research":"NOT_CHECKED_BY_VISUAL_AUDIT"
            }
            if code in SAMPLE and width in (1440,390):
                if width==1440:
                    aswebp=as_webp(page.screenshot(full_page=False),
                                OUT/f"{code}-desktop-above-fold.webp",1440)
                    screens.append(aswebp)
                if width==390:
                    shot=as_webp(page.screenshot(full_page=False),
                                OUT/f"{code}-phone-above-fold.webp",390)
                    screens.append(shot)
                try:
                    loc=page.locator("figure").first
                    loc.scroll_into_view_if_needed(timeout=5000)
                    pic=loc.screenshot(timeout=8000,animations="disabled")
                    sh=as_webp(pic,OUT/f"{code}-first-financial-figure-{width}.webp",1250 if width==1440 else 390)
                    screens.append(sh)
                except Exception as e:
                    errors.append({"code":code,"width":width,"screenshot_error":str(e)[:300]})
            records.append(rec)
            page.close()
    browser.close()
out={"source_git_commit":SRC_COMMIT,"scope":"ALL_ELEVEN_REAL_LOCAL_STANDALONE_HTML_FILES_1440_768_390_BROWSER_ONLY",
     "benchmark":"AEI original Q3FY24 Alphabet/Apple diagrams: business sources -> weighted total revenue -> COGS/GP -> operating expenses -> profit, labels and meaningful geometry, NOT just svg tag count",
     "notes":"An actual Chromium screenshot is an input to editorial judgment, but no independent human designer reviewed or certified this audit.",
     "count_issuers":len(CATALOG["issuers"]),"count_viewport_tests":len(records),
     "screenshots":screens,"screenshot_errors":errors,"records":records}
(OUT/"cross-issuer-visual-audit.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
print("ACTUAL_ELEVEN_COMPANY_CHROMIUM_EDITORIAL_VISUAL_CENSUS",len(records),"SCREENSHOTS",len(screens))
for r in records:
    if r["viewport"][0] in (1440,390):
        print("FIGURE_AUDIT",r["code"],r["viewport"][0],r["figures"],r["svgs"],r["moneyRibbons"],r["evidenceTables"],
             "FIGURE_SCROLL",[(i["client"],i["scroll"]) for i in r["internalHorizontalScrollers"]],"FIRST",r["firstFigureTitle"])
print("SAVED_SAMPLE_IMAGE_FILES",*[x["file"] for x in screens],sep="\n")
