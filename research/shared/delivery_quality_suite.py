"""Full-library quality checks invoked by the existing two-sector CI entrypoint.

Extends the already authorized source/browser validation job; no new workflow
or new token scope is required. Never executes while imported.
"""
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
    checks=[['-O','-m','unittest','discover','-s','research/shared','-p','test_signed_period_generalization.py'],['-m','unittest','discover','-s','research/quality/historical-peer-evidence','-p','test_evidence.py'],['-m','unittest','discover','-s','research/shared','-p','test_*.py'],
            ['-O','-m','unittest','discover','-s','research/shared','-p','test_*economics*.py'],
            ['-O','-m','unittest','discover','-s','research/shared','-p','test_income_generalization.py'],
            ['-m','unittest','discover','-s','research/rebuild-v10','-p','test_bank_profit_bridge.py'],
            ['-m','unittest','discover','-s','research/rebuild-v10','-p','test_profit_mobile_typography.py']]
    for args in checks:subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
    sys.path.insert(0,str(ROOT/'scripts'))
    from audit_delivery_matrix import audit
    result=audit(Path(out))
    if result['blockers']:raise ValueError('FULL_LIBRARY_DELIVERY_BLOCKED '+repr(result['blockers']))
    print('FULL_LIBRARY_FINANCIAL_AND_BROWSER_CI_GATE_PASS',flush=True)
if __name__=='__main__':run(ROOT/'research/issuers/600276/visual-qa/full-library')
