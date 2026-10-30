#!/usr/bin/env python3
"""Conservative PRC GAAP consistency checks for a source-ledger; not a PDF parser.

Usage: python scripts/audit.py evidence.json --out qa.json
Returns 0 for passed or not-checkable optional identities; 2 for definite failures.
"""
import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import hashlib

EPS = Decimal('0.005')
REQUIRED_META = ['issuer','ticker','report_type','period_start','period_end','period_key','currency','pages','scope','audited','source_filename','source_sha256']
REQUIRED_FACT_META = ['amount','page','source_label','period','kind','scope','table','status','source_confidence']
APPROVED_STATUS = {'reported','calculated','unavailable'}


def decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def audit(data):
    doc, facts = data.get('document', {}), data.get('facts', {})
    issues, checks = [], []
    for k in REQUIRED_META:
        if k not in doc or doc[k] in (None, ''):
            issues.append(f'document missing {k}')
    if doc.get('currency') != 'CNY':
        issues.append('Currently only CNY-yuan ledger units supported; do not silently convert')
    if doc.get('scope') != 'consolidated':
        issues.append('Expected consolidated ledger; parent-company-only ledger needs another audit configuration')
    page_count = doc.get('pages')
    main_period = doc.get('period_key')
    previous_period = doc.get('comparative_period_key')
    previous_stock = doc.get('previous_stock_date')
    corrupted = set()
    verification_pending = []
    for k, f in facts.items():
        if not isinstance(f, dict):
            issues.append(f'{k}: fact is not an object'); corrupted.add(k); continue
        for p in REQUIRED_FACT_META:
            if p not in f or f[p] in ('', None):
                issues.append(f'{k}: missing {p}'); corrupted.add(k)
        val = decimal(f.get('amount'))
        if val is None or not val.is_finite():
            issues.append(f'{k}: invalid exact decimal amount'); corrupted.add(k)
        if not isinstance(f.get('page'), int) or isinstance(page_count, int) and not (1 <= f['page'] <= page_count):
            issues.append(f'{k}: page out of bounds or not integer'); corrupted.add(k)
        if f.get('status') not in APPROVED_STATUS:
            issues.append(f'{k}: disallowed status {f.get("status")}'); corrupted.add(k)
        if f.get('scope') != doc.get('scope'):
            issues.append(f'{k}: consolidated/parent scope mismatch'); corrupted.add(k)
        kind = f.get('kind')
        period = f.get('period')
        if kind == 'flow' and period not in (main_period, previous_period):
            issues.append(f'{k}: incompatible flow period {period}'); corrupted.add(k)
        elif kind == 'stock' and period not in (doc.get('period_end'), previous_stock):
            issues.append(f'{k}: incompatible stock date {period}'); corrupted.add(k)
        elif kind not in ('flow','stock'):
            issues.append(f'{k}: unknown period kind'); corrupted.add(k)
        if f.get('status')=='reported' and (not f.get('image_checked') or f.get('source_confidence')!='pdf_page_checked'):
            verification_pending.append(k)
        if f.get('status') == 'calculated' and (not f.get('formula') or not f.get('inputs')):
            issues.append(f'{k}: calculated fact needs formula and inputs'); corrupted.add(k)
    if not facts:
        issues.append('empty facts ledger')
    # Current-field identities cannot mix prior-period values under correct-looking names.
    prior_flow = doc.get('comparative_period_key')
    for key, fact in facts.items():
        if not isinstance(fact, dict) or key in corrupted: continue
        expected = (prior_flow if key.endswith('_prior') else main_period) if fact.get('kind')=='flow' else (previous_stock if key.endswith('_prior') else doc.get('period_end'))
        if fact.get('period') != expected:
            issues.append(f'{key}: expected period {expected}, got {fact.get("period")}')
            corrupted.add(key)

    def number(key):
        if key not in facts or key in corrupted:
            return None
        return decimal(facts[key].get('amount'))

    def equation(label, expected_key, component_keys, signs=None):
        keys = [expected_key] + list(component_keys)
        unavailable = [key for key in keys if number(key) is None]
        if unavailable:
            checks.append({'id':label,'status':'NOT_CHECKED','missing':unavailable})
            return
        signs = signs or [1]*len(component_keys)
        actual = number(expected_key)
        calc = sum((number(k)*D(s) for k,s in zip(component_keys,signs)), D(0))
        residue = actual - calc
        checks.append({'id':label,'status':'PASS' if abs(residue) <= EPS else 'FAIL','expected':str(actual),'computed':str(calc),'residual':str(residue),'inputs':keys})

    D = Decimal
    equation('assets=liabilities+equity','assets',['liabilities','equity'])
    equation('assets=current+noncurrent','assets',['current_assets','noncurrent_assets'])
    equation('operating-profit-reconciliation','operating_profit',['revenue','total_operating_costs','other_income','investment_income','fair_value_income','credit_impairment','asset_impairment','disposal_income'],[1,-1,1,1,1,1,1,1])
    equation('net-profit-reconciliation','net_profit',['operating_profit','nonop_income','nonop_expense','income_tax'],[1,1,-1,-1])
    equation('parent+minority=net-profit','net_profit',['parent_profit','minority_profit'])
    equation('cash-close=open+net-flows+fx','cash_close',['cash_open','cfo','cfi','cff','fx_effect'])
    equation('gross-profit=revenue-cogs','gross_profit',['revenue','cogs'],[1,-1])
    # This is an auditable quantity equality; do not confuse residual with a standalone product.
    if data.get('segments'):
        seg_keys = [s.get('revenue_key') for s in data['segments'] if s.get('dimension') == 'product' and s.get('revenue_key')]
        if seg_keys and number('revenue') is not None and all(number(k) is not None for k in seg_keys):
            residual = number('revenue') - sum((number(k) for k in seg_keys), D(0))
            checks.append({'id':'product-coverage','status':'PASS' if residual >= -EPS else 'FAIL','disclosed_products':seg_keys,'residual_not_a_segment':str(residual),'message':'Residual must be labeled as undisclosed difference, not a named disclosed segment.'})
        else:
            checks.append({'id':'product-coverage','status':'NOT_CHECKED'})
    else:
        checks.append({'id':'product-coverage','status':'NOT_CHECKED'})

    adj = data.get('indirect_cfo_adjustments')
    if adj is not None:
        if number('net_profit') is None or number('cfo') is None or not adj:
            checks.append({'id':'indirect-cfo-reconciliation','status':'NOT_CHECKED','missing':['net_profit/cfo/adjustments']})
        else:
            try:
                amounts = [D(str(a['amount'])) for a in adj]
                if any(not a.is_finite() for a in amounts):
                    raise ValueError('nonfinite')
                for i,a in enumerate(adj):
                    if not isinstance(a.get('page'),int) or not a.get('source_label'):
                        issues.append(f'indirect CFO adjustment {i} missing source page/label')
                computed = number('net_profit') + sum(amounts, D(0))
                residual = number('cfo')-computed
                checks.append({'id':'indirect-cfo-reconciliation','status':'PASS' if abs(residual)<=EPS else 'FAIL','residual':str(residual),'computed':str(computed),'expected':str(number('cfo')),'adjustment_count':len(adj)})
            except (InvalidOperation,ValueError,TypeError,KeyError) as exc:
                checks.append({'id':'indirect-cfo-reconciliation','status':'FAIL','error':str(exc)})
    else:
        checks.append({'id':'indirect-cfo-reconciliation','status':'NOT_CHECKED','note':'No published indirect bridge supplied'})

    if number('capex_cash') is not None and number('cfo') is not None:
        fcf = number('cfo')-number('capex_cash')
        checks.append({'id':'simple-fcf-calculation','status':'PASS','formula':'CFO - cash paid to acquire/build long-term assets','derived_fcf':str(fcf),'note':'Simplified derived metric, not explicitly reported by issuer'})
    else:
        checks.append({'id':'simple-fcf-calculation','status':'NOT_CHECKED'})

    summary = {'PASS':0,'FAIL':0,'NOT_CHECKED':0}
    for check in checks: summary[check['status']]+=1
    status = 'BLOCKED' if issues or summary['FAIL'] else ('CONDITIONAL_DRAFT' if summary['NOT_CHECKED'] or verification_pending else 'CALCULATION_PASS_MANUAL_REVIEW_REQUIRED')
    return {'status':status,'summary':summary,'issues':issues,'verification_pending':verification_pending,'checks':checks,'warning':'A computational PASS is not a publication sign-off; verify page images, original cells, scope, narrative and rendered outputs.'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('ledger'); ap.add_argument('--out',default=None); ap.add_argument('--pdf',default=None,help='Optionally verify the actual source PDF SHA256 against ledger')
    args=ap.parse_args()
    data=json.loads(Path(args.ledger).read_text(encoding='utf-8'))
    result=audit(data)
    if args.pdf:
        source=Path(args.pdf)
        if not source.is_file():
            result['issues'].append('Source PDF not found: '+str(source))
        else:
            found=hashlib.sha256(source.read_bytes()).hexdigest()
            if found!=data.get('document',{}).get('source_sha256'):
                result['issues'].append('Source PDF SHA256 does NOT match evidence ledger')
        if result['issues']: result['status']='BLOCKED'
    serialized=json.dumps(result,ensure_ascii=False,indent=2)
    if args.out:
        path=Path(args.out);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(serialized+'\n',encoding='utf-8')
    print(serialized)
    raise SystemExit(2 if result['status']=='BLOCKED' else 0)

if __name__=='__main__': main()