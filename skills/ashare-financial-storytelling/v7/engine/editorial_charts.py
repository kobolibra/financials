"""Source-driven editorial financial charts. No issuer/period-specific constants.

Charts are illustrative economic allocations rather than evidence of literal cash
movement. Values are Decimal yuan and chart geometry is conserved.
"""
from decimal import Decimal as D
from html import escape

UNIT = D(100000000)

def _v(l, name):
    x = l.get('facts', {}).get(name)
    return None if not x or x.get('amount') is None else D(str(x['amount']))

def _p(l, key):
    f = l['facts'].get(key)
    return ('p.'+str(f['page'])) if f and f.get('page') else '页码未核'

def _n(v):
    return f'{v / UNIT:,.2f}'

def _q(v):
    return f'{v * D(100):.1f}%'

def _path(x1,y1,x2,y2,h,col,desc):
    if h < 0: raise ValueError('negative financial band')
    if not h: return ''
    c1=x1+(x2-x1)*.42;c2=x1+(x2-x1)*.58
    d=f'M {x1:.1f},{y1:.1f} C {c1:.1f},{y1:.1f} {c2:.1f},{y2:.1f} {x2:.1f},{y2:.1f} L {x2:.1f},{y2+h:.1f} C {c2:.1f},{y2+h:.1f} {c1:.1f},{y1+h:.1f} {x1:.1f},{y1+h:.1f} Z'
    return f'<path d="{d}" fill="{col}" fill-opacity=".79" class="ed-band" tabindex="0" role="img" aria-label="{escape(desc,quote=True)}"><title>{escape(desc)}</title></path>'

def _txt(x,y,t,css='ed-label',anchor='start'):
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" class="{css}">{escape(str(t))}</text>'

def _node(x,y,w,h,color):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{max(h,1):.1f}" rx="3" fill="{color}"/>'

def balance_identity(l):
    """Full source→assets→liabilities/equity, as a STOCK identity, not cash flow."""
    keys=('assets','current_assets','noncurrent_assets','liabilities','equity')
    if any(_v(l,k) is None for k in keys): return '<p>资产负债项目不全，暂不生成结构图。</p>'
    a,ca,nca,liab,eq=(_v(l,k) for k in keys)
    if ca+nca!=a or liab+eq!=a or a<=0: raise ValueError('Unbalanced total assets')
    categories=[('货币资金','monetary_funds','#348b9a'),('应收账款净额','accounts_receivable','#4caeaa'),('存货净额','inventory','#78c1a5'),('预付款项','prepayment','#a2cbb1')]
    seen=[]
    for name,key,c in categories:
        v=_v(l,key)
        if v is not None and v>0:seen.append((name,v,key,c))
    rem=ca-sum((x[1] for x in seen),D(0))
    if rem<D(0):raise ValueError('Missing asset stock classifications or overlap: listed current assets > current assets')
    if rem:seen.append(('其他流动资产（计算差额）',rem,'current_assets','#bbcec4'))
    seen.append(('非流动资产',nca,'noncurrent_assets','#9dabb7'))
    scale=340/float(a/UNIT);leftcur=119;centercur=111
    elements=[];leftitems=[]
    for i,(name,v,key,color) in enumerate(seen):
        h=float(v/UNIT)*scale
        elements.append(_path(310,leftcur,674,centercur,h,color,f'{name} {_n(v)}亿元；来源 {_p(l,key)}；图示为资产结构，不代表资金流转'))
        elements.append(_node(295,leftcur,15,h,color))
        leftitems.append((name,v,key,color,leftcur+h/2))
        leftcur+=h+13;centercur+=h
    elements.append(_node(674,111,22,float(a/UNIT)*scale,'#235862'))
    middleheight=float(a/UNIT)*scale
    # right side starts at the exact same y and conserves amount at each node
    rightcur=111
    for name,v,key,col in [('负债',liab,'liabilities','#bf8075'),('所有者权益',eq,'equity','#13836d')]:
        h=float(v/UNIT)*scale
        elements.append(_path(696,rightcur,1100,rightcur,h,col,f'{name} {_n(v)}亿元；来源 {_p(l,key)}；只表示资产=负债+权益的会计恒等式'))
        elements.append(_node(1100,rightcur,18,h,col))
        elements.append(_txt(1145,rightcur+h/2-4,name,'ed-label'))
        elements.append(_txt(1145,rightcur+h/2+21,_n(v)+' 亿元','ed-value'))
        rightcur+=h
    for name,v,key,col,y in leftitems:
        elements.append(_txt(279,y-5,name,'ed-label','end'))
        elements.append(_txt(279,y+20,_n(v)+' 亿 · '+_p(l,key),'ed-sub','end'))
    elements.append(_txt(710,90,'资产总额','ed-label'))
    elements.append(_txt(710,473,_n(a)+' 亿元','ed-value'))
    elements.append(_txt(70,63,'ASSET COMPOSITION / 资产从何构成','ed-kicker'))
    elements.append(_txt(674,63,'ASSETS / 资产','ed-kicker'))
    elements.append(_txt(1100,63,'FUNDING / 负债与权益','ed-kicker'))
    elements.append(_txt(70,561,'左侧：流动资产的主要披露科目及其他流动资产计算差额。右侧：同一总额的负债与权益。','ed-caption'))
    elements.append(_txt(70,586,'这是一张时点资产负债关系图，不代表资产被实际转移给股东或债权人。','ed-caption'))
    return f'<svg class="editorial-flow" viewBox="0 0 1470 630" xmlns="http://www.w3.org/2000/svg" role="group" aria-label="资产负债表：资产主要类别组成与负债权益的同额分解">{"".join(elements)}</svg>'

