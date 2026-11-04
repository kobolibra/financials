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
    mobileSigned:[...document.querySelectorAll('.native-asr-signed')].map(e=>({kind:e.dataset.kind,step:+e.dataset.step,yuan:e.dataset.signedYuan,cumulative:e.dataset.cumulativeYuan,width:+e.getAttribute('width'),fill:e.getAttribute('fill'),svg:e.closest('svg').getAttribute('aria-label')})),
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
  assert len(info["mobileFlowSource"])==4 and len(info["mobileFlowSink"])==2 and len(info["mobileFlowRibbon"])==7
  source_scale=298/float(D(facts["rev"]["yuan"]))
  for item in info["mobileFlowSource"]+info["mobileFlowSink"]:
    assert abs(item["width"]-float(D(item["yuan"]))*source_scale)<1e-6,(width,"MOBILE_NODE_NOT_REAL_YUAN",item)
  for item in info["mobileFlowRibbon"]:
    assert abs(item["width"]-float(D(item["yuan"]))*source_scale)<1e-6,(width,"MOBILE_RIBBON_NOT_REAL_YUAN",item)
    import re
    match=re.search(r"^M([0-9.]+),58 C.* ([0-9.]+),58 Z$",item["path"])
    assert match,(width,"BAD_MOBILE_MONEY_CURVE",item)
    assert abs(float(match.group(2))-float(match.group(1))-item["width"])<1e-6,(width,"MOBILE_CURVE_FALSE_PHYSICAL_WIDTH",item)
  assert len(info["mobileSigned"])>=25,(width,"SIGNED_FINANCIAL_GRAPHS_MISSING")
  by_chart={}
  for step in info["mobileSigned"]:
    by_chart.setdefault(step["svg"],[]).append(step)
  assert len(by_chart)==5,(width,"EXPECTED_FIVE_SIGNED_GRAPHS")
  for title,steps in by_chart.items():
    cumulative=None
    scales=[]
    for step in sorted(steps,key=lambda x:x["step"]):
      delta=D(step["yuan"]);now=D(step["cumulative"])
      if step["kind"]=="step":
        assert cumulative is not None and abs(cumulative+delta-now)<=D("0.01"),(title,"BROKEN_SIGNED_CAS_CUMULATION",step)
        assert step["fill"]==("#087b65" if delta>=0 else "#a84f40"),(title,"WRONG_MONEY_SIGN_COLOR",step)
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
  assert len(info["ribbon"])==7,(width,"4 cost ribbons and 3 nonzero GP ribbons required",info["ribbon"])
  assert len({r["source"] for r in info["ribbon"]})==4
  assert all(D(r["amount"])>0 and (r["bboxHeight"]>0 if width==1440 else r["thickness"]>0) and r["title"] for r in info["ribbon"]),(width,"fake/empty ribbon")
  cost=sum((D(r["amount"]) for r in info["ribbon"] if r["kind"]=="cost"),D(0))
  profit=sum((D(r["amount"]) for r in info["ribbon"] if r["kind"]=="profit"),D(0))
  assert abs(cost-expected_cost)<=D("0.02") and abs(profit-expected_profit)<=D("0.02"),(width,"money-flow totals wrong",cost,profit)
  # A real finance flow needs correct individual edge amounts AND actual SVG path
  # geometry: a correct accounting ledger alone cannot prevent a forged ribbon.
  segment_by_rev={q["rev"]:q for q in ledger["segments"]}
  source_nodes={q["key"]:q for q in info["sourceNodes"]}
  assert len(source_nodes)==len(ledger["segments"])==4,(width,"source node count",info["sourceNodes"])
  sink_nodes={q["kind"]:q for q in info["sinks"]}
  assert set(sink_nodes)=={"cost","profit"},(width,"sink semantics",info["sinks"])
  scale=334.0/float(D(facts["rev"]["yuan"]))
  for q in ledger["segments"]:
    key=q["rev"]
    rev=D(facts[q["rev"]]["yuan"])
    cogs=D(facts[q["cost"]]["yuan"])
    gp=rev-cogs
    node=source_nodes[key]
    assert D(node["amount"])==rev and node["title"],(width,"source node disclosure",node)
    assert abs(node["realHeight"]-float(rev)*scale)<0.000001,(width,"visually inflated revenue source",node)
    assert abs(node["semanticHeight"]-node["realHeight"])<0.000001,(width,"false source width metadata",node)
    for kind,expected,target in [("cost",cogs,"cogs"),("profit",gp,"gross_profit")]:
      edge=[r for r in info["ribbon"] if r["sourceKey"]==key and r["kind"]==kind]
      assert len(edge)==(0 if expected==0 else 1),(width,"missing or phantom 0-GP ribbon",key,kind,edge)
      if expected>0:
        r=edge[0]
        assert D(r["amount"])==expected and r["target"]==target,(width,"business cost/GP attribution",r)
        assert r["period"]=="2026H1" and r["scope"]=="consolidated" and r["sourcePage"]=="178",(width,"ribbon source",r)
        assert r["pathThickness"] is not None,(width,"missing geometric proof",r)
        expected_thick=float(expected)*scale
        assert abs(r["thickness"]-expected_thick)<0.000001,(width,"inflated encoded ribbon",r,expected_thick)
        assert abs(r["pathThickness"]-expected_thick)<0.000001,(width,"actual SVG path disagrees with exact source",r,expected_thick)
  for kind,expected in [("cost",expected_cost),("profit",expected_profit)]:
    sink=sink_nodes[kind]
    assert D(sink["amount"])==expected and abs(sink["height"]-float(expected)*scale)<0.000001,(width,"sink geometry",sink)
  tiny=source_nodes["other_service_rev"]
  assert 0<tiny["realHeight"]<0.02,(width,"microbusiness source node was artificially enlarged",tiny)
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
,edge["path"])
    assert matched,(width,"mobile path malformed",edge)
    assert abs(float(matched.group(4))-float(matched.group(1))-edge["width"])<0.00001,(width,"mobile ribbon true geometry not money scale",edge)
  assert len(info["mobileSigned"])>=25,(width,"missing signed mobile CAS cash and profit")
  for chart in set(x["svg"] for x in info["mobileSigned"]):
    allsteps=sorted((x for x in info["mobileSigned"] if x["svg"]==chart),key=lambda x:x["step"])
    prev=None;scales=[]
    for step in allsteps:
      amount=D(step["yuan"]);cumulative=D(step["cumulative"])
      if step["kind"]=="step":
        assert prev is not None and abs(prev+amount-cumulative)<=D("0.01"),(width,"not cumulative signed CAS mobile graphic",chart,step)
        assert step["fill"]==( "#087b65" if amount>=0 else "#a84f40" ),(width,"negative cash sign color incorrect",step)
      elif step["kind"]=="total" and prev is not None:
        assert abs(prev-cumulative)<=D("0.01"),(width,"final signed source bridge mismatch",chart)
      if abs(amount)>D("0.01"):scales.append(step["width"]/abs(float(amount)))
      prev=cumulative
    assert scales and max(scales)-min(scales)<max(scales)*0.000001,(width,"signed same scale broken",chart)
  if width in (390,768):
    assert info["originalDesktopHidden"]==9,(width,"old 1050 SVG scroll remains visible")
    assert all(x["visible"] and x["inner"]<=x["client"]+2 and x["originalSvg"]>220 for x in info["nativeViews"]),(width,"original mobile has clipped internal 1050 viewport",info["nativeViews"])
    assert all(t["x"]>=-2 and t["right"]<=t["view"]+2 for view in info["nativeViews"] for t in view["cjkTexts"]),(width,"mobile SVG CJK right-side clip",info["nativeViews"])
  else:
    assert info["originalDesktopHidden"]==0 and info["mobileVisible"]==0,(width,"desktop original switched off")

  assert info["navPosition"]=="static",(width,"chapter nav must never obscure figure title",info)
  assert info["bodyExternalScripts"]==0,(width,"offline must need no external JS",info)
  assert len(info["ribbon"])==7,(width,"4 cost ribbons and 3 nonzero GP ribbons required",info["ribbon"])
  assert len({r["source"] for r in info["ribbon"]})==4
  assert all(D(r["amount"])>0 and r["bboxHeight"]>0 and r["title"] for r in info["ribbon"]),(width,"fake/empty ribbon")
  cost=sum((D(r["amount"]) for r in info["ribbon"] if r["kind"]=="cost"),D(0))
  profit=sum((D(r["amount"]) for r in info["ribbon"] if r["kind"]=="profit"),D(0))
  assert abs(cost-expected_cost)<=D("0.02") and abs(profit-expected_profit)<=D("0.02"),(width,"money-flow totals wrong",cost,profit)
  # A real finance flow needs correct individual edge amounts AND actual SVG path
  # geometry: a correct accounting ledger alone cannot prevent a forged ribbon.
  segment_by_rev={q["rev"]:q for q in ledger["segments"]}
  source_nodes={q["key"]:q for q in info["sourceNodes"]}
  assert len(source_nodes)==len(ledger["segments"])==4,(width,"source node count",info["sourceNodes"])
  sink_nodes={q["kind"]:q for q in info["sinks"]}
  assert set(sink_nodes)=={"cost","profit"},(width,"sink semantics",info["sinks"])
  scale=334.0/float(D(facts["rev"]["yuan"]))
  for q in ledger["segments"]:
    key=q["rev"]
    rev=D(facts[q["rev"]]["yuan"])
    cogs=D(facts[q["cost"]]["yuan"])
    gp=rev-cogs
    node=source_nodes[key]
    assert D(node["amount"])==rev and node["title"],(width,"source node disclosure",node)
    assert abs(node["realHeight"]-float(rev)*scale)<0.000001,(width,"visually inflated revenue source",node)
    assert abs(node["semanticHeight"]-node["realHeight"])<0.000001,(width,"false source width metadata",node)
    for kind,expected,target in [("cost",cogs,"cogs"),("profit",gp,"gross_profit")]:
      edge=[r for r in info["ribbon"] if r["sourceKey"]==key and r["kind"]==kind]
      assert len(edge)==(0 if expected==0 else 1),(width,"missing or phantom 0-GP ribbon",key,kind,edge)
      if expected>0:
        r=edge[0]
        assert D(r["amount"])==expected and r["target"]==target,(width,"business cost/GP attribution",r)
        assert r["period"]=="2026H1" and r["scope"]=="consolidated" and r["sourcePage"]=="178",(width,"ribbon source",r)
        assert r["pathThickness"] is not None,(width,"missing geometric proof",r)
        expected_thick=float(expected)*scale
        assert abs(r["thickness"]-expected_thick)<0.000001,(width,"inflated encoded ribbon",r,expected_thick)
        assert abs(r["pathThickness"]-expected_thick)<0.000001,(width,"actual SVG path disagrees with exact source",r,expected_thick)
  for kind,expected in [("cost",expected_cost),("profit",expected_profit)]:
    sink=sink_nodes[kind]
    assert D(sink["amount"])==expected and abs(sink["height"]-float(expected)*scale)<0.000001,(width,"sink geometry",sink)
  tiny=source_nodes["other_service_rev"]
  assert 0<tiny["realHeight"]<0.02,(width,"microbusiness source node was artificially enlarged",tiny)
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
(out/"result.json").write_text(json.dumps({
 "technical_browser":"PASS","accounting_source_flow_visual_structure":"PASS",
 "source_pdf_manual_review":"SELECTED_PAGES_ONLY",
 "full_design_editorial":"NOT_CHECKED_INDEPENDENT_REVIEW",
 "production_route":"NOT_CHECKED_LOCAL_TEST",
 "viewport":statuses,"errors":errors,"screenshots":screenshots
},ensure_ascii=False,indent=2)+"\n")
print("ASR_AEI_REDESIGN_BROWSER_PASS",statuses,"screenshots",screenshots,flush=True)
