#!/usr/bin/env python3
"""Actually browse the deployed Cloudflare 11th-company article, not GitHub artifacts.

Performs content SHA comparison with checked-out main. A Pages provider 'success'
or prior issuer cloudflare screenshot is not an actual new issuer live PASS.
"""
import hashlib,json,re,time,subprocess
from research.shared.live_route_evidence import make_live_navigation_receipt
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3]
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
assert len(catalog["issuers"])==11 and catalog["published_issuer_count"]==11
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
    assert links.count()==11,("LIVE_DIRECTORY_CARD_COUNT",width,links.count())
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
    actual_article_url=page.url
    print("LIVE_ACTUAL_COMPANY_CANONICAL_URL",width,actual_article_url,flush=True)
    assert page.locator("figure.figure").count()==10
    assert page.locator("figure.figure svg").count()==10
    assert page.locator("figure.figure details.audit").count()==10
    assert page.locator("figure.figure .money-ribbon").count()==6
    assert page.locator('#chart-premium [data-value-million="536634"]').count()==1
    assert "b094bf337309e30564dda86ff4b3c4d66aeeb37ce0357a3568e246569f0e2943" in page.content()
    assert page.locator('a[href="/#companies"]').count()>=1
    graph=page.evaluate("""() => {
      const premium=document.querySelector('#chart-premium svg');
      const sources=[...premium.querySelectorAll('rect.money-source')].map(x=>({
        key:x.dataset.sourceKey,value:x.dataset.valueMillion,exact:x.dataset.exactYuan,
        fill:x.getAttribute('fill'),height:+x.getAttribute('height')
      }));
      const sink=premium.querySelector('rect.money-sink');
      const invalid=[...document.querySelectorAll('.chart svg rect')].filter(x=>
        !/^#[0-9a-fA-F]{6}$/.test(x.getAttribute('fill')||'') ||
        (x.getAttribute('class')||'').includes('=')).map(x=>x.outerHTML.slice(0,180));
      return {
        width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,
        charts:[...document.querySelectorAll('.chart')].map(x=>({w:x.scrollWidth,c:x.clientWidth})),
        premiumSources:sources,invalidPaintedSVGRectangles:invalid,
        premiumSink:sink?{fill:sink.getAttribute('fill'),klass:sink.getAttribute('class'),
          value:sink.dataset.valueMillion,exact:sink.dataset.exactYuan,
          height:+sink.getAttribute('height'),y:+sink.getAttribute('y')}:null
      }
    }""")
    assert not graph["invalidPaintedSVGRectangles"],("PRODUCTION_SVG_RECT_NOT_VISIBLY_PAINTED",width,graph["invalidPaintedSVGRectangles"])
    expected_sources={"premium_first_regular":101294,"premium_single":17696,"premium_short":61049,"premium_renew":356595}
    assert len(graph["premiumSources"])==4,("LIVE_FOUR_EXCLUSIVE_PREMIUM_SOURCES_MISSING",width,graph["premiumSources"])
    for node in graph["premiumSources"]:
        k=node["key"]
        assert k in expected_sources,("EXTRA_PREMIUM_SOURCE",k)
        assert node["value"]==str(expected_sources[k]),("SOURCE_VALUE_MISMATCH",width,k)
        assert node["exact"]==report["facts"][k]["yuan"],("SOURCE_PRECISE_YUAN_MISMATCH",width,k)
        assert abs(node["height"]-268*expected_sources[k]/536634)<0.001,("SOURCE_MONEY_GEOMETRY_DRIFT",width,k)
    sink=graph["premiumSink"]
    assert sink is not None and sink["fill"]=="#123F3A" and sink["klass"]=="money-sink",("LIVE_UNPAINTED_OR_MALFORMED_SINK",width,sink)
    assert sink["value"]=="536634" and sink["exact"]==report["facts"]["premium_total"]["yuan"],("LIVE_WRONG_PREMIUM_TOTAL_SOURCE",width,sink)
    assert sink["height"]==268 and sink["y"]==82,("LIVE_WRONG_PREMIUM_TOTAL_GEOMETRY",width,sink)
    assert graph["scroll"]<=width+1,("LIVE_ARTICLE_MOBILE_OVERFLOW",width,graph)
    if width==1440:assert all(x["w"]<=x["c"]+2 for x in graph["charts"]),("LIVE_DESKTOP_FIGURE_INNER_CLIPPING",graph)
    page.screenshot(path=str(OUT/f"live_601628_{width}.png"),full_page=True)
    page.locator('a[href="/#companies"]').first.click()
    page.wait_for_url(re.compile(r"/#companies$"),timeout=30000)
    actual_back_url=page.url
    nav=make_live_navigation_receipt(report_url=actual_article_url,back_url=actual_back_url,code=CODE,origin=SITE)
    assert page.locator("a.company").count()==11,("LIVE_BACK_NAV_DIRECTORY",width)
    report_check.append({"width":width,**nav,"public_home_11_cards":"PASS","new_601628_main_route":"PASS","ten_svg_figures":"PASS","source_table_10":"PASS","visible_real_svg_ribbons":"PASS","live_final_sink_geometrically_conserved":"PASS","back_to_same_home":"PASS","no_page_horizontal_overflow":"PASS","real_live_screenshots":"PASS"})
    page.close()
 assert not errors,("LIVE_CHROMIUM_PAGE_ERRORS",errors)
 # All prior issuer routes: actual GET and matching company code in HTML
 for card in catalog["issuers"]:
    q=req.get(SITE+card["href"],timeout=25000)
    assert q.status==200 and card["code"].encode() in q.body(),("LIVE_PRIOR_ISSUER_MISSING",card["code"],q.status)
 browser.close();req.dispose()
results={"status":"PASS","origin":SITE,"verified_git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"pdf_sha256":report["source"]["original_bytes_sha256"],
         "actual_full_content_sha256_equals_repository_main_601628":expected_sha,
         "actual_full_content_sha256_equals_repository_main_index":expected_home,
         "all_11_issuer_external_routes":"PASS","real_chromium_viewports":report_check,
         "independent_human_editor":"NOT_CHECKED","external_market_peer_valuation":"NOT_CHECKED"}
results["screenshots"]=[{"name":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size} for p in sorted(OUT.glob("live_*.png"))]
assert len(results["screenshots"])==6,("MISSING_PRODUCTION_THREE_VIEWS_ISSUER_AND_LIBRARY")
assert all(z["actual_dedicated_article_final_url"] in {SITE+"/601628",SITE+"/601628.html"} for z in report_check),"LIVE_EVIDENCE_URL_CORRUPTED_AFTER_BACK"
(OUT/"result.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n")
print("ACTUAL_CLOUDFLARE_MAIN_ELEVEN_ISSUERS_THREE_REAL_VIEWPORTS_AND_PUBLIC_HTML_SHA_PASS",expected_sha,expected_home,json.dumps(report_check))
print("PRODUCTION_VERIFICATION_RECEIPT_JSON",json.dumps(results,ensure_ascii=False,sort_keys=True),flush=True)
