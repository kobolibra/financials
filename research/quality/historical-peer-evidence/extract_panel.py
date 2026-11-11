from pathlib import Path
import pymupdf,re,json,hashlib
from decimal import Decimal
B=Path(__file__).resolve().parent
NUM=re.compile(r'^[-−－]?[\d,]+\.\d{2}$')
LABELS={'revenue':['其中：营业收入','营业收入','一、营业收入'],'cost':['其中：营业成本','减：营业成本','营业成本'],'rd_expense':['研发费用'],'cfo':['经营活动产生的现金流量净额']}
def extract(path):
 d=pymupdf.open(path); pages=[p.get_text() for p in d]; out={}
 for kind,heading in [('pnl','合并利润表'),('cash','合并现金流量表')]:
  starts=[i for i,s in enumerate(pages) if heading in s and i>(15 if len(d)>40 else 2)]
  if not starts:continue
  start=starts[0]; scope=''; mapping=[]
  for i in range(start,min(start+12,len(d))):
   s=pages[i]
   if i==start:s=s[s.index(heading):]
   for stop in ['母公司利润表','母公司现金流量表','合并所有者权益变动表']:
    if stop in s:s=s[:s.index(stop)]
   for line in s.splitlines():mapping.append((line.strip(),i+1))
   if ('母公司利润表' in pages[i] or '母公司现金流量表' in pages[i]) and i>start:break
  for metric,labels in LABELS.items():
   if (kind=='cash') != (metric=='cfo'):continue
   for j,(line,pg) in enumerate(mapping):
    compact=re.sub(r'\s','',line)
    consumed=1
    for take in range(1,4):
     candidate=''.join(x.strip() for x,_ in mapping[j:j+take])
     if candidate in labels:compact=candidate;consumed=take;break
    if compact in labels:
     vals=[]
     for text,pp in mapping[j+consumed:j+consumed+10]:
      if NUM.match(text):vals.append(text.replace(',','').replace('−','-').replace('－','-'))
      if len(vals)==2:break
     if len(vals)==2:out[metric]={'values':vals,'physical_page':pg,'literal_label':line,'next_lines':[x for x,_ in mapping[j+consumed:j+consumed+10]]};break
 return {'id':path.stem,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pages':len(d),'facts':out}
rows=[extract(p) for p in sorted(B.glob('*.pdf'))]
# Two legacy H1 revenue cells cross page/table layouts; exclude unreviewed extraction.
for r in rows:
 if r['id'] in ['600276_2024H1','600900_2024H1']:
  r['facts'].pop('revenue',None)
(B/'statement-facts.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
for r in rows:print(r['id'],{k:v['values'] for k,v in r['facts'].items()})
