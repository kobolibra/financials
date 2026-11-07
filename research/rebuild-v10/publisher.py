from __future__ import annotations
from pathlib import Path
from decimal import Decimal as D, ROUND_HALF_UP
import json, math, html, re, hashlib, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from audit_v10_flow_contract import classify as typed_classify
from native_mobile import mobile_for, source_own_sankey, signed_product_profit, FAMILY, NAME
from verify import get, facts, check, SRC, SHA, HERE, LEDGER
CFO_COMPONENTS=json.loads((HERE/"cfo_components.json").read_text())
TYPED={code:typed_classify(HERE.parents[1], code) for code in ('688111','600519','000333','600036')}

OUTPUT=HERE/'site';OUTPUT.mkdir(exist_ok=True)
YI=D('100000000')
def yi(v):return D(str(v))/YI
def n(v,d=2):return f'{D(str(v)):,.{d}f}'
def f(v,d=2):return n(yi(v),d)
def pct(v):return float(D(str(v))*100)
def growth(a,b):return (D(a)/D(b)-1)*100 if D(b) else D(0)
def pp(a,b):return D(a)-D(b)
def x(v):return html.escape(str(v),quote=True)
def tag(name,body,**attrs):return f'<{name} '+ ' '.join(f'{k.replace("_","-")}="{x(v)}"' for k,v in attrs.items())+f'>{body}</{name}>'

COL={'ink':'#17343b','green':'#0b866e','teal':'#0c6f68','copper':'#c8896e','blue':'#487b91','slate':'#93a8a4','muted':'#687d7c','cream':'#f7f5ef','ivory':'#fffdf8','line':'#dce5df'}

def svg_base(content, h=430, title='Financial relationship'):
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 {int(h)}" role="img" aria-label="{x(title)}"><title>{x(title)}</title>{content}</svg>'
def txt(a,b,text,size=18,fill=None,weight='400',anchor='start'):
 return f'<text x="{a:.2f}" y="{b:.2f}" fill="{fill or COL["ink"]}" font-family="-apple-system,BlinkMacSystemFont,Noto Sans CJK SC,Arial,sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{x(text)}</text>'
def bar(a,b,w,h,fill,rx=2):return f'<rect x="{a:.2f}" y="{b:.2f}" width="{max(0,w):.2f}" height="{h:.2f}" rx="{rx}" fill="{fill}"/>'
def rule(a,b,c,d,stroke=None,sw=1):return f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" stroke="{stroke or COL["line"]}" stroke-width="{sw}"/>'

def bars(rows, title='', maxvalue=None, unit='亿元', color=None):
 # rows: name, value (already 亿), optional hint
 rows=[(z[0],float(z[1]),z[2] if len(z)>2 else '') for z in rows]
 m=max((abs(v) for _,v,_ in rows),default=1) if maxvalue is None else float(maxvalue);m=max(m,1e-6)
 count=len(rows);ht=85+count*72;out=txt(24,34,title,16,COL['muted'], '600')
 out+=rule(315,51,315,ht-28,COL['slate'])
 for i,(label,value,hint) in enumerate(rows):
  y=57+i*72;c=(color[i] if isinstance(color,(list,tuple)) else (color or [COL['green'],COL['blue'],COL['copper'],COL['slate']][i%4]))
  w=min(485,abs(value)/m*480)
  out+=txt(295,y+27,label,17,anchor='end')+bar(318,y,w,33,c)
  val=n(value,2)+(' '+unit if unit else '')
  out+=txt(min(890,331+w),y+25,val,17,COL['ink'],'700')
  if hint:out+=txt(320,y+58,hint,13,COL['muted'])
 return svg_base(out,ht,title)

def dumbbell(rows,title,unit='亿元',domain=None):
 # each tuple label, before, after; dynamic per-series range but same row values on common axis
 allv=[float(v) for r in rows for v in r[1:3]]
 lo=0 if domain is None else domain[0]; hi=max(allv)*1.14 if domain is None else domain[1]
 if hi==lo:hi=lo+1
 ht=100+len(rows)*92
 out=txt(23,35,title,17,COL['muted'],'600')+txt(470,62,'前期',14,COL['slate'])+txt(710,62,'本期',14,COL['green'])
 for i,(label,before,after) in enumerate(rows):
  y=103+i*92; a=float(before);b=float(after)
  out+=txt(278,y+5,label,17,anchor='end')
  x1=330+510*(a-lo)/(hi-lo);x2=330+510*(b-lo)/(hi-lo)
  out+=rule(330,y,845,y,'#dae3df',2)+rule(x1,y,x2,y,COL['blue'],5)
  out+=f'<circle cx="{x1}" cy="{y}" r="8" fill="{COL["slate"]}" stroke="white" stroke-width="2"/><circle cx="{x2}" cy="{y}" r="10" fill="{COL["green"]}" stroke="white" stroke-width="2"/>'
  out+=txt(x1,y-17,n(a,2),14,COL['muted'],anchor='middle')+txt(x2,y+31,n(b,2),16,COL['green'],'700',anchor='middle')
 out+=txt(34,ht-12,('单位：'+unit)+' · 左侧灰色＝前期 · 右侧绿色＝本期；点位共同采用同一横轴',13,COL['muted'])
 return svg_base(out,ht,title)

def change_lollipop(rows,title,unit='%'):
 # rows (title, growth percent)
 v=[float(r[1]) for r in rows]; span=max(max(abs(q) for q in v)*1.16,4)
 z=535; s=340/span; h=96+len(rows)*80
 out=txt(24,30,title,17,COL['muted'],'600')+rule(z,49,z,h-32,'#8aa49b',2)+txt(z,44,'0',12,COL['muted'],anchor='middle')
 for i,(label,value) in enumerate(rows):
  value=float(value);y=66+i*80;xval=z+value*s; c=COL['green'] if value>=0 else COL['copper']
  out+=txt(268,y+22,label,17,anchor='end')+rule(z,y+13,xval,y+13,c,8)+f'<circle cx="{xval}" cy="{y+13}" r="9" fill="{c}" stroke="{COL["ivory"]}" stroke-width="2"/>'
  out+=txt(xval+(15 if value>=0 else -15),y+20,('+' if value>0 else '')+n(value,2)+unit,17,c,'700','start' if value>=0 else 'end')
 return svg_base(out,h,title)

def split_funding(curr,prev,title):
 # current/prev (assets, liabilities,equity) yuan; proportional funding
 rows=[('2025-12-31',prev),('2026-06-30',curr)];ht=285
 out=txt(25,29,title,16,COL['muted'],'600')
 for i,(dt,(a,l,e)) in enumerate(rows):
  y=75+i*92; a,l,e=map(float,(a,l,e));w1=705*l/a;w2=705*e/a
  out+=txt(30,y+21,dt,17,COL['ink'],'600')+bar(230,y,w1,40,COL['copper'])+bar(230+w1,y,w2,40,COL['green'])
  out+=txt(230+w1/2,y+26,f'{l/a*100:.1f}%',16,'white','700',anchor='middle')+txt(230+w1+w2/2,y+26,f'{e/a*100:.1f}%',16,'white','700',anchor='middle')
  out+=txt(935,y+27,f'{a/1e8:,.1f} 亿',16,COL['ink'],'700')
 out+=bar(35,243,17,17,COL['copper'])+txt(61,258,'负债（流动性/杠杆依赖资产总量）',14,COL['muted'])+bar(465,243,17,17,COL['green'])+txt(491,258,'所有者权益',14,COL['muted'])
 return svg_base(out,ht,title)


def audited_financial_sankey(source_rows, total, uses, title, *, context='', required_scope='2026H1 consolidated', min_label=None):
    """Conserved financial Sankey: exact Decimal yuan flows, never cosmetic ribbons.

    source_rows and uses are tuples (display_name, original_yuan_amount), same
    fiscal period and consolidation. Negative entries are REJECTED rather than
    disguised as ribbons; mixed assets & cash cannot share this flow grammar.
    """
    src=[(str(label),D(value)) for label,value in source_rows]
    dst=[(str(label),D(value)) for label,value in uses]
    t=D(total)
    assert t>0 and all(v>0 for _,v in src+dst), 'Financial Sankey requires strictly positive comparable flow amounts'
    assert len(src)>=2 and len(dst)==2 and len(src)<=5, 'Use sourced and non-overlapping source and use taxonomy'
    assert sum(v for _,v in src)==t,(title,'SOURCE_FLOW_NOT_CONSERVED',str(sum(v for _,v in src)-t))
    assert sum(v for _,v in dst)==t,(title,'USES_FLOW_NOT_CONSERVED',str(sum(v for _,v in dst)-t))
    h=678; total_h=378.; top=162.; left_x=300.; middle_x=586.;right_x=864.; gap=12.;nodew=20.;
    scale=total_h/float(t)
    colors=['#0c8670','#4b7890','#6da897','#a6a899','#c99872']
    tocolors=['#c18b72','#0a816c']
    gap_src=gap*(len(src)-1)
    source_start=top-gap_src/2
    target_start=top-gap/2
    out='<defs><linearGradient id="flow-left" x1="0" x2="1"><stop stop-color="#0c8670" stop-opacity=".62"/><stop offset="1" stop-color="#0c8670" stop-opacity=".32"/></linearGradient><linearGradient id="flow-gp" x1="0" x2="1"><stop stop-color="#238e78" stop-opacity=".62"/><stop offset="1" stop-color="#238e78" stop-opacity=".78"/></linearGradient></defs>'
    out+=txt(30,37,title,19,COL['ink'],'650')
    out+=txt(30,70,'SOURCE / 收入来源',14,COL['muted'],'650')
    out+=txt(536,70,'CONSOLIDATED / 汇总',13,COL['muted'],'650')
    out+=txt(875,70,'ALLOCATION / 成本与留存',13,COL['muted'],'650')
    out+=txt(30,105,required_scope+'  ·  线带厚度＝披露金额 · 所有连接可按人民币元精确勾稽',14,COL['muted'])
    def band(x0,ya0,ya1,x1,yb0,yb1):
        cp=(x1-x0)*.49
        return f'M {x0:.3f} {ya0:.3f} C {x0+cp:.3f} {ya0:.3f} {x1-cp:.3f} {yb0:.3f} {x1:.3f} {yb0:.3f} L {x1:.3f} {yb1:.3f} C {x1-cp:.3f} {yb1:.3f} {x0+cp:.3f} {ya1:.3f} {x0:.3f} {ya1:.3f} Z'
    source_cursor=source_start; middle_cursor=top
    for i,(label,val) in enumerate(src):
        thick=float(val)*scale; center=source_cursor+thick/2
        innercolor=colors[i]
        out+=f'<path d="{band(left_x+nodew,source_cursor,source_cursor+thick,middle_x,middle_cursor,middle_cursor+thick)}" fill="{innercolor}" fill-opacity=".47"><title>{x(label)} {n(yi(val),2)} 亿元 → 汇总</title></path>'
        out+=bar(left_x,source_cursor,nodew,max(thick,.02),innercolor,0)
        label_y=185.+i*80
        out+=rule(291,center,276,label_y,'#91aaa2',1)
        out+=txt(265,label_y-5,label,17,COL['ink'],'650','end')
        out+=txt(265,label_y+22,n(yi(val),2)+' 亿',16,innercolor,'650','end')
        source_cursor+=thick+gap;middle_cursor+=thick
    out+=bar(middle_x,top,nodew,total_h,COL['ink'],0)
    out+=txt(middle_x+nodew/2,top-24,n(yi(t),2)+' 亿',27,COL['ink'],'750','middle')
    out+=txt(middle_x+nodew/2,top+total_h+31,'合并收入 / 净额',15,COL['muted'],'600','middle')
    middle_cursor=top;target_cursor=target_start
    for i,(label,val) in enumerate(dst):
        thick=float(val)*scale;center=target_cursor+thick/2
        col=tocolors[i];out+=f'<path d="{band(middle_x+nodew,middle_cursor,middle_cursor+thick,right_x,target_cursor,target_cursor+thick)}" fill="{col}" fill-opacity=".51"><title>汇总 → {x(label)} {n(yi(val),2)} 亿元</title></path>'
        out+=bar(right_x,target_cursor,nodew,max(.02,thick),col,0)
        label_y=[235.,440.][i]
        out+=rule(right_x+nodew+8,center,right_x+nodew+27,label_y,'#91aaa2',1)
        out+=txt(923,label_y-3,label,18,COL['ink'],'650')
        out+=txt(923,label_y+28,n(yi(val),2)+' 亿',20,col,'750')
        out+=txt(923,label_y+51,n(val/t*100,2)+'%',15,COL['muted'])
        target_cursor+=thick+gap;middle_cursor+=thick
    out+=rule(30,588,1013,588,'#dce5df',1)
    out+=txt(30,616,'会计守恒：来源 Σ = 汇总 = 去向 Σ · 数据单位：人民币亿元；后台按原始元精度校验',14,COL['muted'])
    if context:out+=txt(30,643,context,13,COL['muted'])
    return svg_base(out,h,title+' · 会计守恒财务桑基图')

