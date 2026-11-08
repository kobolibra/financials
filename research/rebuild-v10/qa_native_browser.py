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
BRIEFS=json.loads((HERE.parents[1]/"research/quality/pr35-hero-figure-briefs.json").read_text())
QUANTIFIED={row["issuer"]:row["quantified_driver"] for row in BRIEFS["hero_figures"]}
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
            # An audited thesis hidden in JSON, or clipped on the actual
            # narrow browser, cannot count as professional research delivery.
            thesis=page.locator('section#quantified-decision[data-research-schema="financials.source_bound_decision.v1"]')
            assert thesis.count()==1,(code,width,"READER_QUANTIFIED_RESEARCH_MISSING")
            q=thesis.evaluate("""el => {
              const r=el.getBoundingClientRect(),facts=[...el.querySelectorAll('.decision-fact')];
              const links=[...el.querySelectorAll('.decision-fact a[href*="#page="]')];
              const money=facts.map(f=>f.querySelector('.decision-fact-money')?.getBoundingClientRect());
              return {visible:getComputedStyle(el).display!=='none' && r.width>250 && r.height>180,
                x:r.left,right:r.right,insideWidth:el.clientWidth,contentWidth:el.scrollWidth,
                factCount:facts.length,links:links.length,
                textClipping:money.some(n=>!n || n.left<r.left-2 || n.right>r.right+2),
                exactResult:el.getAttribute('data-result-yuan'),
                sourceSHA:el.getAttribute('data-original-pdf-sha256'),
                nonCausal:el.getAttribute('data-accounting-not-causal')};
            }""")
            brief=QUANTIFIED[code]
            assert q["visible"] and q["x"]>=-2 and q["right"]<=width+2,(code,width,"READER_EVIDENCE_PANEL_OFFSCREEN",q)
            assert q["insideWidth"]+2>=q["contentWidth"] and not q["textClipping"],(code,width,"QUANTIFIED_RESEARCH_MONEY_CLIPPED",q)
            assert q["factCount"]==q["links"]==len(brief["fact_keys"]),(code,width,"RESEARCH_ORIGINAL_PAGE_LINKS_ABSENT",q)
            assert D(q["exactResult"])==D(brief["expected_yuan"]) and q["sourceSHA"]==brief["source_pdf_sha256"] and q["nonCausal"]=="true",(code,width,"QUANTIFIED_BROWSER_RESEARCH_SOURCE_DRIFT",q)
            page_result["reader_quantified_research"]={"real_visible":"PASS","source_fact_rows":q["factCount"],
                "original_source_links":"PASS","no_phone_clip":"PASS","accounting_not_causal":"PASS"}

            # Industrial issuer total profit: source-bound signed, not fake
            # positive-money Sankey for net income or a bank-like financial flow.
            formation=page.locator('section[data-profit-formation="SOURCE_BOUND_SIGNED_V1"]')
            if code in ("688111","000333"):
                assert formation.count()==1,(code,width,"SOURCE_BOUND_PROFIT_FORMATION_MISSING")
                assert formation.get_attribute("data-source-pdf-sha256")==QUANTIFIED[code]["source_pdf_sha256"]
                svg=formation.locator(".profit-viz-phone svg") if width<=850 else formation.locator(".profit-viz-desktop svg")
                off=formation.locator(".profit-viz-desktop svg") if width<=850 else formation.locator(".profit-viz-phone svg")
                assert svg.is_visible() and not off.is_visible(),(code,width,"WRONG_PROFIT_BRIDGE_EDITORIAL_EDITION")
                observed=svg.evaluate("""el=>{
                    let scale=+el.dataset.yuanPerSvgUnit;
                    let bars=[...el.querySelectorAll('rect[data-step-id]')].map(x=>({
                      id:x.dataset.stepId,money:x.dataset.deltaYuan,
                      before:x.dataset.beforeYuan,after:x.dataset.afterYuan,
                      width:+x.getAttribute('width'),scale:+x.dataset.moneyScaleYuanPerUnit
                    }));
                    let b=el.getBoundingClientRect(),s=el.closest('.profit-formation').getBoundingClientRect();
                    return {source:el.dataset.sourcePdfSha256,
                      net:el.dataset.netYuan,gross:el.dataset.grossYuan,
                      status:el.dataset.residualStatus,
                      layout:el.dataset.layout,
                      visible:b.width>230 && b.right<=innerWidth+3 && b.left>=-3,
                      clipped:el.parentElement.scrollWidth>el.parentElement.clientWidth+2,
                      bars,scale};
                }""")
                assert observed["visible"] and not observed["clipped"],(code,width,"PROFIT_BRIDGE_PHONE_OR_DESKTOP_CLIPPED",observed)
                assert observed["source"]==QUANTIFIED[code]["source_pdf_sha256"] and observed["status"]=="DERIVED_UNATTRIBUTED_NOT_CAUSAL"
                assert observed["scale"]>0 and len(observed["bars"])==(6 if code=="000333" else 5)
                for bar in observed["bars"]:
                    before=D(bar["before"]);delta=D(bar["money"]);after=D(bar["after"])
                    assert before+delta==after,(code,width,bar,"NOT_A_REAL_SIGNED_FINANCIAL_BRIDGE")
                    assert abs(D(str(bar["width"]))-abs(delta)/D(str(bar["scale"])))<D(".001"),(code,width,bar,"AMOUNT_DEPICTION_INFLATED")
                assert formation.locator('.profit-source-table tbody tr[data-exact-yuan][data-physical-page]').count()==(7 if code=="000333" else 4)
                image=OUT/(code+"-"+str(width)+"-profit-formation.png")
                svg.screenshot(path=str(image),timeout=20000)
                page_result["source_bound_industrial_profit_formation"]={
                    "actual_visible_signed_svg":"PASS",
                    "real_original_amount_conservation":"PASS",
                    "unattributed_financial_residual_explicit":"PASS",
                    "no_390_inner_scroll":"PASS",
                    "screenshot_sha256":sha(image)}
            else:
                assert formation.count()==0,(code,width,"FORBIDDEN_INDUSTRIAL_BRIDGE_FOR_OTHER_ACCOUNTING_MODEL")
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
            if width<=850 and code in ("688111","000333","600036"):
                # A real screenshot captured a WPS legend/stage collision and
                # a CMB four-cost footer/caveat collision despite all figure
                # bounds being legal. Test actual transformed CJK font boxes.
                spacing=flow.locator(".native-finance svg").evaluate("""svg => {
                  const nodes=role=>[...svg.querySelectorAll('[data-editorial-role="'+role+'"]')];
                  const bottom=role=>Math.max(...nodes(role).map(x=>x.getBoundingClientRect().bottom));
                  const top=role=>Math.min(...nodes(role).map(x=>x.getBoundingClientRect().top));
                  const bounds=svg.getBoundingClientRect();
                  return {sourceBottom:bottom('source-summary'),
                          sourceStageTop:top('source-stage-header'),
                          outcomeBottom:bottom('outcome-value'),
                          disclaimerTop:top('accounting-limitation'),
                          disclaimerBottom:bottom('accounting-limitation'),
                          noteTop:top('source-caveat'),
                          noteBottom:bottom('source-caveat'),
                          svgBottom:bounds.bottom};
                }""")
                assert spacing["sourceBottom"]+3 < spacing["sourceStageTop"],(code,width,"SOURCE_LEGEND_OVERLAPS_CHART",spacing)
                assert spacing["outcomeBottom"]+3 < spacing["disclaimerTop"],(code,width,"FINANCIAL_OUTCOME_OVERLAPS_CAVEAT",spacing)
                assert spacing["disclaimerBottom"]+3 < spacing["noteTop"],(code,width,"CAVEAT_OVERLAPS_SOURCE_NOTE",spacing)
                assert spacing["noteBottom"]+1 < spacing["svgBottom"],(code,width,"FINANCE_SOURCE_FOOTER_CLIPPED",spacing)
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
