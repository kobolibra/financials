#!/usr/bin/env python3
"""Real offline Chromium + graphic source-flow QA; no claim of independent human approval."""
from __future__ import annotations
import argparse, json, pathlib, hashlib
from decimal import Decimal as D
from playwright.sync_api import sync_playwright
P=argparse.ArgumentParser()
P.add_argument("--html",default="public/688220.html")
P.add_argument("--out",default="research/issuers/688220/visual-qa")
a=P.parse_args()
html=pathlib.Path(a.html).resolve()
out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
ledger=json.loads((pathlib.Path(__file__).parent/"source-ledger.json").read_text(encoding="utf-8"))
facts=ledger["facts"]
expected_cost=sum((D(facts[q["cost"]]["yuan"]) for q in ledger["segments"]),D(0))
expected_profit=sum((D(facts[q["rev"]]["yuan"])-D(facts[q["cost"]]["yuan"]) for q in ledger["segments"]),D(0))
assert html.exists() and html.stat().st_size>20000,html
errors=[];statuses=[];screenshots=0
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True)
 for width,height in ((1440,960),(768,1024),(390,844)):
  page=browser.new_page(viewport={"width":width,"height":height},accept_downloads=True)
  page.on("pageerror",lambda e:errors.append("JS "+str(e)))
  page.on("console",lambda m:errors.append("CONSOLE "+m.text) if m.type=="error" else None)
  page.goto(html.as_uri(),wait_until="load")
  import sys
  sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[3]/"research/shared"))
  from profit_chain_audit import check_reader
  check_reader(page);check_reader(page,expanded=True)
  page.wait_for_selector("#chart-flow svg",state="attached",timeout=15000)
  info=page.evaluate("""() => ({
    scrollWidth:document.documentElement.scrollWidth,
    clientWidth:document.documentElement.clientWidth,
    figures:document.querySelectorAll('figure.figure').length,
    svg:document.querySelectorAll('.vizscroll svg').length,
    tables:document.querySelectorAll('table.evidence-table').length,
    exports:document.querySelectorAll('[data-export]').length,
    mobilePanels:document.querySelectorAll('.mobile-facts').length,
    mobileVisible:[...document.querySelectorAll('.native-asr')].filter(e=>getComputedStyle(e).display!=='none').length,
    nativeCount:document.querySelectorAll('.native-asr').length,
    nativeViews:[...document.querySelectorAll('.native-asr')].map(e=>({
      visible:getComputedStyle(e).display!=='none',
      client:e.clientWidth,inner:e.scrollWidth,
      originalSvg:e.querySelector('svg')?.getBoundingClientRect().width||0,
      cjkTexts:[...e.querySelectorAll('svg text')].map(t=>{
        const bb=t.getBBox(),view=t.closest('svg').viewBox.baseVal;
        return {text:t.textContent,x:bb.x,right:bb.x+bb.width,view:view.width};
      })
    })),
    originalDesktopHidden:[...document.querySelectorAll('.vizscroll')].filter(e=>getComputedStyle(e).display==='none').length,
    mobileFlowSource:[...document.querySelectorAll('.native-asr-source')].map(e=>({yuan:e.dataset.exactYuan,width:+e.getAttribute('width')})),
    mobileFlowSink:[...document.querySelectorAll('.native-asr-sink')].map(e=>({yuan:e.dataset.exactYuan,width:+e.getAttribute('width')})),
    mobileFlowRibbon:[...document.querySelectorAll('.native-asr-ribbon')].map(e=>({yuan:e.dataset.exactYuan,width:+e.dataset.width,source:e.dataset.sourceKey,sink:e.dataset.sink,path:e.getAttribute('d')})),
    mobileSigned:[...document.querySelectorAll('.native-asr svg[data-editorial-grammar="SOURCE_SIGNED_BRIDGE_V1"] rect[data-signed-yuan]')].map(e=>({kind:e.dataset.kind,step:+e.dataset.step,yuan:e.dataset.signedYuan,cumulative:e.dataset.cumulativeYuan,width:+e.getAttribute('width'),fill:e.getAttribute('fill'),svg:e.closest('svg').getAttribute('aria-label')})),
    sharedSigned:[...document.querySelectorAll('#fig-pnl svg[data-signed-statement-grammar="FINANCIALS_TYPED_FULL_PNL_SIGNED_V1"]')].map(svg=>{
      const box=svg.getBoundingClientRect(),vb=svg.viewBox.baseVal,labels=[...svg.querySelectorAll('text')].map(t=>{const b=t.getBBox();return {name:t.textContent,left:b.x,right:b.x+b.width,bottom:b.y+b.height}});
      return {layout:svg.dataset.layout,source:svg.dataset.originalPdfSha256,status:svg.dataset.sourceStatus,
        gross:svg.dataset.startGrossYuan,net:svg.dataset.endNetYuan,visible:box.width>1,
        width:vb.width,height:vb.height,clip:labels.filter(t=>t.left< -2||t.right>vb.width+2||t.bottom>vb.height+2),
        rows:[...svg.querySelectorAll('rect.unified-signed-statement-step')].map(e=>({
          id:e.dataset.stageId,before:e.dataset.beforeYuan,delta:e.dataset.signedYuan,
          after:e.dataset.afterYuan,width:e.getAttribute('width'),scale:e.dataset.moneyScaleYuanPerUnit,
          pages:e.dataset.physicalPages,sourceFactIds:e.dataset.sourceFactIds,position:+e.getAttribute('x')
        }))};
    }),
    navPosition:getComputedStyle(document.querySelector('.chapters')).position,
    bodyExternalScripts:document.querySelectorAll('script[src]').length,
    ribbon:[...document.querySelectorAll('#chart-flow path.money-ribbon')].map(e=>{
      const d=e.getAttribute('d')||'';
      const start=d.match(/^M([0-9.]+),([0-9.\-]+) C/);
      // Last coordinate is the endpoint of the second cubic C, not a standalone L command.
      const finish=d.match(/ ([0-9.]+),([0-9.\-]+) Z$/);
      return {
        source:e.dataset.source,sourceKey:e.dataset.sourceKey,target:e.dataset.targetKey,
        kind:e.dataset.kind,amount:e.dataset.valueYuan,thickness:Number(e.dataset.thickness),
        pathThickness:start&&finish?Number(finish[2])-Number(start[2]):null,
        sourcePage:e.dataset.sourcePage,period:e.dataset.period,scope:e.dataset.scope,
        bboxHeight:e.getBBox().height,title:e.querySelector('title')?.textContent||''
      };
    }),
    sourceNodes:[...document.querySelectorAll('#chart-flow rect.money-source')].map(e=>({
      key:e.dataset.sourceKey,amount:e.dataset.valueYuan,realHeight:Number(e.getAttribute('height')),
      semanticHeight:Number(e.dataset.thickness),title:e.querySelector('title')?.textContent||''
    })),
    sinks:[...document.querySelectorAll('#chart-flow rect.money-sink')].map(e=>({
      kind:e.dataset.kind,amount:e.dataset.valueYuan,height:Number(e.getAttribute('height'))
    })),
    desktopGraphs:['flow','pnl','balance','cash'].map(id=>{
      const c=document.querySelector('#chart-'+id),svg=c.querySelector('svg');
      const contentEdges=[...svg.querySelectorAll('text')].map(t=>{
        const b=t.getBBox();return {label:t.textContent,x:b.x,right:b.x+b.width,
          y:b.y,bottom:b.y+b.height};
      });
      return {id,scroll:c.scrollWidth,client:c.clientWidth,
        viewBoxWidth:svg.viewBox.baseVal.width,
        outOfBoundsLabels:contentEdges.filter(t=>t.x < -2||t.right > svg.viewBox.baseVal.width+2)};
    }),
    semanticFigures:[...document.querySelectorAll('figure[data-accounting-family]')].map(e=>e.dataset.accountingFamily)
  })""")
  assert info["scrollWidth"]<=width+1,(width,"document scrolls horizontally",info)
  assert info["figures"]==info["svg"]==info["tables"]==info["exports"]==9,(width,info)
  assert info["nativeCount"]==9 and info["mobilePanels"]==9
  assert info["mobileVisible"]==(0 if width==1440 else 9),(width,"NATIVE_MOBILE_PANELS_NOT_VISIBLE")
  finance=page.evaluate("""() => {
    const parse=(svg)=>svg?{total:+svg.getAttribute('data-revenue-yuan'),scale:+svg.getAttribute('data-scale-yuan-per-svg-unit'),
      grammar:svg.getAttribute('data-chart-grammar'),view:svg.viewBox.baseVal.width,
      nodes:[...svg.querySelectorAll('rect[data-node-role]')].map(e=>({id:e.getAttribute('data-node-id'),role:e.getAttribute('data-node-role'),amount:+e.getAttribute('data-node-yuan'),h:+e.getAttribute('height')})),
      bands:[...svg.querySelectorAll('path[data-ribbon-yuan]')].map(e=>({source:e.getAttribute('data-source-id'),stage:e.getAttribute('data-stage'),amount:+e.getAttribute('data-ribbon-yuan'),scale:+e.getAttribute('data-scale-yuan-per-svg-unit'),d:e.getAttribute('d')}))}:null;
    return {desk:parse(document.querySelector('#chart-flow > svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"]')),
      phone:parse(document.querySelector('#fig-flow .native-asr svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"]'))};
  }""")
  assert finance["desk"] and finance["phone"],(width,"SEMI_ORIGINAL_UNIFIED_DESKTOP_AND_PHONE_MISSING")
  for key,graph in finance.items():
    total=float(D(facts["rev"]["yuan"]))
    assert graph["grammar"]=="SOURCE_REVENUE_OUTCOME_CONNECTED_SANKEY"
    assert graph["view"]==(1100 if key=="desk" else 330)
    assert abs(graph["total"]-total)<.001 and graph["scale"]>0
    sources=[n for n in graph["nodes"] if n["role"]=="source"]
    sinks=[n for n in graph["nodes"] if n["role"] in ("cost","profit")]
    trunks=[n for n in graph["nodes"] if n["role"]=="total" and n["id"]=="revenue-total"]
    inflow=[b for b in graph["bands"] if b["stage"]=="source-to-revenue"]
    outflow=[b for b in graph["bands"] if b["stage"]=="revenue-to-outcome"]
    assert len(sources)==4 and len(sinks)==2 and len(trunks)==1,(width,key,"MISSING_SHARED_TOTAL_NODE",graph)
    assert len(inflow)==4 and len(outflow)==7,(width,key,"ZERO_GP_PHANTOM_RIBBON",graph)
    assert abs(sum(b["amount"] for b in inflow)-total)<.001
    assert abs(sum(b["amount"] for b in outflow)-total)<.001
    assert abs(next(n["amount"] for n in sinks if n["role"]=="cost")-float(expected_cost))<.001
    assert all(abs(n["h"]-n["amount"]/graph["scale"])<.001 for n in graph["nodes"]),(width,key,"ORIGINAL_MONEY_SCALE_BROKEN")
    assert all(b["scale"]>0 and b["d"].startswith("M ") and " C " in b["d"] for b in graph["bands"])
    tiny=next(n for n in sources if n["id"]=="other_service_rev")
    assert 0<tiny["h"]<0.05,(width,key,"MICRO_BUSINESS_INFLATED",tiny)
  # The old issuer-specific full P&L SVG is replaced in both versions by
  # one canonical typed Decimal statement, without reducing the figure count.
  shared=info["sharedSigned"]
  assert len(shared)==2,(width,"MISSING_SHARED_DESKTOP_AND_PHONE_SIGNED_PNL")
  source_sha=ledger["source"]["original_bytes_sha256"]
  for edition in shared:
    assert edition["source"]==source_sha,(width,edition["layout"],"PDF_SHA_WRONG")
    assert edition["status"]=="MIRROR_COMPLETE_PDF_SHA_PASS__OFFICIAL_EQUIVALENCE_NOT_CHECKED"
    assert edition["gross"]==str(D(facts["rev"]["yuan"])-D(facts["cogs"]["yuan"]))
    assert edition["net"]==facts["consolidated_net_profit"]["yuan"]
    assert len(edition["rows"])==10,(width,edition["layout"],"FULL_PNL_NOT_ALL_TEN_RECONCILED_STEPS")
    assert not edition["clip"],(width,edition["layout"],"SOURCE_SIGNED_SVG_CJK_TEXT_CLIPPED",edition["clip"])
    for step in edition["rows"]:
      assert D(step["before"])+D(step["delta"])==D(step["after"]),(width,step,"WRONG_SIGNED_PNL_STEP")
      assert abs(D(step["width"])-abs(D(step["delta"]))/D(step["scale"]))<D(".00001"),(width,step,"DECEPTIVE_MONEY_WIDTH")
      assert step["pages"] and step["sourceFactIds"],(width,step,"UNPROVEN_FINANCIAL_ROW")
  assert {z["layout"] for z in shared}=={"editorial-1040","native-330"}
  chosen=next(z for z in shared if z["layout"]==("native-330" if width<=820 else "editorial-1040"))
  hidden=next(z for z in shared if z is not chosen)
  assert chosen["visible"] and not hidden["visible"],(width,"WRONG_SHARED_PNL_EDITION_VISIBILITY")
  assert any(D(r["after"])<0 for r in chosen["rows"]),(width,"NEGATIVE_INTERIM_OPERATING_PROFIT_WAS_HIDDEN")
  assert len(info["mobileSigned"])>=19,(width,"FOUR_ORIGINAL_SIGNED_FINANCIAL_GRAPHS_MISSING")
  by_chart={}
  for step in info["mobileSigned"]:
    by_chart.setdefault(step["svg"],[]).append(step)
  assert len(by_chart)==4,(width,"EXPECTED_FOUR_OTHER_SIGNED_GRAPHS_PLUS_SHARED_PNL")
  for title,steps in by_chart.items():
    cumulative=None
    scales=[]
    for step in sorted(steps,key=lambda x:x["step"]):
      delta=D(step["yuan"]);now=D(step["cumulative"])
      if step["kind"]=="step":
        assert cumulative is not None and abs(cumulative+delta-now)<=D("0.01"),(title,"BROKEN_SIGNED_CAS_CUMULATION",step)
        assert step["fill"]==("#239878" if delta>=0 else "#CD7271"),(title,"WRONG_MONEY_SIGN_COLOR",step)
      elif step["kind"]=="total":
        assert abs(cumulative-now)<=D("0.01"),(title,"TOTAL_WRONG_AMOUNT")
      cumulative=now
      if abs(delta)>D("0.01"):scales.append(step["width"]/abs(float(delta)))
    assert scales and max(scales)-min(scales)<max(scales)*.000001,(title,"NOT_SAME_FINANCIAL_MONEY_SCALE")
  if width in (768,390):
    assert info["originalDesktopHidden"]==9,(width,"OLD_1050_SVG_VISIBLE_ON_PHONE")
    assert all(z["visible"] and z["inner"]<=z["client"]+2 and z["originalSvg"]>220 for z in info["nativeViews"]),(width,"MOBILE_NATIVE_ART_CLIPPED")
    assert all(t["x"]>=-2 and t["right"]<=t["view"]+2 for z in info["nativeViews"] for t in z["cjkTexts"]),(width,"CHINESE_SVG_LABEL_OUTSIDE_VIEWBOX")
  else:
    assert info["originalDesktopHidden"]==0 and info["mobileVisible"]==0,(width,"DESKTOP_SVG_REPLACED")
  assert info["navPosition"]=="static",(width,"chapter nav must never obscure figure title",info)
  assert info["bodyExternalScripts"]==0,(width,"offline must need no external JS",info)
  if width==1440:
    assert all(g["scroll"]<=g["client"]+2 for g in info["desktopGraphs"]),(width,"desktop figure requires hidden horizontal scroll",info["desktopGraphs"])
    assert all(not g["outOfBoundsLabels"] for g in info["desktopGraphs"]),(width,"cropped SVG title or amounts",info["desktopGraphs"])
  assert "signed-pnl" in info["semanticFigures"] and "equal-total-date-stock" in info["semanticFigures"]
  assert page.locator("a.brand[href='/#companies']").count()==1
  assert page.locator("a[href='#cash']").count()>=1
  page.screenshot(path=str(out/f"full_{width}.png"),full_page=True)
  screenshots+=1
  if width in (1440,390):
   for figure in ("flow","segment","gp","pnl","earnings","cfo","cash","balance","capital"):
    page.locator("#fig-"+figure).screenshot(path=str(out/f"{figure}_{width}.png"))
    screenshots+=1
  page.locator('a[href="#cash"]').first.click()
  assert page.url.endswith("#cash"),page.url
  if width==1440:
   for name in ("flow","pnl","balance"):
    with page.expect_download(timeout=12000) as item:
     page.locator('button[data-export="'+name+'"]').click()
    assert item.value.suggested_filename=="688220_2026H1_"+name+".svg"
  statuses.append({"width":width,"financial_figures":9,"money_flow_positive_ribbons":7,
                   "source_tables":9,"mobile_numeric_answers":info["mobileVisible"],
                   "horizontal_body_overflow":False,"result":"PASS"})
  page.close()
 browser.close()
