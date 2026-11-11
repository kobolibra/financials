#!/usr/bin/env python3
"""Real local Chromium source, layout, geometry and navigation evidence.

Checks rendered actual money geometry, not a count of SVG files. Records all
screenshots; automated pass is not a human aesthetic or full notes signature.
"""
from pathlib import Path
import argparse,hashlib,json,sys
from decimal import Decimal as D
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
def main():
    p=argparse.ArgumentParser();p.add_argument("--code",choices=["600900","600276"],required=True);a=p.parse_args()
    d=json.loads((ROOT/"research"/"issuers"/a.code/"source-ledger.json").read_text())
    file=ROOT/"public"/(a.code+".html")
    assert file.is_file()
    out=ROOT/"research"/"issuers"/a.code/"visual-qa";out.mkdir(parents=True,exist_ok=True)
    record=[];errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for width,height in [(1440,900),(768,1024),(390,844)]:
            page=browser.new_page(viewport={"width":width,"height":height},device_scale_factor=1)
            page.on("pageerror",lambda e:errors.append(str(e)))
            response=page.goto(file.resolve().as_uri(),wait_until="networkidle",timeout=30000)
            assert page.locator("h1").count()==1
            dec=page.locator("#quantified-decision")
            assert dec.count()==1 and dec.is_visible(),(a.code,width,"READER_VISIBLE_QUANTIFIED_ANALYSIS_MISSING")
            assert dec.get_attribute("data-issuer")==a.code
            assert dec.get_attribute("data-source-pdf-sha256")==d["source"]["original_bytes_sha256"]
            rows=dec.locator("[data-fact-id]")
            assert rows.count()==6,(a.code,width,"MISSING_QUANTIFIED_ORIGINAL_FACTS")
            for row in rows.all():
                key=row.get_attribute("data-fact-id")
                fact=d["facts"][key]
                assert row.get_attribute("data-period")==fact["period"],(a.code,width,key,"QUANTIFIED_PERIOD_SILENT_CHANGE")
                assert row.get_attribute("data-source-unit")==fact["unit"],(a.code,width,key,"QUANTIFIED_UNIT_CHANGED")
                assert D(row.get_attribute("data-exact-source-value"))==D(fact["yuan"]),(a.code,width,key,"QUANTIFIED_READER_NOT_ORIGINAL_VALUE")
                assert int(row.get_attribute("data-physical-page"))==fact["page"],(a.code,width,key,"QUANTIFIED_PDF_PAGE_WRONG")
            assert "NOT_CHECKED" in dec.inner_text(),(a.code,width,"NO_CAUSALITY_REVIEW_LIMITATION")

            assert page.locator("section.chapter").count()==8
            assert page.locator("figure.figure").count()==8
            assert page.locator("figure table").count()==8
            assert page.locator("table").count()-page.locator(".research-context table").count()==10,("SOURCE_TYPED_PROFIT_DETAILS_TABLE_MISSING",a.code,width)
            assert page.locator("figure svg").count()==16,("EIGHT_DESKTOP_AND_EIGHT_NATIVE_MOBILE_SVG_MISSING",a.code,width)
            # Signed V10-compatible research bridge: the two existing signed
            # PNL/CFO exhibits stay intact; this is a separately source-typed
            # exact original Yuan summary with explicit unattributed residual.
            panel=page.locator('section[data-profit-formation="SOURCE_BOUND_SIGNED_V1"]')
            assert panel.count()==1 and panel.is_visible(),(a.code,width,"SOURCE_BOUND_PROFIT_STORY_NOT_VISIBLE")
            assert panel.get_attribute("data-source-pdf-sha256")==d["source"]["original_bytes_sha256"],(a.code,width,"ORIGINAL_DISCLOSURE_PDF_SHA_WRONG")
            chosen=panel.locator(".profit-viz-phone svg") if width<=850 else panel.locator(".profit-viz-desktop svg")
            other=panel.locator(".profit-viz-desktop svg") if width<=850 else panel.locator(".profit-viz-phone svg")
            assert chosen.count()==1 and chosen.is_visible() and not other.is_visible(),(a.code,width,"PROFIT_BRIDGE_NOT_INDEPENDENT_MOBILE_EDITION")
            evidence=chosen.evaluate("""svg=>{
                let b=svg.getBoundingClientRect();
                return {period:svg.dataset.period,source:svg.dataset.sourcePdfSha256,
                  grammar:svg.dataset.profitGrammar,residual:svg.dataset.residualStatus,
                  gross:svg.dataset.grossYuan,net:svg.dataset.netYuan,
                  clipped:b.left< -2||b.right>innerWidth+2||
                    svg.parentElement.scrollWidth>svg.parentElement.clientWidth+2,
                  bars:[...svg.querySelectorAll('rect[data-step-id]')].map(n=>({
                    id:n.dataset.stepId,before:n.dataset.beforeYuan,after:n.dataset.afterYuan,
                    delta:n.dataset.deltaYuan,width:n.getAttribute('width'),
                    scale:n.dataset.moneyScaleYuanPerUnit}))};
            }""")
            assert evidence["grammar"]=="DISCLOSED_INCOME_TO_NET_SIGNED_CONSOLIDATED_BRIDGE" and evidence["residual"]=="DERIVED_UNATTRIBUTED_NOT_CAUSAL"
            assert evidence["period"]=="2026H1" and evidence["source"]==d["source"]["original_bytes_sha256"] and not evidence["clipped"],(a.code,width,"SOURCE_PROFIT_CJK_CLIPPED",evidence)
            assert D(evidence["gross"])==D(d["facts"]["rev"]["yuan"])-D(d["facts"]["cogs"]["yuan"])
            assert D(evidence["net"])==D(d["facts"]["net_profit"]["yuan"])
            assert len(evidence["bars"])==5,(a.code,width,"REAL_SIGNED_INCOME_TO_NET_STEPS_MISSING")
            for bar in evidence["bars"]:
                bef=D(bar["before"]);end=D(bar["after"]);delta=D(bar["delta"])
                assert bef+delta==end,(a.code,width,"SIGNED_INCOME_TO_NET_UNBALANCED",bar)
                assert abs(D(bar["width"])-abs(delta)/D(bar["scale"]))<D(".001"),(a.code,width,"SOURCE_MONEY_GRAPH_NOT_PROPORTIONAL",bar)
            assert panel.locator('.profit-source-table tbody tr[data-fact-id][data-exact-yuan][data-physical-page] a[href*="#page="]').count()==4
            pic=out/(a.code+"-profit-formation-"+str(width)+".png")
            chosen.screenshot(path=str(pic),timeout=20000)

            # Source-linked sector editorial figure is a second genuine industry
            # graphic, not a manually frozen current-period number or a money
            # ribbon connecting generation/management subsets to cash.
            sector=page.locator("#chart-sector > svg")
            source=sector.evaluate("""svg=>({
                production:[...svg.querySelectorAll('[data-source-fact]')].map(x=>({
                    key:x.dataset.sourceFact,original:x.dataset.originalValue,yuan:x.dataset.originalYuan})),
                contracts:[...svg.querySelectorAll('rect[data-contract-source]')].map(x=>({
                    key:x.dataset.contractSource,yuan:x.dataset.sourceYuan,width:+x.getAttribute('width'),
                    scale:+x.dataset.scaleYuanPerSvgUnit})),
                innovation:svg.querySelector('[data-operating-fact="innovative_drug_sales_100m"]')?
                  {yuan:svg.querySelector('[data-operating-fact="innovative_drug_sales_100m"]').dataset.subsetYuan,
                   parent:svg.querySelector('[data-operating-fact="innovative_drug_sales_100m"]').dataset.goodsParentYuan,
                   width:+svg.querySelector('[data-operating-fact="innovative_drug_sales_100m"]').getAttribute('width'),
                   scale:+svg.querySelector('[data-operating-fact="innovative_drug_sales_100m"]').dataset.scaleYuanPerSvgUnit}:null,
                rpo:svg.querySelector('[data-stock-fact="rpo"]')?.dataset.stockYuan
            })""")
            if a.code=="600900":
                gen=next((x for x in source["production"] if x["key"]=="power_gen_100m_kwh"),None)
                assert gen and D(gen["original"])==D(d["facts"]["power_gen_100m_kwh"]["yuan"]),(a.code,width,"HYDRO_PHYSICAL_SOURCE_SILENTLY_FROZEN")
                for key in ("rev","cfo"):
                    fact=next((x for x in source["production"] if x["key"]==key),None)
                    assert fact and D(fact["yuan"])==D(d["facts"][key]["yuan"]),(a.code,width,"HYDRO_MONEY_NOT_SOURCE_BOUND",key)
            else:
                assert len(source["contracts"])==3,(a.code,width,"PHARMA_CONTRACT_SOURCE_MISSING")
                total=sum((D(x["yuan"]) for x in source["contracts"]),D(0))
                assert total==D(d["facts"]["rev"]["yuan"]),(a.code,width,"PHARMA_CONTRACT_INCOME_NOT_EXCLUSIVE")
                assert all(x["width"]>0 and abs(D(str(x["width"]))-D(x["yuan"])/D(str(x["scale"])))<D(".02")
                           for x in source["contracts"]),(a.code,width,"PHARMA_ORIGINAL_MONEY_AREA_CHANGED")
                innovation=source["innovation"]
                assert innovation and D(innovation["yuan"])==D(d["facts"]["innovative_drug_sales_100m"]["yuan"])*D(100000000)
                assert D(innovation["parent"])==D(d["facts"]["drug_sales_rev"]["yuan"])
                assert abs(D(str(innovation["width"]))-D(innovation["yuan"])/D(str(innovation["scale"])))<D(".02")
                assert D(source["rpo"])==D(d["facts"]["rpo"]["yuan"]),(a.code,width,"RPO_BECAME_REVENUE")
            assert page.locator(".plot > svg").count()==8
            assert page.locator(".native-mobile-finance svg").count()==8
            assert page.locator("a[href='/#companies']").count()>=1
            assert page.locator("iframe").count()==0
            assert page.locator("script[src]").count()==0
            if page.evaluate("document.documentElement.scrollWidth")>width+1:
                overflow=page.evaluate("""() => [...document.querySelectorAll('body *')].filter(x=>{const r=x.getBoundingClientRect(); if(r.right<=innerWidth+1&&r.left>=-1)return false;for(let p=x.parentElement;p;p=p.parentElement){if(['auto','scroll','hidden','clip'].includes(getComputedStyle(p).overflowX))return false}return true}).slice(0,30).map(x=>({name:x.tagName,cls:typeof x.className==='string'?x.className:'svg',id:x.id,right:x.getBoundingClientRect().right,width:x.getBoundingClientRect().width,parent:x.parentElement?.className}))""")
                raise AssertionError((a.code,width,"BODY_OVERFLOW",page.evaluate("document.documentElement.scrollWidth"),overflow))
            # Do not gain a false pass by hiding oversized content at the
            # root: every article section, figure, figure head and its lead
            # narrative still has to fit the physical viewport. SVGs alone
            # may scroll in their own .plot container on mobile.
            structural=page.evaluate("""() => [...document.querySelectorAll('.topbar,.hero,.heroaside,.nav,.numbers,.number,.chapter,.chapter h2,.chapter .answer,.figure,.figure-head,.sourcebar,.tablewrap,.disclaimer,.actions,.footer')].map(x=>({tag:x.tagName,cls:x.className,rect:x.getBoundingClientRect()})).filter(z=>z.rect.right>innerWidth+2 || z.rect.left< -2).map(z=>({tag:z.tag,cls:z.cls,left:z.rect.left,right:z.rect.right})).slice(0,20)""")
            assert not structural,("NON_SCROLLING_MOBILE_CONTENT_CLIPPED",a.code,width,structural)
            if width<=850:
                # The previous QA "body<=390" and "overflow-x:auto" gave
                # a false PASS while the primary figures had 780px content
                # inside 354px local chart scroll panes. THIS is the reader gate.
                assert page.locator(".native-mobile-finance:visible").count()==8,(a.code,"NOT_ALL_EIGHT_GENUINE_MOBILE_FINANCIAL_FIGURES_VISIBLE")
                assert page.locator(".native-mobile-finance svg:visible").count()==8
                assert page.locator(".plot > svg:visible").count()==0,(a.code,"DESKTOP_SVG_STILL_TRAPPED_IN_390PX_VIEWPORT")
                native=page.evaluate("""() => [...document.querySelectorAll('.plot')].map(el=>{
                     const m=el.querySelector('.native-mobile-finance'),svg=m.querySelector('svg');
                     const labels=[...svg.querySelectorAll('text')].map(t=>({
                       value:t.textContent.slice(0,45),x:t.getBBox().x,
                       right:t.getBBox().x+t.getBBox().width
                     }));
                     return {id:el.id,client:el.clientWidth,scroll:el.scrollWidth,style:getComputedStyle(el).overflowX,
                       figureWidth:svg.getBoundingClientRect().width,
                       mobileViewbox:svg.viewBox.baseVal.width,textClips:labels.filter(x=>x.x< -1||x.right>svg.viewBox.baseVal.width+2).slice(0,12)};
                 })""")
                assert all(z["scroll"]<=z["client"]+2 for z in native),(a.code,"MOBILE_390_FINANCIAL_FIGURE_INNER_SCROLL_STILL_PRESENT",native)
                assert all(z["mobileViewbox"]==330 and z["figureWidth"]<=z["client"]+1 and z["figureWidth"]>=250 for z in native),(a.code,"MOBILE_390_MONEY_ART_NOT_NATIVE_OR_TOO_TINY",native)
                assert all(not z["textClips"] for z in native),(a.code,"MOBILE_MONEY_SVG_CJK_TEXT_CLIPPED_OR_OVERLONG",native)
                assert all(z["style"] not in ("auto","scroll") for z in native),(a.code,"MOBILE_390_STILL_SHOWS_NESTED_CHART_SCROLL_WINDOW",native)
                source=page.evaluate("""() => {
                  const svg=document.querySelector('#chart-flow .native-mobile-finance svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"]');
                  if(!svg)return null;
                  return {
                    total:+svg.getAttribute('data-revenue-yuan'),scale:+svg.getAttribute('data-scale-yuan-per-svg-unit'),
                    nodes:[...svg.querySelectorAll('rect[data-node-role]')].map(n=>({id:n.getAttribute('data-node-id'),role:n.getAttribute('data-node-role'),money:+n.getAttribute('data-node-yuan'),h:+n.getAttribute('height')})),
                    ribbons:[...svg.querySelectorAll('path[data-ribbon-yuan]')].map(p=>({money:+p.getAttribute('data-ribbon-yuan'),stage:p.getAttribute('data-stage'),scale:+p.getAttribute('data-scale-yuan-per-svg-unit'),d:p.getAttribute('d')}))};
                }""")
                assert source and source["total"]>0 and source["scale"]>0,(a.code,"MOBILE_UNIFIED_FLOW_MISSING")
                # The first mobile graphic was geometrically correct but its
                # source amounts were squeezed into the same 9px line as the
                # business name. Require two genuinely readable visual rows,
                # not just a valid source-table under the chart.
                spacing=page.locator('#chart-flow .native-mobile-finance svg').evaluate("""svg=>{
                  const nodes=[...svg.querySelectorAll('text[data-editorial-role="source-summary"]')];
                  const header=svg.querySelector('text[data-editorial-role="source-stage-header"]');
                  const source=nodes.map(el=>({font:+el.getAttribute('font-size'),
                    top:el.getBoundingClientRect().top,bottom:el.getBoundingClientRect().bottom,
                    text:el.textContent}));
                  return {source, headerTop:header?.getBoundingClientRect().top};
                }""")
                assert len(spacing["source"])==2*len(d["segments"]),(a.code,"MOBILE_SOURCE_NAME_AND_AMOUNT_MUST_HAVE_SEPARATE_ROWS",spacing)
                assert all(z["font"]>=11 for z in spacing["source"]),(a.code,"MOBILE_MONEY_OR_SOURCE_LABEL_TOO_SMALL",spacing)
                assert all(spacing["source"][i]["bottom"]+0.7<spacing["source"][i+1]["top"]
                           for i in range(len(spacing["source"])-1)),(a.code,"MOBILE_SOURCES_OVERPRINT",spacing)
                assert spacing["source"][-1]["bottom"]+2<spacing["headerTop"],(a.code,"MOBILE_SOURCES_OVERLAP_STAGE_HEADER",spacing)
                total=float(d["facts"]["rev"]["yuan"])
                assert abs(source["total"]-total)<.001
                src=[x for x in source["nodes"] if x["role"]=="source"]
                cost=[x for x in source["nodes"] if x["role"]=="cost"]
                profit=[x for x in source["nodes"] if x["role"]=="profit"]
                trunk=[x for x in source["nodes"] if x["role"]=="total" and x["id"]=="revenue-total"]
                incoming=[x for x in source["ribbons"] if x["stage"]=="source-to-revenue"]
                outgoing=[x for x in source["ribbons"] if x["stage"]=="revenue-to-outcome"]
                assert len(src)==len(d["segments"]) and len(cost)==len(profit)==len(trunk)==1,(a.code,"MOBILE_THREE_STAGE_STRUCTURE",source)
                assert len(incoming)==len(src) and len(outgoing)==2*len(src),(a.code,"MOBILE_CONNECTED_RIBBONS",source)
                assert abs(trunk[0]["money"]-total)<.001
                assert abs(sum(x["money"] for x in incoming)-total)<.001
                assert abs(sum(x["money"] for x in outgoing)-total)<.001
                assert all(abs(x["h"]-x["money"]/source["scale"])<.001 for x in source["nodes"]),(a.code,"MOBILE_YUAN_NODE_SCALE")
                assert all(x["scale"]>0 and x["money"]>=0 and x["d"].startswith("M ") for x in source["ribbons"]),(a.code,"MOBILE_GENUINE_MONEY_PATH")
                for fig in ["pnl","cfo","cash","capital"]:
                    signed=page.locator(f'#chart-{fig} .native-mobile-finance .m-signed-bridge')
                    assert signed.count()>=2,(a.code,fig,"NO_SIGNED_CUMULATIVE_NATIVE_MOBILE_BRIDGE")
                    for item in signed.all():
                        data=item.evaluate("""(e)=>({a:+e.dataset.startYuan,b:+e.dataset.endYuan,
                            d:+e.dataset.deltaYuan,fill:e.getAttribute('fill'),width:+e.getAttribute('width')})""")
                        assert abs(data["a"]+data["d"]-data["b"])<.026,(a.code,fig,"SIGNED_SOURCE_CUMULATION_BROKEN",data)
                        assert data["width"]>=0,(a.code,fig,"SIGNED_WIDTH_INVALID")
                        if data["d"]<0 and fig!="capital":
                            assert data["fill"]=="#aa5949",(a.code,fig,"NEGATIVE_DELTA_WAS_DRAWN_POSITIVE_GREEN",data)
                balance=page.evaluate("""() => [...document.querySelectorAll('#chart-balance .native-mobile-finance .m-balance-component')].map(e=>({p:e.dataset.period,v:+e.dataset.amountYuan}))""")
                for tag,k in [("0","assets_prior"),("1","assets")]:
                    assert abs(sum(x["v"] for x in balance if x["p"]==tag)-float(d["facts"][k]["yuan"]))<.02,(a.code,"MOBILE_BALANCE_MUST_BE_TWO_DATE_EQUAL_TOTALS")
                assert page.locator("#chart-trend .native-mobile-finance .m-trend-pair").count()==6
                if a.code=="600276":
                    inn=page.locator("#chart-sector .native-mobile-finance .m-pharma-innovation")
                    assert inn.count()==1,(a.code,"NOT_REAL_NESTED_INNOVATIVE_DRUG_CONTRACT_SUBSET")
                    assert inn.get_attribute("data-operating-fact")=="innovative_drug_sales_100m"
                    mobile_contract=page.locator('#chart-sector .native-mobile-finance .m-pharma-contract')
                    assert mobile_contract.count()==3,(a.code,"PHONE_PHARMA_CONTRACT_TRIPLE_SOURCE_MISSING")
                    mobile_sum=sum((D(z.get_attribute("data-source-yuan")) for z in mobile_contract.all()),D(0))
                    assert mobile_sum==D(d["facts"]["rev"]["yuan"]),(a.code,"PHONE_PHARMA_CONTRACTS_NOT_RECONCILED")
                    source_num=float(d["facts"]["innovative_drug_sales_100m"]["yuan"])*1e8
                    assert abs(float(inn.get_attribute("data-subset-yuan"))-source_num)<.02
                    assert page.locator('#chart-capital .native-mobile-finance [data-capital-supplement="true"]').count()==1
                else:
                    assert "亿千瓦时" in page.locator("#chart-sector .native-mobile-finance").inner_text()
                    pwr=page.locator('#chart-sector .native-mobile-finance [data-source-fact="power_gen_100m_kwh"]')
                    assert pwr.count()==1,(a.code,"PHONE_POWER_SOURCE_ID_MISSING")
                    assert D(pwr.get_attribute("data-original-value"))==D(d["facts"]["power_gen_100m_kwh"]["yuan"]),(a.code,"PHONE_POWER_SOURCE_STALE")
            elif width==768:
                # Tablet is allowed to scroll a true original desktop
                # finance diagram, but a narrow 390px device is NOT.
                for plot in page.locator('.plot').all():
                    state=plot.evaluate("(x) => ({overflow:getComputedStyle(x).overflowX,scroll:x.scrollWidth,visible:x.clientWidth})")
                    assert state["visible"]<=width,(a.code,"TABLET_CHART_CONTAINMENT",state)
            q=page.locator("#chart-flow")
            assert q.locator(':scope > svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"]').count()==1
            assert q.locator('.native-mobile-finance svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"]').count()==1
            for kind in ["pnl","cfo","cash","balance"]:
                assert page.locator("#chart-"+kind+" > svg").count()==1
            geom=page.evaluate("""() => {
              const svg=document.querySelector('#chart-flow > svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"]');
              if(!svg)return null;
              return {
                total:+svg.getAttribute('data-revenue-yuan'),scale:+svg.getAttribute('data-scale-yuan-per-svg-unit'),
                nodes:[...svg.querySelectorAll('rect[data-node-role]')].map(n=>({id:n.getAttribute('data-node-id'),role:n.getAttribute('data-node-role'),money:+n.getAttribute('data-node-yuan'),h:+n.getAttribute('height')})),
                ribbons:[...svg.querySelectorAll('path[data-ribbon-yuan]')].map(p=>({money:+p.getAttribute('data-ribbon-yuan'),stage:p.getAttribute('data-stage'),scale:+p.getAttribute('data-scale-yuan-per-svg-unit'),d:p.getAttribute('d')}))};
            }""")
            assert geom and geom["total"]>0 and geom["scale"]>0,(a.code,"DESKTOP_SHARED_TOTAL_REVENUE_NOT_RENDERED")
            total=float(d["facts"]["rev"]["yuan"])
            costs=float(d["facts"]["cogs"]["yuan"])
            assert abs(geom["total"]-total)<.001,(a.code,"DESKTOP_WRONG_REVENUE_SOURCE")
            src=[x for x in geom["nodes"] if x["role"]=="source"]
            sink=[x for x in geom["nodes"] if x["role"] in ("cost","profit")]
            trunk=[x for x in geom["nodes"] if x["role"]=="total" and x["id"]=="revenue-total"]
            incoming=[x for x in geom["ribbons"] if x["stage"]=="source-to-revenue"]
            outgoing=[x for x in geom["ribbons"] if x["stage"]=="revenue-to-outcome"]
            assert len(src)==len(d["segments"]) and len(sink)==2 and len(trunk)==1,(a.code,"DESKTOP_CONNECTED_NODE_STRUCTURE")
            assert len(incoming)==len(src) and len(outgoing)==2*len(src),(a.code,"DESKTOP_SOURCE_OWN_COST_GP_PATHS")
            assert abs(sum(x["money"] for x in incoming)-total)<.001
            assert abs(sum(x["money"] for x in outgoing)-total)<.001
            assert abs(next(x["money"] for x in sink if x["role"]=="cost")-costs)<.001
            assert all(abs(x["h"]-x["money"]/geom["scale"])<.001 for x in geom["nodes"]),(a.code,"DESKTOP_ORIGINAL_YUAN_NODE_SCALE")
            assert all(x["d"].startswith("M ") and " C " in x["d"] and " L " in x["d"] and x["scale"]>0 for x in geom["ribbons"]),(a.code,"DESKTOP_NOT_REAL_CURVED_RIBBONS")
            # Full-size desktop must never hide sink labels behind nested
            # horizontal scrolling even if the body itself does not overflow.
            if width==1440:
                dimensions=page.evaluate("""() => [...document.querySelectorAll('.plot')].map(x=>({
                  id:x.id,visible:x.clientWidth,scroll:x.scrollWidth}))""")
                assert all(x["scroll"]<=x["visible"]+2 for x in dimensions),("DESKTOP_INNER_CLIP",dimensions)
                boxes=page.evaluate("""() => [...document.querySelectorAll('figure .plot > svg')].map(x=>({
                  w:x.viewBox.baseVal.width,
                  min:Math.min(...Array.from(x.querySelectorAll('text')).map(t=>t.getBBox().x)),
                  max:Math.max(...Array.from(x.querySelectorAll('text')).map(t=>t.getBBox().x+t.getBBox().width))
                }))""")
                assert all(z["min"]>=-1 and z["max"]<=z["w"]+2 for z in boxes),("SVG_TEXT_CLIP",boxes)
            page.screenshot(path=str(out/(a.code+"-"+str(width)+"-full.png")),full_page=True)
            for key in ["flow","sector","pnl","cfo","cash","balance"]:
                page.locator("#fig-"+key).screenshot(path=str(out/(a.code+"-"+str(width)+"-"+key+".png")))
            # Exported bytes must equal the current visible SVG at each viewport.
            visible_xml=page.evaluate("""() => {
                const f=document.querySelector('#fig-flow');
                const svg=[...f.querySelectorAll('svg')].find(el=>{
                    const r=el.getBoundingClientRect(),s=getComputedStyle(el);
                    return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';
                });
                return svg?new XMLSerializer().serializeToString(svg):null;
            }""")
            assert visible_xml,(a.code,width,"VISIBLE_FLOW_SVG_MISSING")
            with page.expect_download(timeout=10000) as dl:
                page.locator('button[data-export="flow"]').click()
            download=dl.value
            assert download.suggested_filename==a.code+"-2026H1-flow.svg"
            assert download.path().read_text(encoding="utf-8")==visible_xml,(a.code,width,"FLOW_EXPORT_NOT_VISIBLE_SVG")
            download.save_as(str(out/(a.code+"-flow-"+str(width)+".svg")))
            record.append({"width":width,"figures":8,"desktop_svg":8,"native_mobile_svg":8,"tables":8,"actual_money_geometry":"PASS","body_no_overflow":"PASS","actual_native_mobile_financial_figures_and_390_no_inner_scroll":"PASS" if width<=850 else "NOT_RELEVANT_THIS_WIDTH","svg_export":"PASS"})
            page.close()
        browser.close()
    assert not errors,errors
    data={"issuer":a.code,"html_sha256":hashlib.sha256(file.read_bytes()).hexdigest(),"actual_3_viewport_checks":record,
          "all_eight_figures_visible":"PASS","all_eight_390px_native_money_visuals_readable_and_source_reconciled":"PASS","source_nodes_sinks_ribbons_exact_svg_geometric_proportions":"PASS",
          "CJK_FONTS_RUNNER_INSTALLED":"NOT_CHECKED_LOCAL_FONT_INSTALLATION","CJK_text_geometry":"MEASURED_ACTUAL_RENDERED_GLYPHS","human_editor":"NOT_CHECKED"}
    (out/"result.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("ACTUAL_CHROMIUM_TWO_SECTOR_QA_PASS",a.code,"screenshots",len(list(out.glob("*.png"))),"views",record)
if __name__=="__main__":
    main()
    # Existing build-two-sectors workflow installs PDF/browser/CJK dependencies
    # and calls 600276 last; extend that actual job rather than require a new
    # workflow credential or silently leave the full-library checks inactive.
    import os
    if os.environ.get('GITHUB_ACTIONS')=='true' and '--code' in sys.argv and sys.argv[sys.argv.index('--code')+1]=='600276':
        from delivery_quality_suite import run
        run(ROOT/'research/issuers/600276/visual-qa/full-library')