def profitability_panel(r0,c0,r1,c1,title):
    rev0,rev1,cost0,cost1=map(D,[r0,r1,c0,c1]);gp0=rev0-cost0;gp1=rev1-cost1
    m0=gp0/rev0*100;m1=gp1/rev1*100;delta=m1-m0
    out=txt(27,30,title,18,COL['muted'],'600')
    out+=txt(48,85,'2025H1',16,COL['muted'],'700')+txt(560,85,'2026H1',16,COL['green'],'700')
    for i,(xp,m,gp) in enumerate([(35,m0,gp0),(540,m1,gp1)]):
        out+=txt(xp+16,151,n(m,2)+'%',54,COL['ink'] if i==0 else COL['green'],'650')
        out+=txt(xp+16,185,'同口径毛利率 · 同期六个月',16,COL['muted'])
        out+=txt(xp+16,242,n(yi(gp),2)+' 亿元',32,COL['ink'],'700')
        out+=txt(xp+16,272,'毛利额 = 营业收入 − 营业成本',14,COL['muted'])
    out+=rule(516,79,516,290,'#cfddd4',2)
    out+=txt(49,337,'毛利率变动 '+('+' if delta>=0 else '')+n(delta,2)+' pp',24,COL['copper'] if delta<0 else COL['green'],'700')
    out+=txt(49,376,'两期比率各自以相同的营业收入口径计算；货币金额不是百分比坐标。',14,COL['muted'])
    return svg_base(out,414,title)

def cash_bridge(begin,flows,close,title,start_label='期初现金',end_label='期末现金',footer='亿元 · 期初 + 经营 + 投资 + 筹资 + 汇兑 = 期末 · 正/负值忠实呈现'):
 # values in yuan; actual signed cash amounts; same baseline, source reconciliation checked externally
 begin=float(yi(begin));close=float(yi(close));steps=[(lab,float(yi(val))) for lab,val in flows]
 changes=[begin];running=begin
 for lab,delta in steps:running+=delta;changes.append(running)
 assert abs(running-close)<1e-6,(running,close)
 vals=[0,begin,close]+changes; ymax=max(vals)*1.16; ymin=min(0,min(vals));scale=245/(ymax-ymin)
 nitems=2+len(steps); gap=950/nitems;out=txt(32,32,title,17,COL['muted'],'600')
 y0=345+ymin*scale # y coordinate for 0
 out+=rule(25,y0,1016,y0,'#91aaa2',1)
 cells=[(start_label,begin,'total')]+[(label,val,'step') for label,val in steps]+[(end_label,close,'total')]
 running=begin
 for i,(label,v,t) in enumerate(cells):
  xx=46+i*gap;bw=min(116,gap-30)
  if i==0 or t=='total':bottom=0;top=v;color=COL['slate'] if i==0 else COL['green']
  else:
   bottom=running;top=running+v;color=COL['green'] if v>=0 else COL['copper'];running+=v
  yy=y0-top*scale;hh=abs(top-bottom)*scale
  if top<bottom: yy=y0-bottom*scale
  out+=bar(xx,yy,bw,max(2,hh),color)
  out+=txt(xx+bw/2,yy-12,('+' if t=='step' and v>0 else '')+n(v,2),15,COL['ink'],'700','middle')
  # 1-2 line chinese chart labels concise
  out+=txt(xx+bw/2,380,label,14,COL['muted'],anchor='middle')
 out+=txt(35,432,footer,14,COL['muted'])
 return svg_base(out,460,title)

def signed_cash_bars(rows,title):
    # zero in center; true net direction; rows are already normalized into 亿.
    vals=[float(v) for _,v in rows]; cap=max(abs(v) for v in vals); ht=112+len(rows)*78
    z=525; scale=430/max(cap,1)
    out=txt(25,32,title,17,COL['muted'],'600')+rule(z,55,z,ht-38,'#869e96',2)+txt(z,52,'0',13,COL['muted'],anchor='middle')
    for i,(lab,val) in enumerate(rows):
        y=69+i*78;v=float(val);w=abs(v)*scale;color=COL['green'] if v>=0 else COL['copper']
        start=z if v>=0 else z-w
        out+=txt(322,y+26,lab,16,anchor='end')+bar(start,y,max(w,2),31,color)
        out+=txt((z+w+11 if v>=0 else z-w-11),y+24,('+' if v>0 else '')+n(v,2),16,color,'700','start' if v>=0 else 'end')
    out+=txt(26,ht-12,'亿元 · 同一零轴；右侧为现金净流入，左侧为现金净流出',13,COL['muted'])
    return svg_base(out,ht,title)

def risk_panels(rows,title):
    # incomparable metrics rendered as isolated change modules, never shared scales
    ht=120+len(rows)*103;out=txt(28,30,title,16,COL['muted'],'600')
    for i,(label,before,after) in enumerate(rows):
        y=66+i*103;diff=float(after)-float(before)
        out+=rule(35,y-6,991,y-6,'#d4dfd7',1)
        out+=txt(36,y+25,label,18,COL['ink'],'650')
        out+=txt(445,y+25,n(before,2)+'%',21,COL['muted'],'500')
        out+=txt(590,y+25,'→',22,COL['slate'],'600')
        out+=txt(655,y+25,n(after,2)+'%',22,COL['green'],'700')
        out+=txt(915,y+25,('+' if diff>0 else '')+n(diff,2)+'pp',16,COL['copper'] if diff<0 else COL['green'],'700',anchor='end')
        out+=txt(35,y+54,'前期 / 本期 · 各项指标单位不同，不共用金额或比例尺',12,COL['muted'])
    return svg_base(out,ht,title)

def indirect_cfo_figure(code,index,question,answer,counter):
    import json
    z=CFO_COMPONENTS[code];groups={}
    order=['impairment','depreciation','noncash','investment','tax','working','other']
    labels={'impairment':'减值','depreciation':'折旧摊销','noncash':'其他非现金','investment':'投资收益调回','tax':'递延所得税','working':'经营营运资本','other':'其他'}
    for lab,val,page,category in z['parts']:
        groups[category]=groups.get(category,D(0))+D(val)
    flows=[(labels[c],groups[c]) for c in order if c in groups]
    start=D(z['start'][1]);end=D(z['end'][1]);assert start+sum(groups.values())==end
    svg=cash_bridge(start,flows,end,'净利润 → 经营现金流 · 全部原始间接法调整',start_label='合并净利润',end_label='经营现金',footer='亿元 · 原始调整项依会计符号归类加总；每个分组均可在下表逐项复核')
    link=LEDGER[code]['source']['url']
    lines=[(z['start'][0],z['start'][1],z['start'][2], '起点')]+[(a,b,c,labels[d]) for a,b,c,d in z['parts']]+[(z['end'][0],z['end'][1],z['end'][2],'终点')]
    table=''.join(f'<tr><td>{x(label)}<br><small>{x(group)}</small></td><td>{(n(D(val)/D(1000),0)+" 千元" if code=="000333" else n(D(val),2)+" 元")}</td><td><a href="{x(link)}#page={page}" target="_blank" rel="noopener">PDF {page}</a></td></tr>' for label,val,page,group in lines)
    summ=''.join(f'<div class="data-item"><span class="data-label">{x(lab)} · 归类调整</span><span class="data-number">{( "+" if value>0 else "")+f(value)} 亿</span></div>' for lab,value in flows)
    return f'''<figure class="graphic" id="fig-{index:02d}"><div class="graphic-top"><div><div class="graphic-index">EXHIBIT {index:02d} / EXACT YUAN RECONCILIATION</div><h3>{x(question)}</h3><p class="figure-answer">{x(answer)}</p></div><p class="graphic-marginal">{x(counter)}</p></div><div class="graphic-svg desktop-finance{' sankey-svg' if '财务桑基图' in svg else ''}">{svg}</div><div class="graphic-svg native-finance">{mobile_for(code,index,[],get,facts(code),CFO_COMPONENTS,TYPED[code])}</div><div class="graphic-data"><div class="tag">合并净利润 {f(start)} 亿 → CFO {f(end)} 亿</div>{summ}</div><div class="figure-bottom"><div class="figure-source">来源：<a href="{x(link)}" target="_blank" rel="noopener">完整半年度财报</a> · 物理页 {', '.join('p.'+str(q) for q in sorted({line[2] for line in lines}))}；全部{len(z['parts'])}个原披露调整项目金额逐项相加，精确到人民币元；分组仅用于阅读。</div><button type="button" class="export">导出 SVG</button></div><details class="details"><summary>展开全部{len(z['parts'])}项原始调节金额与会计符号</summary><table class="evidence-table"><thead><tr><th>原披露项目</th><th>金额（亿元）</th><th>PDF页码</th></tr></thead><tbody>{table}</tbody></table></details></figure>'''

