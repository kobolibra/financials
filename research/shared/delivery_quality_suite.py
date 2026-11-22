"""Full-library quality checks invoked by the existing two-sector CI entrypoint.

Extends the already authorized source/browser validation job; no new workflow
or new token scope is required. Never executes while imported.
"""
import json,hashlib,re
from pathlib import Path
import subprocess,sys,os
ROOT=Path(__file__).resolve().parents[2]

def source_preview_evidence_errors(issuer, html_sha, record, receipt, *, engine='chromium', widths=(1440, 768, 390)):
    """Validate the exact-byte evidence for a newly added source-limited report.

    A report with a different figure grammar cannot borrow the legacy
    full-figure receipt. Recheck its current HTML in real browsers below.
    """
    errors = []
    code = issuer['code']
    if (record.get('schema_version') != 1 or record.get('code') != code
            or record.get('period') != issuer.get('period')
            or record.get('release_class') != 'source_limited_preview'
            or record.get('report_route') != issuer.get('href')
            or record.get('report_file') != 'public/' + issuer['href'].lstrip('/')):
        errors.append('NEW_SOURCE_PREVIEW_IDENTITY_OR_RELEASE_CLASS')
    deployed = record.get('published_html_sha256')
    candidate = record.get('unmerged_candidate')
    if deployed != html_sha and not (
            isinstance(candidate, dict)
            and isinstance(deployed, str) and re.fullmatch(r'[a-f0-9]{64}', deployed)
            and candidate.get('base_deployed_html_sha256') == deployed
            and candidate.get('candidate_full_html_sha256') == html_sha
            and candidate.get('promotion_status') == 'UNMERGED_NOT_DEPLOYED'
            and candidate.get('independent_finance_and_art_review') == 'NOT_CHECKED'):
        errors.append('NEW_SOURCE_PREVIEW_STALE_HTML_SHA')
    required = ('PDF_BYTES', 'SOURCE_ROW_COLUMN', 'ACCOUNTING_CORE',
                'RESEARCH_COUNTERCASE', 'CHART_SEMANTICS', 'VISUAL_EDITORIAL_SELF',
                'BROWSER_LOCAL', 'OFFLINE_REBUILD')
    gates = record.get('gates', {})
    if not isinstance(gates, dict) or any(gates.get(k, {}).get('status') != 'PASS' for k in required):
        errors.append('NEW_SOURCE_PREVIEW_P0_GATE_NOT_PASS')
    if not isinstance(receipt, dict) or receipt.get('browser') != engine or receipt.get('sha256') != html_sha:
        errors.append('NEW_SOURCE_PREVIEW_BROWSER_SOURCE_SHA_DRIFT')
        return errors
    views = receipt.get('viewports', [])
    if (not isinstance(views, list) or len(views) != len(widths)
            or {v.get('width') for v in views if isinstance(v, dict)} != set(widths)):
        errors.append('NEW_SOURCE_PREVIEW_VIEWPORTS_INCOMPLETE')
        return errors
    common_ids = None
    for view in views:
        figures = view.get('figures', [])
        if not isinstance(figures, list) or len(figures) != issuer.get('figures'):
            errors.append('NEW_SOURCE_PREVIEW_FIGURE_COUNT_DRIFT')
            continue
        ids = [f.get('id') for f in figures if isinstance(f, dict)]
        if len(ids) != len(figures) or len(set(ids)) != len(ids) or any(not x for x in ids):
            errors.append('NEW_SOURCE_PREVIEW_FIGURE_ID_INVALID')
            continue
        if common_ids is None:
            common_ids = ids
        elif ids != common_ids:
            errors.append('NEW_SOURCE_PREVIEW_FIGURES_DIFFER_BY_VIEWPORT')
        if sum(f.get('role') == 'primary' for f in figures) != 1:
            errors.append('NEW_SOURCE_PREVIEW_PRIMARY_FIGURE_INVALID')
        for figure in figures:
            if (figure.get('issues') or figure.get('overlap')
                    or not isinstance(figure.get('values'), list) or not figure['values']
                    or any(not isinstance(v.get('source'), str) or not v['source']
                           for v in figure['values'] if isinstance(v, dict))
                    or any(not isinstance(v, dict) for v in figure['values'])):
                errors.append('NEW_SOURCE_PREVIEW_UNPROVED_FIGURE_SOURCE_OR_GEOMETRY')
                break
    return errors

