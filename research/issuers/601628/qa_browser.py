#!/usr/bin/env python3
"""Actual Chromium finance-figure, independent SVG geometry and mobile QA."""
from __future__ import annotations
from pathlib import Path
import hashlib,json,math
import xml.etree.ElementTree as ET
from qa_signed_geometry import FAMILIES, check_signed_svg, expected_steps
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"research/issuers/601628"
HTML=ROOT/"public/601628.html"
L=json.loads((BASE/"source-ledger.json").read_text())
F=L["facts"]
Q=json.loads((BASE/"figure-briefs.json").read_text())
OUT=BASE/"visual-qa";OUT.mkdir(exist_ok=True)
statuses=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
 for width,height in [(1440,900),(768,1024),(390,844)]:
  page=browser.new_page(viewport={"width":width,"height":height},device_scale_factor=1,accept_downloads=True)
  errors=[]
  page.on("pageerror",lambda exc:errors.append(str(exc)))
  page.goto(HTML.as_uri(),wait_until="load",timeout=30000)
  page.evaluate("document.fonts.ready")
  signed_results=[]
  bridge_exports=[]
  from decimal import Decimal as D
  import sys
  sys.path.insert(0,str(BASE))
  from quantified_decision import decisions,FACT_SPEC
  values,derived=decisions(L)
  panel=page.locator('section#quantified-decision')
  assert panel.count()==1 and panel.is_visible(),(width,"INSURANCE_VISIBLE_QUANTIFIED_DECISION_MISSING")
  assert panel.get_attribute("data-pdf-sha256")==L["source"]["original_bytes_sha256"]
  assert panel.get_attribute("data-accounting-not-causal")=="true"
  decision=panel.evaluate("""n=>({
     left:n.getBoundingClientRect().left,right:n.getBoundingClientRect().right,
     source:[...n.querySelectorAll('tr[data-source-key]')].map(x=>({...x.dataset})),
     derived:[...n.querySelectorAll('.insurance-decision-card[data-decision-key]')].map(x=>({...x.dataset})),
     cards:[...n.querySelectorAll('.insurance-decision-card')].map(x=>{
       const r=x.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom};
     }),
     font:+getComputedStyle(n.querySelector('.insurance-decision-lead')).fontSize.replace('px','')
  })""")
  assert len(decision["source"])==len(FACT_SPEC)==13,(width,"DECISION_SOURCE_FACT_COUNT")
  assert len(decision["derived"])==4,(width,"DECISION_DERIVED_CAS_METRIC_COUNT")
  for item in decision["source"]:
     k=item["sourceKey"];fact=F[k]
     assert D(item["exactYuan"])==D(fact["yuan"]),(width,k,"DECISION_ORIGINAL_PDF_YUAN_DRIFT")
     assert item["period"]==FACT_SPEC[k][0] and item["financialKind"]==FACT_SPEC[k][1]
     assert int(item["physicalPage"])==fact["page"]
  assert all(D(item["derivedDecimal"])==derived[item["decisionKey"]] for item in decision["derived"]),(width,"DECISION_SIGNED_CAS_ARITHMETIC_WRONG")
  assert decision["left"]>=-1 and decision["right"]<=width+2 and decision["font"]>=13,(width,"INSURER_QUANTIFIED_DECISION_CROPPED_OR_SMALL")
  if width<=850:
     assert all(decision["cards"][i]["bottom"]<=decision["cards"][i+1]["top"]+.5 for i in range(3)),(width,"INSURER_QUANTIFIED_CARDS_OVERPRINT")
  panel.screenshot(path=str(OUT/f"decision_{width}.png"),animations="disabled")
  assert page.locator("figure.figure").count()==len(Q["figure_briefs"])==10,(width,"figures")
  assert page.locator("figure.figure .audit").count()==10,(width,"independent source tables")
  assert page.locator("figure.figure .chart svg").count()==10,(width,"not real SVG")
  assert page.locator("figure.figure .mobile-chart").count()==10,(width,"ten source-driven mobile finance exhibits missing")
  assert page.locator("[data-export]").count()==10,(width,"export controls")
  assert page.locator('a[href="/#companies"]').count()>=1,(width,"backlink")
  assert L["source"]["original_bytes_sha256"] in page.content(),(width,"source identity")
  assert not errors,(width,"JS errors",errors)
  geometry=page.evaluate("""() => {
    const body=document.documentElement;
    const svg=document.querySelector('#chart-premium svg');
    const premium=(root)=>{
      if(!root)return null;
      return {total:+root.getAttribute('data-premium-yuan'),scale:+root.getAttribute('data-scale-yuan-per-svg-unit'),grammar:root.getAttribute('data-chart-grammar'),
        view:root.viewBox.baseVal.width,
        nodes:[...root.querySelectorAll('rect[data-node-role]')].map(n=>({id:n.getAttribute('data-node-id'),role:n.getAttribute('data-node-role'),amount:+n.getAttribute('data-node-yuan'),height:+n.getAttribute('height')})),
        paths:[...root.querySelectorAll('path[data-ribbon-yuan]')].map(p=>({source:p.getAttribute('data-source-id'),stage:p.getAttribute('data-stage'),amount:+p.getAttribute('data-ribbon-yuan'),d:p.getAttribute('d'),scale:+p.getAttribute('data-scale-yuan-per-svg-unit')}))};
    };
    const graph=premium(svg),phone=premium(document.querySelector('#chart-premium .mobile-chart svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"]'));
    const malformedRects=[...document.querySelectorAll('.chart svg rect')].filter(x=>!/^#[0-9A-Fa-f]{6}$/.test(x.getAttribute('fill')||'')||((x.getAttribute('class')||'').includes('='))).map(x=>x.outerHTML.slice(0,200));
    const money=node=>[...document.querySelectorAll(node)].map(x=>({w:x.scrollWidth,visible:x.clientWidth}));
    const domContents=[...document.querySelectorAll('h1,h2,p,.intro,.closing,.figure,.wrap,footer,header,.topbar')].map(x=>({tag:x.tagName,rect:x.getBoundingClientRect().toJSON()}));
    return {width:innerWidth,bodyWidth:body.scrollWidth,graph,phone,malformedRects,charts:money('.chart'),visible:domContents,
      hasFont:document.fonts.check('16px "Noto Sans CJK SC"'),sourceTables:[...document.querySelectorAll('table')].filter(t=>!t.closest('.research-context')).length,
      mobile:[...document.querySelectorAll('.mobile-chart')].map(el=>({
        family:el.dataset.mobileFigure,visible:getComputedStyle(el).display!=='none',
        panelOverflow:el.scrollWidth-el.clientWidth,
        rows:[...el.querySelectorAll('.m-item')].map(x=>({
          key:x.dataset.mobileFact,exact:x.dataset.exactYuan,group:x.dataset.scaleGroup,
          label:x.querySelector('.m-item-name')?.textContent||'',
          widthPct:parseFloat(x.querySelector('.m-item-rail i')?.style.width||'0'),
          signed:x.querySelector('.m-item-val')?.textContent||''
        }))
      }))}
  }""")
  assert geometry["bodyWidth"]<=width+1,(width,"ROOT_HORIZONTAL_OVERFLOW",geometry["bodyWidth"])
  if width==1440:
   assert all(x["w"]<=x["visible"]+2 for x in geometry["charts"]),(width,"HIDDEN_DESKTOP_FIGURE",geometry["charts"])
   collisions=page.evaluate("""() => {
     const issues=[];
     for(const id of ['insurance','pnl','delta','cash','cashclose']){
       const svg=document.querySelector('#chart-'+id+' .chart svg');
       const texts=[...svg.querySelectorAll('text')];
       const title=texts.find(t=>t.getAttribute('font-size')==='16'&&t.getAttribute('font-weight')==='650'&&t.getAttribute('y')==='38.00');
       const values=texts.filter(t=>t.getAttribute('font-size')==='12'&&t.getAttribute('font-weight')==='650');
       if(!title || !values.length){issues.push({id,error:'MISSING_MONEY_WATERFALL_LABELS'});continue;}
       const t=title.getBBox();
       for(const label of values){
         const b=label.getBBox();
         // Source value labels must sit below the editorial chart title,
         // not merely above their own bar, even when bars approach chart top.
         if(b.y<t.y+t.height+12){issues.push({id,error:'DESKTOP_WATERFALL_TITLE_VALUE_OVERLAP',title:t.y+t.height,valueY:b.y,label:label.textContent});}
       }
     }
     return issues;
   }""")
   assert not collisions,("DESKTOP_WATERFALL_TITLE_VALUE_OVERLAP",collisions)
   clocks_collisions=page.evaluate("""() => {
     const svg=document.querySelector('#chart-clocks .chart svg');
     if(!svg)return [{error:'MISSING_DISCLOSED_CLOCKS_SVG'}];
     const texts=[...svg.querySelectorAll('text')];
     const amounts=texts.filter(x=>/^202[56] [0-9,]+\\.[0-9]+亿$/.test(x.textContent.trim()));
     const yoy=texts.filter(x=>/^[+−-][0-9,.]+%$/.test(x.textContent.trim()));
     const faults=[];
     if(amounts.length!==8 || yoy.length!==4)return [{error:'CLOCK_VALUE_OR_YOY_LABEL_MISSING',amounts:amounts.length,yoy:yoy.length}];
     const intersects=(a,b)=>{
        const x=a.getBBox(),y=b.getBBox();
        return Math.min(x.x+x.width,y.x+y.width)-Math.max(x.x,y.x)>1 &&
               Math.min(x.y+x.height,y.y+y.height)-Math.max(x.y,y.y)>1;
     };
     for(const yr of amounts)for(const pct of yoy){
        if(intersects(yr,pct))faults.push({error:'CLOCK_AMOUNT_YOY_COLLISION',
             yearAmount:yr.textContent,percentage:pct.textContent,
             a:yr.getBBox().toJSON(),b:pct.getBBox().toJSON()});
     }
     const vw=svg.viewBox.baseVal.width;
     for(const v of [...amounts,...yoy]){
        const r=v.getBBox();
        if(r.x<0||r.x+r.width>vw+0.5)faults.push({error:'CLOCK_LABEL_CROPPED',label:v.textContent,rect:r.toJSON(),viewBox:vw});
     }
     return faults;
   }""")
   assert not clocks_collisions,("ACTUAL_CHROMIUM_601628_MONEY_AND_YOY_TEXT_COLLISION",clocks_collisions)
  if width<=850:
   assert page.locator(".mobile-chart:visible").count()==10,(width,"MOBILE_NOT_TEN_COMPLETE_SOURCE_PLOTS")
   assert page.locator(".chart:visible").count()==0,(width,"MOBILE_STILL_USES_900PX_CROPPED_SVG_WINDOW")
   assert all(x["visible"] and x["panelOverflow"]<=1 for x in geometry["mobile"]),(width,"MOBILE_INNER_HORIZ_SCROLL",geometry["mobile"])
   assert len({x["family"] for x in geometry["mobile"]})==10
   for panel in geometry["mobile"]:
    if panel["family"] in FAMILIES:
     graph=page.locator('#chart-'+panel["family"]+' .mobile-chart svg')
     assert graph.count()==1 and graph.is_visible(),(width,panel["family"],"VISIBLE_SIGNED_BRIDGE_REQUIRED")
     signed_results.append(check_signed_svg(graph.evaluate("el=>el.outerHTML"),panel["family"],L))
     continue
    assert len(panel["rows"])>=5,(panel["family"],"MOBILE_NO_FULL_FINANCIAL_ITEMS")
    groups={}
    for item in panel["rows"]:
     yuan=int(item["exact"])
     groups[item["group"]]=max(groups.get(item["group"],0),abs(yuan))
     if item["key"]!="derived":
      assert item["key"] in F,(panel["family"],"UNSUPPORTED_MOBILE_FACT",item["key"])
      assert item["exact"]==F[item["key"]]["yuan"],(panel["family"],"MOBILE_SOURCE_LEDGER_MISMATCH",item["key"])
     assert item["signed"].startswith("−" if yuan<0 else ("+" if yuan>0 else "0")),(panel["family"],"MOBILE_SIGN_LOST",item)
    for item in panel["rows"]:
     maximum=groups[item["group"]]
     assert maximum>0,(panel["family"],"MOBILE_ZERO_DENOMINATOR")
     expected=abs(int(item["exact"]))/maximum*100
     # Chromium CSSOM rounds percent widths to 4 decimals; allow at most half of its last percent-place, not a visual 1px fudge.
     assert math.isclose(item["widthPct"],expected,abs_tol=0.000055),(panel["family"],"MOBILE_BAR_INFLATED_OR_NOT_SOURCE_PROPORTIONAL",item,expected)
   # No significant non-figure container can use overflow:hidden to mask content.
   for el in geometry["visible"]:
    r=el["rect"]
    if r["width"]>0 and r["height"]>0:
     assert r["left"]>=-2 and r["right"]<=width+2,(el["tag"],"NON_SCROLLING_MOBILE_CONTENT_CLIPPED",r)
  assert not geometry["malformedRects"],("SVG_RECT_MALFORMED_OR_UNPAINTED",width,geometry["malformedRects"])
  for view,graph in (("desktop",geometry["graph"]),("phone",geometry["phone"])):
   assert graph and graph["grammar"]=="INSURANCE_PREMIUM_SOURCE_NEW_RENEW_TOTAL",(width,view,"INSURANCE_PREMIUM_SEMANTIC_GRAMMAR_MISSING")
   assert graph["view"]==(1100 if view=="desktop" else 330)
   assert abs(graph["total"]-float(F["premium_total"]["yuan"]))<.001 and graph["scale"]>0
   sources=[x for x in graph["nodes"] if x["role"]=="premium-source"]
   buckets=[x for x in graph["nodes"] if x["role"]=="premium-bucket"]
   totals=[x for x in graph["nodes"] if x["role"]=="premium-total"]
   assert len(sources)==4 and len(buckets)==2 and len(totals)==1,(width,view,"TRUE_INSURANCE_PREMIUM_NODES_MISSING")
   assert totals[0]["id"]=="premium-total"
   stage_a=[x for x in graph["paths"] if x["stage"]=="premium-source-to-new-or-renew"]
   stage_b=[x for x in graph["paths"] if x["stage"]=="new-or-renew-to-premium-total"]
   assert len(stage_a)==4 and len(stage_b)==2,(width,view,"TRUE_INSURANCE_PREMIUM_RIBBONS_MISSING")
   assert abs(sum(x["amount"] for x in stage_a)-graph["total"])<.001
   assert abs(sum(x["amount"] for x in stage_b)-graph["total"])<.001
   for node in graph["nodes"]:
    assert abs(node["height"]-node["amount"]/graph["scale"])<.001,(width,view,"REAL_INSURANCE_PREMIUM_SOURCE_SCALE",node)
   for ribbon in graph["paths"]:
    assert ribbon["scale"]>0 and ribbon["amount"]>0
    # Inspect ACTUAL vector geometry, not just data-* amounts.
    # path is M x y C ... L x y C ... Z.
    import re
    assert ribbon["d"].startswith("M ") and " C " in ribbon["d"] and " L " in ribbon["d"]
    # First cubic's rightmost endpoint is the TARGET top. The following
    # L target is the TARGET bottom. Source top vs target bottom is WRONG
    # whenever individual lanes bend vertically between graph stages.
    top_target=float(ribbon["d"].split(" L ")[0].split()[-1])
    bottom_target=float(ribbon["d"].split(" L ")[1].split(" C ")[0].split()[-1])
    thickness=abs(bottom_target-top_target)
    assert abs(thickness-ribbon["amount"]/graph["scale"])<.001,(width,view,"INSURANCE_PREMIUM_PHYSICAL_RIBBON_HEIGHT_FALSE",thickness,ribbon)
   for key in ("premium_first_regular","premium_single","premium_short","premium_renew"):
    source=next((x for x in sources if x["id"]==key),None)
    assert source and abs(source["amount"]-float(F[key]["yuan"]))<.001,(width,view,"INSURANCE_P10_ORIGINAL_DISJOINT_SOURCE_WRONG",key)
   assert abs(next(x for x in buckets if x["id"]=="premium_new")["amount"]-float(F["premium_new"]["yuan"]))<.001
   assert abs(next(x for x in buckets if x["id"]=="premium_renew")["amount"]-float(F["premium_renew"]["yuan"]))<.001
  for family in sorted(FAMILIES):
   dependencies=set().union(*(step[1] for step in expected_steps(family,F)))
   brief=next(b for b in Q['figure_briefs'] if b['id']==family)
   assert dependencies<=set(brief['facts']),(width,family,'SOURCE_TABLE_DEPENDENCIES_INCOMPLETE')
   table=page.locator('#chart-'+family+' details.audit tbody tr')
   actual=table.evaluate_all("rows=>rows.map(r=>({label:r.querySelector('th').textContent,amount:r.querySelector('td.number').textContent,href:r.querySelector('a').getAttribute('href')}))")
   assert len(actual)==len(brief['facts']),(width,family,'SOURCE_TABLE_ROW_COUNT')
   for row,key in zip(actual,brief['facts']):
    fact=F[key]
    assert row['label']==fact['label'] and row['amount']==f"{D(fact['yuan'])/D(1000000):+,.0f} 百万元",(width,family,key,'SOURCE_TABLE_EXACT_DISCLOSURE')
    assert row['href']==L['source']['official_announcement']+'#page='+str(fact['page']),(width,family,key,'SOURCE_TABLE_ORIGINAL_PAGE')
  # Exercise the actual visible SVG download for every new bridge at every width.
  # Desktop exports must retain their own full-width drawing; phone exports
  # must be the audited native bridge, rather than the hidden desktop SVG.
  for family in sorted(FAMILIES):
   container=page.locator('#chart-'+family)
   visible=container.locator('.mobile-chart svg' if width<=850 else '.chart svg')
   assert visible.count()==1 and visible.is_visible(),(width,family,"VISIBLE_EXPORT_SOURCE")
   raw_visible=visible.evaluate("el=>el.outerHTML")
   with page.expect_download(timeout=10000) as pending:
    container.locator('[data-export]').click()
   downloaded=pending.value
   assert downloaded.failure() is None,(width,family,"DOWNLOAD_FAILED")
   assert downloaded.suggested_filename==f"601628-2026H1-{family}.svg"
   dest=OUT/f"export-{family}-{width}.svg"
   downloaded.save_as(dest)
   raw=dest.read_text();actual=ET.fromstring(raw);expected=ET.fromstring(raw_visible)
   assert actual.get('viewBox')==expected.get('viewBox'),(width,family,"EXPORTED_HIDDEN_LAYOUT")
   assert actual.get('data-chart-grammar')==expected.get('data-chart-grammar'),(width,family,"EXPORTED_WRONG_GRAMMAR")
   ns='{http://www.w3.org/2000/svg}'
   for tag in ('rect','text','path'):
    assert [(n.attrib,n.text) for n in actual.iter(ns+tag)]==[(n.attrib,n.text) for n in expected.iter(ns+tag)],(width,family,"EXPORTED_VISIBLE_VECTOR_DRIFT",tag)
   if width<=850:check_signed_svg(raw,family,L)
   bridge_exports.append({'family':family,'visible_layout':'native-330' if width<=850 else 'desktop','download_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'actual_visible_svg_match':'PASS'})
  with page.expect_download(timeout=10000) as download:
   page.locator('[data-export="premium"]').click()
  got=download.value
  assert got.suggested_filename=="601628-2026H1-premium.svg",got.suggested_filename
  assert got.failure() is None
  assert page.locator("body").count()==1
  page.screenshot(path=str(OUT/f"full_report_{width}.png"),full_page=True)
  for figure in Q["figure_briefs"]:
    if width in (1440,390):
     page.locator(f'#chart-{figure["id"]}').screenshot(path=str(OUT/f'figure_{figure["id"]}_{width}.png'))
  statuses.append({"width":width,"height":height,"result":"PASS","body_no_overflow":"PASS",
                   "source_sankey_actual_path_and_rect":"PASS","cjk_font_available":geometry["hasFont"],
                   "figure_count":10,"original_source_tables":geometry["sourceTables"],
                   "figure_readability":"DESKTOP_ALL_ORIGINAL_SVG_VISIBLE" if width==1440 else ("MOBILE_ALL_TEN_COMPLETE_NO_HORIZ_SCROLL" if width<=850 else "TABLET_FULL_SOURCE_SVG"),
                   "svg_export":"PASS","signed_bridge_source_and_geometry":signed_results,"visible_bridge_svg_exports":bridge_exports,"screenshot_sha256":hashlib.sha256((OUT/f"full_report_{width}.png").read_bytes()).hexdigest(),"screenshot":f"full_report_{width}.png"})
  page.close()
 browser.close()
result={"code":"601628","source_sha":L["source"]["original_bytes_sha256"],
        "candidate_html_sha256":hashlib.sha256(HTML.read_bytes()).hexdigest(),
        "source_nodes_sinks_ribbons_exact_svg_geometric_proportions":"PASS",
        "page_1440_768_390":"PASS","chart_count":10,"source_table_count":statuses[0]["original_source_tables"],
        "export_click_and_svg_download":"PASS","mobile_fully_visible_financial_figures":"PASS","mobile_ledger_exact_value_and_geometry":"PASS","original_actual_3_viewport_checks":statuses,
        "human_editor":"NOT_CHECKED","scope":"real Chromium financial SVG and source-structure invariants, not human financial/aesthetic certification"}
(OUT/"result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print("INSURANCE_ACTUAL_CHROMIUM_1440_768_390_AND_SVG_GEOMETRY_PASS",json.dumps(statuses,ensure_ascii=False))