def income_interests(interest_curr,interest_prior,expenses_curr,expenses_prior,title):
 # use 2 stacks comparable incomes and outflows (not ribbons)
 a=float(yi(interest_curr));b=float(yi(interest_prior));c=float(yi(expenses_curr));d=float(yi(expenses_prior))
 h=320;mx=max(a,b)*1.1
 out=txt(25,34,title,17,COL['muted'],'600')
 for i,(dt,inc,exp) in enumerate([('2025H1',b,d),('2026H1',a,c)]):
  y=77+i*96
  out+=txt(40,y+24,dt,18,COL['ink'],'600')+bar(175,y,640*inc/mx,30,COL['slate'] if i==0 else COL['blue'])+bar(175,y+41,640*exp/mx,15,COL['copper'])
  out+=txt(187+640*inc/mx,y+22,n(inc,2)+' 亿 · 利息收入',15,COL['ink'],'700')
  out+=txt(187+640*exp/mx,y+53,n(exp,2)+' 亿 · 利息支出',14,COL['copper'])
  out+=txt(175,y-10,'净利息收入 '+n(inc-exp,2)+' 亿',14,COL['green'],'700')
 out+=txt(40,305,'利息收入－利息支出＝净利息收入；支出用独立的铜色长度表示，不误作可加总收入',13,COL['muted'])
 return svg_base(out,h,title)

