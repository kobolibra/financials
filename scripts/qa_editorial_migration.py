#!/usr/bin/env python3
"""Observe every source financial figure; require real current-edition SVG downloads.

No issuer renderer whitelist. CLI selects the explicitly requested migration
scope; future issuers must provide the same source archive and real evidence.
"""
from pathlib import Path
import argparse,hashlib,json,re,sys
from decimal import Decimal as D
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'research/shared'))
from editorial_geometry import check_editorial_svg
from audit_delivery_matrix import MEASURE
NS='{http://www.w3.org/2000/svg}'

def check_vector(markup,issuer,pdf_sha):
    svg=ET.fromstring(markup)
    if svg.get('data-chart-grammar')=='FULL_PROFIT_CHAIN_V1':
        from profit_chain_audit import check_svg
        return check_svg(markup,issuer,pdf_sha)
    if svg.get('data-editorial-grammar'):return check_editorial_svg(markup,issuer=issuer,pdf_sha256=pdf_sha)
    grammar=svg.get('data-chart-grammar') or svg.get('data-signed-statement-grammar')
    def require(test,why):
        if not test:raise ValueError('CANONICAL_VECTOR_'+why)
    if grammar in ('SOURCE_REVENUE_OUTCOME_CONNECTED_SANKEY','INSURANCE_PREMIUM_SOURCE_NEW_RENEW_TOTAL'):
        require(svg.get('data-issuer')==issuer,'ISSUER')
        scale=D(svg.get('data-scale-yuan-per-svg-unit'))
        require(scale>0,'SCALE')
        total=D(svg.get('data-revenue-yuan') or svg.get('data-premium-yuan'))
        nodes=[n for n in svg.iter(NS+'rect') if n.get('data-node-yuan') is not None]
        role='source' if grammar.startswith('SOURCE_') else 'premium-source'
        require(sum(D(n.get('data-node-yuan')) for n in nodes if n.get('data-node-role')==role)==total,'SOURCE_TOTAL')
        for n in nodes:require(abs(D(n.get('height'))-D(n.get('data-node-yuan'))/scale)<D('.0002'),'NODE_MONEY_HEIGHT')
        ribbons=[p for p in svg.iter(NS+'path') if p.get('data-ribbon-yuan') is not None]
        require(bool(ribbons),'NO_RIBBONS')
        for p in ribbons:
            amount=D(p.get('data-ribbon-yuan'));expected=amount/scale
            coords=[D(x) for x in re.findall(r'-?\d+(?:\.\d+)?',p.get('d'))]
            require(len(coords)==16 and amount>=0,'PATH_STRUCTURE')
            require(abs(abs(coords[15]-coords[1])-expected)<D('.0002') and abs(abs(coords[9]-coords[7])-expected)<D('.0002'),'RIBBON_ACTUAL_MONEY_WIDTH')
        if grammar.startswith('INSURANCE_'):require(svg.get('data-accounting-basis')=='MANAGEMENT_LEGACY_PREMIUM_STATISTICS_NOT_CAS25','PREMIUM_NOT_CAS25')
        return {'status':'PASS','grammar':grammar,'observed_source_rows':len(nodes)+len(ribbons)}
    if grammar=='FINANCIALS_TYPED_FULL_PNL_SIGNED_V1':
        require(svg.get('data-original-pdf-sha256')==pdf_sha,'ORIGINAL_PDF')
        rows=[r for r in svg.iter(NS+'rect') if r.get('data-stage-id')]
        require(bool(rows),'SIGNED_ROWS')
        for r in rows:
            before,delta,after=map(D,(r.get('data-before-yuan'),r.get('data-signed-yuan'),r.get('data-after-yuan')))
            require(before+delta==after,'SIGNED_CUMULATIVE')
            require(abs(D(r.get('width'))-abs(delta)/D(r.get('data-money-scale-yuan-per-unit')))<D('.00001'),'SIGNED_MONEY_WIDTH')
            require(bool(r.get('data-source-fact-ids')) and bool(r.get('data-physical-pages')),'SIGNED_ORIGINAL_FACTS')
        return {'status':'PASS','grammar':grammar,'observed_source_rows':len(rows)}
    from profit_chain_audit import immutable_v10
    original=immutable_v10(markup,issuer,pdf_sha)
    if original:return original
    raise ValueError('UNMIGRATED_FINANCIAL_FIGURE '+str(grammar))


