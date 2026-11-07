#!/usr/bin/env python3
"""Real Chinese Chromium 1440/768/390 receipts for EVERY V10 finance exhibit.

Use after full original-issuer PDFs were downloaded and publisher rebuilt.
No static check can certify art direction, and no local file check proves live Pages.
"""
from __future__ import annotations
from decimal import Decimal as D
import hashlib, json, re
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "real-browser-qa"
OUT.mkdir(exist_ok=True)
COUNTS = {"688111":9,"600519":9,"000333":10,"600036":8}
EXPECTED = {"688111":"TYPE_A_SOURCE_OWN_COST_GP",
            "600519":"TYPE_C_SANKEY_OMITTED",
            "000333":"TYPE_B_GROUP_ONLY_GROSS_ALLOCATION",
            "600036":"BANK_NET_INCOME_TO_OPERATING_PROFIT"}
records=[]
errors=[]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    for code,count in COUNTS.items():
        file=HERE / "site" / (code+".html")
        digest=sha(file)
        for width,height in ((1440,960),(768,1024),(390,844)):
            page=browser.new_page(viewport={"width":width,"height":height},device_scale_factor=1)
            page.goto(file.resolve().as_uri(),wait_until="load",timeout=45000)
            page.evaluate("document.fonts.ready")
            page.locator("figure.graphic").first.wait_for()
            figs=page.locator("figure.graphic")
            assert figs.count()==count,(code,width,figs.count(),count)
            page_result={"code":code,"width":width,"html_sha256":digest,
                         "real_chromium":True,"actual_all_figures":count,
                         "figures":[]}
            body=page.evaluate("({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth})")
            assert body["scroll"]<=width+2,(code,width,"DOCUMENT_HORIZONTAL_OVERFLOW",body)
            screenshot=OUT/(code+"-"+str(width)+"-whole.png")
            page.screenshot(path=str(screenshot),full_page=True,timeout=45000)
            page_result["full_page_screenshot_sha256"]=sha(screenshot)
            for idx in range(count):
                fig=figs.nth(idx)
                fid=fig.get_attribute("id")
                desktop=fig.locator(".desktop-finance svg")
                native=fig.locator(".native-finance svg")
                assert desktop.count()==1 and native.count()==1,(code,width,fid,"MISSING_DUAL_FINANCE_SVG")
                chosen=native if width<=850 else desktop
                hidden=desktop if width<=850 else native
                info=chosen.evaluate("""el => {
                  const wrap=el.parentElement,fig=wrap.closest('figure');
                  const r=el.getBoundingClientRect(),w=wrap.getBoundingClientRect();
                  const box=(node)=>{const b=node.getBoundingClientRect();return {x:b.x,y:b.y,right:b.right,bottom:b.bottom,width:b.width,height:b.height}};
                  const texts=[...el.querySelectorAll('text')].map(t=>{
                    const b=t.getBBox(),transform=t.getScreenCTM();
                    if(!transform)return {bad:true};
                    const corners=[[b.x,b.y],[b.x+b.width,b.y+b.height]].map(([x,y])=>new DOMPoint(x,y).matrixTransform(transform));
                    return {x:corners[0].x,right:corners[1].x,text:t.textContent};});
                  const money=[...el.querySelectorAll('path[data-ribbon-yuan]')].map(z=>({
                    yuan:z.getAttribute('data-ribbon-yuan'),scale:z.getAttribute('data-scale-yuan-per-svg-unit'),d:z.getAttribute('d')}));
                  return {display:getComputedStyle(el).display,containerDisplay:getComputedStyle(wrap).display,
                    chart:box(el),container:box(wrap),figure:box(fig),scroll:wrap.scrollWidth,client:wrap.clientWidth,
                    texts,money,viewBox:el.viewBox.baseVal.width};}""")
                invisible=hidden.evaluate("el => getComputedStyle(el.parentElement).display")
                assert info["display"]!="none" and info["containerDisplay"]!="none",(code,width,fid,"HIDDEN_FINANCE")
                assert invisible=="none",(code,width,fid,"INACTIVE_DESKTOP_OR_MOBILE_VISIBLE")
                assert info["scroll"]<=info["client"]+2,(code,width,fid,"FIGURE_HORIZONTAL_SCROLL",info)
                assert info["viewBox"]>0 and info["chart"]["width"]>200,(code,width,fid,"CHART_TOO_NARROW",info)
                assert info["chart"]["right"] <= width+3,(code,width,fid,"SVG_OFFSCREEN")
                # CJK SVG labels: reject fully offscreen text, but do not pretend
                # a bbox-only test catches all overlaps or aesthetic quality.
                for node in info["texts"]:
                    assert not node.get("bad"),(code,width,fid,"NO_FONT_TRANSFORM")
                    if node["text"].strip():
                        assert node["right"] <= width+8 and node["x"]>=-6,(code,width,fid,"CJK_TEXT_OUTSIDE_VIEWPORT",node)
                for b in info["money"]:
                    coords=[D(v) for v in re.findall(r"-?\d+(?:\.\d+)?",b["d"])]
                    assert len(coords)>=16,(code,width,fid,"INVALID_MONEY_RIBBON")
                    actual=abs(coords[-1]-coords[1])
                    target=D(b["yuan"])/D(b["scale"])
                    assert abs(actual-target) <= D(".001"),(code,width,fid,"AMOUNT_RIBBON_NOT_PROPORTIONAL",actual,target)
                pic=OUT/(code+"-"+str(width)+"-"+fid+".png")
                chosen.screenshot(path=str(pic),timeout=20000)
                page_result["figures"].append({
                    "figure":fid,
                    "native_source_svg":width<=850,
                    "ribbon_count":len(info["money"]),
                    "actual_figure_png_sha256":sha(pic),
                    "scroll_free":"PASS",
                    "CJK_text_inside_screen":"PASS",
                    "source_ribbon_actual_SVG_thickness":"PASS",
                })
            flow=page.locator("#fig-02")
            assert flow.get_attribute("data-flow-kind")==EXPECTED[code],(code,width,"WRONG_FINANCE_FLOW_SEMANTICS")
            if code=="688111":
                selected=flow.locator(".native-finance svg") if width<=850 else flow.locator(".desktop-finance svg")
                assert selected.locator('path[data-source-id][data-revenue-yuan][data-cost-yuan][data-gp-yuan]').count()>=8
            if code=="600519":
                assert flow.locator(".native-finance svg").get_attribute("data-figure-kind")=="TYPE_C_SANKEY_OMITTED"
                assert flow.locator(".native-finance svg rect[data-signed-yuan]").count()==3
            if code=="000333":
                assert flow.locator('.native-finance svg[data-gp-limitation="PRODUCT_LEVEL_GP_NOT_ESTABLISHED"]').count()==1
                assert flow.locator("text=未披露各业务").count()>=1
                assert flow.locator('text=PRODUCT_LEVEL_GP_NOT_ESTABLISHED').count()==0
            if code=="600036":
                assert "净利息" in flow.inner_text()
            records.append(page_result)
            print("REAL_CHROMIUM_ALL_EXHIBITS_PASS",code,width,count,"HTML_SHA",digest,flush=True)
            page.close()
    browser.close()

assert len(records)==12,len(records)
result={"scope":"local original CJK Chromium 1440/768/390, not live Cloudflare",
        "source_sha_proof":"each figure receipt carries its actual regenerated HTML sha256",
        "all_36_issuer_exhibits_3_viewports":"PASS",
        "independent_finance_and_visual_human_review":"NOT_CHECKED",
        "real_live_pages_full_content_sha":"NOT_CHECKED",
        "cases":records}
(OUT/"result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print("ALL_FINANCE_REAL_CJK_CHROMIUM_PASS",len(records),flush=True)
