"""Real post-merge evidence for every catalog-declared source publication."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time,re
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from qa_editorial_migration import audit,check_vector
from audit_delivery_matrix import MEASURE
from live_route_evidence import make_live_navigation_receipt
from source_publication_audit import check_vector_source
SITE='https://financials-in-visuals.pages.dev'
def run(out=None):
 from playwright.sync_api import sync_playwright
 out=Path(out or ROOT/'research/quality/source-publication-live');out.mkdir(parents=True,exist_ok=True)
 catalog=json.loads((ROOT/'site/research_catalog.json').read_text());issuers=[x for x in catalog['issuers'] if x.get('source_publication') or x.get('editorial_contract')]
 if not issuers:return []
 git_sha=os.environ.get('GITHUB_SHA') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 if not re.fullmatch('[a-f0-9]{40}',git_sha):raise ValueError('SOURCE_LIVE_FULL_COMMIT_REQUIRED')
 home=(ROOT/'public/index.html').read_bytes();receipts=[]
 with sync_playwright() as p:
  req=p.request.new_context(timeout=45000)
  for attempt in range(30):
   try:
    if req.get(SITE+'/').body()==home and all(req.get(SITE+x['href']).body()==(ROOT/'public'/x['href'].lstrip('/')).read_bytes() for x in issuers):break
   except Exception:pass
   if attempt==29:raise ValueError('SOURCE_LIVE_EXACT_MAIN_BYTES_NOT_DEPLOYED')
   time.sleep(10)
  for x in catalog['issuers']:
   response=req.get(SITE+x['href']);assert response.status==200 and response.body()==(ROOT/'public'/x['href'].lstrip('/')).read_bytes(),('LIVE_ROUTE_SOURCE_BYTES',x['code'])
  req.dispose()
 # Audit every visible source vector and all actual downloads on live HTTP.
 audit([x['code'] for x in issuers],out/'all-financial-figures',SITE)
 with sync_playwright() as p:
  chrome=p.chromium.launch(headless=True);webkit=p.webkit.launch(headless=True)
  for issuer in issuers:
   code=issuer['code'];folder=out/code;folder.mkdir(exist_ok=True);ledger=json.loads((ROOT/issuer['source_publication']/'source-ledger.json').read_text()) if issuer.get('source_publication') else None
   from profit_chain_audit import bundle_for,check_reader
   pdf_sha=ledger['source']['original_bytes_sha256'] if ledger else bundle_for(code)['source_pdf']['source_sha256']
   views=[];extra=[]
   for engine,width in [('chromium',1440),('chromium',768),('chromium',390),('webkit',375)]:
    browser=chrome if engine=='chromium' else webkit;page=browser.new_page(viewport={'width':width,'height':960},accept_downloads=True);errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(SITE+'/',wait_until='load');assert page.locator('a.company').count()==len(catalog['issuers'])
    if engine=='chromium':page.screenshot(path=str(folder/f'live_directory_{width}.png'),full_page=True)
    page.locator('a.company[href="'+issuer['href']+'"]').click();page.wait_for_url(re.compile('/'+code+r'(?:\.html)?(?:[?#].*)?$'));article_url=page.url;page.evaluate('document.fonts.ready')
    response=page.request.get(page.url);assert response.body()==(ROOT/'public'/issuer['href'].lstrip('/')).read_bytes()
    check_reader(page);check_reader(page,expanded=True)
    observed=page.evaluate(MEASURE);assert observed['body']['scroll']<=observed['body']['client']+1
    assert not any(s['clippedLabels'] or s['possibleLabelOverlaps'] or s['below10px'] for s in observed['svgs']),('SOURCE_LIVE_TEXT_BOUNDS',engine,width)
    assert len(observed['figures'])==issuer['figures'] and all(f['visibleSvgCount']==1 and f['hasEvidence'] and f['hasAlternative'] for f in observed['figures'])
    if engine=='webkit':
     for i,f in enumerate(page.locator('figure').all()):
      svg=f.locator('svg:visible');raw=svg.evaluate('e=>new XMLSerializer().serializeToString(e)');check_vector(raw,code,pdf_sha)
      if ledger:check_vector_source(raw,ledger)
      with page.expect_download() as event:f.locator('button').click()
      dest=folder/f'webkit-375-figure-{i+1}.svg';event.value.save_as(dest);assert dest.read_text()==raw
     page.locator('details.editorial-reference').evaluate_all('ds=>ds.forEach(d=>d.open=false)')
     page.screenshot(path=str(folder/'webkit_375.png'),full_page=True);extra.append({'engine':'webkit','width':375,'all_source_figures':issuer['figures'],'real_visible_svg_exports':'PASS','text_bounds':'PASS','screenshot_sha256':hashlib.sha256((folder/'webkit_375.png').read_bytes()).hexdigest()})
    else:
     page.locator('details.editorial-reference').evaluate_all('ds=>ds.forEach(d=>d.open=false)')
     page.screenshot(path=str(folder/f'live_{code}_{width}.png'),full_page=True)
    page.locator('a[href="/#companies"]').first.click();page.wait_for_url(re.compile('/#companies$'));back_url=page.url;nav=make_live_navigation_receipt(report_url=article_url,back_url=back_url,code=code,origin=SITE)
    assert not errors,errors
    if engine=='chromium':views.append({'width':width,**nav,'back_to_same_home':'PASS','no_page_horizontal_overflow':'PASS','real_live_screenshots':'PASS','all_source_figures':issuer['figures']})
    page.close()
   receipt={'schema_version':1,'issuer':code,'status':'PASS','verified_git_commit':git_sha,'pdf_sha256':pdf_sha,'actual_publication_action':('https://github.com/kobolibra/financials/actions/runs/'+os.environ['GITHUB_RUN_ID']) if os.environ.get('GITHUB_RUN_ID') else str((folder/'live-release-receipt.json').relative_to(ROOT)),'execution_provenance':'GITHUB_ACTIONS_REAL_PUBLIC_BROWSER' if os.environ.get('GITHUB_RUN_ID') else 'LOCAL_REAL_PUBLIC_BROWSER_NOT_ACTIONS','actual_full_content_sha256_equals_repository_main_'+code:hashlib.sha256((ROOT/'public'/issuer['href'].lstrip('/')).read_bytes()).hexdigest(),'actual_full_content_sha256_equals_repository_main_index':hashlib.sha256(home).hexdigest(),'all_11_issuer_external_routes':'PASS','actual_catalog_issuer_count':len(catalog['issuers']),'real_chromium_viewports':views,'additional_webkit_checks':extra,'screenshots':[{'name':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size} for f in sorted(folder.glob('live_*.png'))],'independent_human_finance_and_art':'NOT_CHECKED','complete_figure_receipt':str((out/'all-financial-figures/result.json').relative_to(ROOT))}
   (folder/'live-release-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');receipts.append(receipt);print('SOURCE_PUBLICATION_REAL_PRODUCTION_PASS',code,git_sha,flush=True)
  chrome.close();webkit.close()
 return receipts
if __name__=='__main__':run()