def _audit_sequential(codes,out,origin=None):
    from playwright.sync_api import sync_playwright
    catalog_data=json.loads((ROOT/'site/research_catalog.json').read_text())
    catalog=catalog_data['issuers'];by_code={r['code']:r for r in catalog}
    sources=catalog_data['figure_quality_contracts']['FULL_SOURCE_FIGURES_V1']['source_review_indices']
    notes={}
    for index in sources:notes.update(json.loads((ROOT/index).read_text())['issuers'])
    out.mkdir(parents=True,exist_ok=True)
    result={'schema':'financials.complete_figure_migration.v1','scope':'ACTUAL_FULL_ARTICLE_FIGURES_NOT_HUMAN_ART_CERTIFICATION','origin':origin or 'LOCAL_FILE_SOURCE','issuers':{},'cases':[],'status':'IN_PROGRESS'}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for code in codes:
            row=by_code[code];path=ROOT/'public'/row['href'].lstrip('/');raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest()
            dossier=json.loads((ROOT/row['source_publication']/'source-ledger.json').read_text()) if row.get('source_publication') else None
            pdf=notes[code]['source_sha256']
            require_path=ROOT/notes[code]['source_path']
            if hashlib.sha256(require_path.read_bytes()).hexdigest()!=pdf:raise ValueError('ORIGINAL_PDF_ARCHIVE_SHA_DRIFT '+code)
            result['issuers'][code]={'html_sha256':sha,'pdf_sha256':pdf,'complete_figure_migration':'NOT_CHECKED'}
            for width in (1440,768,390):
                page=browser.new_page(viewport={'width':width,'height':1000},accept_downloads=True);errors=[]
                page.on('pageerror',lambda exc:errors.append(str(exc)))
                response=page.goto(origin.rstrip('/')+row['href'] if origin else path.as_uri(),wait_until='load',timeout=45000)
                if origin and (not response or response.body()!=raw):raise ValueError('LIVE_FULL_HTML_BYTES_DIFFER '+code)
                page.evaluate('document.fonts.ready')
                if row.get('editorial_contract'):
                    from profit_chain_audit import check_reader
                    check_reader(page)
                    check_reader(page,expanded=True)
                measured=page.evaluate(MEASURE)
                faults=[s for s in measured['svgs'] if s['clippedLabels'] or s['possibleLabelOverlaps'] or s['below10px']]
                if faults or errors or measured['body']['scroll']>measured['body']['client']+1:
                    (out/'failure.json').write_text(json.dumps({'issuer':code,'width':width,'faults':faults,'errors':errors},ensure_ascii=False,indent=2));raise ValueError('ACTUAL_RENDER_BLOCKED '+code+' '+str(width))
                case={'issuer':code,'width':width,'html_sha256':sha,'figures':[]}
                if row.get('editorial_contract'):case['editorial_main_layer']='PASS'
                for index,figure in enumerate(page.locator('figure').all()):
                    visible=figure.locator('svg:visible')
                    if visible.count()!=1:raise ValueError('EACH_FIGURE_NEEDS_ONE_VISIBLE_VECTOR '+code+' '+str(index))
                    diagram=visible.first;markup=diagram.evaluate('e=>e.outerHTML');checked=check_vector(markup,code,pdf)
                    if dossier:
                        from source_publication_audit import check_vector_source
                        check_vector_source(markup,dossier)
                    vb=diagram.get_attribute('viewBox').split();expected=330 if width<=850 else (1040,1100)
                    if (width<=850 and float(vb[2])!=expected) or (width>850 and float(vb[2]) not in expected):raise ValueError('NOT_INDEPENDENT_NATIVE_EDITION')
                    stem=f'{code}-{width}-figure-{index+1:02d}'
                    screenshot=out/(stem+'.png');figure.screenshot(path=str(screenshot))
                    buttons=figure.locator('button').filter(has_text=re.compile('SVG'))
                    if buttons.count()!=1:raise ValueError('ONE_WORKING_SVG_EXPORT_REQUIRED '+code+' '+str(index))
                    with page.expect_download(timeout=12000) as pending:buttons.first.click()
                    dest=out/(stem+'.svg');pending.value.save_as(str(dest));export=dest.read_text()
                    visible_now=diagram.evaluate('e=>new XMLSerializer().serializeToString(e)')
                    if export!=visible_now:raise ValueError('DOWNLOADED_VECTOR_IS_NOT_VISIBLE_EDITION '+code+' '+str(index))
                    check_vector(export,code,pdf)
                    case['figures'].append({'index':index,'id':figure.get_attribute('id'),'grammar':checked['grammar'],'vector_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'screenshot_sha256':hashlib.sha256(screenshot.read_bytes()).hexdigest(),'screenshot_file':str(screenshot.relative_to(out)),'export_file':dest.name,'source_and_actual_geometry':'PASS','visible_edition_download':'PASS'})
                if not case['figures']:raise ValueError('NO_SOURCE_FINANCIAL_FIGURES')
                if len(case['figures'])!=row['figures']:raise ValueError('CATALOG_ACTUAL_FIGURE_COUNT_DRIFT '+code)
                result['cases'].append(case);page.close()
                print('COMPLETE_SOURCE_FIGURE_MIGRATION',code,width,len(case['figures']),flush=True)
            counts={len(c['figures']) for c in result['cases'] if c['issuer']==code}
            if len(counts)!=1:raise ValueError('FIGURE_HIDDEN_IN_DIFFERENT_EDITION '+code)
            result['issuers'][code].update(complete_figure_migration='PASS_LOCAL' if not origin else 'PASS_PRODUCTION',figure_count=counts.pop())
        browser.close()
    result['status']='PASS_LOCAL' if not origin else 'PASS_PRODUCTION'
    result['independent_human_art_review']='NOT_CHECKED'
    result['svg_exports']=sum(len(c['figures']) for c in result['cases'])
    (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result

def audit(codes,out,origin=None,workers=3):
    """Independent browser workers; every original case/file survives merging."""
    from concurrent.futures import ThreadPoolExecutor
    import shutil
    codes=list(codes);out=Path(out)
    if not codes or len(codes)!=len(set(codes)):raise ValueError('QA_EMPTY_OR_DUPLICATE_ISSUER')
    out.mkdir(parents=True,exist_ok=True);(out/'result.json').unlink(missing_ok=True)
    if len(codes)<4 or workers==1:return _audit_sequential(codes,out,origin)
    count=min(workers,len(codes));folders=[out/('worker-'+str(i+1)) for i in range(count)]
    def one(i):return _audit_sequential(codes[i::count],folders[i],origin)
    with ThreadPoolExecutor(max_workers=count) as pool:parts=list(pool.map(one,range(count)))
    result=dict(parts[0]);result['issuers']={};result['cases']=[]
    for folder,part in zip(folders,parts):
        if part['origin']!=result['origin'] or part['status']!=result['status']:raise ValueError('QA_WORKER_ORIGIN_OR_STATUS')
        if set(result['issuers'])&set(part['issuers']):raise ValueError('QA_WORKER_ISSUER_OVERLAP')
        result['issuers'].update(part['issuers']);result['cases'].extend(part['cases'])
        for f in folder.iterdir():
            if f.suffix in ('.svg','.png'):shutil.copyfile(f,out/f.name)
    expected={(code,w) for code in codes for w in (1440,768,390)}
    if set(result['issuers'])!=set(codes) or len(result['cases'])!=len(expected) or {(c['issuer'],c['width']) for c in result['cases']}!=expected:raise ValueError('QA_INCOMPLETE_PARALLEL_RESULT')
    result['svg_exports']=sum(len(c['figures']) for c in result['cases'])
    result['execution_workers']=count
    (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--codes',required=True,nargs='+');parser.add_argument('--out',type=Path,required=True);parser.add_argument('--origin')
    args=parser.parse_args();audit(args.codes,args.out,args.origin)
