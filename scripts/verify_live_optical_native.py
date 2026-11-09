#!/usr/bin/env python3
"""Actual current production Cloudflare optical finance release, source-byte bound.

This is NOT local set_content QA, nor an independent human editorial review.
A failing exact article SHA, 390 finance geometry, source route or CJK screenshot
means public production remains FAIL. Run only after changed main is deployed.
"""
from __future__ import annotations
import hashlib,json,os,time,urllib.request,sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/ashare-financial-storytelling/v7/engine'))
from quantified_optical_decision import CONFIG,decision_values

ROOT=Path(__file__).resolve().parents[1]
ORIGIN="https://financials-in-visuals.pages.dev"
OUT=ROOT/"research/visual-audit/live-optical-native"
OUT.mkdir(parents=True,exist_ok=True)
CODES=("300394","300502","300308")
WIDTHS=(1440,768,390)
SHA=lambda b:hashlib.sha256(b).hexdigest()

def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Financials-in-Visuals-release-proof/1.0"}),timeout=25) as response:
        return response.read()

def expected(code):
    return (ROOT/f"public/{code}.html").read_bytes()

def wait_for_real_deploy():
    for iteration in range(12):
        try:
            home=fetch(ORIGIN+"/")
            if SHA(home)!=SHA((ROOT/"public/index.html").read_bytes()):
                raise AssertionError("PUBLIC_INDEX_MAIN_SOURCE_SHA_DIFFERENCE")
            actual={code:SHA(fetch(ORIGIN+f"/{code}")) for code in CODES}
            expected_sha={code:SHA(expected(code)) for code in CODES}
            if actual==expected_sha:
                return SHA(home),actual
            print("REAL_PUBLIC_ARTICLE_SHA_NOT_YET_SOURCE_MAIN",iteration,actual,expected_sha,flush=True)
        except Exception as error:
            print("REAL_CLOUDFLARE_HTTP_NOT_PROVEN",iteration,str(error),flush=True)
        time.sleep(8)
    raise AssertionError("REAL_CLOUDFLARE_PUBLIC_ARTICLE_SHA_NOT_MATCHED_CURRENT_MAIN")