def operating_cash_allocation(l):
    """CFO to cash capex + analyst residual. A *definition*, not cash-source tracking."""
    cfo,capex=_v(l,'cfo'),_v(l,'capex_cash')
    if cfo is None or capex is None or cfo<=0 or capex<0:return '<p>经营现金流与现金资本开支不足，不能做资金分配图。</p>'
    if cfo<capex:return '<p>经营现金流低于现金资本开支，使用带符号 FCF 桥而非正值 Sankey。</p>'
    fcf=cfo-capex
    scale=240/float(cfo/UNIT);totalh=float(cfo/UNIT)*scale;h1=float(fcf/UNIT)*scale;h2=float(capex/UNIT)*scale
    elements=[_txt(80,65,'CFO / 经营现金流净额','ed-kicker'),_txt(825,65,'ANALYST ALLOCATION / 分析性分解','ed-kicker'),
       _node(300,115,20,totalh,'#285663'),
       _path(320,115,810,110,h1,'#168d72',f'经营现金流扣现金资本开支得到的简化 FCF {_n(fcf)}亿元，计算 p.{_p(l,"cfo")}/{_p(l,"capex_cash")}'),
       _path(320,115+h1,810,115+h1+47,h2,'#c38e73',f'现金资本开支 {_n(capex)}亿元；来源 {_p(l,"capex_cash")}'),
       _node(810,110,18,h1,'#14866b'),_node(810,115+h1+47,18,h2,'#bf8065'),
       _txt(275,228,'经营现金流','ed-label','end'),_txt(275,255,_n(cfo)+' 亿','ed-value','end'),
       _txt(855,110+h1/2-5,'简化自由现金流','ed-label'),_txt(855,110+h1/2+24,_n(fcf)+' 亿','ed-value'),
       _txt(855,115+h1+47+h2/2-5,'购建长期资产支付现金','ed-label'),_txt(855,115+h1+47+h2/2+24,_n(capex)+' 亿','ed-value'),
       _txt(80,468,'定义：经营现金流 − 购建长期资产支付的现金 = 简化 FCF；并非实际现金逐笔去向或可分配股东现金。','ed-caption'),
       _txt(80,493,f'来源：{_p(l,"cfo")}、{_p(l,"capex_cash")}。筹资净流量、其他投资活动和汇率影响另在下方现金余额桥中核算。','ed-caption')]
    return f'<svg class="editorial-flow" viewBox="0 0 1420 530" xmlns="http://www.w3.org/2000/svg" role="group" aria-label="经营现金流简化分解：购建长期资产现金支出与剩余简化自由现金流">{"".join(elements)}</svg>'

def profitability_change(l):
    """Compact paired-interval ratio plot, explicitly ONLY two H1 observations."""
    rev,cogs,prev,pcogs,cfo,pcfo,capex,pcapex=(_v(l,k) for k in ('revenue','cogs','revenue_prior','cogs_prior','cfo','cfo_prior','capex_cash','capex_cash_prior'))
    if None in (rev,cogs,prev,pcogs,cfo,pcfo,capex,pcapex) or rev<=0 or prev<=0:return '<p>缺少可比半年度信息，不绘制利润率双期图。</p>'
    vals=[('毛利率',(prev-pcogs)/prev,(rev-cogs)/rev,'#13876d'),('经营现金流率',pcfo/prev,cfo/rev,'#286d86'),('简化 FCF 率',(pcfo-pcapex)/prev,(cfo-capex)/rev,'#bd8b72')]
    startx,endx=340,890;out=[_txt(70,46,'TWO COMPARABLE PERIODS / 两个同期观察，不是长期趋势','ed-kicker')]
    for i,(lab,a,b,col) in enumerate(vals):
        yy=116+i*100;pos1=startx+float(a)*700;pos2=startx+float(b)*700
        out.append(_txt(70,yy-7,lab,'ed-label'))
        out.append(f'<line x1="{startx}" y1="{yy}" x2="{endx}" y2="{yy}" stroke="#dfe6df" stroke-width="2"/>')
        out.append(f'<line x1="{pos1:.1f}" y1="{yy}" x2="{pos2:.1f}" y2="{yy}" stroke="{col}" stroke-width="8" stroke-linecap="round" opacity=".67"/>')
        for x,val,label in [(pos1,a,l['document'].get('comparative_period_key','上期')),(pos2,b,l['document'].get('period_key','本期'))]:
            out.append(f'<circle cx="{x:.1f}" cy="{yy}" r="9" fill="{col}" stroke="#fff" stroke-width="3"><title>{label} {_q(val)}</title></circle>')
        out.append(_txt(1040,yy-7,_q(a)+' → '+_q(b),'ed-value'))
        out.append(_txt(1040,yy+19,('+' if b>=a else '')+str(round((b-a)*100,2))+' pp','ed-sub'))
    out.append(_txt(70,445, '可比期：'+str(l['document'].get('comparative_period_key','上期'))+' / '+str(l['document'].get('period_key','本期'))+'；收入作分母；简化 FCF=CFO−现金资本开支。','ed-caption'))
    return f'<svg class="editorial-flow" viewBox="0 0 1410 477" xmlns="http://www.w3.org/2000/svg" role="group" aria-label="毛利率经营现金流率与简化自由现金流率上年同期与本期对比">{"".join(out)}</svg>'