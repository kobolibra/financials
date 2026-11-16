"""Canonical Sankey extension: conserved, source-typed group profit stages.

Additional gains enter explicit junctions; deductions leave them. Every reported
profit subtotal remains its own node, never enlarged by incoming gains. Product
net profit is never inferred. Original source cells and exact operands survive.
"""
from decimal import Decimal as D
from html import escape as H
from pathlib import Path
import hashlib,json,re
from unified_income_sankey import PALETTE as P
from editorial_bridge import money,wrap_label
ROOT=Path(__file__).resolve().parents[2]

def amount(bundle,terms):return sum((D(bundle['facts'][k]['yuan'])*D(str(c)) for k,c in terms),D(0))
def catalog_row(catalog,key):
 """Resolve an issuer row by six-digit code, or a later report period by 'code@period'.

 Periods other than the issuer's main catalogue edition live in `period_reports`
 so the one-row-per-issuer invariants of the homepage stay untouched.
 """
 if '@' in key:
  code,period=key.split('@',1)
  return next((r for r in catalog.get('period_reports',[]) if r['code']==code and r['period']==period),None)
 return next((r for r in catalog['issuers'] if r['code']==key),None)
def load(code):
 catalog=json.loads((ROOT/'site/research_catalog.json').read_text())
 row=catalog_row(catalog,code)
 if not row or not row.get('editorial_manifest'):raise ValueError('CHAIN_EXPLICIT_SOURCE_MANIFEST_REQUIRED '+code)
 path=(ROOT/row['editorial_manifest']).resolve();path.relative_to(ROOT.resolve())
 bundle=json.loads(path.read_text())
 if bundle['issuer']!=code.split('@')[0]:raise ValueError('CHAIN_SOURCE_MANIFEST_ISSUER')
 if '@' in code and bundle['period']!=code.split('@')[1]:raise ValueError('CHAIN_SOURCE_MANIFEST_PERIOD')
 return bundle
LAYOUT_V2='PROFIT_CHAIN_LAYOUT_V2'
RATE_LABEL={'gross':'毛利率','operating':'营业利润率','pretax':'税前利润率','net':'净利率','parent':'归母净利率'}
def q1(x):
 """One decimal, half-up: the same rule the independent audit applies to the annotation text."""
 return D(x).quantize(D('0.1'),rounding='ROUND_HALF_UP')
def prior_value(bundle,stage_id):
 """Same stage terms read from the issuer's prior-period source cells (fact key + '_prior')."""
 comp=bundle['comparatives'];stage=next(s for s in bundle['stages'] if s['id']==stage_id)
 return sum((D(comp['facts'][k+'_prior']['yuan'])*D(str(c)) for k,c in stage['terms']),D(0))
def annotations(bundle,mains):
 """Margin and year-over-year strings per checkpoint, from original prior-period cells (opt-in layout only)."""
 comp=bundle.get('comparatives')
 if not comp:return {}
 rev=mains[0]['value'];prior_rev=prior_value(bundle,'revenue');out={}
 for n in mains:
  prior=prior_value(bundle,n['id']);margin=yoy=None
  if n['id']!='revenue' and rev>0 and prior_rev>0:
   m=n['value']/rev*100;pm=prior/prior_rev*100
   margin=f"{RATE_LABEL[n['id']]} {q1(m)}%（{q1(m-pm):+}pp）"
  if prior>0:yoy=f"同比 {q1((n['value']/prior-1)*100):+}%"
  out[n['id']]={'prior':prior,'margin':margin,'yoy':yoy}
 return out
