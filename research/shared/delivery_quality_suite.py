"""Full-library quality checks invoked by the existing two-sector CI entrypoint.

Extends the already authorized source/browser validation job; no new workflow
or new token scope is required. Never executes while imported.
"""
import json,hashlib
from pathlib import Path
import subprocess,sys,os
ROOT=Path(__file__).resolve().parents[2]
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
    from source_publication import publish
    for issuer in catalog['issuers']:
        if issuer.get('source_publication'):
            original=ROOT/'public'/issuer['href'].lstrip('/')
            rebuilt=Path(out)/('rebuilt-'+issuer['code']+'.html')
            publish(ROOT/issuer['source_publication'],rebuilt)
            if rebuilt.read_bytes()!=original.read_bytes():raise ValueError('NEW_DOSSIER_CLEAN_REBUILD_DRIFT '+issuer['code'])
    checks=[['-O','-m','unittest','discover','-s','research/shared','-p','test_signed_period_generalization.py'],['-O','-m','unittest','discover','-s','research/shared','-p','test_editorial_bridge.py'],['-m','unittest','discover','-s','research/quality/historical-peer-evidence','-p','test_evidence.py'],['-m','unittest','discover','-s','research/shared','-p','test_*.py'],
            ['-O','-m','unittest','discover','-s','research/shared','-p','test_*economics*.py'],
            ['-O','-m','unittest','discover','-s','research/shared','-p','test_income_generalization.py'],
            ['-m','unittest','discover','-s','research/rebuild-v10','-p','test_bank_profit_bridge.py'],
            ['-m','unittest','discover','-s','research/rebuild-v10','-p','test_profit_mobile_typography.py']]
    for args in checks:subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
    sys.path.insert(0,str(ROOT/'scripts'))
    from audit_delivery_matrix import audit
    result=audit(Path(out))
    if result['blockers']:raise ValueError('FULL_LIBRARY_DELIVERY_BLOCKED '+repr(result['blockers']))
    from qa_editorial_migration import audit as full_figure_audit
    catalog=json.loads((ROOT/'site/research_catalog.json').read_text())
    codes=[r['code'] for r in catalog['issuers'] if r.get('figure_quality_contract')=='FULL_SOURCE_FIGURES_V1']
    # Newly added issuers cannot inherit the four pre-migration V10 snapshots.
    snapshots=catalog['figure_quality_contracts']['FULL_SOURCE_FIGURES_V1']['historical_exact_html_snapshots']
    missing=[r['code'] for r in catalog['issuers'] if r.get('figure_quality_contract')!='FULL_SOURCE_FIGURES_V1' and
             hashlib.sha256((ROOT/'public'/r['href'].lstrip('/')).read_bytes()).hexdigest()!=snapshots.get(r['code'])]
    if missing:raise ValueError('NEW_ISSUER_WITHOUT_COMPLETE_FIGURE_CONTRACT '+repr(missing))
    full_figure_audit(codes,Path(out)/'complete-source-figures')
    from qa_source_publication_local import run as check_source_webkit
    check_source_webkit(Path(out)/'new-source-webkit')
    print('FULL_LIBRARY_FINANCIAL_AND_BROWSER_CI_GATE_PASS',flush=True)
if __name__=='__main__':run(ROOT/'research/issuers/600276/visual-qa/full-library')
