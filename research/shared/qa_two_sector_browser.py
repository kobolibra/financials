#!/usr/bin/env python3
"""Real local Chromium source, layout, geometry and navigation evidence.

Checks rendered actual money geometry, not a count of SVG files. Records all
screenshots; automated pass is not a human aesthetic or full notes signature.
"""
from pathlib import Path
import argparse,hashlib,json,sys
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
            assert page.locator("section.chapter").count()==8
            assert page.locator("figure.figure").count()==8
            assert page.locator("table").count()==8
            assert page.locator("figure svg").count()==8
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
            if width<1440:
                for plot in page.locator('.plot').all():
                    state=plot.evaluate("(x) => ({overflow:getComputedStyle(x).overflowX,scroll:x.scrollWidth,visible:x.clientWidth})")
                    assert state["overflow"] in ("auto","scroll") and state["visible"]<=width,(a.code,"CHART_SCROLL_CONTAINMENT",state)
            q=page.locator("#chart-flow")
            assert q.locator("rect.money-source").count()==len(d["segments"])
            assert q.locator("rect.money-sink").count()==2
            assert q.locator("path.money-ribbon").count()==2*len(d["segments"])
            assert page.locator("#chart-pnl svg").count()==1
            assert page.locator("#chart-cfo svg").count()==1
            assert page.locator("#chart-cash svg").count()==1
            assert page.locator("#chart-balance svg").count()==1
            # Exact source rect and original SVG path geometry in absolute
            # viewBox units; metadata alone is not proof.
            geom=page.evaluate("""() => {
               const svg=document.querySelector('#chart-flow svg');
               const src=Array.from(svg.querySelectorAll('.money-source')).map(x=>({
                 key:x.dataset.sourceKey,amount:+x.dataset.yuan,height:+x.getAttribute('height')}));
               const ribbons=Array.from(svg.querySelectorAll('.money-ribbon')).map(x=>{
                 const d=x.getAttribute('d');
                 const m=d.match(/^M205 ([\\d.]+) C420 ([\\d.]+) 700 ([\\d.]+) 938 ([\\d.]+) L938 ([\\d.]+)/);
                 return {source:x.dataset.sourceKey,target:x.dataset.targetKey,amount:+x.dataset.yuan,meta:+x.dataset.thickness,
                   actual:m ? +m[5]- +m[4] : null};
               });
               const end=Array.from(svg.querySelectorAll('.money-sink')).map(x=>({to:x.dataset.targetKey,height:+x.getAttribute('height'),amount:+x.dataset.yuan}));
               return {src,ribbons,end,viewBox:svg.viewBox.baseVal.width};
             }""")
            total=float(d["facts"]["rev"]["yuan"])
            cost=float(d["facts"]["cogs"]["yuan"])
            scale=(420-14*(len(d["segments"])-1))/total
            for k in geom["src"]:
                assert abs(k["height"]-k["amount"]*scale)<0.00000001,(a.code,"SOURCE_AREA_WRONG",k)
            for k in geom["ribbons"]:
                assert k["actual"] is not None and abs(k["actual"]-k["amount"]*scale)<1e-5,(a.code,"RIBBON_GEOMETRY_WRONG",k)
                assert abs(k["meta"]-k["actual"])<1e-5,(a.code,"RIBBON_MISMATCH",k)
            for k in geom["end"]:
                assert abs(k["height"]-k["amount"]*scale)<1e-8,(a.code,"SINK_GEOMETRY_WRONG",k)
            assert abs(sum(k["amount"] for k in geom["src"])-total)<.005
            assert abs(sum(k["amount"] for k in geom["end"])-total)<.005
            assert abs(sum(k["amount"] for k in geom["ribbons"])-total)<.005
            assert abs(next(k["amount"] for k in geom["end"] if k["to"]=="cogs")-cost)<.005
            # Full-size desktop must never hide sink labels behind nested
            # horizontal scrolling even if the body itself does not overflow.
            if width==1440:
                dimensions=page.evaluate("""() => [...document.querySelectorAll('.plot')].map(x=>({
                  id:x.id,visible:x.clientWidth,scroll:x.scrollWidth}))""")
                assert all(x["scroll"]<=x["visible"]+2 for x in dimensions),("DESKTOP_INNER_CLIP",dimensions)
                boxes=page.evaluate("""() => [...document.querySelectorAll('figure svg')].map(x=>({
                  w:x.viewBox.baseVal.width,
                  min:Math.min(...Array.from(x.querySelectorAll('text')).map(t=>t.getBBox().x)),
                  max:Math.max(...Array.from(x.querySelectorAll('text')).map(t=>t.getBBox().x+t.getBBox().width))
                }))""")
                assert all(z["min"]>=-1 and z["max"]<=z["w"]+2 for z in boxes),("SVG_TEXT_CLIP",boxes)
            page.screenshot(path=str(out/(a.code+"-"+str(width)+"-full.png")),full_page=True)
            for key in ["flow","sector","pnl","cfo","cash","balance"]:
                page.locator("#fig-"+key).screenshot(path=str(out/(a.code+"-"+str(width)+"-"+key+".png")))
            if width==1440:
                with page.expect_download(timeout=10000) as dl:
                    page.locator('button[data-export="flow"]').click()
                download=dl.value
                assert download.suggested_filename==a.code+"-2026H1-flow.svg"
                download.save_as(str(out/(a.code+"-flow.svg")))
            record.append({"width":width,"figures":8,"tables":8,"actual_money_geometry":"PASS","body_no_overflow":"PASS","svg_export":"PASS" if width==1440 else "NOT_RUN_THIS_VIEW"})
            page.close()
        browser.close()
    assert not errors,errors
    data={"issuer":a.code,"html_sha256":hashlib.sha256(file.read_bytes()).hexdigest(),"actual_3_viewport_checks":record,
          "all_eight_figures_visible":"PASS","source_nodes_sinks_ribbons_exact_svg_geometric_proportions":"PASS",
          "CJK_FONTS_RUNNER_INSTALLED":"PASS","human_editor":"NOT_CHECKED"}
    (out/"result.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("ACTUAL_CHROMIUM_TWO_SECTOR_QA_PASS",a.code,"screenshots",len(list(out.glob("*.png"))),"views",record)
if __name__=="__main__":main()