def compile_chain(bundle):
 if bundle['scope']!='consolidated' or bundle['currency']!='CNY' or bundle['unit']!='元':raise ValueError('CHAIN_ACCOUNTING_BASIS')
 facts=bundle['facts'];period=bundle['period'];nodes=[];edges=[]
 def add(id,label,terms,role,stage):
  v=amount(bundle,terms)
  if not v.is_finite() or v<0:raise ValueError('CHAIN_NEGATIVE_SUBTOTAL_REQUIRES_SIGNED_EXCEPTION '+id)
  for k,c in terms:
   if facts[k]['period']!=period:raise ValueError('CHAIN_MIXED_PERIOD '+k)
  n={'id':id,'label':label,'terms':terms,'value':v,'role':role,'stage':stage};nodes.append(n);return n
 def edge(a,b,v):
  if v<0 or not v.is_finite():raise ValueError('CHAIN_NEGATIVE_EDGE')
  if v:edges.append({'source':a['id'],'target':b['id'],'value':v})
 stages=bundle['stages']
 if [s['id'] for s in stages] not in (['revenue','gross','operating','pretax','net','parent'],['revenue','operating','pretax','net','parent']):raise ValueError('CHAIN_REQUIRED_PROFIT_ENDPOINTS')
 mains=[add(s['id'],s['label'],s['terms'],'checkpoint',i) for i,s in enumerate(stages)]
 source_nodes=[]
 for i,g in enumerate(bundle['sources']):
  n=add('source-'+str(i),g['label'],g['terms'],'source',-1);source_nodes.append(n);edge(n,mains[0],n['value'])
 if sum((n['value'] for n in source_nodes),D(0))!=mains[0]['value']:raise ValueError('CHAIN_REVENUE_PARTITION')
 transitions=[]
 for i,(prev,nxt,s) in enumerate(zip(mains,mains[1:],stages[1:])):
  positive=[];negative=[]
  for group in s['adjustments']:
   # Split every source term by its real sign; unrelated gains/losses cannot hide
   # behind a net group. Explicit original NET facts retain their NET label.
   for k,c in group['terms']:
    v=amount(bundle,[[k,c]])
    if v>0:positive.append([k,c])
    elif v<0:negative.append([k,c])
  p=amount(bundle,positive);q=-amount(bundle,negative)
  if prev['value']+p-q!=nxt['value']:raise ValueError('CHAIN_STAGE_NOT_CLOSED '+s['id'])
  gain=None;cost=None;pool=prev
  if p:
   label='少数亏损归属调整' if s['id']=='parent' else '所得税收益' if s['id']=='net' else '营业外收益' if s['id']=='pretax' else '其他营业流入'
   gain=add('gain-'+s['id'],label,positive,'gain',i+.5)
   pool=add('pool-'+s['id'],'本层会计流入合计',prev['terms']+positive,'pool',i+.5)
   edge(prev,pool,prev['value']);edge(gain,pool,p)
  if q:
   label={'gross':'营业成本','operating':'营业费用及损失','pretax':'营业外支出','net':'所得税费用','parent':'少数股东损益'}[s['id']]
   cost=add('cost-'+s['id'],label,[[k,-c] for k,c in negative],'cost',i+1);edge(pool,cost,q)
  edge(pool,nxt,nxt['value']);transitions.append({'from':prev,'to':nxt,'pool':pool,'gain':gain,'cost':cost,'groups':s['adjustments']})
 # Conservation is checked on actual node values, including all join nodes.
 for n in nodes:
  inc=sum((e['value'] for e in edges if e['target']==n['id']),D(0));out=sum((e['value'] for e in edges if e['source']==n['id']),D(0))
  if n['role'] in ('checkpoint','pool') and (inc!=n['value'] or (n['id']!='parent' and out!=n['value'])):raise ValueError('CHAIN_NODE_NOT_CONSERVED '+n['id'])
 return {'nodes':nodes,'edges':edges,'mains':mains,'sources':source_nodes,'transitions':transitions}

