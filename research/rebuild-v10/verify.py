from __future__ import annotations
import json, hashlib, re, sys, os
from decimal import Decimal as D
from pathlib import Path
import fitz
HERE=Path(__file__).parent
ROOT=Path(os.environ.get('FINANCIALS_SOURCE_ROOT', HERE.parent/'work'))
EXTRA=json.loads((HERE/'extras.json').read_text())
SRC={
'688111': ROOT/'financials_v8_case_study/sources/688111_2026H1_original.pdf',
'600519': ROOT/'financials_v8_case_study/sources/600519_2026H1_original.pdf',
'000333': ROOT/'financials_v8_case_study/sources/000333_2026H1_original.pdf',
'600036': ROOT/'additional/600036_2026H1_original.pdf'
}
LEDGER={x:json.loads((ROOT/f'financials_v8_case_study/research/{x}_2026H1_ledger.json').read_text()) for x in ['688111','600519','000333']}
SHA={'600036':'0194f5122575ee8576dbce941fcc10fb171e0cd17c627dd63330da952c52b57c'}
for k,d in LEDGER.items():SHA[k]=d['source']['pdf_sha256']
DCT={}
def get(code,key):
 if key in EXTRA[code] and isinstance(EXTRA[code][key],dict):return D(EXTRA[code][key]['val'])
 return D(LEDGER[code]['facts'][key]['yuan'])
def facts(code):
 def stated_period(key,record):
  # A prior closing stock is dated 2025-12-31, not the prior H1 flow.
  # Do not silently re-label comparative 2025H1 income/cash facts as 2026H1.
  if record.get('period'): return record['period']
  if key.endswith('_prior_bs') or key in {'assets_prior','liabilities_prior','equity_prior','contract_liab_prior','inventory_prior','customer_deposits_prior','net_loans_prior','ar_prior_bs','npl_pct_prior','coverage_pct_prior','cet1_pct_prior'}:
   return '2025-12-31'
  if key.endswith('_prior'): return '2025H1'
  if key.endswith('_begin_bs'): return '2025-12-31'
  return '2026H1'
 return {**(LEDGER[code]['facts'] if code in LEDGER else {}),**{k:{'yuan':v['val'],'page':v['page'],'label':v['label'],'period':stated_period(k,v),'scope':'consolidated','status':v.get('status','DISCLOSED'),'reported_unit':v.get('unit',EXTRA[code]['statement_unit'])} for k,v in EXTRA[code].items() if isinstance(v,dict)}}