def run():
    home_sha,article_shas=wait_for_real_deploy()
    catalog=json.loads((ROOT/"site/research_catalog.json").read_text())["issuers"]
    assert len(catalog)>=11 and {code for code in CODES}<={x["code"] for x in catalog}
    results=[];screens=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(args=["--no-sandbox"])
        for width in WIDTHS:
            page=browser.new_page(viewport={"width":width,"height":900},device_scale_factor=1)
            page.goto(ORIGIN+"/",wait_until="networkidle")
            assert page.locator("a.company").count()==len(catalog),("REAL_UNIFIED_INDEX_COUNT",width)
            screenshot=OUT/f"live_directory_{width}.png"
            page.screenshot(path=str(screenshot),full_page=True)
            screens.append({"name":screenshot.name,"sha256":SHA(screenshot.read_bytes()),"bytes":screenshot.stat().st_size})
            page.close()
        for company in catalog:
            path=company["href"]
            content=fetch(ORIGIN+path)
            assert b"<html" in content.lower() or b"<!doctype" in content.lower(),("MISSING_INDEPENDENT_COMPANY_ROUTE",company["code"])
        for code in CODES:
            # Independent signed ledger identity is embedded in full HTML.
            ledgers={
                "300394":ROOT/"skills/ashare-financial-storytelling/v7/engine/sample-ledger.json",
                "300502":ROOT/"skills/ashare-financial-storytelling/v7/examples/xinyisheng-2026H1-ledger.json",
                "300308":ROOT/"skills/ashare-financial-storytelling/v7/examples/zhongji-2026H1-ledger.json",
            }
            ledgerpath=ledgers[code]
            ledger=json.loads(ledgerpath.read_text())
            pdf_sha=ledger["document"]["source_sha256"]
            assert len(pdf_sha)==64
            assert pdf_sha.encode() in expected(code),(code,"PUBLISHED_PDF_ORIGINAL_SHA_MISSING")
            for width in WIDTHS:
                page=browser.new_page(viewport={"width":width,"height":900},device_scale_factor=1,accept_downloads=True)
                page.goto(ORIGIN+"/",wait_until="networkidle")
                page.locator(f'a.company[href="/{code}.html"]').click()
                page.wait_for_load_state("networkidle")
                article_url=page.url
                assert article_url in (ORIGIN+f"/{code}",ORIGIN+f"/{code}.html"),(code,width,"ARTICLE_REDIRECTED_TO_DIRECTORY",article_url)
                assert page.locator("figure.exhibit.has-native-finance").count()>=9
                assert pdf_sha in page.content()
                if code in ("300394","300502"):
                    from decimal import Decimal as D
                    target=decision_values(ledger)
                    decision=page.locator('section#quantified-decision[data-research-schema="financials.optical_decision.v1"]')
                    assert decision.count()==1 and decision.is_visible(),(code,width,"LIVE_READER_VISIBLE_RESEARCH_NOT_RELEASED")
                    assert decision.get_attribute("data-original-pdf-sha256")==pdf_sha
                    assert decision.get_attribute("data-accounting-not-causal")=="true"
                    proof=decision.evaluate("""node=>({
                      facts:[...node.querySelectorAll('tr[data-fact-id]')].map(x=>({...x.dataset})),
                      derived:[...node.querySelectorAll('.optical-decision-metric')].map(x=>({...x.dataset})),
                      left:node.getBoundingClientRect().left,right:node.getBoundingClientRect().right,
                      fonts:[...node.querySelectorAll('.optical-decision-lead')].map(x=>+getComputedStyle(x).fontSize.replace('px',''))
                    })""")
                    assert len(proof["facts"])==8 and len(proof["derived"])==3,(code,width,"LIVE_RESEARCH_EVIDENCE_ROW_COUNT")
                    for fact in proof["facts"]:
                        key=fact["factId"]
                        expected=ledger["facts"][key]
                        specification=next(x for x in CONFIG[code] if x[0]==key)
                        assert D(fact["originalValue"])==D(expected["amount"]),(code,width,key,"LIVE_RESEARCH_SOURCE_YUAN_DIFFERENCE")
                        assert fact["period"]==specification[1] and fact["statementKind"]==specification[2]
                        assert fact["sourceUnit"]==specification[3] and int(fact["physicalPage"])==expected["page"]
                    assert {x["derivedKey"]:D(x["derivedRatio"]) for x in proof["derived"]}=={
                        k:v for k,_,v in target["metrics"]},(code,width,"LIVE_RESEARCH_QUANTIFIED_DECISION_WRONG")
                    assert proof["left"]>=-1 and proof["right"]<=width+2
                    assert proof["fonts"] and min(proof["fonts"])>=14,(code,width,"LIVE_RESEARCH_LEAD_TOO_SMALL")
                    assert "NOT_CHECKED" in decision.inner_text(),(code,width,"MISSING_RESEARCH_CAUSALITY_BOUNDARY")
                    shot=OUT/f"live_{code}_decision_{width}.png"
                    decision.screenshot(path=str(shot),animations="disabled")
                    screens.append({"name":shot.name,"sha256":SHA(shot.read_bytes()),"bytes":shot.stat().st_size})
                if code=="300308":
                    assert pdf_sha=="e0ecd7c365c65e90b1fa4b4616ba3f4649449d64451e0ba0b1b78ba9ce3170bf"
                    proof=json.loads((ROOT/"research/issuers/300308/source-verification.json").read_text(encoding="utf8"))
                    assert proof["source_page_amount_checks"]==63 and proof["indirect_CFO_all_original_signed_adjustments"]==15
                    assert "422,649,612.97" in page.locator(".disclosure-conflict").inner_text()
                    assert "422,649,613.97" in page.locator(".disclosure-conflict").inner_text()
                    assert "独立第二名人类研究分析师" in page.content()

                assert page.evaluate("document.documentElement.scrollWidth")<=width+2,(code,width,"FULL_HTML_BODY_HORIZONTAL_OVERFLOW")
                # All three optical issuers migrated to original-yuan V9
                # source -> consolidated revenue -> own reported COGS / GP.
                # The old native-money-* classes, widths and filter buttons
                # were removed. Never let a stale selector hide a real
                # financial regression or falsely fail a lawful upgrade.
                state=page.evaluate("""() => {
                  const f=[...document.querySelectorAll('figure.has-native-finance')][0];
                  const native=f.querySelector('.native-finance'),desktop=f.querySelector('.chart-shell');
                  const sourceSvg=native.querySelector('svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"][data-chart-grammar="SOURCE_REVENUE_OUTCOME_CONNECTED_SANKEY"]');
                  const desktopSvg=desktop.querySelector('svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"][data-chart-grammar="SOURCE_REVENUE_OUTCOME_CONNECTED_SANKEY"]');
                  const info=svg=>svg?{
                    total:svg.dataset.revenueYuan,scale:svg.dataset.scaleYuanPerSvgUnit,
                    nodes:[...svg.querySelectorAll('rect[data-node-role][data-node-yuan]')].map(n=>({
                      id:n.dataset.nodeId,role:n.dataset.nodeRole,
                      money:n.dataset.nodeYuan,height:n.getAttribute('height')})),
                    ribbons:[...svg.querySelectorAll('path[data-stage][data-ribbon-yuan]')].map(p=>({
                      stage:p.dataset.stage,source:p.dataset.sourceId,outcome:p.dataset.outcomeId,
                      money:p.dataset.ribbonYuan,scale:p.dataset.scaleYuanPerSvgUnit,d:p.getAttribute('d')}))
                  }:null;
                  return {figures:document.querySelectorAll('figure.has-native-finance').length,
                    nativeVisible:getComputedStyle(native).display!=='none',
                    desktopVisible:getComputedStyle(desktop).display!=='none',
                    inner:native.scrollWidth,client:native.clientWidth,
                    original:info(desktopSvg),current:info(sourceSvg),
                    signed:document.querySelectorAll('.native-signed-svg').length,
                    bodyOverflow:document.documentElement.scrollWidth-window.innerWidth};
                }""")
                from decimal import Decimal as D
                assert state["original"] and state["current"],(code,width,"REAL_V9_SOURCE_SVG_MISSING")
                graph=state["current"] if width<900 else state["original"]
                amount=D(ledger["facts"]["revenue"]["amount"])
                costs=D(ledger["facts"]["cogs"]["amount"])
                assert D(graph["total"])==amount and D(graph["scale"])>0,(code,width,"GROUP_REVENUE_OR_SCALE_NOT_SOURCE_BOUND")
                parts=ledger["segments"]
                exact={x["revenue_key"]:D(ledger["facts"][x["revenue_key"]]["amount"]) for x in parts}
                expected_cost={x["revenue_key"]:D(ledger["facts"][x["cost_key"]]["amount"]) for x in parts}
                assert len(exact)==len(parts),(code,width,"DUPLICATED_DISCLOSED_REVENUE_SOURCE")
                nodes=graph["nodes"]
                sources=[x for x in nodes if x["role"]=="source"]
                group=[x for x in nodes if x["role"]=="total" and x["id"]=="revenue-total"]
                sinks=[x for x in nodes if x["role"] in ("cost","profit")]
                assert len(sources)==len(parts) and len(group)==1 and len(sinks)==2,(code,width,"WRONG_SOURCE_TOTAL_GP_NODES")
                assert {x["id"]:D(x["money"]) for x in sources}==exact,(code,width,"ORIGINAL_PER_BUSINESS_YUAN_CHANGED")
                assert D(group[0]["money"])==amount
                assert {x["role"]:D(x["money"]) for x in sinks}=={"cost":costs,"profit":amount-costs}
                assert all(abs(D(x["height"])-D(x["money"])/D(graph["scale"]))<D(".001") for x in nodes),(code,width,"FALSE_ORIGINAL_AMOUNT_NODE_HEIGHT")
                ribbons=graph["ribbons"]
                inbound=[x for x in ribbons if x["stage"]=="source-to-revenue"]
                outbound=[x for x in ribbons if x["stage"]=="revenue-to-outcome"]
                expected_out=sum(int(expected_cost[k]>0)+int(exact[k]>expected_cost[k]) for k in exact)
                assert len(inbound)==len(parts) and len(outbound)==expected_out,(code,width,"NONCONSERVED_REVENUE_OR_PHANTOM_ZERO_MONEY_RIBBON")
                assert {x["source"]:D(x["money"]) for x in inbound}==exact
                expected_alloc={(k,"group_cogs"):expected_cost[k] for k in exact if expected_cost[k]>0}
                expected_alloc.update({(k,"group_gp"):exact[k]-expected_cost[k] for k in exact if exact[k]>expected_cost[k]})
                assert {(x["source"],x["outcome"]):D(x["money"]) for x in outbound}==expected_alloc,(code,width,"INVENTED_PRODUCT_GROSS_PROFIT_OR_COST_SPLIT")
                assert sum((D(x["money"]) for x in inbound),D(0))==amount
                assert sum((D(x["money"]) for x in outbound),D(0))==amount
                assert all(D(x["scale"])>0 and x["d"].startswith("M ") and " C " in x["d"] for x in ribbons)
                assert state["signed"]>=(4 if code=="300308" else 5)
                if code=="300308":
                    from decimal import Decimal as D
                    graphs=page.locator('figure.exhibit svg[data-signed-statement-grammar="FINANCIALS_TYPED_FULL_PNL_SIGNED_V1"]')
                    assert graphs.count()==2,(code,width,"LIVE_CANONICAL_PNL_DUAL_EDITIONS_MISSING")
                    real=graphs.nth(1) if width<900 else graphs.nth(0)
                    hidden=graphs.nth(0) if width<900 else graphs.nth(1)
                    assert real.is_visible() and not hidden.is_visible(),(code,width,"LIVE_OPTICAL_PNL_MOBILE_DESKTOP_WRONG_VERSION")
                    evidence=real.evaluate("""svg=>{
                      let b=svg.getBoundingClientRect(),vb=svg.viewBox.baseVal;
                      let labels=[...svg.querySelectorAll('text')].map(x=>{let r=x.getBBox();return {l:r.x,right:r.x+r.width,b:r.y+r.height}});
                      return {sha:svg.dataset.originalPdfSha256,
                        gross:svg.dataset.startGrossYuan,net:svg.dataset.endNetYuan,
                        clipped:b.left< -2||b.right>innerWidth+2||svg.parentElement.scrollWidth>svg.parentElement.clientWidth+2,
                        labelClip:labels.filter(x=>x.l< -2||x.right>vb.width+2||x.b>vb.height+2),
                        stages:[...svg.querySelectorAll('rect.unified-signed-statement-step')].map(n=>({
                          id:n.dataset.stageId,before:n.dataset.beforeYuan,delta:n.dataset.signedYuan,
                          after:n.dataset.afterYuan,width:n.getAttribute('width'),
                          scale:n.dataset.moneyScaleYuanPerUnit,ids:n.dataset.sourceFactIds,pages:n.dataset.physicalPages,
                          proof:n.dataset.moneyProvenance}))};
                    }""")
                    assert evidence["sha"]==pdf_sha and not evidence["clipped"] and not evidence["labelClip"],(code,width,"LIVE_OPTICAL_SIGNED_PNL_CJK_CLIPPED",evidence)
                    assert D(evidence["gross"])==D(ledger["facts"]["revenue"]["amount"])-D(ledger["facts"]["cogs"]["amount"])
                    assert D(evidence["net"])==D(ledger["facts"]["net_profit"]["amount"]) and len(evidence["stages"])==7
                    assert any(z["proof"]=="DERIVED_UNATTRIBUTED_GROUP_OPERATING_NET_DIFFERENCE" for z in evidence["stages"]),(code,width,"FAKE_OPTICAL_OPERATING_PROFIT_ATTRIBUTION")
                    for z in evidence["stages"]:
                        assert D(z["before"])+D(z["delta"])==D(z["after"])
                        assert abs(D(z["width"])-abs(D(z["delta"]))/D(z["scale"]))<D(".000001"),(code,width,"LIVE_OPTICAL_PNL_FALSE_MONEY_LENGTH",z)
                        assert z["ids"] and z["pages"]
                if width<900 and code in ("300394","300502"):
                    # Original-yuan Sankey source business name and exact
                    # amount/margin are now separate, genuinely legible
                    # Noto CJK 11-unit rows. Actual screen rectangles—not
                    # merely nominal source font-size—must not intersect.
                    # 300308 is separately source-pinned and unchanged.
                    legend=page.evaluate("""() => {
                      const svg=document.querySelector('.native-finance svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"]');
                      if(!svg)return null;
                      const words=[...svg.querySelectorAll('text[data-editorial-role="source-summary"]')];
                      const header=svg.querySelector('text[data-editorial-role="source-stage-header"]');
                      return {words:words.map(el=>({
                        text:el.textContent,font:+el.getAttribute('font-size'),
                        top:el.getBoundingClientRect().top,
                        bottom:el.getBoundingClientRect().bottom})),
                        headerTop:header?.getBoundingClientRect().top};
                    }""")
                    assert legend and len(legend["words"])==2*len(parts),(code,width,"LIVE_OPTICAL_SOURCE_NAME_AND_MONEY_ROWS_MISSING")
                    glyphs=legend["words"]
                    assert all(g["font"]>=11 for g in glyphs),(code,width,"LIVE_OPTICAL_MONEY_SOURCE_LABEL_TOO_SMALL")
                    assert all(glyphs[i]["bottom"]+.5<glyphs[i+1]["top"] for i in range(len(glyphs)-1)),(code,width,"LIVE_OPTICAL_MONEY_SOURCE_LABELS_OVERPRINT",glyphs)
                    assert legend["headerTop"] is not None and glyphs[-1]["bottom"]+2<legend["headerTop"],(code,width,"LIVE_OPTICAL_SOURCES_OVERPRINT_REVENUE_HEADER",legend)
                if width<900:
                    assert state["nativeVisible"] and not state["desktopVisible"] and state["inner"]<=state["client"]+2,(code,width,"PUBLIC_NATIVE_MONEY_HIDDEN_OR_CROPPED",state)
                    figures=page.evaluate("""() => [...document.querySelectorAll('figure.has-native-finance')].map(f=>{
                      const n=f.querySelector('.native-finance');
                      return {inner:n.scrollWidth,visible:n.clientWidth,display:getComputedStyle(n).display};
                    })""")
                    assert all(z["inner"]<=z["visible"]+2 and z["display"]!="none" for z in figures),(code,width,"PUBLIC_OTHER_FINANCE_FIGURE_INTERNAL_SCROLL")
                else:
                    assert not state["nativeVisible"] and state["desktopVisible"]
                    with page.expect_download() as export:
                        page.locator("figure.exhibit .svg-save").first.click()
                    assert export.value.suggested_filename.endswith(".svg"),(code,"LIVE_EDITABLE_FINANCIAL_SVG_EXPORT_MISSING")
                if width==390:
                    # Selection buttons belonged to the retired issuer-only
                    # mobile money illustrator. The current editable V9 SVG
                    # must preserve all source IDs, exact CNY and all stages.
                    assert state["nativeVisible"] and not state["desktopVisible"]
                    assert len(state["current"]["ribbons"])==len(ribbons)
                    assert {x["source"] for x in inbound}==set(exact),(code,"MISSING_ACTUAL_SOURCE_NAVIGABLE_FACT_IDS")
                screenshot=OUT/f"live_{code}_{width}.png"
                page.screenshot(path=str(screenshot),full_page=True)
                screens.append({"name":screenshot.name,"sha256":SHA(screenshot.read_bytes()),"bytes":screenshot.stat().st_size})
                page.locator('a.site-library-link[href="/#companies"]').first.click()
                assert page.url==ORIGIN+"/#companies",(code,width,"RETURN_TO_SINGLE_COMPANY_DIRECTORY_FAILED",page.url)
                results.append({"code":code,"width":width,"real_article_url":article_url,"article_html_sha256":article_shas[code],"pdf_source_sha":pdf_sha,
                    "real_return_to_library":"PASS","source_weighted_cost_gp":"PASS","native_390_unclipped":"PASS" if width==390 else "NOT_PHONE",
                    "reader_visible_original_source_decision":"PASS" if code in ("300394","300502") else "NOT_THIS_MIGRATION"})
                page.close()
        browser.close()
    receipt={"source_main_commit":os.environ.get("GITHUB_SHA","NOT_CHECKED"),"company_directory_issuer_count":len(catalog),
        "actual_public_site":ORIGIN,"actual_home_complete_html_sha256":home_sha,"real_public_company_complete_html_sha256":article_shas,
        "real_CJK_1440_768_390_financial_editorial":results,"real_screenshots":screens,
        "independent_human_financial_editor":"NOT_CHECKED","independent_human_art_director":"NOT_CHECKED",
        "exhaustive_material_notes":"NOT_CHECKED"}
    (OUT/"result.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    assert len(results)==len(CODES)*len(WIDTHS) and len(screens)==(len(CODES)+1+2)*len(WIDTHS)
    print("ACTUAL_REAL_CLOUDFLARE_OPTICAL_SOURCE_THREE_ARTICLES_THREE_CHINESE_WIDTHS_EXACT_HTML_SOURCE_SHA_PASS",json.dumps({"commit":receipt["source_main_commit"],"articles":article_shas,"screenshots":len(screens)},ensure_ascii=False),flush=True)

if __name__=="__main__":run()
