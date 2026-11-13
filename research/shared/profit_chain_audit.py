"""Independent original-cell, P&L, node/edge and actual-path acceptance.

Does not import or call the Sankey compiler/renderer. Reconstructs expected
relationships from source facts, and measures the actual exported SVG paths.
"""
from pathlib import Path
from decimal import Decimal as D
import hashlib,json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];NS='{http://www.w3.org/2000/svg}'
def bundle_for(code):
 # Resolve independently of the rendering loader.
 catalog=json.loads((ROOT/'site/research_catalog.json').read_text())
 row=next((r for r in catalog['issuers'] if r['code']==code),None)
 if not row or not row.get('editorial_manifest'):raise ValueError('CHAIN_AUDIT_MANIFEST_REQUIRED')
 path=(ROOT/row['editorial_manifest']).resolve();path.relative_to(ROOT.resolve())
 result=json.loads(path.read_text())
 if result['issuer']!=code:raise ValueError('CHAIN_AUDIT_MANIFEST_ISSUER')
 return result
def value(b,terms):return sum((D(b['facts'][k]['yuan'])*D(str(c)) for k,c in terms),D(0))
def validate_source(b):
 import pymupdf
 path=(ROOT/b['source_pdf']['source_path']).resolve();path.relative_to(ROOT.resolve());raw=path.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=b['source_pdf']['source_sha256']:raise ValueError('CHAIN_SOURCE_PDF_DRIFT')
 doc=pymupdf.open(path)
 if len(doc)!=b['source_pdf']['physical_page_count']:raise ValueError('CHAIN_SOURCE_PAGES')
 if b['issuer'] not in ''.join(doc[i].get_text() for i in range(min(10,len(doc)))):raise ValueError('CHAIN_SOURCE_ISSUER')
 identity_page=b.get('report_identity_page',1)
 if type(identity_page) is not int or not 1<=identity_page<=len(doc):raise ValueError('CHAIN_SOURCE_COVER_PAGE')
 cover=re.sub(r'\s+','',doc[identity_page-1].get_text()).replace('報告','报告');kind={'H1':'半年度','FY':'年度','Q1':'第一季度','9M':'第三季度'}.get(b['period'][4:])
 if not re.search(re.escape(b['period'][:4])+r'年?'+str(kind)+'报告',cover):raise ValueError('CHAIN_SOURCE_PERIOD')
 visiting=set();done=set()
 def fact(k):
  if k in done:return
  if k in visiting:raise ValueError('CHAIN_SOURCE_CYCLIC_DERIVATION')
  visiting.add(k);f=b['facts'][k];want=D(f['yuan'])
  if not want.is_finite() or f['period']!=b['period']:raise ValueError('CHAIN_SOURCE_FACT_PERIOD_OR_NUMBER')
  if f.get('classification')=='DERIVED':
   for key,c in f['terms']:fact(key)
   if value(b,f['terms'])!=want:raise ValueError('CHAIN_SOURCE_DERIVATION_FALSE')
  else:
   if type(f['page']) is not int or not 1<=f['page']<=len(doc):raise ValueError('CHAIN_SOURCE_PHYSICAL_PAGE')
   if not f.get('source_cells'):raise ValueError('CHAIN_SOURCE_CELL_REQUIRED')
   for cell in f['source_cells']:
    region=doc[f['page']-1].get_textbox(pymupdf.Rect(cell['bbox'])+(-.5,-.5,.5,.5)).replace(',','').replace('−','-')
    if cell.get('wrapped_number'):region=re.sub(r'\s+','',region)
    observed=D(cell['original_number']);unit=D(cell['unit_scale']);normal=cell['normalization'];magnitude=normal=='EXPENSE_MAGNITUDE'
    if unit<=0 or normal not in ('SIGNED_ORIGINAL','EXPENSE_MAGNITUDE'):raise ValueError('CHAIN_SOURCE_NORMALIZATION')
    if magnitude and not(f.get('source_kind')=='expense_magnitude' or re.search('费|支出|成本|减值',f['label'])):raise ValueError('CHAIN_SOURCE_UNDECLARED_SIGN_CHANGE')
    if (abs(observed) if magnitude else observed)*unit!=want:raise ValueError('CHAIN_SOURCE_UNIT_OR_SIGN_FALSE')
    number=format(abs(observed),'f');number=number.rstrip('0').rstrip('.') if '.' in number else number
    # Printed trailing decimal zeros are harmless; a missing minus is not.
    numeric=re.escape(number)+(r'(?:\.0+)?' if '.' not in number else '0*')
    token=(r'(?:-'+numeric+r'|\('+numeric+r'\))') if observed<0 else numeric
    if not re.search(r'(?<![0-9.+-])'+token+r'(?![0-9.])',region):raise ValueError('CHAIN_SOURCE_CELL_VALUE_FALSE '+k)
  visiting.remove(k);done.add(k)
 for k in b['facts']:fact(k)
 for prev,nxt in zip(b['stages'],b['stages'][1:]):
  if value(b,prev['terms'])+sum((value(b,a['terms']) for a in nxt['adjustments']),D(0))!=value(b,nxt['terms']):raise ValueError('CHAIN_SOURCE_STAGE_NOT_CLOSED')
 if value(b,b['stages'][-1]['terms'])<0:pass # Signed publication route, never a positive ribbon.
 return {'status':'PASS','source_cells_and_derivations':len(done),'pdf_sha256':b['source_pdf']['source_sha256']}