def run(out):
    # Rebuild the four V10 articles from independently re-downloaded original
    # bytes as part of this existing source/browser job, not a static receipt.
    env=dict(os.environ);env['FINANCIALS_SOURCE_ROOT']=str(ROOT/'work')
    subprocess.run([sys.executable,'research/rebuild-v10/download_originals.py'],cwd=ROOT,env=env,check=True)
    subprocess.run([sys.executable,'research/rebuild-v10/publisher.py'],cwd=ROOT,env=env,check=True)
    for code in ('688111','600519','000333','600036'):
        if (ROOT/'research/rebuild-v10/site'/f'{code}.html').read_bytes()!=(ROOT/'public/research/2026-h1-v10'/f'{code}.html').read_bytes():
            raise ValueError('ORIGINAL_PDF_REBUILD_BYTES_DRIFT '+code)
    catalog=json.loads((ROOT/'site/research_catalog.json').read_text())
    from profit_chain_audit import validate_source, bundle_for
    for issuer in catalog['issuers']:
        if issuer.get('editorial_contract'):validate_source(bundle_for(issuer['code']))
    for issuer in catalog.get('period_reports',[]):
        if issuer.get('editorial_contract'):validate_source(bundle_for(issuer['code']+'@'+issuer['period']))
    from source_publication import publish
    for issuer in catalog['issuers']+catalog.get('period_reports',[]):
        if issuer.get('source_publication'):
            original=ROOT/'public'/issuer['href'].lstrip('/')
            rebuilt=Path(out)/('rebuilt-'+Path(issuer['href']).stem+'.html')
            publish(ROOT/issuer['source_publication'],rebuilt)
            if rebuilt.read_bytes()!=original.read_bytes():raise ValueError('NEW_DOSSIER_CLEAN_REBUILD_DRIFT '+issuer['code'])
    checks=[['-m','unittest','discover','-s','scripts','-p','test_parallel_figure_audit.py'],['-m','unittest','discover','-s','research/shared','-p','test_signed_period_generalization.py'],['-m','unittest','discover','-s','research/shared','-p','test_editorial_bridge.py'],['-m','unittest','discover','-s','research/quality/historical-peer-evidence','-p','test_evidence.py'],['-m','unittest','discover','-s','research/shared','-p','test_*.py'],
            ['-m','unittest','discover','-s','research/shared','-p','test_*economics*.py'],
            ['-m','unittest','discover','-s','research/shared','-p','test_income_generalization.py'],
            ['-m','unittest','discover','-s','research/rebuild-v10','-p','test_bank_profit_bridge.py'],
            ['-m','unittest','discover','-s','research/rebuild-v10','-p','test_profit_mobile_typography.py']]
    for args in checks:subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
    sys.path.insert(0,str(ROOT/'scripts'))
    from audit_delivery_matrix import audit
    result=audit(Path(out),capture_all_figures=False)
    if result['blockers']:raise ValueError('FULL_LIBRARY_DELIVERY_BLOCKED '+repr(result['blockers']))
    from qa_editorial_migration import audit as full_figure_audit
    catalog=json.loads((ROOT/'site/research_catalog.json').read_text())
    codes=[r['code'] for r in catalog['issuers'] if r.get('figure_quality_contract')=='FULL_SOURCE_FIGURES_V1']
    # Later report periods of an issuer are audited with the same all-figure gate, keyed code@period.
    codes+=[r['code']+'@'+r['period'] for r in catalog.get('period_reports',[]) if r.get('figure_quality_contract')=='FULL_SOURCE_FIGURES_V1']
    # Existing fully migrated reports retain their strict source/figure gate.
    # A genuinely new source-limited issuer MUST supply a different, current-SHA
    # release contract and pass fresh Chromium + WebKit verification. Never
    # silently grandfather it via a historical 11-issuer snapshot.
    snapshots=catalog['figure_quality_contracts']['FULL_SOURCE_FIGURES_V1']['historical_exact_html_snapshots']
    source_previews=[]
    sys.path.insert(0,str(ROOT/'scripts'))
    from check_release_contract import validate_release
    for issuer in catalog['issuers']:
        if issuer.get('figure_quality_contract')=='FULL_SOURCE_FIGURES_V1':
            continue
        code=issuer['code']
        report=ROOT/'public'/issuer['href'].lstrip('/')
        html_sha=hashlib.sha256(report.read_bytes()).hexdigest()
        if snapshots.get(code)==html_sha:
            continue
        dossier=ROOT/'research/issuers'/code
        gate_file=dossier/'release-gates.json'
        browser_file=dossier/'visual-qa/result.json'
        if not gate_file.is_file() or not browser_file.is_file():
            raise ValueError('NEW_ISSUER_WITHOUT_CURRENT_SOURCE_PREVIEW_EVIDENCE '+code)
        record=json.loads(gate_file.read_text(encoding='utf8'))
        receipt=json.loads(browser_file.read_text(encoding='utf8'))
        errors=validate_release(ROOT,issuer,record)
        errors+=source_preview_evidence_errors(issuer,html_sha,record,receipt)
        if errors:
            raise ValueError('NEW_ISSUER_SOURCE_PREVIEW_EVIDENCE_INVALID '+code+' '+repr(errors))
        source_previews.append((issuer,html_sha,record,report))
    full_figure_audit(codes,Path(out)/'complete-source-figures')
    if source_previews:
        from qa_offline_candidate import audit as audit_source_preview
        for issuer,html_sha,record,report in source_previews:
            for engine,widths in (('chromium',(1440,768,390)),('webkit',(375,))):
                dest=Path(out)/'fresh-source-preview'/issuer['code']/engine
                audit_source_preview(report,dest,engine,widths)
                receipt=json.loads((dest/'browser.json').read_text(encoding='utf8'))
                errors=source_preview_evidence_errors(
                    issuer,html_sha,record,receipt,engine=engine,widths=widths)
                if errors:
                    raise ValueError('NEW_ISSUER_FRESH_BROWSER_REPLAY_INVALID '
                                     +issuer['code']+' '+engine+' '+repr(errors))
            print('NEW_ISSUER_SOURCE_PREVIEW_CURRENT_HTML_CHROMIUM_WEBKIT_PASS',
                  issuer['code'],html_sha,flush=True)
    from qa_source_publication_local import run as check_source_webkit
    check_source_webkit(Path(out)/'new-source-webkit')
    print('FULL_LIBRARY_FINANCIAL_AND_BROWSER_CI_GATE_PASS',flush=True)
if __name__=='__main__':run(ROOT/'research/issuers/600276/visual-qa/full-library')