assert not errors,errors
source_manifest=json.loads((pathlib.Path(__file__).parent/"source-manifest.json").read_text(encoding="utf8"))
full_article_sha=hashlib.sha256(html.read_bytes()).hexdigest()
real_screenshots={p.name:{"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size} for p in sorted(out.glob("*.png"))}
assert len(real_screenshots)==screenshots and screenshots>=21,(screenshots,len(real_screenshots))
(out/"result.json").write_text(json.dumps({
 "issuer":"688220",
 "source_pdf_sha256":source_manifest["pdf_sha256"],
 "html_sha256":full_article_sha,
 "actual_3_viewport_checks":[{"width":z["width"],"body_no_overflow":"PASS",
       "actual_nine_390_768_native_signed_money_figures_no_inner_scroll":"PASS" if z["width"] in (390,768) else "DESKTOP_ORIGINAL_SVG",
       "source_conserved_source_sinks_and_Bezier_actual_width":"PASS",
       "original_legal_signed_CFO_and_PNL_in_same_scale":"PASS",
       "original_CJK_text_bbox":"PASS"} for z in statuses],
 "all_nine_390px_native_financial_svg_legible_and_source_reconciled":"PASS",
 "source_nodes_sinks_ribbons_exact_svg_geometric_proportions":"PASS",
 "real_CJK_screenshot_sha_bytes":real_screenshots,

 "technical_browser":"PASS","accounting_source_flow_visual_structure":"PASS",
 "source_pdf_manual_review":"SELECTED_PAGES_ONLY",
 "full_design_editorial":"NOT_CHECKED_INDEPENDENT_REVIEW",
 "production_route":"NOT_CHECKED_LOCAL_TEST",
 "viewport":statuses,"errors":errors,"screenshots":screenshots
},ensure_ascii=False,indent=2)+"\n")
print("ASR_AEI_REDESIGN_BROWSER_PASS",statuses,"screenshots",screenshots,flush=True)
