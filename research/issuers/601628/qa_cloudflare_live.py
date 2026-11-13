#!/usr/bin/env python3
"""Actually browse the deployed Cloudflare 11th-company article, not GitHub artifacts.

Performs content SHA comparison with checked-out main. A Pages provider 'success'
or prior issuer cloudflare screenshot is not an actual new issuer live PASS.
"""
import hashlib,json,re,time,subprocess,sys,os
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
# Direct execution (python research/issuers/601628/qa_cloudflare_live.py)
# otherwise places only this script directory on sys.path, not the project root.
sys.path.insert(0,str(ROOT))
from research.shared.live_route_evidence import make_live_navigation_receipt
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(ROOT/'research/issuers/601628'))
from quantified_decision import FACT_SPEC,decisions
from qa_signed_geometry import FAMILIES,check_signed_svg,expected_steps,COMMON_FAMILIES,check_common_insurance_svg

def verified_git_commit(environ=None,rev_parse=None):
    """Bind CI to its checked-out deployment SHA; local defaults to Git HEAD."""
    env=os.environ if environ is None else environ
    sha=env.get("GITHUB_SHA")
    if not sha:
        sha=(rev_parse() if rev_parse else subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True)).strip()
    if not re.fullmatch(r"[0-9a-fA-F]{40}",sha):
        raise ValueError("VERIFIED_GIT_COMMIT_MUST_BE_FULL_SHA")
    return sha.lower()