def check(code):
 p=SRC[code];assert p.is_file(),p
 assert hashlib.sha256(p.read_bytes()).hexdigest()==SHA[code], 'source hash mismatch '+code
 pdf=fitz.open(p); f=facts(code)
 mismatches=[]; notes=[]
 for key,v in f.items():
  if v.get('status')=='DERIVED':notes.append(key);continue
  page=v['page'];text=pdf[page-1].get_text(sort=True)
  orig=D(str(v['yuan']));unit=v.get('reported_unit','元')
  if unit=='%':pass
  elif '百万元' in unit:orig/=D(1000000)
  elif '万元' in unit: orig/=D(10000)
  elif '千元' in unit:orig/=D(1000)
  # numeric tokens only, exact number in the claimed original page (not semantic row-col verification)
  num=('{:,.2f}'.format(orig)) if orig!=orig.to_integral_value() else '{:,.0f}'.format(orig)
  q=num.lstrip('-').replace(',','')
  original=text.replace(',','').replace(' ','').replace('\n','')
  if q not in original: mismatches.append({'field':key,'page':page,'expected':num,'unit':unit})
  else: notes.append(key)
 if mismatches:print('PAGE_NUMERIC_MISMATCH',code,mismatches[:12],file=sys.stderr)
 # hard invariants independent of PDF string matching
 a,l,e=[get(code,k) for k in ('assets_bs','liabilities','equity')]
 assert a==l+e,(code,'BS now',a-l-e)
 ap,lp,ep=[get(code,k) for k in ('assets_prior_bs','liabilities_prior','equity_prior')]
 assert ap==lp+ep,(code,'BS prior',ap-lp-ep)
 asserts=['BS_2026','BS_2025']
 if code in ('688111','000333','600036'):
  pfx={'688111':('cash_begin','cfo','cfi','cff','cash_fx','cash_close'),
      '000333':('cash_begin_bs','cfo','cfi_bs','cff_bs','fx_bs','cash_close_bs'),
      '600036':('cash_begin_bs','cfo','cfi_bs','cff_bs','fx_bs','cash_close_bs')}[code]
  a,cfo,cfi,cff,fx,z=[get(code,x) for x in pfx]
  assert a+cfo+cfi+cff+fx==z,(code,'cash identity',a+cfo+cfi+cff+fx-z)
  asserts+=['CASH_CLOSE']
 elif code=='600519':
  assert get(code,'cfo')+get(code,'cfi_bs')+get(code,'cff_bs')+get(code,'fx_bs')==get(code,'cash_change')
  asserts+=['CASH_CHANGE']
 if code=='688111':
  assert sum(get(code,k) for k in ('wps_personal','wps365','wps_software','other_rev'))==get(code,'rev')
  asserts+=['REV_SEGMENTS']
 if code=='600519':
  assert sum(get(code,k) for k in ('maotai_rev','series_rev','other_rev'))==get(code,'rev')
  assert get(code,'direct_rev')+get(code,'wholesale_rev')==get(code,'rev')
  asserts+=['PRODUCT_REV','CHANNEL_REV']
 if code=='000333':
  assert sum(get(code,k) for k in ('home','industrial_solution','other_total'))==get(code,'rev')
  assert sum(get(code,k) for k in ('building','robotics','industrial_tech','sub_other'))==get(code,'industrial_solution')
  assert get(code,'rev')+get(code,'interest_income')+get(code,'fee_income')==get(code,'total_rev')
  assert get(code,'parent_ni')+get(code,'nci_ni')==get(code,'consolidated_ni')
  assert get(code,'parent_ni')-get(code,'reg_ni')==get(code,'nonrecurring_net')
  asserts+=['REV_SEGMENTS','SEGMENT_HIERARCHY','TOTAL_REVENUE','MINORITY_PROFIT','DEDUCTED_PROFIT']
 if code=='600036':
  assert sum(get(code,k) for k in ('taxes_surcharges','other_asset_impairment','other_business_cost'))==get(code,'other_operating_cost')
  assert get(code,'revenue')-get(code,'administrative_expense')-get(code,'credit_impairment_expense')-get(code,'other_operating_cost')==get(code,'operating_profit')
  assert get(code,'operating_profit')+get(code,'nonoperating_income')-get(code,'nonoperating_expense')-get(code,'income_tax_expense')==get(code,'consolidated_ni')
  assert get(code,'interest_in')-get(code,'interest_out')==get(code,'nii')
  assert get(code,'nii')+get(code,'fees_net')+get(code,'other_net')==get(code,'revenue')
  assert get(code,'parent_ni')+get(code,'nci_ni')==get(code,'consolidated_ni')
  asserts+=['NET_INTEREST','REVENUE','MINORITY_PROFIT','FULL_PNL_TO_PARENT','OTHER_OPERATING_COST_COMPONENTS']

 # complete disclosed indirect reconciliation, when the issuer provides one
 if code in ('688111','600519','000333'):
  comp=json.loads((HERE/'cfo_components.json').read_text())[code]
  bs=D(comp['start'][1])+sum((D(v[1]) for v in comp['parts']),D(0))
  assert bs==D(comp['end'][1])==get(code,'cfo'),(code,'CFO indirect failure')
  for label,amt,pg in [comp['start'],comp['end']]+[row[:3] for row in comp['parts']]:
   original=pdf[int(pg)-1].get_text(sort=True).replace(',','').replace(' ','').replace('\n','')
   value=D(amt)
   if code=='000333':value/=D(1000)
   magnitude=('{:.2f}'.format(abs(value)) if code!='000333' else '{:.0f}'.format(abs(value)))
   if value<0:
    assert ('-'+magnitude in original or '('+magnitude+')' in original),(code,'Signed CFO source not found',label,pg,magnitude)
   else:
    assert magnitude in original,(code,'CFO source not found',label,pg,magnitude)
  asserts+=['CFO_INDIRECT_ALL_REPORTED_ADJUSTMENTS','CFO_SIGNED_LITERAL_SOURCE_ITEMS']
 return {'ticker':code,'sha256':SHA[code],'pdf_pages':len(pdf),'selected_facts':len(f),'literal_page_numeric_found':len(notes),'literal_page_numeric_missing':mismatches,'accounting_identities':asserts,'numeric_only_not_semantic_review':True}

if __name__=='__main__':
 result=[check(x) for x in ['600036','688111','600519','000333']]
 (HERE/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps(result,ensure_ascii=False,indent=2))