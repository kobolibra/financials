#!/usr/bin/env python3
"""Independent REAL Cloudflare full HTML + Chromium semiconductor mobile release.
No manual human design approval is asserted.
"""
from __future__ import annotations
import hashlib,json,os,time,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
ORG="https://financials-in-visuals.pages.dev"
OUT=ROOT/"research/issuers/688220/live-visual-qa"
OUT.mkdir(exist_ok=True,parents=True)
SHA=lambda b: hashlib.sha256(b).hexdigest()

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Financials-in-Visuals-688220-exact-release-check"})
    with urllib.request.urlopen(req,timeout=25) as r:
        return r.read()

def main():
    local=(ROOT/"public/688220.html").read_bytes()
    home=(ROOT/"public/index.html").read_bytes()
    remote=b""
    for retry in range(16):
        try:
            remote=get(ORG+"/688220.html")
            if remote==local and get(ORG+"/")==home:
                break
        except Exception as exc:
            print("PUBLIC_DEPLOY_PENDING_HTTP",retry,str(exc),flush=True)
        print("PUBLIC_DEPLOY_PENDING_FULL_SOURCE_HTML_SHA",retry,SHA(remote),SHA(local),flush=True)
        time.sleep(10)
    assert local==remote,("ACTUAL_CLOUDFLARE_688220_HTML_SHA_MISMATCH",SHA(local),SHA(remote))
    assert get(ORG+"/")==home,"PUBLIC_SITE_DIRECTORY_HTML_NOT_MAIN_SHA"
    manifest=json.loads((ROOT/"research/issuers/688220/source-manifest.json").read_text())
    ledger=json.loads((ROOT/"research/issuers/688220/source-ledger.json").read_text())
    assert ledger["issuer"]["code"]=="688220"
    pdf_sha=manifest["pdf_sha256"]
    assert pdf_sha.encode() in local and len(pdf_sha)==64
    catalog=json.loads((ROOT/"site/research_catalog.json").read_text())["issuers"]
    assert len(catalog)>=11 and any(z["code"]=="688220" for z in catalog)
    for company in catalog:
        independent=get(ORG+company["href"])
        assert b"<html" in independent.lower() or b"<!doctype" in independent.lower(),("PUBLIC_COMPANY_HTML_MISSING",company["code"])
        assert independent!=home,("COMPANY_LINK_REDIRECTS_TO_HOMEPAGE",company["code"])
    rows=[];screens=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(args=["--no-sandbox"])
        for width in (1440,768,390):
            page=browser.new_page(viewport={"width":width,"height":900},device_scale_factor=1,accept_downloads=True)
            page.goto(ORG+"/",wait_until="networkidle")
            assert page.locator("a.company").count()==len(catalog),(width,"COMPANY_DIRECTORY_COUNT")
            directory_shot=OUT/f"live_directory_{width}.png"
            page.screenshot(path=str(directory_shot),full_page=True)
            screens.append({"viewport":width,"sha256":SHA(directory_shot.read_bytes()),"bytes":directory_shot.stat().st_size,"name":directory_shot.name})
            page.locator('a.company[href="/688220.html"]').click()
            assert page.url.rstrip("/").endswith("/688220.html") or page.url.rstrip("/").endswith("/688220"),(width,page.url)
            actual_article_url=page.url
            import sys
            sys.path.insert(0,str(ROOT/"research/shared"))
            from profit_chain_audit import check_reader
            check_reader(page);check_reader(page,expanded=True)
            page.wait_for_selector("#chart-flow svg",state="attached")
            facts=page.evaluate("""() => {
              const sourceSvg=document.querySelector('#fig-flow .native-asr svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"][data-chart-grammar="SOURCE_REVENUE_OUTCOME_CONNECTED_SANKEY"]');
              const desktopSvg=document.querySelector('#chart-flow > svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"][data-chart-grammar="SOURCE_REVENUE_OUTCOME_CONNECTED_SANKEY"]');
              const source=sourceSvg?{
                  total:sourceSvg.dataset.revenueYuan,
                  scale:sourceSvg.dataset.scaleYuanPerSvgUnit,
                  nodes:[...sourceSvg.querySelectorAll('rect[data-node-role][data-node-yuan]')].map(x=>({
                    role:x.dataset.nodeRole,id:x.dataset.nodeId,amount:x.dataset.nodeYuan,
                    height:x.getAttribute('height')})),
                  ribbons:[...sourceSvg.querySelectorAll('path[data-stage][data-ribbon-yuan]')].map(x=>({
                    stage:x.dataset.stage,source:x.dataset.sourceId,outcome:x.dataset.outcomeId,
                    amount:x.dataset.ribbonYuan,scale:x.dataset.scaleYuanPerSvgUnit,
                    d:x.getAttribute('d')}))
                }:null;
              const native=[...document.querySelectorAll('.native-asr')];
              const bbox=native.flatMap(n=>[...n.querySelectorAll('svg text')].map(t=>{const b=t.getBBox();return {x:b.x,right:b.x+b.width,total:t.ownerSVGElement.viewBox.baseVal.width}}));
              return {n:native.length,visible:native.filter(n=>getComputedStyle(n).display!=='none').length,
                originals:[...document.querySelectorAll('.vizscroll')].filter(n=>getComputedStyle(n).display!=='none').length,
                cropped:native.filter(n=>n.scrollWidth>n.clientWidth+2).length,root:document.documentElement.scrollWidth,
                source,desktopGraph:!!desktopSvg,bbox,steps:document.querySelectorAll('.native-asr svg[data-editorial-grammar="SOURCE_SIGNED_BRIDGE_V1"] rect[data-signed-yuan]').length,
                tables:document.querySelectorAll('table.evidence-table').length,
                exports:document.querySelectorAll('[data-export]').length};
            }""")
            assert facts["root"]<=width+1 and facts["n"]==facts["tables"]==facts["exports"]==9
            # The old node/ribbon classes were legitimately retired when
            # the shared V9 positive-money Sankey went live. Test that actual
            # source→group-revenue→source-cost/GP graph, NOT obsolete CSS.
            assert facts["desktopGraph"] and facts["source"] and facts["steps"]>=19,(width,"CURRENT_SHARED_V9_INCOME_GRAPH_MISSING")
            from decimal import Decimal as D
            graph=facts["source"]
            rev=D(ledger["facts"]["rev"]["yuan"])
            assert D(graph["total"])==rev and D(graph["scale"])>0,(width,"GROUP_REVENUE_SOURCE_WRONG")
            nodes=graph["nodes"]
            sources=[z for z in nodes if z["role"]=="source"]
            trunk=[z for z in nodes if z["role"]=="total" and z["id"]=="revenue-total"]
            sinks=[z for z in nodes if z["role"] in ("cost","profit")]
            assert len(sources)==4 and len(trunk)==1 and len(sinks)==2,(width,"SHARED_GROSS_FLOW_NODES_MISSING",nodes)
            actual_sources={z["id"]:D(z["amount"]) for z in sources}
            expected_sources={entry["rev"]:D(ledger["facts"][entry["rev"]]["yuan"]) for entry in ledger["segments"]}
            assert actual_sources==expected_sources,(width,"SANKKEY_SOURCE_IDS_OR_YUAN_CHANGED")
            assert D(trunk[0]["amount"])==rev
            assert {z["role"]:D(z["amount"]) for z in sinks}=={
                "cost":D(ledger["facts"]["cogs"]["yuan"]),
                "profit":rev-D(ledger["facts"]["cogs"]["yuan"])}
            assert all(abs(D(z["height"])-D(z["amount"])/D(graph["scale"]))<D(".001") for z in nodes),(width,"FALSIFIED_SOURCE_NODE_YUAN_GEOMETRY")
            ribbons=graph["ribbons"]
            inbound=[z for z in ribbons if z["stage"]=="source-to-revenue"]
            outbound=[z for z in ribbons if z["stage"]=="revenue-to-outcome"]
            assert len(inbound)==4 and len(outbound)==7,(width,"SOURCE_BRANCH_OR_ZERO_GP_PHANTOM_RIBBON")
            assert {x["source"] for x in inbound}==set(expected_sources)
            assert sum((D(z["amount"]) for z in inbound),D(0))==rev
            assert sum((D(z["amount"]) for z in outbound),D(0))==rev
            assert all(D(z["scale"])>0 and z["d"].startswith("M ") and " C " in z["d"] for z in ribbons)
            assert len([z for z in outbound if z["source"]=="other_service_rev" and z["outcome"]=="group_gp"])==0,(width,"ZERO_ORIGINAL_GP_MUST_NOT_BE_PAINTED")
            assert len([z for z in outbound if z["source"]=="other_service_rev" and z["outcome"]=="group_cogs"])==1
            assert all(b["x"]>=-2 and b["right"]<=b["total"]+2 for b in facts["bbox"]),("ACTUAL_CJK_SVG_TEXT_CLIPPED",width)
            # Real live source-authorized full-income signed bridge is checked
            # independently of remaining four mobile issuer-specific signed art.
            from decimal import Decimal as D
            shared=page.locator('#fig-pnl svg[data-signed-statement-grammar="FINANCIALS_TYPED_FULL_PNL_SIGNED_V1"]')
            assert shared.count()==2,(width,"LIVE_SHARED_PNL_DESKTOP_PHONE_MISSING")
            selected=shared.nth(1) if width<=820 else shared.nth(0)
            assert selected.is_visible() and not (shared.nth(0) if width<=820 else shared.nth(1)).is_visible(),(width,"WRONG_LIVE_SOURCE_PNL_EDITION")
            actual=selected.evaluate("""e=>{
              let b=e.getBoundingClientRect();
              return {sha:e.dataset.originalPdfSha256,mode:e.dataset.sourceStatus,
                 net:e.dataset.endNetYuan,gross:e.dataset.startGrossYuan,
                 clipped:b.left< -2||b.right>innerWidth+2||e.parentElement.scrollWidth>e.parentElement.clientWidth+2,
                 rows:[...e.querySelectorAll('rect.unified-signed-statement-step')].map(n=>({
                   before:n.dataset.beforeYuan,delta:n.dataset.signedYuan,
                   after:n.dataset.afterYuan,width:n.getAttribute('width'),
                   scale:n.dataset.moneyScaleYuanPerUnit,src:n.dataset.sourceFactIds
                 }))};
            }""")
            assert actual["sha"]==pdf_sha and actual["mode"]=="MIRROR_COMPLETE_PDF_SHA_PASS__OFFICIAL_EQUIVALENCE_NOT_CHECKED"
            assert D(actual["gross"])==D(ledger["facts"]["rev"]["yuan"])-D(ledger["facts"]["cogs"]["yuan"])
            assert D(actual["net"])==D(ledger["facts"]["consolidated_net_profit"]["yuan"])
            assert len(actual["rows"])==10 and not actual["clipped"],(width,"LIVE_SHARED_PNL_CJK_CLIPPED_OR_INCOMPLETE",actual)
            assert any(D(z["after"])<0 for z in actual["rows"]),(width,"LIVE_INTERIM_NEGATIVE_PROFIT_HIDDEN")
            for z in actual["rows"]:
                assert D(z["before"])+D(z["delta"])==D(z["after"])
                assert abs(D(z["width"])-abs(D(z["delta"]))/D(z["scale"]))<D(".00001"),(width,"LIVE_SIGNED_PROFIT_WIDTH_NOT_PROPORTIONAL",z)
                assert z["src"]

            if width<900:
                assert facts["visible"]==9 and facts["originals"]==0 and facts["cropped"]==0,("PUBLIC_MOBILE_FINANCE_CLIPPED",width,facts)
            else:
                assert facts["visible"]==0 and facts["originals"]==9
                with page.expect_download() as item:
                    page.locator('button[data-export="flow"]').click()
                assert item.value.suggested_filename=="688220_2026H1_flow.svg"
            shot=OUT/f"live_688220_{width}.png";page.screenshot(path=str(shot),full_page=True)
            screens.append({"viewport":width,"sha256":SHA(shot.read_bytes()),"bytes":shot.stat().st_size,"name":shot.name})
            page.locator('a.brand[href="/#companies"]').click()
            assert page.url.startswith(ORG+"/") and page.url.endswith("#companies"),(width,"PUBLIC_DIRECTORY_RETURN_BROKEN",page.url)
            rows.append({"width":width,"viewport":width,"actual_dedicated_article_final_url":actual_article_url,"actual_return_to_library_url":page.url,"back_to_same_home":"PASS","no_page_horizontal_overflow":"PASS","real_live_screenshots":"PASS","source_graph_real_yuan":"PASS","original_production_route":"PASS","CJK_label_bbox":"PASS","nine_figure_phone_no_inner_scroll":"PASS" if width<900 else "ORIGINAL_DESKTOP","evidence_tables":9})
            page.close()
        browser.close()
    receipt={"schema_version":1,"status":"PASS","issuer":"688220",
        "source_main_commit":os.getenv("GITHUB_SHA","NOT_CHECKED"),"verified_git_commit":os.getenv("GITHUB_SHA","NOT_CHECKED"),
        "actual_publication_action":"https://github.com/kobolibra/financials/actions/runs/"+os.getenv("GITHUB_RUN_ID","NOT_CHECKED"),
        "source_pdf_sha256":pdf_sha,"pdf_sha256":pdf_sha,
        "public_html_sha256":SHA(remote),"actual_full_content_sha256_equals_repository_main_688220":SHA(remote),
        "home_html_sha256":SHA(home),"actual_full_content_sha256_equals_repository_main_index":SHA(home),"public_origin":ORG,
        "unified_company_count":len(catalog),"all_11_issuer_external_routes":"PASS",
        "real_browser":rows,"real_chromium_viewports":rows,"screenshots":screens,
        "independent_second_human_finance_editor":"NOT_CHECKED",
        "independent_second_human_visual_editor":"NOT_CHECKED",
        "SSE_original_bytes_equivalence":"NOT_CHECKED",
        "AR_top5_reported_ratio_vs_derived":"FAIL_BOUNDED_DENOMINATOR_UNKNOWN"}
    (OUT/"result.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    print("ACTUAL_CLOUDFLARE_688220_FULL_HTML_SHA_AND_ORIGINAL_9_NATIVE_FINANCE_CJK_PASS",receipt["public_html_sha256"],flush=True)
if __name__=="__main__":main()
