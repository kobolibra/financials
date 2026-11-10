#!/usr/bin/env python3
"""Dynamic canonical-catalog browser evidence for every article and figure.

No issuer whitelist. Measurements are observations, not an aesthetic score.
Every captured figure and browser state is bound to the actual article bytes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

MEASURE=r"""() => {
 const visible=e=>{const b=e.getBoundingClientRect(),s=getComputedStyle(e);
  return b.width>1&&b.height>1&&s.display!=='none'&&s.visibility!=='hidden'};
 const box=e=>{const b=e.getBoundingClientRect();return {left:b.left,right:b.right,top:b.top,bottom:b.bottom,width:b.width,height:b.height}};
 const svgs=[...document.querySelectorAll('svg')].filter(visible);
 return {body:{client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth},
  figures:[...document.querySelectorAll('figure,section[data-comparative-economics]')].map((f,i)=>({index:i,id:f.id,
    title:(f.querySelector('h2,h3,h4,.question')?.textContent||f.textContent).trim().slice(0,100),
    box:box(f),visibleSvgCount:[...f.querySelectorAll('svg')].filter(visible).length,
    hasEvidence:!!f.querySelector('table,details'),
    hasAlternative:/反证|反方|替代|竞争|边界|counter/i.test(f.textContent)})),
  svgs:svgs.map((s,i)=>{
    const bounds=box(s),vb=s.viewBox.baseVal,ctm=s.getScreenCTM();
    const labels=[...s.querySelectorAll('text')].filter(visible).map(t=>{
      const b=box(t);return {text:t.textContent.trim().slice(0,90),...b,
       actualFont:parseFloat(getComputedStyle(t).fontSize)*Math.hypot(ctm.a,ctm.b)};
    }).filter(t=>t.text);
    const clipped=labels.filter(t=>t.left<bounds.left-2||t.right>bounds.right+2||t.top<bounds.top-2||t.bottom>bounds.bottom+2);
    const overlaps=[];
    for(let a=0;a<labels.length;a++)for(let b=a+1;b<labels.length;b++){
      const x=labels[a],y=labels[b];
      const iw=Math.min(x.right,y.right)-Math.max(x.left,y.left),ih=Math.min(x.bottom,y.bottom)-Math.max(x.top,y.top);
      if(iw>2&&ih>2&&iw*ih>Math.min(x.width*x.height,y.width*y.height)*.15)overlaps.push([x.text,y.text]);
    }
    return {index:i,figure:s.closest('figure')?.id||null,grammar:s.dataset.chartGrammar||s.dataset.signedStatementGrammar||s.dataset.figureKind||'OTHER',
      bounds,viewBox:[vb.width,vb.height],labelCount:labels.length,
      smallestActualFont:labels.length?Math.min(...labels.map(t=>t.actualFont)):null,
      below10px:labels.filter(t=>t.actualFont<10).length,
      clippedLabels:clipped,possibleLabelOverlaps:overlaps,
      ribbons:[...s.querySelectorAll('path[data-ribbon-yuan]')].map(p=>({amount:p.dataset.ribbonYuan,scale:p.dataset.scaleYuanPerSvgUnit,d:p.getAttribute('d')}))};
  })};
}"""


def audit(out:Path, widths=(1440,768,390)):
    from playwright.sync_api import sync_playwright
    from decimal import Decimal as D
    import re
    catalog=json.loads((ROOT/"site/research_catalog.json").read_text())
    out.mkdir(parents=True,exist_ok=True)
    records=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for issuer in catalog["issuers"]:
            route=issuer["href"]
            file=(ROOT/"public"/route.lstrip("/")).resolve()
            file.relative_to((ROOT/"public").resolve())
            raw=file.read_bytes();sha=hashlib.sha256(raw).hexdigest()
            for width in widths:
                page=browser.new_page(viewport={"width":width,"height":960})
                errors=[]
                page.on("pageerror",lambda error: errors.append(str(error)))
                page.goto(file.as_uri(),wait_until="load")
                page.evaluate("document.fonts.ready")
                measured=page.evaluate(MEASURE)
                exports=[]
                for button in page.locator('[data-export-economics]').all():
                    with page.expect_download() as pending:button.click()
                    download=pending.value
                    dest=out/download.suggested_filename
                    download.save_as(dest)
                    root=ET.fromstring(dest.read_text())
                    expected=330 if width<=850 else 1040
                    if float(root.attrib['width'])!=expected or root.attrib['data-layout']!=('native-330' if expected==330 else 'editorial-1040'):
                        raise ValueError('EXPORTED_LAYOUT_IS_NOT_VISIBLE_LAYOUT')
                    exports.append({'file':dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'width':expected})
                for svg in measured["svgs"]:
                    geometry=[]
                    for ribbon in svg.pop("ribbons"):
                        coords=[D(n) for n in re.findall(r"-?\d+(?:\.\d+)?",ribbon["d"])]
                        # Our canonical cubic ribbon has exactly 16 values:
                        # start upper, controls/end upper, end lower, return.
                        if len(coords)!=16:
                            geometry.append("UNSUPPORTED_PATH_COMMANDS");continue
                        expected=D(ribbon["amount"])/D(ribbon["scale"])
                        if (abs(abs(coords[15]-coords[1])-expected)>D(".001")
                                or abs(abs(coords[9]-coords[7])-expected)>D(".001")):
                            geometry.append("RIBBON_ENDPOINT_AMOUNT_MISMATCH")
                    svg["canonical_ribbon_endpoint_issues"]=geometry
                for fig in measured["figures"]:
                    image=out/f'{issuer["code"]}-{width}-{fig["index"]:02d}.png'
                    locator=page.locator("figure,section[data-comparative-economics]").nth(fig["index"])
                    locator.screenshot(path=str(image),animations="disabled")
                    fig["screenshot"]=image.name
                    fig["screenshot_sha256"]=hashlib.sha256(image.read_bytes()).hexdigest()
                record={"issuer":issuer["code"],"name":issuer["name"],"route":route,
                        "width":width,"article_sha256":sha,"js_errors":errors,"economics_svg_exports":exports,**measured}
                records.append(record)
                print("ARTICLE_ALL_FIGURES_OBSERVED",issuer["code"],width,len(measured["figures"]),flush=True)
                page.close()
        browser.close()
    blockers=[]
    for row in records:
        if row["js_errors"]:blockers.append([row["issuer"],row["width"],"JS_ERROR"])
        if row["body"]["scroll"]>row["body"]["client"]+2:blockers.append([row["issuer"],row["width"],"BODY_OVERFLOW"])
        for svg in row["svgs"]:
            if svg['clippedLabels']:blockers.append([row['issuer'],row['width'],svg['index'],'SVG_LABEL_CLIPPED'])
            if svg['possibleLabelOverlaps']:blockers.append([row['issuer'],row['width'],svg['index'],'SVG_LABEL_OVERLAP_REQUIRES_REVIEW'])
            if svg["canonical_ribbon_endpoint_issues"]:blockers.append([row["issuer"],row["width"],svg["index"],"RIBBON_AMOUNT"])
    result={"schema":"financials.delivery_matrix.v1","scope":"LOCAL_CURRENT_HTML_OBSERVATION",
        "issuer_count":len(catalog["issuers"]),"article_viewports":len(records),
        "figure_observations":sum(len(r["figures"]) for r in records),
        "blockers":blockers,"records":records,
        "font_and_overlap_findings":"EDITORIAL_REVIEW_REQUIRED_NOT_AUTOMATIC_AESTHETIC_SCORE",
        "independent_financial_and_art_review":"NOT_CHECKED","live_sha_match":"NOT_CHECKED"}
    (out/"result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    return result


if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args();result=audit(args.out)
    print("DELIVERY_MATRIX_OBSERVED",result["article_viewports"],result["figure_observations"],"BLOCKERS",len(result["blockers"]))
    raise SystemExit(1 if result["blockers"] else 0)
