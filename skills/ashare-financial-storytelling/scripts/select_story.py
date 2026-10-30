#!/usr/bin/env python3
"""Evidence-based chart *eligibility* shortlist, not an autonomous investment analyst.
Usage: python scripts/select_story.py ledger.json --out story_plan.json
"""
import argparse, json
from pathlib import Path
from audit import audit

def plan(data):
    qa=audit(data)
    facts=data.get('facts',{})
    valid=set(facts)
    def eligible(required, check=None):
        missing=sorted(set(required)-valid)
        if check:
            named=[c for c in qa['checks'] if c['id']==check]
            if not named or named[0]['status']!='PASS':
                return False, f'{check} not PASS',missing
        return not missing, ('required facts present; requires visual source verification' if not missing else 'missing required facts'),missing
    templates=[
      ('income_structure','利润是如何形成的',['revenue','cogs','operating_profit','net_profit'],'operating-profit-reconciliation',5),
      ('revenue_mix','业务增长由谁驱动',['revenue'], 'product-coverage',5),
      ('earnings_to_cash','利润如何转化为经营现金流',['net_profit','cfo'],'indirect-cfo-reconciliation',5),
      ('cash_movement','经营、投资、筹资与汇率如何影响现金',['cash_open','cash_close','cfo','cfi','cff','fx_effect'],'cash-close=open+net-flows+fx',4),
      ('balance_sheet','资产与负债权益结构如何变化',['assets','liabilities','equity','current_assets','noncurrent_assets'],'assets=liabilities+equity',3),
      ('earnings_quality','利润、经营现金流与现金资本开支是否同步',['parent_profit','cfo','capex_cash'],None,4),
    ]
    cards=[]
    for ident,title,req,check,materiality in templates:
        ok,explanation,missing=eligible(req,check)
        if ident=='revenue_mix':
            segments=data.get('segments',[])
            dimensions={s.get('dimension') for s in segments}
            revenue_keys=[s.get('revenue_key') for s in segments]
            if len(segments)<2 or len(dimensions)!=1 or any(k not in valid for k in revenue_keys):
                ok=False; explanation='At least two non-overlapping segments from exactly one dimension with sourced revenue required'
        if ident=='earnings_to_cash' and not data.get('indirect_cfo_adjustments'):
            ok=False; explanation='Published indirect CFO bridge missing'
        if data.get('document',{}).get('business_type') in ('bank','insurer','broker') and ident in ('income_structure','revenue_mix'):
            ok=False;explanation='Specialist financial-institution mapping required'
        cards.append({'id':ident,'question':title,'eligible':ok and qa['status']!='BLOCKED','reason':explanation if qa['status']!='BLOCKED' else 'ledger has accounting/provenance FAIL','missing':missing,'provisional_materiality_out_of_5':materiality,'editorial_scoring_required':['explanatory_power','reliability','nonredundancy','readability'],'note':'Eligibility is not a chart order or story thesis.'})
    return {'document':data.get('document',{}),'qa_status':qa['status'],'purpose':'Select 3–5 nonredundant narrative charts; all labels and causal claims remain editor-verified.','candidates':cards,'note':'Rank eligibility + significance; do not generate all eligible visuals mechanically.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('ledger');ap.add_argument('--out',default=None);a=ap.parse_args()
    out=plan(json.loads(Path(a.ledger).read_text(encoding='utf-8')))
    s=json.dumps(out,ensure_ascii=False,indent=2)
    if a.out:
        p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s+'\n',encoding='utf-8')
    print(s)
if __name__=='__main__':main()