def check_svg(markup,code,pdf_sha):
 b=bundle_for(code);root=ET.fromstring(markup)
 def need(ok,why):
  if not ok:raise ValueError('PROFIT_CHAIN_'+why)
 def close(a,c):return abs(D(a)-D(c))<D('.00001')
 need(root.get('data-chart-grammar')=='FULL_PROFIT_CHAIN_V1','GRAMMAR')
 need(root.get('data-issuer')==code and root.get('data-period')==b['period'],'ISSUER_PERIOD')
 need(root.get('data-original-pdf-sha256')==pdf_sha==b['source_pdf']['source_sha256'],'PDF')
 expected={};links={}
 def node(id,terms,role):expected[id]=(value(b,terms),terms,role)
 def edge(a,c,v):
  if v:links[(a,c)]=v
 for s in b['stages']:node(s['id'],s['terms'],'checkpoint')
 for i,g in enumerate(b['sources']):node('source-'+str(i),g['terms'],'source');edge('source-'+str(i),'revenue',value(b,g['terms']))
 for prev,nxt in zip(b['stages'],b['stages'][1:]):
  pos=[];neg=[]
  for a in nxt['adjustments']:
   for k,c in a['terms']:
    v=value(b,[[k,c]])
    if v>0:pos.append([k,c])
    elif v<0:neg.append([k,c])
  p=value(b,pos);q=-value(b,neg);from_id=prev['id']
  if p:
   gain='gain-'+nxt['id'];pool='pool-'+nxt['id'];node(gain,pos,'gain');node(pool,prev['terms']+pos,'pool');edge(from_id,pool,value(b,prev['terms']));edge(gain,pool,p);from_id=pool
  if q:
   target='cost-'+nxt['id'];node(target,[[k,-c] for k,c in neg],'cost');edge(from_id,target,q)
  edge(from_id,nxt['id'],value(b,nxt['terms']))
 actual={n.get('data-chain-node'):n for n in root.iter(NS+'rect') if n.get('data-chain-node')}
 need(set(actual)==set(expected),'NODE_SET')
 axis=root.get('data-chain-axis');need(axis in ('width','height'),'AXIS');scale=D(root.get('data-chain-scale'));need(scale>0 and scale==max(v for v,t,r in expected.values())/D(150 if axis=='width' else 340),'EXACT_COMMON_SCALE')
 for key,(v,terms,role) in expected.items():
  n=actual[key];need(D(n.get('data-chain-node-yuan'))==v and json.loads(n.get('data-chain-terms'))==terms and n.get('data-chain-role')==role,'SOURCE_NODE_AMOUNT_OR_TERMS');need(close(n.get(axis),v/scale),'NODE_MONEY_SIZE')
 actual_links={};ports_in={k:[] for k in expected};ports_out={k:[] for k in expected}
 for p in root.iter(NS+'path'):
  if p.get('data-chain-yuan') is None:continue
  a=p.get('data-chain-source');c=p.get('data-chain-target');v=D(p.get('data-chain-yuan'));need((a,c) not in actual_links,'DUPLICATE_EDGE');need((a,c) in links and v==links[(a,c)] and v>=0,'SOURCE_EDGE_AMOUNT');actual_links[(a,c)]=v
  z=[D(x) for x in re.findall(r'-?\d+(?:\.\d+)?',p.get('d'))];need(len(z)==16,'PATH_STRUCTURE');th=v/scale;aa=actual[a];cc=actual[c]
  if axis=='height':
   middle=(z[0]+z[6])/2
   need(all(close(z[i],middle) for i in (2,4,10,12)) and close(z[8],z[6]) and close(z[14],z[0]),'CUBIC_CONTROL_CONNECTION')
   need(close(z[15]-z[1],th) and close(z[9]-z[7],th) and close(z[13]-z[3],th) and close(z[11]-z[5],th),'PATH_ACTUAL_MONEY_HEIGHT')
   need(close(z[0],D(aa.get('x'))+D(aa.get('width'))) and close(z[6],cc.get('x')),'ACTUAL_NODE_CONNECTION');so=z[1]-D(aa.get('y'));ti=z[7]-D(cc.get('y'))
  else:
   middle=(z[1]+z[7])/2
   need(all(close(z[i],middle) for i in (3,5,11,13)) and close(z[9],z[7]) and close(z[15],z[1]),'CUBIC_CONTROL_CONNECTION')
   need(close(z[14]-z[0],th) and close(z[8]-z[6],th) and close(z[12]-z[2],th) and close(z[10]-z[4],th),'PATH_ACTUAL_MONEY_WIDTH')
   need(close(z[1],D(aa.get('y'))+D(aa.get('height'))) and close(z[7],cc.get('y')),'ACTUAL_NODE_CONNECTION');so=z[0]-D(aa.get('x'));ti=z[6]-D(cc.get('x'))
  ports_out[a].append((so,so+th));ports_in[c].append((ti,ti+th))
 need(actual_links==links,'EDGE_SET')
 for key,(_,_,role) in expected.items():
  for mode,ports in [('in',ports_in[key]),('out',ports_out[key])]:
   if not ports:continue
   cursor=D(0)
   for start,end in sorted(ports):need(close(start,cursor) and end>=start,'PORT_GAP_OR_OVERLAP');cursor=end
   need(close(cursor,actual[key].get(axis)),'NODE_PORT_NOT_CONSERVED')
 return {'status':'PASS','grammar':'FULL_PROFIT_CHAIN_V1','original_source_vector_values':'PASS','source_rows':len(expected),'edges':len(links),'endpoint':'parent','actual_path_geometry':'PASS'}

