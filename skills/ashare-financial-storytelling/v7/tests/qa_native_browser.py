#!/usr/bin/env python3
"""Offline CJK 1440/768/390 QA for original-yuan native optical art."""
import argparse,hashlib,json,re
from pathlib import Path
from playwright.sync_api import sync_playwright

ap=argparse.ArgumentParser()
ap.add_argument("--out",default="optical-native-visual-qa")
ap.add_argument("--codes",default="300394,300502",help="Issuer source ledgers to run; defaults to legacy two real-source incumbents")
args=ap.parse_args()
codes=[x.strip() for x in args.codes.split(",") if x.strip()]
if not codes or len(set(codes))!=len(codes) or any(x not in ("300308","300394","300502") for x in codes):
    raise ValueError("UNSUPPORTED_OR_DUPLICATE_OPTICAL_SOURCE_CENSUS")
out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
ROOT=Path(__file__).resolve().parents[4]
records=[]
with sync_playwright() as p:
    browser=p.chromium.launch(args=["--no-sandbox"])
    for code in codes:
        file=ROOT/"public"/(code+".html")
        sha=hashlib.sha256(file.read_bytes()).hexdigest()
        for width in (1440,768,390):
            page=browser.new_page(viewport={"width":width,"height":900})
            page.goto(file.resolve().as_uri(),wait_until="load")
            if code=="300308":
                assert page.locator("aside.disclosure-conflict").count()==1,(code,"REAL_P139_PRINTED_DUPLICATE_VALUE_CONFLICT_HIDDEN")
                assert "422,649,612.97" in page.locator("aside.disclosure-conflict").inner_text()
                assert "422,649,613.97" in page.locator("aside.disclosure-conflict").inner_text()
                assert "独立第二名人类研究分析师" in page.content(),(code,"FALSE_HUMAN_REVIEW_CLAIM_BOUNDARY_MISSING")
            if code=="300308":
                focus=page.evaluate("""() => {
                  const e=document.querySelector('.cash-feature-graph');
                  const n=e?.querySelector('.bar-net'),c=e?.querySelector('.bar-cfo');
                  if(!e||!n||!c)return null;
                  return {net:+e.dataset.netExactYuan,cfo:+e.dataset.cfoExactYuan,
                    capex:+e.dataset.cashActualCapexYuan,base:+e.dataset.barBaseYuan,
                    netWidth:parseFloat(n.getAttribute('style').match(/width:([0-9.]+)%/)[1]),
                    cfoWidth:parseFloat(c.getAttribute('style').match(/width:([0-9.]+)%/)[1]),
                    cfoRendered:c.getBoundingClientRect().width,
                    actualBarTrack:c.parentElement.getBoundingClientRect().width,
                    left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right};
                }""")
                assert focus and focus["net"]==14733426763.13 and focus["cfo"]==1799674832.02,(code,"CASH_LEAD_SOURCE_AMOUNT_WRONG",focus)
                assert focus["capex"]==4802161195.37 and focus["base"]==focus["net"],(code,"CASH_LEAD_CASH_CAPEX_AS_STOCK")
                assert abs(focus["netWidth"]-100.0)<1e-5
                assert abs(focus["cfoWidth"]-focus["cfo"]/focus["net"]*100)<1e-6,(code,"CASH_LEAD_SOURCE_RAW_CSS_PERCENT_CONTRADICTS_YUAN")
                assert focus["actualBarTrack"]>100 and abs(focus["cfoRendered"]/focus["actualBarTrack"]*100-focus["cfoWidth"])<0.25,(code,width,"CASH_LEAD_ACTUAL_BROWSER_PHYSICAL_BAR_LENGTH_WRONG",focus)
                assert 0<=focus["left"] and focus["right"]<=width+2,(code,width,"EDITORIAL_FOCUS_MOBILE_CROPPED")
            if code in ("300394","300502"):
                import sys
                from decimal import Decimal as D
                sys.path.insert(0,str(ROOT/"skills/ashare-financial-storytelling/v7/engine"))
                from quantified_optical_decision import CONFIG, decision_values
                fixture=(ROOT/"skills/ashare-financial-storytelling/v7/engine/sample-ledger.json"
                         if code=="300394" else
                         ROOT/"skills/ashare-financial-storytelling/v7/examples/xinyisheng-2026H1-ledger.json")
                ledger=json.loads(fixture.read_text(encoding="utf-8"))
                expected=decision_values(ledger)
                decision=page.locator("#quantified-decision")
                assert decision.count()==1 and decision.is_visible(),(code,width,"READER_RESEARCH_DECISION_NOT_VISIBLE")
                assert decision.get_attribute("data-original-pdf-sha256")==ledger["document"]["source_sha256"]
                assert decision.get_attribute("data-accounting-not-causal")=="true"
                source=decision.evaluate("""node=>({
                  facts:[...node.querySelectorAll('tr[data-fact-id]')].map(el=>({...el.dataset})),
                  derived:[...node.querySelectorAll('.optical-decision-metric')].map(el=>({...el.dataset})),
                  bbox:(()=>{const r=node.getBoundingClientRect();return {left:r.left,right:r.right,width:r.width}})(),
                  cards:[...node.querySelectorAll('.optical-decision-metric')].map(el=>{
                    const r=el.getBoundingClientRect();
                    return {left:r.left,right:r.right,top:r.top,bottom:r.bottom};
                  }),
                  font:+getComputedStyle(node.querySelector('.optical-decision-lead')).fontSize.replace('px','')
                })""")
                assert len(source["facts"])==8,(code,width,"MISSING_EXACT_ORIGINAL_EVIDENCE_FACTS")
                assert len(source["derived"])==3,(code,width,"MISSING_SOURCE_DERIVED_DECISION")
                for raw in source["facts"]:
                    key=raw["factId"]
                    fact=ledger["facts"][key]
                    spec=next(z for z in CONFIG[code] if z[0]==key)
                    assert D(raw["originalValue"])==D(fact["amount"]),(code,width,key,"DECISION_PUBLISHED_MONEY_DRIFT")
                    assert raw["period"]==spec[1] and raw["statementKind"]==spec[2]
                    assert raw["sourceUnit"]==spec[3] and int(raw["physicalPage"])==fact["page"]
                derived={z["derivedKey"]:D(z["derivedRatio"]) for z in source["derived"]}
                assert derived==dict((k,v) for k,_,v in expected["metrics"]),(code,width,"RESEARCH_DECISION_FORMULA_DRIFT")
                assert source["bbox"]["width"]>200 and source["bbox"]["left"]>=-1 and source["bbox"]["right"]<=width+2,(code,width,"QUANTIFIED_EDITORIAL_CARD_OFFSCREEN")
                assert source["font"]>=14,(code,width,"QUANTIFIED_DECISION_COPY_TOO_SMALL")
                if width==390:
                    boxes=source["cards"]
                    assert all(box["left"]>=source["bbox"]["left"]-1 and box["right"]<=source["bbox"]["right"]+1 for box in boxes)
                    assert all(boxes[i]["bottom"]<=boxes[i+1]["top"]+1 for i in range(2)),(code,width,"MOBILE_RESEARCH_METRICS_OVERPRINT")
                else:
                    assert all(x["right"]<=source["bbox"]["right"]+1 for x in source["cards"])
                assert "NOT_CHECKED" in decision.inner_text(),(code,width,"FALSE_INDEPENDENT_REVIEW_CLAIM")
                decision.screenshot(path=str(out/f"{code}_decision_{width}.png"),animations="disabled")
            n=page.locator("figure.has-native-finance").count()
            assert n>=9,(code,width,"MISSING_MONEY_NATIVE_FIGURES",n)
            assert page.locator(".hero-svg").count()==1,(code,"DESKTOP_ORIGINAL_LOST")
            assert page.evaluate("document.documentElement.scrollWidth")<=width+1,(code,width,"ROOT_OVERFLOW")
            if code in ("300394","300502","300308"):
                graph=page.evaluate("""() => {
                  const selector=window.innerWidth>900
                    ? '.chart-shell .hero-svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"]'
                    : '.native-finance svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"]';
                  const s=document.querySelector(selector);
                  if(!s)return null;
                  return {total:+s.getAttribute('data-revenue-yuan'),
                    boxes:[...s.querySelectorAll('rect[data-node-role]')].map(e=>({id:e.getAttribute('data-node-id'),role:e.getAttribute('data-node-role'),yuan:+e.getAttribute('data-node-yuan')})),
                    ribbons:[...s.querySelectorAll('path[data-ribbon-yuan]')].map(e=>({yuan:+e.getAttribute('data-ribbon-yuan'),stage:e.getAttribute('data-stage'),scale:+e.getAttribute('data-scale-yuan-per-svg-unit')})),
                    right:s.getBoundingClientRect().right,width:s.getBoundingClientRect().width,
                    placement:s.getAttribute('data-editorial-placement'),
                    repeatedHeader:[...s.querySelectorAll('text')].some(t=>t.textContent.includes('业务收入如何形成真实披露的成本与毛利')),
                    clippedLabels:[...s.querySelectorAll('text')].filter(t=>{
                      const v=t.getBoundingClientRect(),box=s.getBoundingClientRect();
                      return v.width>0 && (v.left<box.left-2||v.right>box.right+2||v.top<box.top-2||v.bottom>box.bottom+2);
                    }).map(t=>t.textContent)};
                }""")
                assert graph and graph["width"]>200 and graph["right"]<=width+3,(code,width,"UNIFIED_FLOW_CLIPPED_OR_MISSING",graph)
                assert graph["placement"]=="embedded-article" and not graph["repeatedHeader"],(code,width,"DUPLICATED_OUTER_AND_INNER_HEADLINE")
                assert not graph["clippedLabels"],(code,width,"SVG_EDITORIAL_TEXT_CLIPPED",graph["clippedLabels"])
                srcs=[x for x in graph["ribbons"] if x["stage"]=="source-to-revenue"]
                sinks=[x for x in graph["ribbons"] if x["stage"]=="revenue-to-outcome"]
                assert len(srcs)>=2 and len(sinks)==2*len(srcs),(code,width,"NOT_TRUE_CONNECTED_SANKEY")
                assert abs(sum(x["yuan"] for x in srcs)-graph["total"])<.001
                assert abs(sum(x["yuan"] for x in sinks)-graph["total"])<.001
                assert all(x["scale"]>0 and x["yuan"]>=0 for x in graph["ribbons"])
                assert len([x for x in graph["boxes"] if x["role"]=="total" and x["id"]=="revenue-total" and abs(x["yuan"]-graph["total"])<.001])==1
            else:
                graph=page.evaluate("""() => {
                  const s=document.querySelector('.native-money-svg');
                  return {sources:[...s.querySelectorAll('.native-money-source')].map(x=>[+x.dataset.exactYuan,+x.getAttribute('width')]),
                  sinks:[...s.querySelectorAll('.native-money-sink')].map(x=>[+x.dataset.exactYuan,+x.getAttribute('width')]),
                  ribbons:[...s.querySelectorAll('.native-money-ribbon')].map(x=>({yuan:+x.dataset.exactYuan,d:x.getAttribute('d')}))};
                }""")
                rev=sum(x[0] for x in graph["sources"])
                assert abs(sum(x[0] for x in graph["sinks"])-rev)<.001
                assert abs(sum(x["yuan"] for x in graph["ribbons"])-rev)<.001
                for value,width_svg in graph["sources"]+graph["sinks"]:
                    assert abs(width_svg-value/rev*302)<1e-7,(code,"NODE_REAL_MONEY_AREA")
                for edge in graph["ribbons"]:
                    m=re.match(r"M([0-9.]+),65 C.*?L([0-9.]+),276 C([0-9.]+),200 [0-9.]+,130 ([0-9.]+),65 Z",edge["d"])
                    assert m,(code,"INVALID_RIBBON_PATH",edge["d"])
                    assert abs(float(m.group(4))-float(m.group(1))-edge["yuan"]/rev*302)<1e-6,(code,"FALSE_RIBBON_AREA")
            signed=page.evaluate("""() => [...document.querySelectorAll('.native-signed-svg')].map(svg=>{
              const all=[...svg.querySelectorAll('rect.native-signed-money')];
              const view=svg.viewBox.baseVal;
              const steps=all.map(el=>({kind:el.dataset.kind,step:+el.dataset.step,
                amount:+el.dataset.signedYuan,cumulative:+el.dataset.cumulativeYuan,
                width:+el.getAttribute('width'),fill:el.getAttribute('fill')}));
              const texts=[...svg.querySelectorAll('text')].map(t=>{
                const b=t.getBBox();return {x:b.x,y:b.y,right:b.x+b.width,bottom:b.y+b.height};});
              return {steps,texts,view:[view.width,view.height]};
            })""")
            assert len(signed)>=(4 if code=="300308" else 5),(code,width,"MISSING_SIGNED_SOURCE_WATERFALLS")
            if code=="300308":
                # The original optical source already has accurate signed money;
                # now verify FIGURE 03's two editions use the SAME typed P&L
                # with 7 precise actual-yuan stages, original 184-page SHA,
                # honest unallocated operating difference, and no fake width.
                from decimal import Decimal as D
                both=page.evaluate("""() => [...document.querySelectorAll('figure.exhibit')].flatMap(f=>[...f.querySelectorAll('svg[data-signed-statement-grammar="FINANCIALS_TYPED_FULL_PNL_SIGNED_V1"]')]).map(el=>{
                  let r=el.getBoundingClientRect(),vb=el.viewBox.baseVal,
                  labels=[...el.querySelectorAll('text')].map(t=>{let b=t.getBBox();return {text:t.textContent,left:b.x,right:b.x+b.width,bottom:b.y+b.height};});
                  return {layout:el.dataset.layout,source:el.dataset.originalPdfSha256,
                    gross:el.dataset.startGrossYuan,net:el.dataset.endNetYuan,
                    visible:r.width>2,overflows:r.left< -2||r.right>innerWidth+2,
                    clipped:labels.filter(z=>z.left< -2||z.right>vb.width+2||z.bottom>vb.height+2),
                    rows:[...el.querySelectorAll('rect.unified-signed-statement-step')].map(n=>({
                      name:n.dataset.stageId,before:n.dataset.beforeYuan,
                      delta:n.dataset.signedYuan,after:n.dataset.afterYuan,
                      width:n.getAttribute('width'),scale:n.dataset.moneyScaleYuanPerUnit,
                      physical:n.dataset.physicalPages,ids:n.dataset.sourceFactIds,
                      proof:n.dataset.moneyProvenance}))};
                })""")
                assert len(both)==2,(code,width,"MISSING_SHARED_OPTICAL_PNL_DESKTOP_PHONE")
                assert {z["layout"] for z in both}=={"native-330","editorial-1040"}
                for art in both:
                    assert art["source"]=="e0ecd7c365c65e90b1fa4b4616ba3f4649449d64451e0ba0b1b78ba9ce3170bf"
                    assert D(art["gross"])==D("19323173654.59") and D(art["net"])==D("14733426763.13")
                    assert not art["clipped"],(code,width,art["layout"],"SOURCE_PNL_CJK_LABEL_CLIPPED",art["clipped"])
                    assert len(art["rows"])==7,(code,width,"SHARED_FULL_PNL_SEVEN_STEP_MISSING")
                    assert any(row["proof"]=="DERIVED_UNATTRIBUTED_GROUP_OPERATING_NET_DIFFERENCE" for row in art["rows"]),(code,width,"FAKE_OPERATING_CAUSAL_DETAIL")
                    for row in art["rows"]:
                        assert D(row["before"])+D(row["delta"])==D(row["after"])
                        assert abs(D(row["width"])-abs(D(row["delta"]))/D(row["scale"]))<D(".000001"),(code,width,row,"FALSE_MONEY_GEOMETRY")
                        assert row["physical"] and row["ids"]
                active=next(z for z in both if z["layout"]==("native-330" if width<=900 else "editorial-1040"))
                inactive=next(z for z in both if z is not active)
                assert active["visible"] and not inactive["visible"],(code,width,"SHARED_NATIVE_PNL_NOT_GENUINE_MOBILE")
                assert not active["overflows"],(code,width,"SHARED_PNL_HORIZONTALLY_CROPPED")

            for panel in signed:
                st=panel["steps"]
                ratios=[z["width"]/abs(z["amount"]) for z in st if abs(z["amount"])>0]
                assert ratios and max(ratios)-min(ratios)<=max(ratios)*0.000005,(code,width,"SIGNED_GEOMETRY_VALUE_SCALE_DRIFT")
                prev=None
                for z in st:
                    if z["kind"]=="start":
                        assert abs(z["cumulative"]-z["amount"])<0.01
                    elif z["kind"]=="total":
                        assert abs(z["cumulative"]-prev)<0.01
                    else:
                        assert abs(prev+z["amount"]-z["cumulative"])<0.01,(code,width,"SIGNED_CASH_WATERFALL_ACCOUNTING_BROKEN")
                        assert z["fill"]==("#087e69" if z["amount"]>=0 else "#af745b"),(code,width,"WRONG_FINANCIAL_SIGN_COLOR")
                    prev=z["cumulative"]
                assert all(t["x"]>=-2 and t["right"]<=panel["view"][0]+2 and t["y"]>=-2 and t["bottom"]<=panel["view"][1]+2 for t in panel["texts"]),(code,width,"CJK_SVG_TEXT_BBOX_CLIPPED",panel["texts"])
            if width in (768,390):
                figures=page.evaluate("""() => [...document.querySelectorAll('figure.has-native-finance')].map(f=>{
                  const n=f.querySelector('.native-finance'),old=f.querySelector('.chart-shell'),svg=n.querySelector('svg');
                  const graphic=svg||n;const r=graphic.getBoundingClientRect();
                  return {active:getComputedStyle(n).display!=='none',oldHidden:getComputedStyle(old).display==='none',
                    inner:n.scrollWidth,visible:n.clientWidth,width:r.width,
                    clipped:r.right>f.getBoundingClientRect().right+2};
                })""")
                assert all(z["active"] and z["oldHidden"] and z["inner"]<=z["visible"]+2 and z["width"]>220 and not z["clipped"] for z in figures),(code,width,"REAL_NATIVE_FIGURE_CLIP",figures)
            if width==390 and page.locator("button.native-source-row[data-source-key]").count()>0:
                source_row=page.locator("button.native-source-row[data-source-key]").first
                assert source_row.count()==1,(code,"MISSING_ACCESSIBLE_SOURCE_FILTER")
                original_d=page.locator("path.native-money-ribbon").first.get_attribute("d")
                source_row.click()
                assert page.locator("path.native-money-ribbon.is-selected").count()==2,(code,"SELECTED_SOURCE_PATHS_NOT_HIGHLIGHTED")
                assert page.locator("path.native-money-ribbon.is-muted").count()==len(graph["ribbons"])-2,(code,"UNSELECTED_SOURCE_PATHS_NOT_DIMMED")
                assert page.locator("button.native-source-row[aria-pressed=true]").count()==1,(code,"ACCESSIBLE_PRESS_STATE_MISSING")
                source_row.click()
                assert page.locator("path.native-money-ribbon.is-muted").count()==0 and page.locator("path.native-money-ribbon.is-selected").count()==0
                assert page.locator("path.native-money-ribbon").first.get_attribute("d")==original_d,(code,"INTERACTION_CHANGED_ORIGINAL_AMOUNT_WIDTH")
            if width==1440:
                assert page.locator(".chart-shell .hero-svg:visible").count()==1
                if code in ("300394","300502"):
                    assert page.locator('.chart-shell .hero-svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"]').count()==1
            visible_xml=page.evaluate("""() => {
                const f=document.querySelector('figure.exhibit');
                const svg=[...f.querySelectorAll('svg')].find(el=>{
                    const b=el.getBoundingClientRect(),s=getComputedStyle(el);
                    return b.width>0&&b.height>0&&s.display!=='none'&&s.visibility!=='hidden';
                });
                return svg?new XMLSerializer().serializeToString(svg):null;
            }""")
            assert visible_xml and "<svg" in visible_xml,(code,width,"VISIBLE_SVG_MISSING")
            with page.expect_download(timeout=10000) as event:
                page.locator("figure.exhibit .svg-save").first.click()
            got=event.value
            assert got.suggested_filename.endswith(".svg")
            assert got.path().read_text(encoding="utf-8")==visible_xml,(code,width,"EXPORTED_HIDDEN_DESKTOP_SVG")
            img=out/(f"{code}_{width}.png");page.screenshot(path=str(img),full_page=True)
            if code=="300308" and width in (1440,768,390):
                page.locator(".cash-editorial-focus").screenshot(path=str(out/f"{code}_cashfocus_{width}.png"))
            page.locator("figure.exhibit").first.screenshot(path=str(out/f"{code}_figure01_{width}.png"))
            if width==390:
                for chart_idx in (2,5,8):
                    page.locator("figure.exhibit").nth(chart_idx).screenshot(path=str(out/f"{code}_figure{chart_idx+1:02d}_{width}.png"))
            records.append({"issuer":code,"width":width,"figures":n,"money_area":"PASS","signed_accounting_and_svg_geometry":"PASS","native_mobile_finance_no_inner_scroll":"PASS" if width in (390,768) else "NOT_MOBILE","sha256":sha,"screenshot_sha256":hashlib.sha256(img.read_bytes()).hexdigest()})
            page.close()
    browser.close()
(out/"result.json").write_text(json.dumps({"cases":records,"second_human_review":"NOT_CHECKED"},ensure_ascii=False,indent=2)+"\n")
assert len(records)==len(codes)*3
print("OPTICAL_NATIVE_MOBILE_REAL_CJK_SOURCE_FINANCE_3_SCREEN_PER_ISSUER_PASS",codes,len(records))
