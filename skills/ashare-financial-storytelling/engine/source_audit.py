"""Checks whether reviewer-approved ledger amounts can be located on claimed PDF pages.

Numbers in broken PDF tables may be split across lines; such results are NOT proof
of the proper accounting row. This reports evidence matching + reviewer exceptions.
"""
import argparse, hashlib, json, re
from pathlib import Path
import fitz

def inspect(pdf:Path,ledger:dict):
  fingerprint=hashlib.sha256(pdf.read_bytes()).hexdigest()
  if fingerprint!=ledger['document']['source_sha256']:
    raise ValueError('Source PDF SHA-256 mismatch; stop publication')
  p=fitz.open(str(pdf));rows=[]
  for name,fact in ledger['facts'].items():
    if fact['status']!='reported':
      rows.append({'id':name,'status':'DERIVED_OR_UNCHECKED','page':fact['page']});continue
    page=p[fact['page']-1]
    original=page.get_text('text',sort=True)
    expected=fact['amount'];pretty=format(float(expected),',.2f') if '.' in expected else expected
    direct=pretty in original or expected in original
    reconstructed=re.sub(r'\D','',expected) in re.sub(r'\D','',original)
    status='VALUE_TEXT_FOUND' if direct else ('BROKEN_TABLE_DIGITS_POSSIBLE' if reconstructed else 'NOT_LOCATED_REVIEW_REQUIRED')
    rows.append({'id':name,'page':fact['page'],'status':status,'amount':expected,'source_label':fact.get('source_label'),'note':'value presence alone does not verify accounting label, prior column or period'})
  counts={k:sum(x['status']==k for x in rows) for k in {x['status'] for x in rows}}
  return {'sha256_match':True,'counts':counts,'rows':rows,'status':'SOURCE_TEXT_CROSSCHECK_NOT_MANUAL_SIGNOFF','warning':'Broken columns, missing text, and adjacent numbers require PDF page-image and table review.'}

def main():
  a=argparse.ArgumentParser();a.add_argument('--pdf',required=True);a.add_argument('--ledger',required=True);a.add_argument('--out',required=True);x=a.parse_args()
  data=inspect(Path(x.pdf),json.loads(Path(x.ledger).read_text()))
  Path(x.out).parent.mkdir(parents=True,exist_ok=True);Path(x.out).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
  print(data['counts'])
if __name__=='__main__':main()