def render(bundle,*,mobile=False):
 layout2=bundle.get('editorial',{}).get('layout')==LAYOUT_V2
 if layout2 and not bundle.get('comparatives'):raise ValueError('CHAIN_LAYOUT_V2_REQUIRES_PRIOR_PERIOD_SOURCE_CELLS')
 plan=compile_chain(bundle);nodes=plan['nodes'];edges=plan['edges'];mains=plan['mains'];trans=plan['transitions'];by={n['id']:n for n in nodes}
 width=330 if mobile else 1100;scale=max(n['value'] for n in nodes)/D(150 if mobile else 340)
 if scale<=0:raise ValueError('CHAIN_ZERO_DOMAIN')
 def f(x):return format(D(str(x)).quantize(D('.000001')),'f')
 def size(n):return n['value']/scale
 # Node coordinates hold the exact money dimension; labels are separately laid
 # out. No decorative lower bound is applied to small financial amounts.
 if mobile:
  legend=68+len(plan['sources'])*38;first=legend+92
  if layout2:
   steps=[D(205) if t['gain'] else D(175) if (t['cost'] and t['from']['value'] and t['cost']['value']/t['from']['value']>D('0.02')) else D(150) for t in trans]
  else:steps=[D(190)]*len(trans)
  ys=[D(first)]
  for s in steps:ys.append(ys[-1]+s)
  h=int(ys[-1])+135
  cursor=D(160)
  for n in plan['sources']:n.update(x=cursor,y=D(legend),w=size(n),h=D(8));cursor+=size(n)
  for i,n in enumerate(mains):n.update(x=D(160),y=ys[i],w=size(n),h=D(8))
  for t in trans:
   prev=t['from'];nxt=t['to'];gain=t['gain'];cost=t['cost'];pool=t['pool']
   if gain:gain.update(x=D(16),y=prev['y']+115,w=size(gain),h=D(8));pool.update(x=D(160),y=prev['y']+155,w=size(pool),h=D(8))
   if cost:cost.update(x=D(16),y=nxt['y']+20,w=size(cost),h=D(8))
 else:
  if layout2:
   # Same total span as the fixed layout (790 units), allocated by how much each step actually removes.
   floor=D(100);extra=D(790)-floor*len(trans);share=[(t['cost']['value']/t['from']['value'] if t['cost'] and t['from']['value'] else D(0)) for t in trans];total=sum(share) or D(1)
   xs=[D(210)]
   for s in share:xs.append(xs[-1]+floor+extra*s/total)
  else:xs=[D(210)]+[D(360)+D(i)*D(160) for i in range(len(mains)-1)]
  for x,n in zip(xs,mains):n.update(x=x,y=D(500)-size(n),w=D(9),h=size(n))
  y=D(98)
  for n in plan['sources']:n.update(x=D(142),y=y,w=D(9),h=size(n));y+=max(size(n)+D(28),D(68))
  h=int(max(D(650),y+40))
  stagger=layout2 and min(mains[i+1]['x']-mains[i]['x'] for i in range(len(mains)-1))<150
  if stagger:h=max(h,700)
  previous_cost_bottom=D(55)
  for t in trans:
   prev=t['from'];nxt=t['to'];gain=t['gain'];cost=t['cost'];pool=t['pool']
   if gain:
    pool.update(x=(prev['x']+nxt['x'])/2,y=D(500)-size(pool),w=D(5),h=size(pool))
    gain.update(x=prev['x']+D(24),y=min(previous_cost_bottom+D(60),D(500)-size(gain)),w=D(7),h=size(gain))
   if cost:cost.update(x=nxt['x'],y=D(55),w=D(9),h=size(cost))
   previous_cost_bottom=D(55)+(size(cost) if cost else D(0))
 notes=annotations(bundle,mains) if layout2 else {}
 out=[]
 def text(x,y,t,size=12,anchor='start',color=None,weight=600,halo=False):
  ring=' stroke="#fffefb" stroke-width="3" paint-order="stroke" stroke-linejoin="round"' if halo else ''
  out.append(f'<text x="{f(x)}" y="{f(y)}" fill="{color or P["ink"]}" font-size="{size}" style="font-size:{size}px" font-family="Noto Sans CJK SC,PingFang SC,Arial,sans-serif" text-anchor="{anchor}" font-weight="{weight}"{ring}>{H(t)}</text>')
 text(16 if mobile else 24,24,'收入 → 利润 → 股东归属',14)
 text(16 if mobile else 24,47,'同一金额比例 · 会计形成关系，非现金流',11,color=P['muted'])
 # Incoming and outgoing ports are independent true-value stacks, so pooled
 # gains can enter without enlarging any reported profit checkpoint.
 source_offsets={n['id']:D(0) for n in nodes};target_offsets={n['id']:D(0) for n in nodes}
 for e in edges:
  a=by[e['source']];b=by[e['target']];v=e['value'];th=v/scale;so=source_offsets[a['id']];to=target_offsets[b['id']];source_offsets[a['id']]+=th;target_offsets[b['id']]+=th
  color=P['cost'] if b['role']=='cost' else '#A38458' if a['role']=='gain' else P['source'] if a['role']=='source' else P['profit']
  if mobile:
   x1=a['x']+so;y1=a['y']+a['h'];x2=b['x']+to;y2=b['y'];m=(y1+y2)/2
   path=f'M{f(x1)},{f(y1)} C{f(x1)},{f(m)} {f(x2)},{f(m)} {f(x2)},{f(y2)} L{f(x2+th)},{f(y2)} C{f(x2+th)},{f(m)} {f(x1+th)},{f(m)} {f(x1+th)},{f(y1)} Z'
  else:
   x1=a['x']+a['w'];y1=a['y']+so;x2=b['x'];y2=b['y']+to;m=(x1+x2)/2
   path=f'M{f(x1)},{f(y1)} C{f(m)},{f(y1)} {f(m)},{f(y2)} {f(x2)},{f(y2)} L{f(x2)},{f(y2+th)} C{f(m)},{f(y2+th)} {f(m)},{f(y1+th)} {f(x1)},{f(y1+th)} Z'
  out.append(f'<path d="{path}" fill="{color}" fill-opacity=".66" data-chain-source="{a["id"]}" data-chain-target="{b["id"]}" data-chain-yuan="{v}"><title>{H(a["label"])} → {H(b["label"])}：{v}元</title></path>')
 for n in nodes:
  c=P['cost'] if n['role']=='cost' else '#A38458' if n['role']=='gain' else P['source_dark'] if n['role']=='source' else P['trunk'] if n['role']=='pool' else P['profit']
  prior_attr=f' data-chain-prior-yuan="{notes[n["id"]]["prior"]}"' if n['id'] in notes else ''
  out.append(f'<rect x="{f(n["x"])}" y="{f(n["y"])}" width="{f(n["w"])}" height="{f(n["h"])}" fill="{c}" data-chain-node="{n["id"]}" data-chain-role="{n["role"]}" data-chain-node-yuan="{n["value"]}"{prior_attr} data-chain-terms="{H(json.dumps(n["terms"],ensure_ascii=False,separators=(",",":")),quote=True)}"><title>{H(n["label"])}：{n["value"]}元</title></rect>')
 if mobile:
  for i,n in enumerate(plan['sources']):text(16,76+i*38,f'{i+1:02d} '+n['label'],12);text(314,93+i*38,money(n['value']),11,'end',P['muted'])
  for n in mains:
   text(16,n['y']-24,n['label'],13);text(16,n['y']-6,money(n['value']),12,color=P['profit'])
   a=notes.get(n['id'])
   if a:
    # Two short lines inside the 160-unit left gutter; a combined line ran into the flow.
    line=n['y']-60
    for key in ('margin','yoy'):
     if a[key]:text(16,line,a[key],11,color=P['muted'],weight=500,halo=True);line+=16
  for t in trans:
   gain=t['gain'];cost=t['cost']
   if gain:text(16,gain['y']-30,'加：'+gain['label'],11,color='#8C6B38');text(16,gain['y']-12,money(gain['value']),11,color='#8C6B38')
   if cost:text(16,cost['y']+26,'减：'+cost['label'],11,color=P['cost']);text(16,cost['y']+44,money(cost['value']),11,color=P['cost'])
 else:
  for n in plan['sources']:
   lines=wrap_label(n['label'],8)
   for j,line in enumerate(lines):text(16,n['y']+12+j*16,line,12)
   text(16,n['y']+max(48,16+len(lines)*16),money(n['value']),11,color=P['muted'])
  for i,n in enumerate(mains):
   base=526+(84 if stagger and i%2 else 0)
   text(n['x']+4,base,n['label'],13,'middle');text(n['x']+4,base+22,money(n['value']),12,'middle',P['profit'])
   a=notes.get(n['id'])
   if a:
    line=base+40
    for key in ('margin','yoy'):
     if a[key]:text(n['x']+4,line,a[key],11,'middle',P['muted'],500,halo=True);line+=18
  for t in trans:
   gain=t['gain'];cost=t['cost']
   if cost:text(cost['x']+4,24,cost['label'],11,'middle',P['cost']);text(cost['x']+4,43,money(cost['value']),11,'middle',P['cost'])
   if gain:
    for j,line in enumerate(wrap_label(gain['label'],9)):text(gain['x']+2,gain['y']-46+j*16,line,11,color='#8C6B38')
    text(gain['x']+2,gain['y']-10,money(gain['value']),11,color='#8C6B38')
 text(16 if mobile else 24,h-22,'原始元逐层闭合；完整科目、计算组成与来源见下方核对表。',10 if mobile else 12,color=P['muted'])
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {h}" role="img" aria-label="完整利润形成桑基图" data-chart-grammar="FULL_PROFIT_CHAIN_V1" data-design-system="FINANCIALS_UNIFIED_STORY_V1" data-issuer="{bundle["issuer"]}" data-period="{bundle["period"]}" data-original-pdf-sha256="{bundle["source_pdf"]["source_sha256"]}" data-chain-axis="{"width" if mobile else "height"}" data-chain-scale="{scale}"{" data-chain-layout="+chr(34)+LAYOUT_V2+chr(34) if layout2 else ""}><title>完整利润形成：会计金额比例及股东归属</title>'+''.join(out)+'</svg>'