def hierarchy(top,children,title):
 # top-level categories plus separate nested children; additive only within each level; two panels independent scaling
 ht=460; out=txt(25,34,title,16,COL['muted'],'600')
 out+=txt(24,68,'LEVEL 01 · 全集团互斥业务板块',16,COL['ink'],'700')
 max_top=float(sum(v for _,v in top))
 left=25
 for i,(lab,v) in enumerate(top):
  w=890*float(v)/max_top;out+=bar(left,87,w,59,[COL['green'],COL['blue'],COL['slate']][i]);
  if w>95:out+=txt(left+12,124,lab,16,'white','700')
  left+=w
 for i,(lab,v) in enumerate(top):out+=txt(30+(i%2)*475,176+(i//2)*31,lab+'：'+n(v,2)+' 亿',15,COL['ink'])
 out+=rule(24,236,995,236)
 out+=txt(24,265,'LEVEL 02 · 工业解决方案内部拆分（已经包含在上方父类）',16,COL['ink'],'700')
 xmax=sum(v for _,v in children);left=25
 for i,(lab,v) in enumerate(children):
  w=890*float(v)/float(xmax);out+=bar(left,283,w,56,[COL['blue'],COL['green'],COL['copper'],COL['slate']][i]);left+=w
 for i,(lab,v) in enumerate(children):out+=txt(30+(i%2)*475,365+(i//2)*36,lab+'：'+n(v,2)+' 亿',16,COL['ink'])
 out+=txt(28,444,'两个层级不可再次相加；地区收入是另一种分类维度，亦不得重复合计。',13,COL['muted'])
 return svg_base(out,ht,title)

CSS='''
:root{--paper:#fffdf7;--canvas:#f6f4ee;--ink:#18343c;--dim:#5d7072;--muted:#72817f;--green:#0b806d;--coral:#b87c63;--line:#d8e1db;--black:#102c35;--serif:Georgia,"Noto Serif CJK SC","Songti SC",serif;--sans:-apple-system,BlinkMacSystemFont,"Noto Sans CJK SC","PingFang SC",Arial,sans-serif}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.86 var(--sans);-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}a{color:inherit}a:focus-visible,button:focus-visible{outline:3px solid #0da487;outline-offset:5px}.wrap{width:min(1160px,calc(100% - 56px));margin:0 auto}.mast{background:var(--black);color:#eff6f0}.mast-inner{min-height:80px;display:flex;align-items:center;justify-content:space-between;gap:20px;border-bottom:1px solid #3c5557}.brand{font-size:14px;line-height:1.28;font-weight:800;text-decoration:none;letter-spacing:.16em}.brand span{display:block;font-size:9px;color:#94bcb0;letter-spacing:.23em;margin-top:4px}.mast-links{display:flex;gap:26px;font-size:12px;color:#b1d2c9}.mast-links a{text-decoration:none}.hero{background:var(--black);color:#fffaf4;padding:84px 0 94px;position:relative;overflow:hidden}.hero:before{content:"";position:absolute;right:-155px;top:10%;width:510px;height:510px;border:1px solid rgba(156,198,185,.11);border-radius:50%;pointer-events:none}.eyebrow{color:#9bd7c3;font-size:11px;letter-spacing:.22em;font-weight:800;text-transform:uppercase}.hero-grid{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(235px,.55fr);gap:60px;align-items:end}.hero h1{font-size:clamp(49px,6.4vw,84px);line-height:1.15;letter-spacing:-.055em;font-family:var(--serif);font-weight:550;margin:22px 0 23px;max-width:850px;word-break:normal}.hero .dek{font-size:clamp(18px,2vw,24px);line-height:1.7;color:#c4dad3;max-width:790px}.meta-row{font-size:12px;color:#8fb2a8;display:flex;gap:13px;flex-wrap:wrap;margin-top:33px}.hero-aside{border-left:1px solid #49615f;padding:14px 0 7px 28px}.big-number{font:600 clamp(38px,3.65vw,53px)/1 var(--serif);white-space:nowrap;letter-spacing:-.045em;color:#9ee0c6;margin:15px 0}.hero-aside p{font-size:13px;line-height:1.65;color:#aac7bd}.page-nav{background:#fffefa;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:6;box-shadow:0 5px 22px #071b220a}.page-nav .wrap{display:flex;gap:28px;align-items:center;white-space:nowrap;overflow-x:auto;padding:15px 0;scrollbar-width:none}.page-nav a{font-size:12px;text-decoration:none;color:#4f6565;flex:0 0 auto}.page-nav a:hover{color:var(--green)}main{padding:0 0 125px}.executive{padding:66px 0 55px;border-bottom:1px solid var(--line)}.executive-grid{display:grid;grid-template-columns:minmax(0,1.38fr) minmax(0,.62fr);gap:9%}.tag{font-size:11px;text-transform:uppercase;letter-spacing:.18em;font-weight:800;color:var(--green)}.executive h2{font-family:var(--serif);font-size:clamp(32px,3.8vw,54px);line-height:1.29;font-weight:560;letter-spacing:-.04em;margin:15px 0 26px}.executive p{font-size:18px;line-height:1.95}.executive .counter{background:var(--canvas);border-left:3px solid var(--coral);padding:22px 25px;font-size:15px;margin-top:22px}.speed-reading{padding:27px 0 0}.speed-reading .mini{font-size:11px;font-weight:800;letter-spacing:.16em;color:var(--muted)}.facts-strip{border-top:1px solid var(--line);border-bottom:1px solid var(--line);display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;margin-top:31px}.facts-strip>div{padding:22px 23px;border-right:1px solid var(--line)}.facts-strip>div:last-child{border:0}.facts-strip b{display:block;font:600 clamp(24px,3.2vw,39px)/1.25 var(--serif);letter-spacing:-.04em}.facts-strip small{display:block;color:var(--muted);font-size:12px;line-height:1.6;margin-top:8px}.chapter{padding-top:95px}.chapter:target{scroll-margin-top:90px}.chapter-head{display:grid;grid-template-columns:180px minmax(0,1fr);gap:50px;border-top:2px solid var(--ink);padding-top:25px;margin-bottom:35px}.chapter-no{font:500 44px/1 var(--serif);color:var(--green)}.chapter-head h2{font:550 clamp(34px,4.4vw,56px)/1.21 var(--serif);letter-spacing:-.045em;margin:10px 0 22px}.chapter-head .intro{max-width:780px;font-size:19px;line-height:1.9;color:#465d5e}.chapter-body{margin-left:230px;max-width:850px}.prose{font-size:17px;line-height:2;max-width:820px;margin:0 0 39px}.prose strong{color:var(--green)}.graphic{margin:54px 0 58px;border-top:1px solid var(--line);padding-top:24px}.graphic-top{display:grid;grid-template-columns:1fr .43fr;gap:55px;align-items:start}.graphic-index{font-size:11px;color:var(--green);font-weight:800;letter-spacing:.15em}.graphic h3{font:550 clamp(27px,3.1vw,40px)/1.25 var(--serif);letter-spacing:-.04em;margin:12px 0 10px}.graphic .figure-answer{font-size:15px;line-height:1.85;color:#4d6863}.graphic-marginal{color:#5d7170;font-size:13px;line-height:1.75;margin-top:12px;border-left:2px solid #d0ddd5;padding-left:18px}.graphic-svg{margin:26px 0 0;width:100%;background:var(--canvas);padding:26px 17px 12px;min-height:190px}.graphic-svg svg{display:block;width:100%;height:auto;max-width:100%;overflow:visible}.graphic-data{display:none;margin:19px 0 0;background:#f7f5ef;padding:20px}.data-grid{display:grid;gap:13px}.data-item{border-bottom:1px solid #dfe6df;padding:11px 0}.data-item .data-label{font-size:12px;color:#687e78}.data-item .data-number{font:650 25px/1.2 var(--serif);display:block;margin-top:3px}.figure-bottom{display:flex;align-items:start;gap:16px;justify-content:space-between;margin-top:13px}.figure-source{font-size:11px;color:#657775;line-height:1.9;overflow-wrap:anywhere}.figure-source a{color:#096f5c}.export{font-size:11px;color:var(--green);background:none;border:1px solid #c8d9d0;cursor:pointer;padding:7px 10px;white-space:nowrap}.details{margin-top:12px}.details summary{cursor:pointer;color:var(--green);font-size:12px;font-weight:700}.evidence-table{width:100%;border-collapse:collapse;font-size:12px;margin-top:10px}.evidence-table th,.evidence-table td{padding:9px 10px;text-align:left;border-bottom:1px solid var(--line)}.evidence-table td:nth-child(2){font-variant-numeric:tabular-nums}.evidence-table a{color:var(--green)}.quote{background:#eef2ec;border-left:4px solid #609b87;margin:40px 0;padding:26px 33px;font:500 clamp(20px,2.2vw,28px)/1.65 var(--serif)}.counterview{background:#f3eee5;border-top:2px solid var(--coral);padding:28px 34px;margin:39px 0}.counterview b{font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:#935d48}.counterview p{font-size:15px;line-height:1.85;margin:8px 0 0}.bottomline{background:var(--black);color:#eaf0e8;padding:60px;margin:80px 0 0}.bottomline h2{font:550 42px/1.28 var(--serif);margin:9px 0 24px}.bottomline ol{margin:10px 0;padding-left:20px}.bottomline li{margin-bottom:14px;line-height:1.85}.bottomline p{color:#adcbc2;font-size:13px;line-height:1.75}.method{border-top:1px solid var(--line);padding-top:38px;margin-top:55px;color:#526a67;font-size:13px;line-height:1.9}.method code{overflow-wrap:anywhere;word-break:break-word;font-size:11px}.footer{background:#0e2b34;color:#aac7c0;padding:28px 0;font-size:12px}.footer .wrap{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:18px}.footer a{color:#dbebe5}.native-finance{display:none}.flow-semantics{font-size:12px;color:#985d45;line-height:1.7;margin:9px 0 5px}.sankey-hint{display:none;font-size:12px;color:var(--muted);margin:-8px 0 15px}.mobile-kpi{display:none}.ornament{height:1px;background:linear-gradient(90deg,#cddfd4,transparent);margin-top:25px}
@media(max-width:850px){.wrap{width:calc(100% - 38px)}.hero-grid,.executive-grid{grid-template-columns:1fr;gap:26px}.hero{padding:58px 0 65px}.hero-aside{border-left:0;border-top:1px solid #49615f;padding:20px 0 0}.chapter-head{grid-template-columns:1fr;gap:9px}.chapter-body{margin-left:0;max-width:none}.chapter{padding-top:76px}.graphic-top{grid-template-columns:1fr;gap:9px}.graphic-marginal{margin-top:0}.bottomline{padding:33px}.graphic-svg{padding:15px 7px}.facts-strip>div{padding:17px 12px}.hero h1{font-size:clamp(42px,7.4vw,64px)}}
@media(max-width:560px){body{font-size:15px}.wrap{width:calc(100% - 34px)}.mast-inner{min-height:65px}.mast-links{gap:10px}.mast-links a{font-size:11px}.hero h1{font-size:clamp(38px,10vw,52px);line-height:1.2}.hero .dek{font-size:17px}.hero{padding:48px 0 53px}.executive{padding:44px 0}.executive h2{font-size:34px}.executive p{font-size:16px}.facts-strip{grid-template-columns:1fr}.facts-strip>div{border-right:0;border-bottom:1px solid var(--line);padding:16px 5px}.facts-strip>div:last-child{border:0}.facts-strip b{font-size:30px}.chapter{padding-top:65px}.chapter-head h2{font-size:35px}.chapter-head .intro{font-size:16px}.graphic{margin:39px 0}.graphic h3{font-size:30px}.graphic .figure-answer{font-size:14px}.graphic-svg.desktop-finance{display:none}.graphic-svg.native-finance{display:block;overflow:visible;padding:18px 4px}.graphic-svg.native-finance svg{width:100%;max-width:100%;height:auto;overflow:visible}.graphic-data{display:block}.graphic-data{display:block}.figure-bottom{flex-wrap:wrap}.export{display:none}.counterview{padding:20px}.bottomline h2{font-size:32px}.bottomline{padding:25px}.quote{padding:19px 22px}.page-nav .wrap{gap:21px}.graphic-marginal{border-left:2px solid var(--coral)}}
@media(max-width:850px){.graphic-svg.desktop-finance{display:none}.graphic-svg.native-finance{display:block;overflow:visible;padding:18px 4px}.graphic-svg.native-finance svg{width:100%;height:auto;max-width:100%;overflow:visible}.graphic-data{display:block}.graphic-svg{min-height:0}.graphic-svg.native-finance{margin-top:14px}}
'''

JAVASCRIPT='''
document.querySelectorAll('button.export').forEach(button=>button.addEventListener('click',()=>{
 const figure=button.closest('figure');
 // Export the currently visible edition: original 330-unit money SVG on
 // phones/tablets, independent original editorial drawing on desktop.
 const choices=[...figure.querySelectorAll('.graphic-svg svg')];
 const svg=choices.find(node=>getComputedStyle(node).display!=='none'
   && getComputedStyle(node.parentElement).display!=='none'
   && node.getClientRects().length>0);
 if(!svg)return;
 const blob=new Blob([new XMLSerializer().serializeToString(svg)],{type:'image/svg+xml;charset=utf-8'});
 const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url;a.download=figure.id+'.svg'; a.click();setTimeout(()=>URL.revokeObjectURL(url),300);
}));
'''

def fig(code,idx,question,answer,svg,keys,counter=''):
 items=facts(code);rows=[];mobile=[];pages=[]
 for key in keys:
  if key not in items:raise KeyError((code,key))
  v=items[key];pages.append(v['page'])
  amount=(str(v['yuan'])+'%' if v.get('reported_unit')=='%' else ((n(D(str(v['yuan']))/D(10000),2)+' 万元') if D(str(v['yuan']))!=0 and abs(D(str(v['yuan'])))<D(500000) else (f(v['yuan'])+' 亿'))); mobile.append(f'<div class="data-item"><span class="data-label">{x(v["label"])} · p.{v["page"]}</span><span class="data-number">{amount}</span></div>')
  url=(LEDGER[code]['source']['url'] if code in LEDGER else 'https://static.cninfo.com.cn/finalpage/2026-08-28/1225531453.PDF')
  rows.append(f'<tr><td>{x(v["label"])}<br><small>{x(key)}</small></td><td>{amount}</td><td><a href="{x(url)}#page={v["page"]}" target="_blank" rel="noopener">PDF {v["page"]}</a></td></tr>')
 url=(LEDGER[code]['source']['url'] if code in LEDGER else 'https://static.cninfo.com.cn/finalpage/2026-08-28/1225531453.PDF')
 if not counter:counter='该图仅展示原始披露支持的会计关系，不能单凭相关性证明因果。'
 return f'''<figure class="graphic" id="fig-{idx:02d}"{(' data-flow-kind="'+TYPED[code]["kind"]+'"') if idx==2 else ""}>
 <div class="graphic-top"><div><div class="graphic-index">EXHIBIT {idx:02d} / PRIMARY-SOURCE GRAPHIC</div><h3>{x(question)}</h3><p class="figure-answer">{x(answer)}</p></div><p class="graphic-marginal">{x(counter)}</p></div>
 <div class="graphic-svg desktop-finance{' sankey-svg' if '财务桑基图' in svg else ''}">{svg}</div><div class="graphic-svg native-finance">{mobile_for(code,idx,keys,get,items,CFO_COMPONENTS,TYPED[code])}</div>{('<p class="flow-semantics">PRODUCT_LEVEL_GP_NOT_ESTABLISHED · 不代表各分部自身毛利</p>') if idx==2 and code=='000333' else ''}<div class="graphic-data"><div class="tag">原始金额 · 便于手机直接阅读</div><div class="data-grid">{''.join(mobile)}</div></div>
 <div class="figure-bottom"><div class="figure-source">来源：<a href="{x(url)}" target="_blank" rel="noopener">发行人2026H1完整PDF</a> · 物理页 {', '.join('p.'+str(z) for z in sorted(set(pages)))}；底层以原披露金额勾稽，图中换算为人民币亿元。</div><button type="button" class="export" aria-label="导出本图SVG">导出 SVG</button></div>
 <details class="details"><summary>查看精确来源索引与数据表</summary><table class="evidence-table"><thead><tr><th>原始字段</th><th>换算金额</th><th>可点击来源</th></tr></thead><tbody>{''.join(rows)}</tbody></table></details>
 </figure>'''

def chapter(i,name,title,lead,content,anchor):
 return f'''<section id="{anchor}" class="chapter"><div class="chapter-head"><div><div class="tag">{x(name)}</div><div class="chapter-no">{i:02d}.</div></div><div><h2>{x(title)}</h2><p class="intro">{x(lead)}</p></div></div><div class="chapter-body">{content}</div></section>'''
def para(body):return '<p class="prose">'+body+'</p>'
def counterview(body):return '<div class="counterview"><b>Counter-interpretation / 竞争性解释</b><p>'+x(body)+'</p></div>'

def portfolio():
 # per-issuer source-bound editorial compositions; all charts selected by economic relationship.
 out={}
 # SOFTWARE
 c='688111';G=lambda k:get(c,k)
 rev=G('rev'); ni=G('parent_ni'); adj=G('adjusted_ni');cfo=G('cfo')
 f1=fig(c,1,'这不是同一条增长曲线','收入、归母利润、经营现金流的增速相互背离；公司调整后盈利的增速又不同于法定归母利润。',change_lollipop([('收入同比',growth(rev,G('rev_prior'))),('归母利润同比',growth(ni,G('parent_ni_prior'))),('经营现金流同比',growth(cfo,G('cfo_prior')))],'2026H1 vs 2025H1 / 不同会计口径的变化率'),['rev','rev_prior','parent_ni','parent_ni_prior','cfo','cfo_prior'],'公司经调整归母利润约10.87亿元，与法定归母利润25.18亿元定义不同，不能画未经核实的精确调整瀑布。')
 seg=[('WPS个人',G('wps_personal')),('WPS365',G('wps365')),('WPS软件',G('wps_software')),('其他',G('other_rev'))]
 f2=fig(c,2,'四类业务各自如何创造毛利？','WPS四类收入分别连接自己实际披露的业务成本和推导毛利。',source_own_sankey(c,TYPED[c],NAME[c]),['wps_personal','wps_personal_cost','wps365','wps365_cost','wps_software','wps_software_cost','other_rev','other_cost','rev','cogs'],'这些是产品业务的披露划分，不能与公司销售渠道或客户分组交叉相加。')
 gp=[('WPS个人',G('wps_personal')-G('wps_personal_cost')),('WPS365',G('wps365')-G('wps365_cost')),('WPS软件',G('wps_software')-G('wps_software_cost')),('其他',G('other_rev')-G('other_cost'))]
 f3=fig(c,3,'毛利贡献和收入贡献并不是一回事','高毛利业务贡献方向更重要；图示为各分部披露收入减成本所得毛利，并非现金利润。',bars([(lab,yi(v)) for lab,v in gp],'毛利贡献 · 根据分部披露衍生'),['wps_personal','wps_personal_cost','wps365','wps365_cost','wps_software','wps_software_cost','other_rev','other_cost'],'毛利没有扣除研发、销售、管理等期间费用。不要把毛利贡献写成净利润贡献。')
 f4=fig(c,4,'三个利润口径，不应揉成一个瀑布','归母约25.18亿元、扣非归母24.87亿元、公司经调整归母约10.87亿元。',bars([('法定归母净利润',yi(ni)),('监管扣非归母',yi(G('reg_ni'))),('公司调整归母',yi(adj))],'同一期间 · 三种不同定义的利润'),['parent_ni','reg_ni','adjusted_ni','investment_income','equity_income'],'股权投资收益约17.56亿元具有重要解释力，但不能简单从法定利润扣除来重构公司的税后调整口径。')
 f5=fig(c,5,'资产增长落在什么结构上？','2026年6月末资产约208.80亿元，负债约58.03亿元；合同负债体现收款与收入确认的时间差。',split_funding([G(z) for z in ('assets_bs','liabilities','equity')],[G(z) for z in ('assets_prior_bs','liabilities_prior','equity_prior')],'合并资产 = 合并负债 + 所有者权益'),['assets_bs','liabilities','equity','assets_prior_bs','liabilities_prior','equity_prior'],'这是两个时点的资本结构，不是资金的流动路径。')
 f6=fig(c,6,'合同负债与应收账款分别指向不同的现金问题','合同负债约27.64亿元、较年末略增；应收账款约7.55亿元、亦增长，不能混称“收入增长的回款”。',dumbbell([('合同负债',yi(G('contract_liab_prior')),yi(G('contract_liab'))),('应收账款',yi(G('ar_prior_bs')),yi(G('ar_bs')))],'2025年末→2026年6月末 · 存量对照'),['contract_liab','contract_liab_prior','ar_bs','ar_prior_bs'],'合同负债不等于ARR或已确认销售收入，应收账款余额增长也不能直接等同收款率恶化。')
 f7=fig(c,7,'利润没有同步转化为经营现金','经营现金流6.43亿元，低于上年同期7.38亿元；现金及现金等价物的期末增加主要还受到投资和筹资现金流影响。',cash_bridge(G('cash_begin'),[('经营',G('cfo')),('投资',G('cfi')),('筹资',G('cff')),('汇兑',G('cash_fx'))],G('cash_close'),'从期初现金到期末现金 · 2026H1'),['cash_begin','cfo','cfi','cff','cash_fx','cash_close'],'经营现金流是合并口径，归母利润是归属母公司口径；两者比值不可直接称为严格的现金转换率。')
 f8=fig(c,9,'研发投入与现金资本开支是两类不同的投入','研发费用约11.52亿元属于利润表费用；购建长期资产现金支出约0.45亿元，不能将其相加作为“资本开支”。',bars([('研发费用',yi(G('rnd'))),('现金资本开支',yi(G('capex_cash'))),('经营现金流',yi(G('cfo')))],'同一期间 · 研发费用 / 现金支出 / CFO'),['rnd','capex_cash','cfo'],'研发费用不是现金流量表的研发付款；现金资本开支不等于固定资产账面增量。')
 chapters=[
 chapter(1,'BUSINESS ECONOMICS','增长究竟来自软件使用，还是一次性许可？','先把持续性不同的业务拆开，再讨论增长质量。',para('披露的WPS个人、WPS365、WPS软件和其他业务构成可加总的同一收入轴。订阅业务的用户关系与传统许可收入的确认时点不相同；仅有半年收入尚不足以推导续费率、ARR或用户生命周期价值。')+f1+f2+f3,'economics'),
 chapter(2,'EARNINGS QUALITY','法定利润不能直接代表核心经营增长','投资收益与财务会计口径的分歧，是本期最需要拆开的故事。',para('权益法投资收益约'+f(G('equity_income'))+'亿元，合并投资收益约'+f(G('investment_income'))+'亿元，不能被视为全部来自WPS产品收费。监管扣非与公司自定义经调整利润之间亦没有简单的等号：前者遵循非经常性损益口径，后者采用公司的管理层定义。')+f4+counterview('投资收益具有真实的会计归属，也可能代表有经济价值的长期投资。把它一概排除未必更客观；但将当期会计投资收益等同软件商业化能力同样失真。'),'earnings'),
 chapter(3,'BALANCE & CONTRACTS','资产负债表是收入持续性的另一面','预收性质负债、应收款和权益法投资一起决定了利润能否长期兑现。',para('资产从上年末的'+f(G('assets_prior_bs'))+'亿元增加至'+f(G('assets_bs'))+'亿元，尤其应追踪长期股权投资与流动资产构成。合同负债是一项尚待履约的负债，不是无条件获得的未来利润。')+f5+f6,'balance'),
 chapter(4,'CASH & REINVESTMENT','最后让现金回答利润的问题','现金流低于利润并非错误结论，但这种差异必须有可核验的原因。',para('本期经营现金流'+f(G('cfo'))+'亿元，研发费用和人工支付等支出压力并存。通过报表，现金及等价物能够从期初'+f(G('cash_begin'))+'亿元经四类带符号现金流闭合至'+f(G('cash_close'))+'亿元；这是核对现金余额，不是间接法CFO全部调整项已经复核的证明。')+f7+indirect_cfo_figure(c,8,'为什么净利润25.18亿元，CFO只有6.43亿元？','完整间接法附注的16项调整精确闭合。投资收益调回约−19.14亿元和经营性应收变动，是理解利润—现金分歧的重要项目。','净利润是合并口径；报告间接法使用完整净利润，不应错误地从归母利润起桥。')+f8,'cash')]
 out[c]=dict(name='金山办公',ticker=c,sector='SOFTWARE / CLOUD COLLABORATION',headline='利润暴增，\n软件经营增长几何？',deck='利润表最惊人的数字，恰恰不是评估软件商业模式质量的最好起点。',hero_number='25.18 亿',hero_label='2026H1 法定归母净利润 · +236.94%',intro='关键问题不是“会计利润涨了多少”，而是订阅与许可业务创造多少持续毛利、投资收益解释多少财务口径，以及这些利润最终转成了多少经营现金。',counter='公司自定义经调整利润不能自动视作正确的“核心利润”；权益法收益也不一定没有经济价值。真正的结论需要业务持续性、税后调整和现金证据共同支持。',stats=[(f(G('rev'))+' 亿','营业收入 / 同比 +'+n(growth(rev,G('rev_prior')))+'%'),(f(adj)+' 亿','公司调整归母净利润 · 定义另见原报告'),(f(cfo)+' 亿','合并经营现金流 / 同比 '+n(growth(cfo,G('cfo_prior')))+'%')],chapters=chapters,watch=['WPS365订阅业务的真实续费及客单价披露','权益法投资收益的延续性、收现与税务影响','研发人员开支及合同负债转为确认收入的节奏'],limitations='已完成原 PDF 净利润→经营现金流16项调整的逐项签名校验与精确勾稽，但公司经调整利润税后归属桥、股权投资现金创造和全部重大附注尚需独立复核；不据此给出股票估值。')
 # MAOTAI
 c='600519';G=lambda k:get(c,k)
 f1=fig(c,1,'收入与CFO属于完全不同的两条增长曲线','酒类相关营业收入同比约1.47%，但合并经营现金流增长约438.84%，背后的金融资金往来必须独立分析。',change_lollipop([('营业收入',growth(G('rev'),G('rev_prior'))),('归母净利润',growth(G('parent_ni'),G('parent_ni_prior'))),('经营现金流',growth(G('cfo'),G('cfo_prior')))],'2026H1 vs 2025H1'),['rev','rev_prior','parent_ni','parent_ni_prior','cfo','cfo_prior'],'现金流激增不能自动解释为酒类销售改善，财务公司资金流是不可省略的财务机制。')
 product=[('茅台酒',G('maotai_rev')),('系列酒',G('series_rev')),('其他',G('other_rev'))]
 f2=fig(c,2,'各产品毛利必须保留正负方向','茅台酒、系列酒和其他业务的毛利差异；其他业务是负毛利，不能将其伪装成正向桑基流。',signed_product_profit(c,TYPED[c],get,NAME[c]),['maotai_rev','maotai_cogs','series_rev','series_cogs','other_rev','other_cogs','rev','cogs'],'财务公司利息收入已在合并营业总收入中额外披露，产品营收分解不能把该利息混入酒类收入。')
 f3=fig(c,3,'同样卖酒，贡献的毛利率差异巨大','茅台酒收入减成本得到约717.24亿元毛利；系列酒约95.18亿元，绝对贡献与毛利率必须同时看。',bars([('茅台酒毛利',yi(G('maotai_rev')-G('maotai_cogs'))),('系列酒毛利',yi(G('series_rev')-G('series_cogs')))],'按披露产品计算的毛利贡献'),['maotai_rev','maotai_cogs','series_rev','series_cogs','other_rev','other_cogs'],'其他业务成本高于其他收入，毛利为负，故未放入仅包含非负毛利项目的比例柱图，仍保留其原始收入和成本证据。')
 f4=fig(c,4,'销售渠道，属于另一条收入轴','直销约520.07亿元、批发代理约386.97亿元；渠道分类与产品分类是两个维度，不可加总为两倍营收。',bars([('直销',yi(G('direct_rev'))),('批发代理',yi(G('wholesale_rev')))],'同一期间 · 渠道收入'),['direct_rev','wholesale_rev','rev'],'渠道收入与零售终端动销或渠道库存不同；需要终端价格、经销商库存等独立数据才能判断终端需求。')
 f5=fig(c,7,'白酒销售收现与财务公司资金变动必须分开看','销售商品收到现金984.22亿元；会员存款和同业存放净增加额约73.83亿元，而存放央行及同业净增加额列于现金流出项且为负，意味着对CFO是正贡献。',bars([('销售商品收现',yi(G('sales_cash'))),('成员存款净增加（流入）',yi(G('member_deposit_delta'))),('同业资金流出减少（CFO正效应）',yi(-G('interbank_placed_change')))],'不同性质的现金项目 · 不构成精确CFO贡献桥'),['sales_cash','sales_cash_prior','member_deposit_delta','interbank_placed_change','cfo'],'不应将销售回款、成员存款和同业资金调度相加当作“白酒业务现金收入”。财务公司列报符号经过 CFO 经济方向变换。')
 f6=fig(c,5,'合同负债下降，值得与渠道收现一起核查','期末合同负债约31.78亿元，相对上年末约80.07亿元明显下降，但不等于全额新增已确认收入。',dumbbell([('合同负债',yi(G('contract_liab_prior')),yi(G('contract_liab'))),('存货',yi(G('inventory_prior')),yi(G('inventory_bs')))],'年末与半年末 · 时点存量'),['contract_liab','contract_liab_prior','inventory_bs','inventory_prior'],'合同负债变动受订单、交付及收款时间影响；需结合附注具体履约义务和销售时点。')
 f7=fig(c,6,'合并资产规模庞大，不等于全部现金可随意调用','2026H1末资产约3,090.51亿元，负债约469.54亿元；拆出资金等金融资产不等于可立即分配股东的自由现金。',split_funding([G(z) for z in ('assets_bs','liabilities','equity')],[G(z) for z in ('assets_prior_bs','liabilities_prior','equity_prior')],'合并资金结构 · 日期口径一致'),['assets_bs','liabilities','equity','assets_prior_bs','liabilities_prior','equity_prior'],'流动性判断应识别财务公司金融资产、受限资金、客户存款负债及资金的法律可用性。')
 f8=fig(c,9,'经营、投资与筹资现金的方向各不相同','经营现金净流入约706.91亿元，投资现金净流入256.41亿元，筹资现金净流出379.44亿元；净现金增加约583.85亿元（含汇兑）。',signed_cash_bars([('经营现金净额',yi(G('cfo'))),('投资现金净额',yi(G('cfi_bs'))),('筹资现金净额',yi(G('cff_bs'))),('汇兑净影响',yi(G('fx_bs')))],'合并三类现金流及汇率效应 · 原始正负方向'),['cfo','cfi_bs','cff_bs','fx_bs','cash_change'],'同一零基准显示流入向右、流出向左；净现金增量为各带符号数值之和。')
 chapters=[chapter(1,'PRODUCT ECONOMICS','产品和渠道不是同一件事','白酒收入增长放缓时，先读产品毛利和渠道结构，再讨论品牌护城河。',para('产品收入'+f(G('rev'))+'亿元，同比增加约'+n(growth(G('rev'),G('rev_prior')))+'%。其中茅台酒与系列酒的成本结构差异显著。渠道收入口径与产品收入轴独立，不应把直销增减机械归因为涨价或零售终端动销。')+f1+f2+f3+f4,'economics'),chapter(2,'PROFIT ENGINE','高毛利不等于利润没有压力','产品毛利、销售费用和财务公司贡献需要分开解释。',para('本期营业成本'+f(G('cogs'))+'亿元，较上年同期'+f(G('cogs_prior'))+'亿元增加；与此同时归母净利润从'+f(G('parent_ni_prior'))+'亿元降至'+f(G('parent_ni'))+'亿元。毛利与净利的差额包含税费、期间费用和金融业务项目，不能只用品牌定价能力解释全部变动。')+counterview('如果直销和系列酒结构变化只是时点性，产品毛利下降未必构成长周期定价权受损。要区分成本、渠道返利、产品组合和价盘，需要更细的销售与成本附注。'),'earnings'),chapter(3,'BALANCE & WORKING CAPITAL','已收款的履约义务，与库存存量一起读','合同负债的收缩可能影响未来收入确认节奏，但单独一张资产负债表不支持销售预测。',f6+f7+para('将集团财务公司存放、拆出等金融资产直接等同白酒业务账上现金，会高估可自由动用的流动性。必须通过法律主体与受限资金附注判断这些资产的可用性。'),'balance'),chapter(4,'CASH FLOW FORENSICS','现金流暴增，必须首先审视金融子公司','合并经营现金流不能被直接解释为白酒销售经营质量同比改善四倍。',para('合并现金流量表中，财务公司客户存款和同业资金收付会进入经营活动；尤其“存放中央银行和同业款项净增加额”属于现金流出行，负数意味着流出减少，对 CFO 为正贡献。若不先转化会计展示符号，图形会直接讲反故事。')+f5+indirect_cfo_figure(c,8,'从460.33亿元净利润到706.91亿元经营现金，差别在哪里？','财报间接法15项调整全部勾稽；其中经营性应收项目减少带来显著正向贡献，但不等于全部来自白酒客户回款。','这里使用合并净利润46,033,330,566.78元作间接法起点，而不是归母净利润；财务公司资产负债收付会体现在营运资金。')+f8,'cash')]
 out[c]=dict(name='贵州茅台',ticker=c,sector='CONSUMER / PREMIUM SPIRITS',headline='现金流猛增，\n白酒主业真的更好吗？',deck='高毛利品牌的财报，不应该被一家财务公司的资金往来替代解读。',hero_number='706.91 亿',hero_label='2026H1 合并经营现金流 · 并非全为酒类回款',intro='营收仅小幅增长，经营现金净额却大幅上升。最重要的不是庆祝百分比，而是把白酒销售收现与成员存款、同业资金周转从同一张现金流表中正确区分。',counter='销售收现确实是经营活动的重要部分；不能因为金融业务影响了 CFO 就否认白酒主业的现金创造。但也不能用合并现金流的总增幅来证明终端需求和利润质量改善。',stats=[(f(G('rev'))+' 亿','合并营业收入（不含金融利息收入）'),(f(G('parent_ni'))+' 亿','归母净利润 / 同比 '+n(growth(G('parent_ni'),G('parent_ni_prior')))+'%'),(f(G('cfo'))+' 亿','经营现金净额 / 含财务公司资金收付')],chapters=chapters,watch=['合同负债与直销收入的相互验证','茅台酒及系列酒成本和毛利率恢复程度','财务公司存款、同业及拆出资金的时点与流量'],limitations='间接法15项调整已经逐项验证并闭合，但尚未从财务公司分实体报表完整重建内部资金流与集团抵销；不能据合并CFO推算纯白酒业务现金流。')
 # MIDEA
 c='000333';G=lambda k:get(c,k)
 f1=fig(c,1,'三条增速相互背离','营收增加约3.55%，归母净利润增加约1.66%，扣非归母净利润却下降约25.31%。',change_lollipop([('营业收入',growth(G('rev'),G('rev_prior'))),('归母净利润',growth(G('parent_ni'),G('parent_ni_prior'))),('扣非归母',growth(G('reg_ni'),G('reg_ni_prior')))],'2026H1 vs 2025H1 · 法定/监管口径'),['rev','rev_prior','parent_ni','parent_ni_prior','reg_ni','reg_ni_prior'],'净利润口径的差异需要逐项查税后和少数股东调整，不能仅凭衍生品税前收益推断套保有效性。')
 f2=fig(c,2,'三类收入与集团成本、毛利如何守恒？','智能家居、商业及工业解决方案和其他属于同一级；子项只在来源表披露，不被二次计入工业收入。',audited_financial_sankey([('智能家居',G('home')),('工业解决方案',G('industrial_solution')),('其他',G('other_total'))],G('rev'),[('营业成本',G('cogs')),('营业毛利',G('rev')-G('cogs'))],'三类收入 → 集团成本与毛利（未披露各分部自身毛利）',context='PRODUCT_LEVEL_GP_NOT_ESTABLISHED；财务子公司利息/手续费不在本图工业营业收入中；工业子项不得重复加总'),['home','industrial_solution','other_total','building','robotics','industrial_tech','sub_other','rev','cogs'],'此图按集团顶级业务分类，工业解决方案内部四项只保留在来源表作为层级核验；金融收入未进入工业毛利桥。')
 f3=fig(c,3,'海外贡献正在发生什么变化？','境外收入约1,131.27亿元，境内约1,469.15亿元。地区是另一条分类轴，不是可以加到业务板块上的新收入。',dumbbell([('境内收入',yi(G('domestic_prior')),yi(G('domestic'))),('境外收入',yi(G('overseas_prior')),yi(G('overseas')))],'2025H1 → 2026H1 · 地区收入'),['domestic','domestic_prior','overseas','overseas_prior'],'汇率及并购可能影响人民币地区收入；缺乏本币口径不得称之为海外实际销量增长。')
 f4=fig(c,4,'规模增长，毛利率改善了吗？','合并营业收入增长，成本也增长；本期营业毛利约656.76亿元，毛利率略低于上年同期。',profitability_panel(G('rev_prior'),G('cogs_prior'),G('rev'),G('cogs'),'营业收入和营业成本的同口径毛利率'),['rev','rev_prior','cogs','cogs_prior'],'毛利额增长和毛利率上升不是同一回事；业务结构、汇率和成本重分类需要附注才能解释原因。')
 f5=fig(c,5,'法定归母与扣非归母为何距离拉大？','本期归母约264.46亿元，扣非归母约195.95亿元，两者相差68.51亿元，等于报告税后及少数股东调整后的非经常性损益净额。',bars([('法定归母净利润',yi(G('parent_ni'))),('扣非归母净利润',yi(G('reg_ni'))),('披露非经常性净额',yi(G('nonrecurring_net')))],'三种口径相关但不是三类可相加利润'),['parent_ni','reg_ni','nonrecurring_net','derivatives_gain_pretax','financial_exp'],'衍生工具收益的税前金额与扣非归母税后差额不可直接相减或相互抵销。')
 f6=fig(c,7,'经营应收增长，库存余额却下降','应收账款从年末约404.50亿元上升到619.55亿元，存货从646.29亿元下降到554.41亿元。',dumbbell([('应收账款',yi(G('ar_prior')),yi(G('ar'))),('存货',yi(G('inventory_prior')),yi(G('inventory')))],'2025年末→2026年中 · 存量变化'),['ar','ar_prior','inventory','inventory_prior'],'资产负债表余额变动不等于CFO间接调整；须核对票据、汇率、减值、收并购和金融业务账户变化。')
 f7=fig(c,6,'金融子公司让总收入略大于工业收入','营业总收入约2,610.52亿元，包含工业营业收入约2,600.42亿元以及金融利息和手续费项目。',bars([('营业收入',yi(G('rev'))),('金融利息收入',yi(G('interest_income')))],'营业收入≠营业总收入（手续费项目极小，下表保留）'),['rev','total_rev','interest_income','fee_income'],'金融利息收入与家电销售是不同的业务机制，不能把两者画成同一种产品销量。')
 f8=fig(c,8,'资产负债表反映的是资金结构，而非经营资金流','合并资产约6,431.02亿元，负债约4,173.09亿元；权益结构和现金余额不能等同。',split_funding([G(z) for z in ('assets_bs','liabilities','equity')],[G(z) for z in ('assets_prior_bs','liabilities_prior','equity_prior')],'集团资产与负债权益结构'),['assets_bs','liabilities','equity','assets_prior_bs','liabilities_prior','equity_prior'],'现金与金融资产的可用性及金融业务存款债务需在附注中分开判断。')
 f9=fig(c,9,'利润到现金：现金流闭合，但不证明盈利质量','经营现金流约375.52亿元，投资现金净流出158.72亿元、筹资净流出151.56亿元、汇兑负影响4.18亿元，期末现金及等价物746.14亿元。',cash_bridge(G('cash_begin_bs'),[('经营',G('cfo')),('投资',G('cfi_bs')),('筹资',G('cff_bs')),('汇兑',G('fx_bs'))],G('cash_close_bs'),'真实符号现金桥 · 2026H1'),['cash_begin_bs','cfo','cfi_bs','cff_bs','fx_bs','cash_close_bs','capex_cash'],'现金余额闭合与利润→CFO间接法分别勾稽，但两者均不代表衍生品套保现金结算、税后归属与经营风险已经完成独立复核。')
 chapters=[chapter(1,'BUSINESS STRUCTURE','先解除重复计算，才有真实分部分析','全球多业务集团最容易把“父业务、子业务、地区”误当独立收入来源。',para('智能家居收入'+f(G('home'))+'亿元，商业及工业解决方案'+f(G('industrial_solution'))+'亿元，后者细分四类已全部计入父层收入。中国境内和海外收入是另一条维度；这套结构的严谨性优先于画一张复杂桑基图。')+f1+f2+f3,'economics'),chapter(2,'MARGIN & EARNINGS','盈利能力要区分经营与金融市场影响','营业收入、产品毛利、投资收益、套保与非经常性损益必须按会计位置区分。',para('本期归母净利润'+f(G('parent_ni'))+'亿元，而扣非归母仅'+f(G('reg_ni'))+'亿元。报告披露的非经常性损益净额'+f(G('nonrecurring_net'))+'亿元经过税收及非控制性权益等处理，不能用一笔税前衍生品收益直接解释全部差异。')+f4+f5+f7+counterview('汇兑损益与衍生品公允价值变化在会计报表中可能分别列示；扣非下滑不意味着套保完全失效，但也不能据此证明套保已经成功。'),'earnings'),chapter(3,'BALANCE SHEET','盈利变化背后的资产占用','应收账款、库存与金融业务结构共同决定资产质量。',f6+f8+para('截至期末应收账款较年末增长而存货减少；是否是销售账期拉长，需要应收款龄、票据、海外业务汇率及合并范围变化配合验证。单张金额图不能得出“回款恶化”的定论。'),'balance'),chapter(4,'CASH & CAPITAL ALLOCATION','现金可以闭合，经营质量仍需继续追问','集团经营现金、投融资现金与汇率变动性质不同，必须逐一带符号核对。',f9+indirect_cfo_figure(c,10,'经营性应收、应付和库存如何改变 CFO？','间接法13项披露调整全部勾稽。经营性应收增加约240.89亿元、经营性应付增加约254.84亿元、存货减少约90.63亿元，不能直接用两张资产负债表期末存量代替。','这是一座完整原文间接法现金桥；它解释调整项的会计位置，并不单独证实应收质量与风险套保现金结算。')+para('经营活动现金流'+f(G('cfo'))+'亿元，相对法定归母利润较高并不直接证明质量优越，因为混合业务集团包含财务子公司项目。间接法现金流量补充资料已经逐项闭合，但需继续解读金融业务资金收付及经营性应收、应付形成的原因。'),'cash')]
 out[c]=dict(name='美的集团',ticker=c,sector='GLOBAL INDUSTRIAL CONGLOMERATE',headline='利润看似稳定，\n经营表现为何分裂？',deck='同一份财报中，收入、毛利、法定利润、扣非利润和金融风险管理讲的是不同的故事。',hero_number='−25.31%',hero_label='扣非归母净利润同比 · 法定归母仍+1.66%',intro='最危险的捷径，是用“家电收入增长”解释整家集团，或者把一笔税前衍生工具收益与税后扣非利润直接相减。真正的研究要先识别业务层级和会计归属。',counter='扣非利润恶化是需要解释的信号，但未必等同主业竞争力崩塌；从汇兑、衍生品到税后归属的完整桥尚需更细附注。',stats=[(f(G('rev'))+' 亿','营业收入 / 同比 +'+n(growth(G('rev'),G('rev_prior')))+'%'),(f(G('parent_ni'))+' 亿','法定归母净利润'),(f(G('reg_ni'))+' 亿','扣非归母净利润')],chapters=chapters,watch=['汇兑损益、金融衍生工具的税后归属与现金结算','境内外业务同比与同币种利润质量','应收账款账龄、票据及存货周转变化'],limitations='未完成全体子公司分部抵销、衍生品税前税后及OCI匹配专项复核；无法证明套期保值经济有效性。')
 # BANK
 c='600036';G=lambda k:get(c,k)
 f1=fig(c,1,'利息收入下降，净利息收入为何反而增长？','利息收入同比减少42.81亿元，利息支出减少102.18亿元；负债成本改善抵消资产端压力，净利息收入增加59.37亿元。',income_interests(G('interest_in'),G('interest_in_prior'),G('interest_out'),G('interest_out_prior'),'净利息收入 = 利息收入 − 利息支出'),['interest_in','interest_in_prior','interest_out','interest_out_prior','nii','nii_prior'],'本图是会计收入/支出同比归因，不是严格资产规模 × 收益率分解；要做后者需要日均生息资产负债数据。')
 f2=fig(c,2,'银行收入必须从净额开始阅读','净利息收入约1,120.22亿元，净手续费佣金约398.55亿元，其他净收入约263.04亿元，共同构成1,781.81亿元营业收入。',audited_financial_sankey([('净利息收入',G('nii')),('净手续费收入',G('fees_net')),('其他净收入',G('other_net'))],G('revenue'),[('营业支出合计',G('administrative_expense')+G('credit_impairment_expense')+G('other_operating_cost')),('营业利润',G('operating_profit'))],'银行净收入 → 支出与营业利润（已扣息净收入）',context='净利息收入已减利息支出；本图不另减一次，税费及少数股东见下一张桥'),['nii','fees_net','other_net','revenue','administrative_expense','credit_impairment_expense','other_operating_cost','operating_profit'],'净利息收入已经扣除了利息支出，不能再当作普通工业企业的营业收入减一次成本。')
 fpl=fig(c,3,'银行收入经过信用成本和运营费用后留下多少利润？',
  '营业收入1,781.81亿元，减业务管理费529.12亿元、信用减值291.77亿元、其他营业支出53.09亿元，营业利润907.83亿元；再经营业外净损益、税费及少数股东损益后，归母利润764.45亿元。',
  cash_bridge(G('revenue'),[('业务管理费',-G('administrative_expense')),('信用减值',-G('credit_impairment_expense')),('其他营业支出',-G('other_operating_cost')),('营业外收入',G('nonoperating_income')),('营业外支出',-G('nonoperating_expense')),('所得税',-G('income_tax_expense')),('少数股东',-G('nci_ni'))],G('parent_ni'),'利润表·经费用与信用成本到归母净利润',start_label='银行营业收入',end_label='归母净利润',footer='亿元 · 费用扣减、营业外净额、所得税、少数股东损益全部以合并法定利润表准确列报'),
  ['revenue','administrative_expense','credit_impairment_expense','taxes_surcharges','other_asset_impairment','other_business_cost','other_operating_cost','nonoperating_income','nonoperating_expense','income_tax_expense','nci_ni','operating_profit','consolidated_ni','parent_ni'],
  '其他营业支出由税金及附加、其他资产减值及其他业务成本构成。净利润口径不是“营业利润直接减所得税”；中间还存在营业外净额。')
 f3=fig(c,4,'贷款扩张与存款扩张是否同步？','期末资产负债表贷款及垫款净额约71,942.63亿元，客户存款约102,405.29亿元；二者既不等同“存贷比”监管定义，也不反映全部流动性。',dumbbell([('客户存款',yi(G('customer_deposits_prior')),yi(G('customer_deposits'))),('贷款及垫款净额',yi(G('net_loans_prior')),yi(G('net_loans')))],'2025年末→2026年6月末 · 金融资产负债存量'),['customer_deposits','customer_deposits_prior','net_loans','net_loans_prior'],'资产负债表贷款是净值，而经营披露的贷款总额可能使用拨备前本金，不能混用分母。')
 f4=fig(c,5,'资本缓冲不能只看一个绝对数','核心一级资本充足率14.07%，较上年末低0.09个百分点；监管资本受风险加权资产增速影响。',risk_panels([('不良贷款率',G('npl_pct_prior'),G('npl_pct')),('贷款拨备覆盖率',G('coverage_pct_prior'),G('coverage_pct')),('核心一级资本充足率',G('cet1_pct_prior'),G('cet1_pct'))],'三个监管质量指标 · 分开衡量'),['npl_pct','npl_pct_prior','coverage_pct','coverage_pct_prior','cet1_pct','cet1_pct_prior'],'这些比率不处于同一数量级；新图以完全不同指标的独立变动值呈现，不做虚假的共轴视觉比较。')
 f5=fig(c,6,'银行的资产负债结构，本来就不同于工业企业','2026年6月末合并资产约137,852.80亿元，负债约124,319.79亿元；大部分资金来自对存款人等承担的负债。',split_funding([G(z) for z in ('assets_bs','liabilities','equity')],[G(z) for z in ('assets_prior_bs','liabilities_prior','equity_prior')],'资本与负债构成 · 两个资产负债表日期'),['assets_bs','liabilities','equity','assets_prior_bs','liabilities_prior','equity_prior'],'商业银行的高负债率属于商业模式的一部分，不应套用制造业资产负债率“越低越好”的判据。')
 f6=fig(c,7,'银行利润与现金流不能按工业式转换率打分','净利润约769.19亿元，经营现金净流入3,046.11亿元，主要受到银行资金往来的大额收付驱动。',bars([('合并净利润',yi(G('consolidated_ni'))),('经营现金净额',yi(G('cfo')))],'同一期间 · 不是利润的转化率'),['consolidated_ni','cfo','cfo_prior'],'不能将银行CFO/净利润直接解释为经营效率、自由现金或可分红能力。')
 f7=fig(c,8,'三类现金流闭合，不代表盈利已经收现','从期初现金7,098.22亿元，经经营、投资、筹资和汇兑影响，期末现金等价物8,397.42亿元。',cash_bridge(G('cash_begin_bs'),[('经营',G('cfo')),('投资',G('cfi_bs')),('筹资',G('cff_bs')),('汇兑',G('fx_bs'))],G('cash_close_bs'),'现金及等价物的真实净变动'),['cash_begin_bs','cfo','cfi_bs','cff_bs','fx_bs','cash_close_bs'],'经营资产负债资金收付导致CFO大幅波动。该桥验证现金闭合，不是银行盈利质量评分。')
 chapters=[chapter(1,'NET INTEREST ECONOMICS','存款成本优势能抵住多少资产收益下行？','利率下降环境下，观察净利息收入要把收入端与成本端分拆。',para('2026H1银行利息收入'+f(G('interest_in'))+'亿元，较上年同期减少'+f(G('interest_in_prior')-G('interest_in'))+'亿元；利息支出减少'+f(G('interest_out_prior')-G('interest_out'))+'亿元，令净利息收入仍增长。净息差的变化仍需用平均生息资产、负债结构及重定价时间解释；两期会计收入差异不是纯利差归因。')+f1+f2,'economics'),chapter(2,'EARNINGS & PROVISION','从净利息收入到利润，还要面对信贷成本','银行营业支出包括减值，不能将整个净利息收入视为类工业毛利。',para('合并营业收入约'+f(G('revenue'))+'亿元，营业利润'+f(G('operating_profit'))+'亿元，净利润'+f(G('consolidated_ni'))+'亿元。资产减值、金融市场公允价值波动、手续费收入和税负都有各自机制。期末不良贷款率0.94%，但不良余额和拨备覆盖的边际变化值得跟踪。')+fpl+counterview('当前存款成本下降显示负债管理优势，但也可能来自市场利率周期。零售资产质量及信用风险暴露如果恶化，会抵消净息差方面的改善。'),'earnings'),chapter(3,'FUNDING, CREDIT & CAPITAL','规模不是优势的全部，资本才是约束','客户存款、贷款净额、损失准备及风险加权资产是银行研究的核心存量。',f3+f4+f5+para('风险加权资产增速可能超过核心资本积累，令资本率边际下行。拨备覆盖率385.10%虽然仍较高，却比上年末有所下降；这不是直接信用损失预测，需要结合不良生成、逾期、迁徙率和核销具体分析。'),'balance'),chapter(4,'BANK CASH FLOW','现金流巨额波动，不代表可分红现金','对商业银行，现金流量表的“经营活动”包含客户存贷款及金融机构业务本身。',f6+f7+para('本期CFO显著增长，不能像制造业那样以CFO/净利润直接评价盈利质量。真正的流动性与资本安全需要高质量流动资产、稳定资金、监管资本及期限错配分析。'),'cash')]
 out[c]=dict(name='招商银行',ticker=c,sector='COMMERCIAL BANKING / NET INTEREST',headline='净息差仍承压，\n净利息收入为何增长？',deck='存款成本改善救回了部分利息收益，但银行的真实质量，还要交给信贷、资本和资金期限检验。',hero_number='1,120.22 亿',hero_label='2026H1 净利息收入 · 利息收入减利息支出',intro='当利息收入下降、支出下降更多，净利息收入仍可能增长。不能仅盯利润增速；必须看资金来源、信贷资产质量、拨备与风险加权资本的变化。',counter='这份报告证明负债端成本改善，但不能证明可持续的核心净息差优势；信用成本、零售业务压力和期限结构可能改变判断。',stats=[(f(G('nii'))+' 亿','净利息收入 / 同比 +'+n(growth(G('nii'),G('nii_prior')))+'%'),(f(G('parent_ni'))+' 亿','归属于本行股东净利润'),('14.07%','集团核心一级资本充足率 / 较年末-0.09pp')],chapters=chapters,watch=['生息资产平均收益率与存款平均成本率变动','零售不良生成、逾期、拨备和核销对信用成本的影响','核心一级资本净额增速与风险加权资产增长'],limitations='银行各类减值及风险迁徙完整附注、流动性覆盖率和同业多季度数据尚未全部完成第二次独立审阅；不据本期CFO给出银行FCF。')
 return out


def render_case(case,code):
 chapters=''.join(case['chapters'])
 nav=''.join(f'<a href="#{anchor}">{label}</a>' for anchor,label in [('overview','执行摘要'),('economics','商业模式'),('earnings','盈利质量'),('balance','资产负债'),('cash','现金流'),('conclusion','反证与展望'),('sources','来源审计')])
 strip=''.join(f'<div><b>{x(amount)}</b><small>{x(label)}</small></div>' for amount,label in case['stats'])
 watch=''.join('<li>'+x(z)+'</li>' for z in case['watch'])
 title=case['headline'].replace('\n','<br>')
 source=(LEDGER[code]['source']['url'] if code in LEDGER else 'https://static.cninfo.com.cn/finalpage/2026-08-28/1225531453.PDF')
 statement='''本研究以发行人2026年半年度完整披露PDF为原始来源；全文金额原始精度保留在审计账本中，网页以亿元展示并按约定小数位四舍五入。对流量比较2026H1/2025H1，对存量比较2026-06-30/2025-12-31。会计勾稽通过不等于已独立完成整份PDF逐行研究；缺少外部行业、股价或逐季数据，不提供目标价。'''
 htmltext=f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><link rel="canonical" href="https://financials-in-visuals.pages.dev/research/2026-h1-v10/{code}.html"><meta name="description" content="{x(case['name'])} 2026年半年报：从真实业务、利润、资产负债和现金流的会计证据出发进行独立可视化研究。"><title>{x(case['name'])} · 2026H1 财务研究 | Financials in Visuals</title><style>{CSS}</style></head><body>
<header class="mast"><div class="wrap mast-inner"><a class="brand" href="/#companies">FINANCIALS IN VISUALS<span>ORIGINAL A-SHARE EQUITY RESEARCH</span></a><div class="mast-links"><a href="/#companies">全部公司</a><a href="{x(source)}" target="_blank" rel="noopener">原始PDF</a></div></div></header>
<section class="hero"><div class="wrap hero-grid"><div><div class="eyebrow">SOURCE-FIRST RESEARCH / 2026 H1 / {x(case['sector'])}</div><h1>{title}</h1><p class="dek">{x(case['deck'])}</p><div class="meta-row"><span>{x(case['name'])} · {code}</span><span>2026年半年度 · 未经审计</span><span>研究预览 · 2026-11-03</span></div></div><aside class="hero-aside"><div class="eyebrow">THE NUMBER THAT MISLEADS</div><div class="big-number">{x(case['hero_number'])}</div><p>{x(case['hero_label'])}</p></aside></div></section>
<nav class="page-nav" aria-label="研究章节导航"><div class="wrap">{nav}</div></nav>
<main><div class="wrap"><section class="executive" id="overview"><div class="executive-grid"><div><div class="tag">01 / EXECUTIVE READ · 90 SECOND THESIS</div><h2>{x(case['intro'])}</h2><p>本稿的判断只从能够在原始财报复核的财务事实出发。不同会计主体、收入和利润定义、现金流经济方向必须拆开，避免把同期变化写成没有证据的因果关系。</p></div><div class="speed-reading"><div class="mini">ALTERNATIVE EXPLANATION / 反方观点</div><div class="counter">{x(case['counter'])}</div><p class="tag">NOT AN INVESTMENT RECOMMENDATION</p></div></div><div class="facts-strip">{strip}</div></section>
{chapters}
<section id="conclusion" class="bottomline"><div class="tag" style="color:#9fd7c1">WHAT WOULD CHANGE THE THESIS?</div><h2>下一份报告，需要回答这些问题。</h2><ol>{watch}</ol><p>关键局限：{x(case['limitations'])}</p></section>
<section id="sources" class="method"><div class="tag">SOURCE & ACCOUNTING CONTROL</div><h2 style="font:550 30px/1.3 var(--serif)">可复核，不意味着夸大确定性。</h2><p>{statement}</p><p>原始披露：<a href="{x(source)}" target="_blank" rel="noopener">{x(case['name'])} · 2026H1 PDF</a> · SHA-256：<code>{SHA[code]}</code></p><p>通过基础硬校验：PDF SHA、选定原始数值页码匹配、合并资产=负债+权益（当期及上期）、签名现金流闭合和适用的分部/口径勾稽。<strong>仍未完成：</strong>全量附注独立同行审阅、真实季度/同业与估值数据库。状态：研究预览，不是正式独立机构评级。</p></section></div></main>
<footer class="footer"><div class="wrap"><div>FINANCIALS IN VISUALS · ORIGINAL RESEARCH / VERIFIABLE EVIDENCE</div><div><a href="/#companies">返回全部公司</a>　·　<a href="#overview">回到摘要</a></div></div></footer><script>{JAVASCRIPT}</script></body></html>'''
 return htmltext

def render_index(cases):
 cards=''.join(f'''<a class="feature" href="./{code}.html"><span class="tag">{x(c['sector'])}</span><div class="feature-number">{i:02d}</div><h2>{x(c['headline'].replace(chr(10),' '))}</h2><p>{x(c['deck'])}</p><div class="feature-foot">{x(c['name'])} · 2026H1 · 深度研究预览　↗</div></a>''' for i,(code,c) in enumerate(cases.items(),1))
 return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,follow"><title>历史研究系列 · 四公司归档 · Financials in Visuals</title><style>{CSS}.indexhero{{padding:83px 0 91px;background:var(--black);color:var(--paper)}}.indexhero h1{{font:560 clamp(49px,7vw,93px)/1.15 var(--serif);letter-spacing:-.055em;max-width:920px;margin:23px 0}}.indexhero p{{font-size:20px;color:#b5cfc8;max-width:800px}}.portfolio{{padding:65px 0 110px}}.features{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;background:var(--line);border:1px solid var(--line)}}.feature{{position:relative;text-decoration:none;padding:43px 44px 50px;background:var(--paper);min-height:350px;display:flex;flex-direction:column;transition:background .18s}}.feature:hover{{background:#edf6ef}}.feature h2{{font:560 clamp(27px,3vw,40px)/1.36 var(--serif);letter-spacing:-.04em;margin:32px 0 14px}}.feature p{{font-size:15px;color:#617777;line-height:1.8;max-width:440px}}.feature-number{{position:absolute;right:35px;top:26px;color:#dae8df;font:700 65px/1 var(--serif)}}.feature-foot{{font-size:13px;font-weight:700;color:var(--green);margin-top:auto;padding-top:25px}}.disclosure{{font-size:14px;color:#566c69;padding-top:35px;max-width:900px}}@media(max-width:740px){{.features{{grid-template-columns:1fr}}.feature{{padding:32px 25px;min-height:300px}}.indexhero{{padding:63px 0 70px}}}}</style></head><body><header class="mast"><div class="wrap mast-inner"><a class="brand" href="/#companies">FINANCIALS IN VISUALS<span>RESEARCH, NOT DECORATIVE CHARTS</span></a><div class="mast-links"><a href="/#companies">全部公司</a></div></div></header><section class="indexhero"><div class="wrap"><div class="eyebrow">ARCHIVE / 2026H1 · 早期四公司目录</div><h1>此为历史四公司目录。<br>统一研究库已整合现有研究公司。</h1><p>原始全部公司研究均已通过网站首页统一入口查找。本页仅保留旧链接兼容，请阅读<a href="/#companies" style="color:#9de5c8">完整全部公司研究库 ↗</a>。</p></div></section><main class="portfolio"><div class="wrap"><div class="eyebrow" style="color:var(--green);margin-bottom:24px">FEATURED REPORTS</div><div class="features">{cards}</div><p class="disclosure">本系列为基于2026年半年度原始PDF的来源限定研究预览；已核对主要会计恒等式，但未完成全部附注的第二位独立分析师审核、完整多季度外部数据和估值建模。所有公司均提供原PDF及逐图来源表。网页为独立、离线可阅读的HTML，无外部字体或脚本依赖。</p></div></main><footer class="footer"><div class="wrap">FINANCIALS IN VISUALS · 2026H1 REBUILT EDITION</div></footer></body></html>'''

if __name__=='__main__':
 checks=[check(k) for k in ['688111','600519','000333','600036']]
 if any(z['literal_page_numeric_missing'] for z in checks):raise SystemExit('Source page numeric verification failed')
 portfolio_data=portfolio()
 for code,c in portfolio_data.items():
  content=render_case(c,code)
  path=OUTPUT/f'{code}.html';path.write_text(content)
  print('BUILD',code,'bytes',path.stat().st_size,'figures',content.count('<figure'),'tables',content.count('<table'))
 (OUTPUT/'index.html').write_text(render_index(portfolio_data))
 (HERE/'build-manifest.json').write_text(json.dumps({'source_check':checks,'files':{f.name:{'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'figures':f.read_text().count('<figure')} for f in OUTPUT.glob('*.html')}},ensure_ascii=False,indent=2))
 print('BUILD done',OUTPUT)