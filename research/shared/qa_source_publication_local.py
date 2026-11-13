"""Pre-merge WebKit acceptance for every actual new-company source dossier."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from qa_editorial_migration import check_vector
from audit_delivery_matrix import MEASURE
from source_publication_audit import check_vector_source

def run(out):
 from playwright.sync_api import sync_playwright
 out=Path(out);out.mkdir(exist_ok=True,parents=True)
 catalog=json.loads((ROOT/'site/research_catalog.json').read_text());result=[]
 with sync_playwright() as p:
  browser=p.webkit.launch(headless=True)
  for issuer in catalog['issuers']:
   if not (issuer.get('source_publication') or issuer.get('editorial_contract')):continue
   code=issuer['code'];ledger=json.loads((ROOT/issuer['source_publication']/'source-ledger.json').read_text()) if issuer.get('source_publication') else None
   from profit_chain_audit import bundle_for
   pdf_sha=ledger['source']['original_bytes_sha256'] if ledger else bundle_for(code)['source_pdf']['source_sha256']
   folder=out/code;folder.mkdir(exist_ok=True);file=ROOT/'public'/issuer['href'].lstrip('/')
   page=browser.new_page(viewport={'width':375,'height':812},accept_downloads=True);page.goto(file.as_uri());page.evaluate('document.fonts.ready');measured=page.evaluate(MEASURE)
   if issuer.get('editorial_contract'):
    from profit_chain_audit import check_reader
    check_reader(page);check_reader(page,expanded=True);measured=page.evaluate(MEASURE)
   if measured['body']['scroll']>measured['body']['client']+1 or any(x['clippedLabels'] or x['possibleLabelOverlaps'] or x['below10px'] for x in measured['svgs']):raise ValueError('SOURCE_WEBKIT_TEXT_OR_OVERFLOW '+code)
   figures=page.locator('figure').all()
   if len(figures)!=issuer['figures']:raise ValueError('SOURCE_WEBKIT_FIGURE_COUNT '+code)
   for i,f in enumerate(figures):
    raw=f.locator('svg:visible').evaluate('e=>new XMLSerializer().serializeToString(e)');check_vector(raw,code,pdf_sha)
    if ledger:check_vector_source(raw,ledger)
    with page.expect_download() as pending:f.locator('button').click()
    dest=folder/f'figure-{i+1:02d}.svg';pending.value.save_as(dest)
    if dest.read_text()!=raw:raise ValueError('SOURCE_WEBKIT_WRONG_VISIBLE_EXPORT '+code)
   if issuer.get('editorial_contract'):page.locator('details.editorial-reference').evaluate_all('ds=>ds.forEach(d=>d.open=false)')
   page.screenshot(path=str(folder/'full-375.png'),full_page=True);page.close()
   row={'status':'PASS_LOCAL','engine':'webkit','issuer':code,'width':375,'figures':len(figures),'real_visible_svg_downloads':len(figures),'html_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'geometry_and_source_values':'PASS','text_bounds':'PASS','artifacts':[{'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size} for f in sorted(folder.iterdir()) if f.suffix in ('.svg','.png')]}
   (folder/'result.json').write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n');result.append(row);print('SOURCE_DOSSIER_PREMERGE_WEBKIT_PASS',code,len(figures),flush=True)
  browser.close()
 return result
if __name__=='__main__':run(ROOT/'research/quality/source-dossier-webkit')
