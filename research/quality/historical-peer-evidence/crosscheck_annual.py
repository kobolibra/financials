from pathlib import Path
import pymupdf,re,json
from decimal import Decimal
B=Path(__file__).resolve().parent;panel=json.loads((B/'quarterly-panel.json').read_text());out=[]
for c in ['600900','600276','688220']:
 for y in [2024,2025]:
  d=pymupdf.open(B/f'{c}_{y}FY.pdf')
  for i,p in enumerate(d):
   s=p.get_text()
   if '分季度主要财务数据' in s and '第四季度' in s:
    s=s[s.index('分季度主要财务数据'):]+d[i+1].get_text()
    for m,label in [('revenue','营业收入'),('cfo','经营活动产生的现金流量净额')]:
     match=re.search(r'\s*'.join(label),s);assert match,(c,y,m)
     tail=s[match.end():];v=re.findall(r'[-−]?[\d,]+\.\d{2}',tail)[:4]
     for q in ([4] if y==2024 else [1,2,3,4]):
      r=next(r for r in panel['rows'] if r['issuer']==c and r['quarter']==f'{y}Q{q}'); expected=v[q-1].replace(',','').replace('−','-');actual=r['facts'][m]['value'];out.append(dict(issuer=c,quarter=f'{y}Q{q}',metric=m,annual_disclosed=expected,derived=actual,physical_page=i+1,match=Decimal(actual)==Decimal(expected)))
    break
(B/'annual-quarter-crosscheck.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps([r for r in out if not r['match']],ensure_ascii=False,indent=2));print('checks',len(out),'PASS',sum(r['match'] for r in out));assert all(r['match'] for r in out)
