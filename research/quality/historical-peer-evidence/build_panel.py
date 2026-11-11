from pathlib import Path
import json,sys,csv,pymupdf,hashlib,re
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B.parents[1]/'shared'))
from historical_panel import quarter_difference
facts=json.loads((B/'statement-facts.json').read_text()); idx={r['id']:r for r in facts}
# These two historical H1 column layouts need dedicated parsing and are outside target FY-Q3 differences.
idx['600276_2024H1']['facts'].pop('revenue',None)
rows=[]
for code in ['600900','600276','688220']:
 for year,q,end,prev in [(2024,4,'2024FY','2024Q3'),(2025,1,'2025Q1',None),(2025,2,'2025H1','2025Q1'),(2025,3,'2025Q3','2025H1'),(2025,4,'2025FY','2025Q3'),(2026,1,'2026Q1',None),(2026,2,'2026H1','2026Q1'),(2026,3,'2026Q3','2026H1')]:
  a=idx[code+'_'+end]; z=idx.get(code+'_'+str(prev)); out=dict(issuer=code,quarter=f'{year}Q{q}',unit='CNY yuan',scope='consolidated',classification='DERIVED_SINGLE_QUARTER' if z else 'DISCLOSED_Q1',facts={},comparability='AS_REPORTED_SCOPE; full note and acquisition audit NOT_CHECKED')
  for metric in ['revenue','cost','rd_expense','cfo']:
   af=a['facts'][metric];zf=z['facts'][metric] if z else None
   out['facts'][metric]={'value':quarter_difference(af['values'][0],zf['values'][0] if zf else None),'formula':f"{af['values'][0]} - {zf['values'][0] if zf else '0'}",'sources':[{'id':a['id'],'sha256':a['sha256'],'page':af['physical_page'],'operand':af['values'][0]}]+([{'id':z['id'],'sha256':z['sha256'],'page':zf['physical_page'],'operand':zf['values'][0]}] if z else [])}
  if code=='600900':out['comparability']='CAUTION: 2025 common-control acquisition restates 2024 Q1/H1; 2024Q4 retained as-original, no causal cross-break inference'
  rows.append(out)
# detect actual later comparative changes, independent of prose assumptions
revisions=[]
for code in ['600900','600276','688220']:
 for suffix in ['Q1','H1','Q3','FY']:
  old=idx.get(f'{code}_2024{suffix}');new=idx.get(f'{code}_2025{suffix}')
  if not old or not new:continue
  for k,of in old['facts'].items():
   if k in new['facts'] and of['values'][0]!=new['facts'][k]['values'][1]:revisions.append({'issuer':code,'period':'2024'+suffix,'metric':k,'original':of['values'][0],'later_comparative':new['facts'][k]['values'][1],'original_source':old['id'],'later_source':new['id'],'resolution':'REQUIRES_NOTE_RECONCILIATION; do not mechanically splice'})
(B/'quarterly-panel.json').write_text(json.dumps({'status':'24 quarter rows / 96 exact differences, NOT fully comparable causal panel','rows':rows,'comparative_revisions':revisions},ensure_ascii=False,indent=2))
with (B/'quarterly-panel.csv').open('w') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['issuer','quarter','revenue_CNY','cost_CNY','rd_expense_CNY','cfo_CNY','comparability'])
 for r in rows:w.writerow([r['issuer'],r['quarter']]+[r['facts'][k]['value'] for k in ['revenue','cost','rd_expense','cfo']]+[r['comparability']])
# Every operand must occur literally on its physical original PDF page.
for r in rows:
 for fact in r['facts'].values():
  for src in fact['sources']:
   p=B/(src['id']+'.pdf');assert hashlib.sha256(p.read_bytes()).hexdigest()==src['sha256'];d=pymupdf.open(p);s=d[src['page']-1].get_text().replace(',','').replace('−','-').replace('－','-');assert src['operand'] in s,(r['quarter'],src)
print('PASS 24 quarterly rows, 96 decimal facts, original-page and SHA operands; revisions',len(revisions))
print(json.dumps(revisions,ensure_ascii=False,indent=2))