def immutable_v10(markup,code,pdf_sha):
 p=ROOT/'research/editorial-20261113/frozen-original-v10-vectors.json'
 if not p.exists():return None
 rec=json.loads(p.read_text())['issuers'].get(code)
 if rec and hashlib.sha256(markup.encode()).hexdigest() in rec['vectors']:
  if bundle_for(code)['source_pdf']['source_sha256']!=pdf_sha:raise ValueError('ORIGINAL_VECTOR_WRONG_PDF')
  return {'status':'PASS','grammar':'IMMUTABLE_PREEXISTING_SOURCE_V10_VECTOR','scope':'EXACT_ORIGINAL_VECTOR_PRESERVED_NEW_PROFIT_CHAIN_INDEPENDENTLY_AUDITED','observed_source_rows':0}
 return None

def check_reader(page,*,expanded=False):
 """Read real rendered roles before reference expansion; no chart-count proxy."""
 page.wait_for_selector('#editorial-composition-ready',state='attached',timeout=15000)
 fault=page.locator('body').get_attribute('data-editorial-failure')
 if fault:raise ValueError(fault)
 if page.locator('figure#profit-chain-overview').count()!=1:raise ValueError('EDITORIAL_ONE_COMPLETE_BACKBONE_REQUIRED')
 if page.locator('.editorial-reading-card table').count():raise ValueError('EDITORIAL_SUMMARY_COPIED_FULL_RECONCILIATION')
 if not expanded:
  for f in page.locator('.editorial-reference figure').all():
   if f.is_visible():raise ValueError('EDITORIAL_FULL_RECONCILIATION_NOT_DOWNSTREAM')
  if not page.locator('#profit-chain-overview svg:visible').count()==1:raise ValueError('EDITORIAL_PRIMARY_VISIBLE_EDITION')
 if expanded:page.locator('details.editorial-reference').evaluate_all('ds=>ds.forEach(d=>d.open=true)')
 return {'main_reading_layer':'PASS','complete_reconciliation':'EXPANDED' if expanded else 'COLLAPSED','profit_endpoint':'parent'}