SITE="https://financials-in-visuals.pages.dev"
HERE=ROOT/"research/issuers/601628"
OUT=HERE/"live-qa"
OUT.mkdir(parents=True,exist_ok=True)
CODE="601628"
local_html=(ROOT/"public/601628.html").read_bytes()
local_home=(ROOT/"public/index.html").read_bytes()
expected_sha=hashlib.sha256(local_html).hexdigest()
expected_home=hashlib.sha256(local_home).hexdigest()
catalog=json.loads((ROOT/"site/research_catalog.json").read_text(encoding="utf-8"))
assert len(catalog["issuers"])==catalog["published_issuer_count"] and len(catalog["issuers"])>=11
report=json.loads((HERE/"source-ledger.json").read_text())
assert report["source"]["original_bytes_sha256"]=="b094bf337309e30564dda86ff4b3c4d66aeeb37ce0357a3568e246569f0e2943"
report_check=[]
errors=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
 req=pw.request.new_context(user_agent="Financials-in-Visuals real post-deployment browser publication verification",timeout=25000)
 # Pages deployments are asynchronous following main. Wait for MAIN bytes, not provider check or 200 old-page.
 latest={}
 for n in range(24):
    try:
      a=req.get(SITE+"/",timeout=25000)
      b=req.get(SITE+"/601628.html",timeout=25000)
      h=a.body() if a.status==200 else b""
      x=b.body() if b.status==200 else b""
      latest={"home_status":a.status,"report_status":b.status,"home_final_url":a.url,"report_final_url":b.url,"home_sha":hashlib.sha256(h).hexdigest(),"report_sha":hashlib.sha256(x).hexdigest(),"try":n+1}
      if (latest["home_sha"]==expected_home and latest["report_sha"]==expected_sha and b"601628" in x):
          break
    except Exception as e:latest={"attempt":n+1,"error":str(e)[:300]}
    if n!=23:time.sleep(15)
 else:
    (OUT/"result.json").write_text(json.dumps({"status":"FAIL","reason":"CLOUDFLARE_NEW_11TH_PUBLIC_BYTES_MISMATCH","expected_home_sha":expected_home,"expected_601628_sha":expected_sha,"observed":latest},ensure_ascii=False,indent=2))
    raise AssertionError("CLOUDFLARE_NEW_11TH_PUBLIC_BYTES_MISMATCH "+str(latest))
 for width,height in [(1440,900),(768,1024),(390,844)]:
    page=browser.new_page(viewport={"width":width,"height":height},device_scale_factor=1,accept_downloads=True)
    page.on("pageerror",lambda x:errors.append(str(x)))
    page.goto(SITE+"/",wait_until="load",timeout=40000)
    links=page.locator("a.company")
    assert links.count()==len(catalog["issuers"]),("LIVE_DIRECTORY_CARD_COUNT",width,links.count())
    hrefs=links.evaluate_all("els=>els.map(x=>x.getAttribute('href'))")
    assert set(hrefs)==set(x["href"] for x in catalog["issuers"]),("LIVE_DIRECTORY_ROUTE_SET",width,hrefs)
    assert page.locator('a.company[href="/601628.html"]').count()==1
    assert page.locator('iframe').count()==0
    info=page.evaluate("() => ({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth})")
    assert info["scroll"]<=width+1,("LIVE_DIRECTORY_HORIZ_OVERFLOW",width,info)
    page.screenshot(path=str(OUT/f"live_directory_{width}.png"),full_page=True)
    page.locator('a.company[href="/601628.html"]').click()
    # Cloudflare Pages may canonicalize /601628.html to /601628; the only
    # release condition is an independently navigated COMPANY page with ten
    # actual source-linked figures, NOT a literal browser URL suffix.
    page.wait_for_url(re.compile(r"/601628(?:\.html)?/?(?:[?#].*)?$"),timeout=30000)
    import sys
    sys.path.insert(0,str(ROOT/"research/shared"))
    from profit_chain_audit import check_reader
    check_reader(page);check_reader(page,expanded=True)
    actual_article_url=page.url
    page.evaluate("document.fonts.ready")
    signed_bridge_checks=[]
    visible_bridge_exports=[]
    print("LIVE_ACTUAL_COMPANY_CANONICAL_URL",width,actual_article_url,flush=True)
    # Real Cloudflare, not just a green issuer preview: 13 source rows and
    # all four signed CAS calculations must match original consolidated CNY.
    from decimal import Decimal as D
    original,formulas=decisions(report)
    panel=page.locator('#quantified-decision')
    assert panel.count()==1 and panel.is_visible(),(width,"LIVE_INSURANCE_DECISION_NOT_PUBLISHED")
    assert panel.get_attribute('data-pdf-sha256')==report['source']['original_bytes_sha256']
    got=panel.evaluate("""e=>({
      left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right,
      rows:[...e.querySelectorAll('tr[data-source-key]')].map(x=>({...x.dataset})),
      cards:[...e.querySelectorAll('.insurance-decision-card')].map(x=>{
        const r=x.getBoundingClientRect();
        return {key:x.dataset.decisionKey,v:x.dataset.derivedDecimal,
          top:r.top,bottom:r.bottom};
      })
    })""")
    assert len(got["rows"])==len(FACT_SPEC)==13 and len(got["cards"])==4
    assert got["left"]>=-1 and got["right"]<=width+2
    for item in got["rows"]:
        key=item["sourceKey"]
        assert D(item["exactYuan"])==D(report["facts"][key]["yuan"]),(width,key,"LIVE_INSURER_SOURCE_MONEY_FALSE")
        assert item["period"]==FACT_SPEC[key][0] and item["financialKind"]==FACT_SPEC[key][1]
        assert int(item["physicalPage"])==report["facts"][key]["page"]
    assert all(D(x["v"])==formulas[x["key"]] for x in got["cards"]),(width,"LIVE_INSURER_DECISION_FORMULA_FALSE")
    if width==390:
        cards=got["cards"]
        assert all(cards[i]["bottom"]<=cards[i+1]["top"]+.5 for i in range(3)),(width,"INSURER_SOURCE_DECISION_MOBILE_OVERPRINT")
    assert "NOT_CHECKED" in panel.inner_text()
    panel.screenshot(path=str(OUT/f"live_decision_{width}.png"),animations="disabled")
    assert page.locator("figure.figure").count()==10
    # Every one of the ten figures has distinct desktop and native editions.
    # Validate the visible edition against original insurance facts at each width.
    assert page.locator("figure.figure .chart svg").count()==10,(width,"LIVE_TEN_ORIGINAL_DESKTOP_FINANCE_SVGS_MISSING")
    assert page.locator('#chart-premium .mobile-chart svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"]').count()==1,(width,"LIVE_SOURCE_CONSERVED_NATIVE_INSURANCE_PREMIUM_SVG_MISSING")
    assert page.locator("figure.figure svg").count()==2*(1+len(FAMILIES)+len(COMMON_FAMILIES)),(width,"LIVE_UNEXPECTED_DESKTOP_OR_MOBILE_SVG_FAMILY_COUNT")
    for family in sorted(FAMILIES|COMMON_FAMILIES):
        current=page.locator('#chart-'+family+(' .mobile-chart > svg' if width<=850 else ' .chart > svg'))
        assert current.count()==1 and current.is_visible(),(width,family,'LIVE_VISIBLE_SOURCE_FAMILY_MISSING')
        raw=current.evaluate('e=>e.outerHTML')
        checked=check_signed_svg(raw,family,report,mobile=width<=850) if family in FAMILIES else check_common_insurance_svg(raw,family,report)
        signed_bridge_checks.append(checked)
    assert page.locator("figure.figure details.audit").count()==10
    assert page.locator('#chart-premium .mobile-chart').count()==1
    assert page.locator("figure.figure .mobile-chart").count()==10,("LIVE_MOBILE_ALTERNATIVE_DOM_MISSING",width)
    if width<=850:
        assert page.locator(".mobile-chart:visible").count()==10,("LIVE_390_MOBILE_FULL_TEN_FIGURES_NOT_VISIBLE")
        assert page.locator(".chart:visible").count()==0,("LIVE_390_STILL_TRAPPED_IN_DESKTOP_900PX_SCROLL_WINDOWS")
        mobile=page.evaluate("""() => [...document.querySelectorAll('.mobile-chart')].map(panel=>({
          family:panel.dataset.mobileFigure,overflow:panel.scrollWidth-panel.clientWidth,
          rows:[...panel.querySelectorAll('.m-item')].map(x=>({
            key:x.dataset.mobileFact,exact:x.dataset.exactYuan,
            scaleGroup:x.dataset.scaleGroup,width:parseFloat(x.querySelector('.m-item-rail i').style.width||'0')
          }))
        }))""")
        assert len(mobile)==10
        for family in mobile:
            assert family["overflow"]<=1,("LIVE_390_MOBILE_INNER_HORIZ_OVERFLOW",family["family"],family["overflow"])
            if family["family"] in FAMILIES:
                svg=page.locator('#chart-'+family['family']+' .mobile-chart svg')
                assert svg.count()==1 and svg.is_visible(),(width,family['family'],'LIVE_NATIVE_BRIDGE_MISSING')
                signed_bridge_checks.append(check_signed_svg(svg.evaluate('el=>el.outerHTML'),family['family'],report))
                continue
            if family['family'] in COMMON_FAMILIES:
                svg=page.locator('#chart-'+family['family']+' .mobile-chart > svg')
                assert svg.count()==1 and svg.is_visible()
                signed_bridge_checks.append(check_common_insurance_svg(svg.evaluate('e=>e.outerHTML'),family['family'],report))
                continue
            assert len(family["rows"])>=5,("LIVE_MOBILE_FAMILY_INCOMPLETE",family["family"])
            scales={}
            for item in family["rows"]:
                raw=int(item["exact"])
                scales[item["scaleGroup"]]=max(scales.get(item["scaleGroup"],0),abs(raw))
                if item["key"]!="derived":
                    assert item["key"] in report["facts"],("LIVE_MOBILE_FAKE_LEDGER_KEY",item)
                    assert item["exact"]==report["facts"][item["key"]]["yuan"],("LIVE_MOBILE_LEDGER_SOURCE_MISMATCH",item)
            for item in family["rows"]:
                expected=abs(int(item["exact"]))/scales[item["scaleGroup"]]*100
                assert abs(item["width"]-expected)<0.000055,("LIVE_MOBILE_MONEY_BAR_INFLATED",family["family"],item,expected)
    # Every derived source must also appear in the actual online figure table.
    briefs=json.loads((HERE/'figure-briefs.json').read_text())['figure_briefs']
    for family in sorted(FAMILIES):
        dependencies=set().union(*(step[1] for step in expected_steps(family,report['facts'])))
        brief=next(b for b in briefs if b['id']==family)
        assert dependencies<=set(brief['facts']),(width,family,'LIVE_SOURCE_TABLE_DEPENDENCIES_INCOMPLETE')
        rows=page.locator('#chart-'+family+' details.audit tbody tr').evaluate_all("rows=>rows.map(r=>({label:r.querySelector('th').textContent,amount:r.querySelector('td.number').textContent,href:r.querySelector('a').getAttribute('href')}))")
        assert len(rows)==len(brief['facts']),(width,family,'LIVE_FIGURE_SOURCE_TABLE_COUNT')
        for row,key in zip(rows,brief['facts']):
            fact=report['facts'][key]
            assert row['label']==fact['label'] and row['amount']==f"{D(fact['yuan'])/D(1000000):+,.0f} 百万元",(width,family,key,'LIVE_SOURCE_TABLE_EXACT_YUAN')
            assert row['href']==report['source']['official_announcement']+'#page='+str(fact['page']),(width,family,key,'LIVE_SOURCE_TABLE_PDF_PHYSICAL_PAGE')
        # Keep notes/context tables separate from the ten figure-source tables.
        assert page.locator('figure.figure details.audit table').count()==10
        container=page.locator('#chart-'+family)
        visible=container.locator('.mobile-chart svg' if width<=850 else '.chart svg')
        assert visible.count()==1 and visible.is_visible(),(width,family,'LIVE_VISIBLE_SVG_EXPORT_SOURCE')
        expected_vector=ET.fromstring(visible.evaluate('el=>el.outerHTML'))
        with page.expect_download(timeout=10000) as pending:
            container.locator('[data-export]').click()
        download=pending.value
        assert download.failure() is None
        assert download.suggested_filename==f"601628-2026H1-{family}.svg"
        target=OUT/f'export-{family}-{width}.svg';download.save_as(target)
        raw=target.read_text();actual_vector=ET.fromstring(raw)
        assert actual_vector.get('viewBox')==expected_vector.get('viewBox'),(width,family,'LIVE_EXPORTED_HIDDEN_LAYOUT')
        assert actual_vector.get('data-chart-grammar')==expected_vector.get('data-chart-grammar'),(width,family,'LIVE_EXPORTED_WRONG_GRAMMAR')
        ns='{http://www.w3.org/2000/svg}'
        for tag in ('rect','text','path'):
            assert [(n.attrib,n.text) for n in actual_vector.iter(ns+tag)]==[(n.attrib,n.text) for n in expected_vector.iter(ns+tag)],(width,family,'LIVE_EXPORT_VISIBLE_VECTOR_DRIFT',tag)
        check_signed_svg(raw,family,report,mobile=width<=850)
        visible_bridge_exports.append({'family':family,'layout':'native-330' if width<=850 else 'desktop','sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'actual_visible_vector_match':'PASS'})
    graph=page.evaluate("""() => {
      const details=(root)=>{
        if(!root)return null;
        const attr=(x,key)=>x.getAttribute(key);
        return {
          grammar:attr(root,'data-chart-grammar'),
          unit:attr(root,'data-premium-yuan'),
          scale:attr(root,'data-scale-yuan-per-svg-unit'),
          width:root.viewBox.baseVal.width,
          nodes:[...root.querySelectorAll('rect[data-node-role]')].map(x=>({
            id:attr(x,'data-node-id'), role:attr(x,'data-node-role'),
            yuan:attr(x,'data-node-yuan'), h:attr(x,'height'),
            y:attr(x,'y'),fill:attr(x,'fill')
          })),
          ribbons:[...root.querySelectorAll('path[data-ribbon-yuan]')].map(x=>({
            source:attr(x,'data-source-id'),stage:attr(x,'data-stage'),
            yuan:attr(x,'data-ribbon-yuan'),
            scale:attr(x,'data-scale-yuan-per-svg-unit'),
            d:attr(x,'d')
          }))
        };
      };
      return {
        width:document.documentElement.clientWidth,
        scroll:document.documentElement.scrollWidth,
        charts:[...document.querySelectorAll('.chart')].map(x=>({w:x.scrollWidth,c:x.clientWidth})),
        malformed:[...document.querySelectorAll('.chart svg rect')].filter(x=>
          !/^#[0-9a-fA-F]{6}$/.test(x.getAttribute('fill')||'')||
          (x.getAttribute('class')||'').includes('=')).map(x=>x.outerHTML.slice(0,180)),
        desktop:details(document.querySelector('#chart-premium .chart svg')),
        mobile:details(document.querySelector('#chart-premium .mobile-chart svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"]'))
      };
    }""")
    assert graph["scroll"]<=width+1,(width,"LIVE_ARTICLE_MOBILE_OVERFLOW",graph["scroll"])
    assert not graph["malformed"],(width,"LIVE_MALFORMED_DESKTOP_SVG_RECT",graph["malformed"])
    if width==1440:assert all(x["w"]<=x["c"]+2 for x in graph["charts"]),(width,"LIVE_DESKTOP_FIGURE_INNER_CLIPPING",graph["charts"])
    from decimal import Decimal as D
    total=D(report["facts"]["premium_total"]["yuan"])
    expected_sources=("premium_first_regular","premium_single","premium_short","premium_renew")
    expected_buckets={"premium_new","premium_renew"}
    for view,fig in (("desktop",graph["desktop"]),("mobile",graph["mobile"])):
        assert fig and fig["grammar"]=="INSURANCE_PREMIUM_SOURCE_NEW_RENEW_TOTAL",(width,view,"WRONG_CAS_OR_PREMIUM_GRAPH")
        assert fig["width"]==(1100 if view=="desktop" else 330),(width,view,"NON_NATIVE_SOURCE_SVG")
        assert D(fig["unit"])==total and D(fig["scale"])>0,(width,view,"FALSE_PREMIUM_TOTAL_OR_SCALE")
        nodes=fig["nodes"]; ribbons=fig["ribbons"]
        sources=[x for x in nodes if x["role"]=="premium-source"]
        buckets=[x for x in nodes if x["role"]=="premium-bucket"]
        totals=[x for x in nodes if x["role"]=="premium-total"]
        assert len(sources)==4 and len(buckets)==2 and len(totals)==1,(width,view,"SANKY_NODES_MISSING")
        assert {x["id"] for x in sources}==set(expected_sources)
        assert {x["id"] for x in buckets}==expected_buckets
        for node in nodes:
            key="premium_total" if node["id"]=="premium-total" else node["id"]
            assert D(node["yuan"])==D(report["facts"][key]["yuan"]),(width,view,key,"ORIGINAL_PREMIUM_CNY_WRONG")
            assert abs(D(node["h"])-D(node["yuan"])/D(fig["scale"]))<D(".001"),(width,view,key,"ORIGINAL_NODE_MONEY_HEIGHT_WRONG")
        left=[x for x in ribbons if x["stage"]=="premium-source-to-new-or-renew"]
        right=[x for x in ribbons if x["stage"]=="new-or-renew-to-premium-total"]
        assert len(left)==4 and len(right)==2,(width,view,"SOURCE_TO_NEW_TO_RENEW_TO_TOTAL_NOT_CONNECTED")
        assert {x["source"] for x in left}==set(expected_sources)
        assert sum((D(x["yuan"]) for x in left),D(0))==total,(width,view,"SOURCE_PREMIUM_NOT_CLOSED")
        assert sum((D(x["yuan"]) for x in right),D(0))==total,(width,view,"NEW_RENEW_PREMIUM_NOT_CLOSED")
        for ribbon in ribbons:
            d=ribbon["d"]
            assert d.startswith("M ") and " C " in d and " L " in d,(width,view,"SVG_NOT_A_CURVED_RIBBON")
            top=D(d.split(" L ")[0].split()[-1])
            bottom=D(d.split(" L ")[1].split(" C ")[0].split()[-1])
            assert abs(abs(bottom-top)-D(ribbon["yuan"])/D(ribbon["scale"]))<D(".001"),(width,view,ribbon["source"],"LIVE_ORIGINAL_YUAN_RIBBON_GEOMETRY_FALSE")
    page.screenshot(path=str(OUT/f"live_601628_{width}.png"),full_page=True)
    page.locator('a[href="/#companies"]').first.click()
    page.wait_for_url(re.compile(r"/#companies$"),timeout=30000)
    actual_back_url=page.url
    nav=make_live_navigation_receipt(report_url=actual_article_url,back_url=actual_back_url,code=CODE,origin=SITE)
    assert page.locator("a.company").count()==len(catalog["issuers"]),("LIVE_BACK_NAV_DIRECTORY",width)
    report_check.append({"width":width,**nav,"public_home_11_cards":"PASS","new_601628_main_route":"PASS","ten_desktop_plus_premium_and_five_native_bridges":"PASS","source_signed_bridge_checks":signed_bridge_checks,"visible_bridge_exports":visible_bridge_exports,"source_table_10":"PASS","visible_real_svg_ribbons":"PASS","live_final_sink_geometrically_conserved":"PASS","mobile_ten_full_width_source_exact_money_exhibits":"PASS" if width<=850 else "DESKTOP_SVG","back_to_same_home":"PASS","no_page_horizontal_overflow":"PASS","real_live_screenshots":"PASS"})
    page.close()
 assert not errors,("LIVE_CHROMIUM_PAGE_ERRORS",errors)
 # All prior issuer routes: actual GET and matching company code in HTML
 for card in catalog["issuers"]:
    q=req.get(SITE+card["href"],timeout=25000)
    assert q.status==200 and card["code"].encode() in q.body(),("LIVE_PRIOR_ISSUER_MISSING",card["code"],q.status)
 browser.close();req.dispose()
results={"status":"PASS","origin":SITE,"verified_git_commit":verified_git_commit(),"pdf_sha256":report["source"]["original_bytes_sha256"],
         "actual_full_content_sha256_equals_repository_main_601628":expected_sha,
         "actual_full_content_sha256_equals_repository_main_index":expected_home,
         "all_11_issuer_external_routes":"PASS","real_chromium_viewports":report_check,
         "independent_human_editor":"NOT_CHECKED","external_market_peer_valuation":"NOT_CHECKED"}
results["screenshots"]=[{"name":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size} for p in sorted(OUT.glob("live_*.png"))]
assert len(results["screenshots"])==9,("MISSING_PRODUCTION_THREE_VIEWS_ISSUER_LIBRARY_AND_FINANCE_DECISION")
assert all(z["actual_dedicated_article_final_url"] in {SITE+"/601628",SITE+"/601628.html"} for z in report_check),"LIVE_EVIDENCE_URL_CORRUPTED_AFTER_BACK"
(OUT/"result.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n")
print("ACTUAL_CLOUDFLARE_MAIN_ELEVEN_ISSUERS_THREE_REAL_VIEWPORTS_AND_PUBLIC_HTML_SHA_PASS",expected_sha,expected_home,json.dumps(report_check))
print("PRODUCTION_VERIFICATION_RECEIPT_JSON",json.dumps(results,ensure_ascii=False,sort_keys=True),flush=True)
