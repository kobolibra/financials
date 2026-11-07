#!/usr/bin/env python3
"""Cross-company real CJK Chromium editorial screenshot matrix (11 x 3).

This is NOT a signoff from an independent art director. It inspects the same
visible source-money figure on real browsers, including genuinely different
insured premiums and lawful signed no-Sankey cases; preserves CSS, measures
literal text bounding boxes, screenshots and binds every output to file bytes.
It does not falsely certify a professional 5-second comprehension review.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
CANONICAL={"300394","300308","300502","600036","688111","600519",
           "000333","688220","600900","600276","601628"}
INSURANCE="INSURANCE_PREMIUM_SOURCE_NEW_RENEW_TOTAL"
INCOME="SOURCE_REVENUE_OUTCOME_CONNECTED_SANKEY"
WIDTHS=((1440,900),(768,1024),(390,844))

def qa(out:Path):
    catalog=json.loads((ROOT/"site/research_catalog.json").read_text())
    company_rows=catalog["issuers"]
    if len(company_rows)!=11 or {x["code"] for x in company_rows}!=CANONICAL:
        raise AssertionError("CANONICAL_11_COMPANY_RESEARCH_SCOPE_CHANGED")
    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for item in company_rows:
            code=item["code"]
            html=ROOT/"public"/item["href"].lstrip("/")
            if not html.is_file(): raise AssertionError(("MISSING_ORIGINAL_COMPANY_ARTICLE",code))
            content=html.read_bytes()
            sha=hashlib.sha256(content).hexdigest()
            for width,height in WIDTHS:
                page=browser.new_page(viewport={"width":width,"height":height},device_scale_factor=1,
                    accept_downloads=True)
                errors=[]
                page.on("pageerror",lambda error:errors.append(str(error)))
                page.goto(html.as_uri(),wait_until="load",timeout=30000)
                page.wait_for_timeout(120)
                state=page.evaluate("""() => {
                  const body=document.documentElement;
                  const all=[...document.querySelectorAll('svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"]')];
                  const visible=all.filter(e=>{
                    const b=e.getBoundingClientRect();
                    return b.width>=145&&b.height>65;
                  });
                  const chosen=visible.find(e=>e.getAttribute('data-chart-grammar')==='INSURANCE_PREMIUM_SOURCE_NEW_RENEW_TOTAL')||
                    visible.find(e=>e.getAttribute('data-chart-grammar')==='SOURCE_REVENUE_OUTCOME_CONNECTED_SANKEY')||visible[0]||null;
                  if(!chosen)return {found:false,available:all.length,client:body.clientWidth,scroll:body.scrollWidth};
                  const r=chosen.getBoundingClientRect();
                  const labels=[...chosen.querySelectorAll('text')].filter(e=>e.textContent.trim()).map(e=>{
                    const bb=e.getBoundingClientRect();
                    return {name:e.textContent.slice(0,70),size:parseFloat(getComputedStyle(e).fontSize),
                      x:bb.left,y:bb.top,right:bb.right,bottom:bb.bottom};
                  });
                  const cut=labels.filter(x=>x.x<r.left-3||x.right>r.right+3||x.y<r.top-3||x.bottom>r.bottom+3);
                  const ribbons=[...chosen.querySelectorAll('path[data-ribbon-yuan]')];
                  return {found:true,available:all.length,client:body.clientWidth,scroll:body.scrollWidth,
                    chosen:{grammar:chosen.getAttribute('data-chart-grammar'),kind:chosen.getAttribute('data-figure-kind'),
                      width:r.width,height:r.height,box_width:chosen.viewBox?.baseVal?.width,
                      monetary_total:chosen.getAttribute('data-revenue-yuan')||chosen.getAttribute('data-premium-yuan'),
                      source_nodes:chosen.querySelectorAll('rect[data-node-role="source"],rect[data-node-role="premium-source"]').length,
                      total_nodes:chosen.querySelectorAll('rect[data-node-role="total"],rect[data-node-role="premium-total"]').length,
                      ribbon_count:ribbons.length,
                      paths_staged:[...new Set(ribbons.map(e=>e.getAttribute('data-stage')))]},
                    titles:labels.length,min_font_px:labels.length?Math.min(...labels.map(x=>x.size)):null,
                    cut:cut.slice(0,12),bounds:{left:r.left,right:r.right,top:r.top,bottom:r.bottom}};
                }""")
                if errors: raise AssertionError(("ACTUAL_BROWSER_JS_ERRORS",code,width,errors[:4]))
                if state["scroll"]>width+1:
                    raise AssertionError(("COMPANY_HAS_HIDDEN_HORIZ_BODY_SCROLL",code,width,state))
                if code!="600519":
                    if not state["found"]:raise AssertionError(("CURRENT_PRIMARY_COMPANY_FINANCE_SVG_NOT_VISIBLE",code,width,state))
                    primary=state["chosen"]
                    needed=INSURANCE if code=="601628" else INCOME
                    if primary["grammar"]!=needed or primary["total_nodes"]!=1 or not primary["monetary_total"]:
                        raise AssertionError(("COMPANY_WRONG_FINANCE_GRAPH",code,width,primary))
                    if code=="601628" and (primary["source_nodes"]!=4 or primary["ribbon_count"]!=6):
                        raise AssertionError(("INSURANCE_OLD_PREMIUM_4_2_1_NOT_DISPLAYED",code,width,primary))
                    if (code not in {"601628"} and primary["source_nodes"]<2):
                        raise AssertionError(("INDUSTRIAL_SOURCE_TO_MONEY_MISSING",code,width,primary))
                    if width==390 and (primary["width"]>width or primary["box_width"]!=330):
                        raise AssertionError(("MOBILE_NOT_NATIVE_330_LAYOUT",code,width,primary))
                    if width==1440 and primary["box_width"] not in (1100,):
                        raise AssertionError(("DESKTOP_NOT_UNIFIED_1100_LAYOUT",code,width,primary))
                    # A text bbox outside the primary SVG is a blocking
                    # source-layout integrity issue, not merely a CSS color.
                    if state["cut"]:
                        raise AssertionError(("SOURCE_MONEY_SVG_CJK_LABEL_CLIPPED",code,width,state["cut"]))
                else:
                    if "data-flow-omission" not in page.content():
                        raise AssertionError(("NEGATIVE_MARGIN_SOURCE_SIGNED_EXCEPTION_LOST",code,width))
                image_name=f"{code}-source-finance-{width}.png"
                if state["found"]:
                    locator=page.locator('svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"]')
                    # Select ACTUAL visible figure, not CSS-hidden desktop SVG
                    # in the mobile DOM. Locator.index is original DOM index.
                    all_boxes=locator.all()
                    target=next((x for x in all_boxes if x.bounding_box() and
                         x.bounding_box()["width"]>=145 and x.bounding_box()["height"]>65),None)
                    if target is None:raise AssertionError(("SCREENSHOT_NOT_ACTUAL_VISIBLE_FINANCE",code,width))
                    target.screenshot(path=str(out/image_name),animations="disabled",timeout=15000)
                else:
                    page.screenshot(path=str(out/image_name),full_page=False,animations="disabled")
                raw=(out/image_name).read_bytes()
                rows.append({"code":code,"width":width,"source_html_sha256":sha,
                    "source_html_bytes":len(content),"browser_js_error_count":0,
                    "full_body_no_horiz_scroll":"PASS","visible_finance":state,
                    "screenshot":image_name,"screenshot_sha256":hashlib.sha256(raw).hexdigest(),
                    "screenshot_bytes":len(raw),
                    "independent_editorial_human":"NOT_CHECKED"})
                page.close()
        browser.close()
    if len(rows)!=33:raise AssertionError("THREE_ACTUAL_VIEWPORTS_PER_ELEVEN_MISSING")
    receipt={"schema":"financials.eleven.actual_cjk_side_by_side.v1",
             "scope":"CURRENT_PR_LOCAL_CJK_BROWSER_SOURCE_BYTES",
             "all_11_factual_money_visibility_and_geometry":"PASS",
             "full_11_issuer_aesthetic_and_research":"NOT_ESTABLISHED",
             "human_second_art_and_financial_editor":"NOT_CHECKED",
             "production_live_same_html_sha":"NOT_CHECKED",
             "count_issuer":11,"count_viewport":33,"screenshots":rows}
    (out/"result.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    print("ELEVEN_COMPANIES_ACTUAL_33_CJK_FINANCE_FIGURE_SCREENSHOTS_LOCAL_ONLY",len(rows))
    return receipt

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=ROOT/"research/quality/pr35-11-finance-original-browser")
    args=ap.parse_args()
    qa(args.out)
