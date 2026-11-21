#!/usr/bin/env python3
"""Actual browser proof for source-true income Sankeys; no invented approval.

Capture *current* HTML and SVG bytes in native Chromium and WebKit at target
viewports. Independently inspect crossing geometry and preserve screenshot
paths/SHA for an editorial reviewer. This is a geometry/source browser receipt,
NOT an independent aesthetic or financial research signoff.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from decimal import Decimal as D
from pathlib import Path
from playwright.sync_api import sync_playwright

ROUTES = (
    "600206.html","600690.html","300548.html","300570.html",
    "688220.html","300394.html","300502.html","300308.html",
    "research/2026-h1-v10/688111.html",
    "research/2026-h1-v10/000333.html",
    "research/2026-h1-v10/600036.html",
)

def decimal_coords(d):
    return [D(v) for v in re.findall(r"-?\d+(?:\.\d+)?", d)]

def audit_svg(svg, route):
    import xml.etree.ElementTree as E
    root = E.fromstring(svg)
    uri = "{http://www.w3.org/2000/svg}"
    scale = D(root.attrib["data-scale-yuan-per-svg-unit"])
    if scale <= 0:
        raise ValueError("NONPOSITIVE_SCALE " + route)
    ribbons = []
    for el in root.iter(uri+"path"):
        if el.attrib.get("data-stage") != "revenue-to-outcome":
            continue
        coords = decimal_coords(el.attrib["d"])
        if len(coords) != 16:
            raise ValueError("BAD_PATH_COORDINATES " + route)
        val = D(el.attrib["data-ribbon-yuan"])
        thickness = val / scale
        if val <= 0 or abs(abs(coords[15]-coords[1])-thickness) > D("0.0001") or abs(abs(coords[9]-coords[7])-thickness) > D("0.0001"):
            raise ValueError("RIBBON_AMOUNT_SCALE_MISMATCH " + route)
        ribbons.append(((coords[1]+coords[15])/2,(coords[7]+coords[9])/2))
    if not ribbons:
        raise ValueError("NO_OUTCOME_RIBBONS " + route)
    for i,a in enumerate(ribbons):
        for b in ribbons[i+1:]:
            if (a[0]-b[0])*(a[1]-b[1]) < D("-0.00001"):
                raise ValueError("PUBLISHED_SVG_CROSSED " + route)
    return len(ribbons)

def run(root, out):
    out.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"financials.current_sankey_native_browser.v1",
             "status":"MACHINE_SOURCE_GEOMETRY_ONLY",
             "independent_art_and_financial_review":"NOT_CHECKED",
             "routes":[]}
    with sync_playwright() as p:
        for browser_name,viewports in (("chromium",(1440,768,390)),("webkit",(375,))):
            browser=getattr(p,browser_name).launch(headless=True)
            try:
                for route in ROUTES:
                    path=root/"public"/route
                    raw=path.read_bytes()
                    expected=hashlib.sha256(raw).hexdigest()
                    name=route.replace("/","__").replace(".html","")
                    for width in viewports:
                        ctx=browser.new_context(viewport={"width":width,"height":960},device_scale_factor=1,accept_downloads=True)
                        page=ctx.new_page()
                        errors=[]
                        page.on("pageerror",lambda exc:errors.append(str(exc)))
                        page.goto(path.resolve().as_uri(),wait_until="domcontentloaded",timeout=30000)
                        locator=page.locator('svg[data-chart-grammar="SOURCE_REVENUE_OUTCOME_CONNECTED_SANKEY"]')
                        count=locator.count()
                        if route.endswith("600036.html"):
                            assert count>=1,(route,"BANK_GRAPH_MISSING")
                        else:
                            assert count>=1,(route,"SOURCE_GRAPH_MISSING")
                        screenshot_count=0
                        for i in range(count):
                            svg=locator.nth(i)
                            source=svg.evaluate("(x)=>x.outerHTML")
                            ribbons=audit_svg(source,route)
                            visible=svg.is_visible() and svg.evaluate("(x)=>{let r=x.getBoundingClientRect();return r.width>=30&&r.height>=30}")
                            if visible:
                                pic=out/f"{name}__{browser_name}__{width}__{i}.png"
                                svg.screenshot(path=pic,animations="disabled",timeout=15000)
                                screenshot_count+=1
                                picsha=hashlib.sha256(pic.read_bytes()).hexdigest()
                                receipt["routes"].append({"route":route,"html_sha256":expected,
                                    "engine":browser_name,"viewport_width":width,
                                    "svg_index":i,"ribbons":ribbons,"screenshot":str(pic),
                                    "screenshot_sha256":picsha,"all_source_values":"RENDERED",
                                    "geometry_crossings":0,"status":"SOURCE_GEOMETRY_PASS"})
                        if screenshot_count==0:
                            raise ValueError("NO_VISIBLE_SVG "+route+" "+str(width))
                        if errors:
                            raise ValueError("PAGE_RUNTIME_ERROR "+route+" "+str(errors))
                        ctx.close()
                        print("CURRENT_SOURCE_SANKEY_NATIVE_BROWSER_PASS",route,browser_name,width,
                              "screenshots",screenshot_count,"sha",expected,flush=True)
            finally:
                browser.close()
    (out/"receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    return receipt

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    run(a.root,a.out)
