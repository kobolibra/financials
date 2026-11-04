#!/usr/bin/env python3
"""Actual Chromium finance-figure, independent SVG geometry and mobile QA."""
from __future__ import annotations
from pathlib import Path
import hashlib,json,math
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
    const nodes=[...svg.querySelectorAll('rect.money-source')].map(x=>({key:x.dataset.sourceKey,height:+x.getAttribute('height'),exact:x.dataset.exactYuan}));
    const paths=[...svg.querySelectorAll('path.money-ribbon')].map(x=>({key:x.dataset.sourceKey,d:x.getAttribute('d'),v:+x.dataset.valueMillion}));
    const sinks=[...svg.querySelectorAll('rect.money-sink')].map(x=>({fill:x.getAttribute('fill'),klass:x.getAttribute('class'),y:+x.getAttribute('y'),height:+x.getAttribute('height'),million:x.dataset.valueMillion,exact:x.dataset.exactYuan}));
    const malformedRects=[...document.querySelectorAll('.chart svg rect')].filter(x=>!/^#[0-9A-Fa-f]{6}$/.test(x.getAttribute('fill')||'')||((x.getAttribute('class')||'').includes('='))).map(x=>x.outerHTML.slice(0,200));
    const money=node=>[...document.querySelectorAll(node)].map(x=>({w:x.scrollWidth,visible:x.clientWidth}));
    const domContents=[...document.querySelectorAll('h1,h2,p,.intro,.closing,.figure,.wrap,footer,header,.topbar')].map(x=>({tag:x.tagName,rect:x.getBoundingClientRect().toJSON()}));
    return {width:innerWidth,bodyWidth:body.scrollWidth,nodes,paths,sinks,malformedRects,charts:money('.chart'),visible:domContents,
      hasFont:document.fonts.check('16px "Noto Sans CJK SC"'),sourceTables:document.querySelectorAll('table').length,
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
  if width==390:
   assert page.locator(".mobile-chart:visible").count()==10,(width,"MOBILE_NOT_TEN_COMPLETE_SOURCE_PLOTS")
   assert page.locator(".chart:visible").count()==0,(width,"MOBILE_STILL_USES_900PX_CROPPED_SVG_WINDOW")
   assert all(x["visible"] and x["panelOverflow"]<=1 for x in geometry["mobile"]),(width,"MOBILE_INNER_HORIZ_SCROLL",geometry["mobile"])
   assert len({x["family"] for x in geometry["mobile"]})==10
   for panel in geometry["mobile"]:
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
  assert len(geometry["nodes"])==4 and len(geometry["paths"])==6
  assert not geometry["malformedRects"], ("SVG_RECT_MALFORMED_OR_UNPAINTED",width,geometry["malformedRects"])
  assert len(geometry["sinks"])==1,("MISSING_PREMIUM_TOTAL_MONEY_SINK",width,geometry["sinks"])
  sink=geometry["sinks"][0]
  assert sink["klass"]=="money-sink",("BAD_SVG_SINK_CLASS",sink)
  assert sink["fill"]=="#123F3A",("UNPAINTED_PREMIUM_TOTAL_SINK",sink)
  assert sink["million"]=="536634" and sink["exact"]==F["premium_total"]["yuan"],("PREMIUM_SINK_WRONG_SOURCE_AMOUNT",sink)
  assert math.isclose(sink["height"],268.0,abs_tol=0.00001) and math.isclose(sink["y"],82.0,abs_tol=0.00001),("PREMIUM_MONEY_SINK_NOT_CONSERVED",sink)
  total=536634.0
  expected={
   "premium_first_regular":101294,
   "premium_single":17696,
   "premium_short":61049,
   "premium_renew":356595
  }
  for node in geometry["nodes"]:
   k=node["key"];assert k in expected
   assert math.isclose(node["height"],268*expected[k]/total,abs_tol=.0005),(k,"VISUAL_RECT_GEOMETRY",node)
   assert node["exact"]==F[k]["yuan"],(k,"RECT_SOURCE_DRIFT")
  actual_flow={x["key"]:[] for x in geometry["paths"]}
  for path in geometry["paths"]:
   # SVG actual path starts M x,source_y and has a first L x,target_y.
   # Parse true path coordinates, do not trust just correct data-*.
   import re
   nums=re.findall(r"[-+]?(?:\d+\.\d+|\d+)",path["d"])
   # format starts 'M {x},{ya} C ... L {x},{zb} ...';
   ystart=float(nums[1]); ylow=float(nums[3]); end=float(nums[13])
   # The geometry under test is source thickness. Extract the first
   # M y and the third pair following first L.
   coords=re.findall(r"\b([ML])\s+([\d.]+),([\d.]+)",path["d"])
   assert len(coords)>=2,(path["key"],"PATH_COORDS_NOT_PARSEABLE",path["d"][:150])
   yend=float(coords[1][2])
   expectedheight=268*path["v"]/total
   assert math.isclose(abs(yend-ystart),expectedheight,abs_tol=.0006),(path["key"],"NOT_MONEY_WEIGHTED_ACTUAL_PATH",yend-ystart,expectedheight)
   actual_flow[path["key"]].append(path["v"])
  assert all(len(actual_flow[k])==1 and actual_flow[k][0]==expected[k] for k in ["premium_first_regular","premium_single","premium_short"]), "LEFT_SOURCES_NOT_EXACT"
  assert len(actual_flow["premium_renew"])==2 and actual_flow["premium_renew"]==[356595,356595], "RENEWAL_INTERMEDIATE_NOT_CLOSED"
  assert len(actual_flow["premium_new"])==1 and actual_flow["premium_new"][0]==180039, "NEW_INTERMEDIATE_NOT_CLOSED"
  assert sum(actual_flow[k][0] for k in ["premium_first_regular","premium_single","premium_short"])==actual_flow["premium_new"][0], "NEW_SOURCE_CONSERVATION"
  assert actual_flow["premium_new"][0]+actual_flow["premium_renew"][1]==536634,"TOTAL_SINK_NOT_CLOSED"
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
                   "figure_readability":"DESKTOP_ALL_ORIGINAL_SVG_VISIBLE" if width==1440 else ("MOBILE_ALL_TEN_COMPLETE_NO_HORIZ_SCROLL" if width==390 else "TABLET_FULL_SOURCE_SVG"),
                   "svg_export":"PASS","screenshot":f"full_report_{width}.png"})
  page.close()
 browser.close()
result={"code":"601628","source_sha":L["source"]["original_bytes_sha256"],
        "source_nodes_sinks_ribbons_exact_svg_geometric_proportions":"PASS",
        "page_1440_768_390":"PASS","chart_count":10,"source_table_count":10,
        "export_click_and_svg_download":"PASS","mobile_fully_visible_financial_figures":"PASS","mobile_ledger_exact_value_and_geometry":"PASS","original_actual_3_viewport_checks":statuses,
        "human_editor":"NOT_CHECKED","scope":"real Chromium financial SVG and source-structure invariants, not human financial/aesthetic certification"}
(OUT/"result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print("INSURANCE_ACTUAL_CHROMIUM_1440_768_390_AND_SVG_GEOMETRY_PASS",json.dumps(statuses,ensure_ascii=False))
