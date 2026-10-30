#!/usr/bin/env python3
"""Evidence-first financial visual publication engine — industrial statements.

No company names, reporting periods or hard-coded source pages are allowed in
this engine. Invalid accounting relationships fail closed. Figures 1-7 are
not generated unless applicable source values exist.
"""
from __future__ import annotations
import argparse, html, hashlib, json, math, re
from pathlib import Path
from decimal import Decimal as D
from collections import defaultdict

def esc(x): return html.escape(str(x),quote=True)
def num(l,k):
    f=l.get('facts',{}).get(k)
    return None if f is None or f.get('amount') is None else D(str(f['amount']))
def y(x): return f'{x/D(100000000):,.2f}'
def sign(x): return ('+' if x>=0 else '−')+y(abs(x))
def pc(x): return f'{x*D(100):,.1f}%'
def pp(x): return f'{x*D(100):+.1f}pp'
def page(l,k):
    f=l.get('facts',{}).get(k)
    return ('p.'+str(f['page'])) if f and f.get('page') else '页码待核'
def factmeta(l,*keys):return ' / '.join(dict.fromkeys(page(l,k) for k in keys))
def dot(v): return float(v/D(100000000))
def n(v):return f'{v:,.2f}'
def tag(txt,color='neutral'):return f'<span class="pill {color}">{esc(txt)}</span>'
def tooltip(s):return f'data-tip="{esc(s)}" tabindex="0"'
def money(v):return y(v)+' 亿'
def add(terms):return sum(terms,D('0'))
def ribbon(x1,y1,x2,y2,h,c,tip,group):
    if h<0:raise ValueError('Negative Sankey width')
    if h<0.15:return ''
    c1=x1+(x2-x1)*.4;c2=x1+(x2-x1)*.6
    d=f'M {x1:.2f} {y1:.2f} C {c1:.2f} {y1:.2f} {c2:.2f} {y2:.2f} {x2:.2f} {y2:.2f} L {x2:.2f} {y2+h:.2f} C {c2:.2f} {y2+h:.2f} {c1:.2f} {y1+h:.2f} {x1:.2f} {y1+h:.2f} Z'
    return f'<path class="money-ribbon" d="{d}" fill="{c}" data-group="{group}" {tooltip(tip)} role="img" aria-label="{esc(tip)}"><title>{esc(tip)}</title></path>'

def moneyflow(l):
    """Conserved product→revenue→COGS/GP→operating core/spending.

    Net positive signed operating and non-operating items go in the separate
    adjacent signed profit bridge; never masquerade as revenue flows.
    """
    rev,cogs=num(l,'revenue'),num(l,'cogs')
    otc=num(l,'total_operating_costs')
    if rev is None or cogs is None or otc is None or rev<=0 or cogs<0 or otc<cogs or otc>rev:
        return '<div class="no-data">缺少可靠的收入/成本口径：不生成财务流带图。</div>',0
    gp=rev-cogs;opex=otc-cogs;core=gp-opex
    if core<0: return '<div class="no-data">经营盈余为负，本期不适合绘制正值连续流带，改用带符号利润桥。</div>',0
    groups=[]
    for g in l.get('segments',[]):
        if g.get('dimension')!='product' or not g.get('cost_key'):continue
        rv,cv=num(l,g['revenue_key']),num(l,g['cost_key'])
        if rv is None or cv is None or rv<0 or cv<0 or rv<cv:raise ValueError('Invalid product revenue/cost')
        if not rv: continue
        groups.append({'name':g['name'],'r':rv,'c':cv,'gp':rv-cv,'p':factmeta(l,g['revenue_key'],g['cost_key']),'derived':False})
    if not groups:return '<div class="no-data">分部收入与成本不足，改用真实可用的比较图。</div>',0
    diff_rev=rev-add(g['r'] for g in groups);diff_cost=cogs-add(g['c'] for g in groups)
    if diff_rev<0 or diff_cost<0 or diff_cost>diff_rev:raise ValueError('Product totals do not reconcile')
    if diff_rev:
        groups.append({'name':'未列示差额（计算）','r':diff_rev,'c':diff_cost,'gp':diff_rev-diff_cost,'p':factmeta(l,'revenue','cogs'),'derived':True})
    scale=285/dot(rev);start=126; rev_y=120; gp_y=125;cost_y=gp_y+dot(gp)*scale+54
    group_gaps=27;out=[];labels=[];colors=['#6ca8c4','#a19ad1','#b0b5ac','#b1b7c6','#73978d']
    # stage 1: all product revenue to consolidated revenue
    cur_src=start;cur_dest=rev_y;maxend=0
    for i,g in enumerate(groups):
        h=dot(g['r'])*scale;color=colors[i%len(colors)]
        out.append(ribbon(240,cur_src,465,cur_dest,h,color+'C5',f"{g['name']}｜收入 {money(g['r'])}｜{g['p']}" ,f's{i}'))
        labels.append(f'<text x="226" y="{cur_src+max(12,h/2-8):.1f}" text-anchor="end" class="svg-name">{esc(g["name"][:14])}</text><text x="226" y="{cur_src+max(26,h/2+12):.1f}" text-anchor="end" class="svg-value">{y(g["r"])} 亿</text>')
        cur_src+=h+group_gaps;cur_dest+=h;maxend=max(maxend,cur_src)
    # stage 2: consolidated revenue to COGS and GP
    rheight=dot(rev)*scale;gh=dot(gp)*scale;ch=dot(cogs)*scale
    out.append(ribbon(483,rev_y,702,gp_y,gh,'#83c4a5CF',f'合并收入进入毛利润｜{money(gp)}｜{factmeta(l,"revenue","cogs")}', 'gp'))
    out.append(ribbon(483,rev_y+gh,702,cost_y,ch,'#ce7a70BA',f'营业成本｜{money(cogs)}｜{page(l,"cogs")}', 'cost'))
    # stage 3: GP allocated to net operating surplus before other operating income and operating expense / taxes.
    x2=973; core_y=131;opex_y=core_y+dot(core)*scale+60
    out.append(ribbon(720,gp_y,x2,core_y,dot(core)*scale,'#0c9273B8',f'营业毛利润－营业总成本中不含营业成本的部分，经营盈余（尚未考虑其他经营净收益）｜{money(core)}｜{factmeta(l,"revenue","total_operating_costs")}', 'core'))
    out.append(ribbon(720,gp_y+dot(core)*scale,x2,opex_y,dot(opex)*scale,'#d1a16eB8',f'营业总成本中非营业成本部分｜{money(opex)}｜{page(l,"total_operating_costs")}', 'opex'))
    def node(x,yy,h,col):return f'<rect x="{x}" y="{yy:.2f}" width="17" height="{max(h,2):.2f}" rx="2" fill="{col}"/>'
    nodes=[node(465,rev_y,rheight,'#445e6c'),node(702,gp_y,gh,'#0b936f'),node(702,cost_y,ch,'#c77769'),node(x2,core_y,dot(core)*scale,'#0c8d75'),node(x2,opex_y,dot(opex)*scale,'#bf9375')]
    labels += [f'<text x="503" y="{rev_y+34}" class="svg-label">合并收入</text><text x="503" y="{rev_y+56}" class="svg-value">{y(rev)} 亿</text>', f'<text x="731" y="{gp_y+28}" class="svg-label">毛利润</text><text x="731" y="{gp_y+50}" class="svg-value">{y(gp)} 亿</text>', f'<text x="731" y="{cost_y+25}" class="svg-label">营业成本</text><text x="731" y="{cost_y+47}" class="svg-value">{y(cogs)} 亿</text>', f'<text x="1002" y="{core_y+26}" class="svg-label">经营盈余*</text><text x="1002" y="{core_y+50}" class="svg-value">{y(core)} 亿</text>', f'<text x="1002" y="{opex_y+24}" class="svg-label">其他营业总成本</text><text x="1002" y="{opex_y+45}" class="svg-value">{y(opex)} 亿</text>']
    height=max(555, math.ceil(max(maxend,opex_y+dot(opex)*scale,cost_y+ch)+65))
    svg=f'<svg class="hero-svg" role="group" aria-label="产品收入经合并收入分解为营业成本、毛利润，毛利润进一步分解为经营盈余和其余营业总成本；所有流带与金额保持一致" viewBox="0 0 1250 {height}" xmlns="http://www.w3.org/2000/svg"><text x="33" y="61" class="svg-kicker">01 / PRODUCT MIX</text><text x="465" y="61" class="svg-kicker">02 / CONSOLIDATED</text><text x="702" y="61" class="svg-kicker">03 / GROSS PROFIT</text><text x="973" y="61" class="svg-kicker">04 / OPERATING CORE</text>{"".join(out+nodes+labels)}</svg>'
    return svg,len(groups)*1+4

def waterfall(l,series,title,units='亿元',maximum=None):
    """Correct signed bridge. Items [label, signed yuan, page, kind=start|step|total]."""
    # Derive coordinates from values; zero and negative levels supported
    levels=[];cur=D('0');all_heights=[D('0')]
    for label,amount,p,kind in series:
        if kind=='start':cur=amount;before=D('0');after=cur
        elif kind=='total':before=D('0');after=amount;cur=amount
        else:before=cur;cur+=amount;after=cur
        levels.append((before,after));all_heights.extend([before,after])
    hi=max(all_heights);lo=min(all_heights)
    span=hi-lo if hi!=lo else D(1)
    top,bottom=75,355;scale=(bottom-top)/dot(span);zero=top+dot(hi)*scale
    pad,left,plotw=84,60,1110;gap=plotw/(len(series)+0.3);w=min(72,gap*0.58)
    chunks=[f'<svg class="waterfall" role="img" aria-label="{esc(title)}，各步骤正负号按会计金额绘制" viewBox="0 0 1220 445" xmlns="http://www.w3.org/2000/svg">', f'<line x1="40" y1="{zero:.1f}" x2="1160" y2="{zero:.1f}" stroke="#a4afa7" stroke-width="1.4" stroke-dasharray="5 6"/>']
    for i,((label,value,p,kind),(before,after)) in enumerate(zip(series,levels)):
        center=left+i*gap+w/2;x=center-w/2
        if kind in ('start','total'): y1=top+dot(hi-max(D(0),after))*scale; y2=top+dot(hi-min(D(0),after))*scale;color='#163e49' if kind=='start' else '#0e8e70'
        else:y1=top+dot(hi-max(before,after))*scale;y2=top+dot(hi-min(before,after))*scale;color='#0e9072' if value>=0 else '#d0766b'
        height=max(2, y2-y1)
        detail=f'{label}｜{(sign(value) if kind=="step" else y(value))} 亿｜{p or "来源页未提供"}'
        chunks.append(f'<rect x="{x:.2f}" y="{y1:.2f}" width="{w:.2f}" height="{height:.2f}" rx="3" fill="{color}" {tooltip(detail)} role="img" aria-label="{esc(detail)}"/>')
        # label top, first row top 45 second bottom x wrap via SVG tspans? use 2-lines with split label
        short=(label[:7]+'…') if len(label)>8 else label
        ylab=403
        chunks.append(f'<text x="{center:.1f}" y="{ylab}" text-anchor="middle" class="svg-step-label">{esc(short)}</text>')
        shown=sign(value) if kind=='step' else y(value)
        ty=max(39,y1-9) if kind=='step' else max(39,y1-9)
        chunks.append(f'<text x="{center:.1f}" y="{ty:.1f}" text-anchor="middle" class="svg-step-value">{shown}</text>')
        if i<len(series)-1 and kind!='total':
            nxtx=left+(i+1)*gap
            connect=top+dot(hi-after)*scale
            chunks.append(f'<line x1="{x+w:.1f}" y1="{connect:.1f}" x2="{nxtx:.1f}" y2="{connect:.1f}" stroke="#9baba3" stroke-width="1.2" stroke-dasharray="3 4"/>')
    chunks.append('</svg>')
    return ''.join(chunks)

def cmpbars(l, pairs):
    # pairs of (label,prior,current,source). Draw paired proportional horizontal bars with same cross-metric common width.
    values=[abs(v) for _,a,b,_ in pairs for v in (a,b) if v is not None]; mx=max(values) if values else D(0)
    rows=[]
    for label,a,b,source in pairs:
        aa='—' if a is None else y(a)+' 亿';bb='—' if b is None else y(b)+' 亿'
        oldw=0 if a is None or not mx else float(abs(a)/mx*100);neww=0 if b is None or not mx else float(abs(b)/mx*100)
        rows.append(f'<div class="pair" data-source="{esc(source)}"><div class="pair-label"><b>{esc(label)}</b><span>{esc(source)}</span></div><div class="pair-line"><small>上年同期</small><div class="pair-track"><i style="width:{oldw:.2f}%;background:#9ab4b6"></i></div><em>{aa}</em></div><div class="pair-line"><small>本期</small><div class="pair-track"><i style="width:{neww:.2f}%;background:#078c70"></i></div><em>{bb}</em></div></div>')
    return ''.join(rows)

def stockbars(l, pairs):
    allv=[a for _,a,b,_ in pairs if a is not None]+[b for _,a,b,_ in pairs if b is not None];mx=max(allv) if allv else D(0)
    rows=[]
    for label,old,new,source in pairs:
        w1=float(old/mx*100) if old is not None and mx else 0;w2=float(new/mx*100) if new is not None and mx else 0
        rows.append(f'<div class="stock-pair"><div class="stock-head"><strong>{esc(label)}</strong><span>{esc(source)}</span></div><div class="stock-line"><small>上年末</small><span class="stock-track"><i style="width:{w1:.1f}%;background:#9caeb2"></i></span><b>{y(old) if old is not None else "—"}</b></div><div class="stock-line"><small>本期末</small><span class="stock-track"><i style="width:{w2:.1f}%;background:#1e947b"></i></span><b>{y(new) if new is not None else "—"}</b></div></div>')
    return ''.join(rows)

def balance(l):
    total=num(l,'assets');cur=num(l,'current_assets');non=num(l,'noncurrent_assets');debt=num(l,'liabilities');eq=num(l,'equity')
    if None in (total,cur,non,debt,eq):return '<p class="no-data">缺少经核实的资产负债项目。</p>'
    if cur+non!=total or debt+eq!=total: raise ValueError('Balance sheet out of balance')
    ca=float(cur/total*100);na=float(non/total*100);le=float(debt/total*100);e=float(eq/total*100)
    return f'''<div class="balance-grid"><div class="balance-side"><div class="balance-caption"><b>ASSETS · 资产</b><strong>{y(total)} 亿</strong></div><div class="balance-stack" role="img" aria-label="流动资产{y(cur)}亿元，非流动资产{y(non)}亿元"><div style="height:{ca:.4f}%;background:#277d91"><span>流动资产<br><b>{y(cur)} 亿</b></span></div><div style="height:{na:.4f}%;background:#80b8bd"><span>非流动资产<br><b>{y(non)} 亿</b></span></div></div></div><div class="balance-equals" aria-hidden="true">=</div><div class="balance-side"><div class="balance-caption"><b>FUNDING · 资金来源</b><strong>{y(total)} 亿</strong></div><div class="balance-stack" role="img" aria-label="股东权益{y(eq)}亿元，负债{y(debt)}亿元"><div style="height:{e:.4f}%;background:#14816c"><span>股东权益<br><b>{y(eq)} 亿</b></span></div><div style="height:{le:.4f}%;background:#bf8276"><span>负债<br><b>{y(debt)} 亿</b></span></div></div></div></div>'''

def piepercent(value,label,detail):
    if value is None:return ''
    val=max(0,min(100,float(value)))
    return f'<div class="donut-detail"><div class="donut" role="img" aria-label="{esc(label)}：{val:.2f}%" style="--part:{val:.2f}%"><div><b>{val:.2f}%</b><small>占对应余额</small></div></div><div><strong>{esc(label)}</strong><p>{esc(detail)}</p></div></div>'

def article(l,m,checks):
    doc=l['document'];issuer=esc(m.get('issuer_short') or doc['issuer']);per=esc(doc['period_key']);f=l['facts']
    rev=num(l,'revenue');cogs=num(l,'cogs');gp=rev-cogs;totcost=num(l,'total_operating_costs');op=num(l,'operating_profit');net=num(l,'net_profit');cfo=num(l,'cfo');capex=num(l,'capex_cash')
    if None in (rev,cogs,totcost,op,net,cfo,capex):raise ValueError('Missing headline P&L or cash figures')
    if any(x.get('status')=='FAIL' for x in checks.get('checks',[])):raise ValueError('Accounting failed')
    a=m.get('sections',{})
    # Strict core P&L bridge: GP -> other operating total cost -> net other operating gains -> OP -> nonop -> tax -> net
    coreexpense=totcost-cogs
    opother=op-(gp-coreexpense)
    nonop=num(l,'nonop_income')-num(l,'nonop_expense');income_tax=num(l,'income_tax')
    pretax=op+nonop
    if pretax-income_tax!=net:raise ValueError('Profit bridge fails to exactly reconcile to net')
    flow,flowcount=moneyflow(l)
    pseries=[('毛利润',gp,factmeta(l,'revenue','cogs'),'start'),('其他营业总成本',-coreexpense,page(l,'total_operating_costs'),'step'),('其他经营净收益',opother,page(l,'operating_profit'),'step'),('营业外收支净额',nonop,factmeta(l,'nonop_income','nonop_expense'),'step'),('所得税',-income_tax,page(l,'income_tax'),'step'),('合并净利润',net,page(l,'net_profit'),'total')]
    profitbridge=waterfall(l,pseries,'毛利润到合并净利润的完整带符号利润桥')
    priorrev,priorcost=num(l,'revenue_prior'),num(l,'cogs_prior')
    priorgp=(priorrev-priorcost) if priorrev is not None and priorcost is not None else None
    if priorgp is not None:
        delta_rev=rev-priorrev;delta_cost=cogs-priorcost
        deltabridge=waterfall(l,[('上期毛利润',priorgp,factmeta(l,'revenue_prior','cogs_prior'),'start'),('收入变化',delta_rev,factmeta(l,'revenue','revenue_prior'),'step'),('成本变化',-delta_cost,factmeta(l,'cogs','cogs_prior'),'step'),('本期毛利润',gp,factmeta(l,'revenue','cogs'),'total')],'毛利润同比变化会计桥')
    else:
        deltabridge='<div class="no-data">同口径上期收入/营业成本缺失：不生成虚构的毛利润同比桥，不显示零增长。</div>'
    # indirect cash adjustment grouped: the only cash working capital lines are those identified by label patterns, preserving exact source amounts.
    adjustments=l.get('indirect_cfo_adjustments') or []; wc={};others=[]
    for item in adjustments:
        label=item['source_label'];amount=D(str(item['amount']))
        found=None
        if '存货减少' in label:found='存货变化'
        elif '经营性应收' in label:found='经营性应收变化'
        elif '经营性应付' in label:found='经营性应付变化'
        if found:
            if found in wc:raise ValueError('Duplicate working capital line')
            wc[found]=amount
        else:others.append(item)
    if len(wc)!=3:raise ValueError('Working capital adjustments incomplete')
    othersum=add(D(x['amount']) for x in others)
    if net+othersum+add(wc.values())!=cfo:raise ValueError('Net income to CFO adjustment fails')
    cashseries=[('合并净利润',net,page(l,'net_profit'),'start'),('其他12项调整净额' if len(others)==12 else f'其他{len(others)}项调整净额',othersum,'明细附注','step'),('存货变化',wc['存货变化'],'CFO间接调节','step'),('经营性应收',wc['经营性应收变化'],'CFO间接调节','step'),('经营性应付',wc['经营性应付变化'],'CFO间接调节','step'),('经营现金流',cfo,page(l,'cfo'),'total')]
    cashbridge=waterfall(l,cashseries,'净利润经过非现金和营运资本调整到经营现金流')
    startcash=num(l,'cash_open');endcash=num(l,'cash_close');cfi=num(l,'cfi');cff=num(l,'cff');fx=num(l,'fx_effect')
    if startcash+cfo+cfi+cff+fx!=endcash:raise ValueError('Cash closing reconciliation fails')
    cashbalance=waterfall(l,[('期初现金',startcash,page(l,'cash_open'),'start'),('经营活动',cfo,page(l,'cfo'),'step'),('投资活动',cfi,page(l,'cfi'),'step'),('筹资活动',cff,page(l,'cff'),'step'),('汇率影响',fx,page(l,'fx_effect'),'step'),('期末现金',endcash,page(l,'cash_close'),'total')],'期初期末现金及现金等价物增减桥')
    riskpairs=[('存货净额',num(l,'inventory_prior'),num(l,'inventory'),factmeta(l,'inventory','inventory_prior')),('原材料净额',num(l,'raw_material_prior'),num(l,'raw_material'),factmeta(l,'raw_material','raw_material_prior')),('应收账款净额',num(l,'accounts_receivable_prior'),num(l,'accounts_receivable'),factmeta(l,'accounts_receivable','accounts_receivable_prior')),('预付款项',num(l,'prepayment_prior'),num(l,'prepayment'),factmeta(l,'prepayment','prepayment_prior'))]
    conc=num(l,'top_five_ar');ar_gross=num(l,'ar_gross'); top_prep=num(l,'top_prepay');prep=num(l,'prepayment')
    # denominator for top-5 AR includes contract assets; if only AR gross is present, cannot recalculate true percentage -> use stated note only if explicit case metadata exists.
    published=m.get('source_notes',{});ar_pct=published.get('top5_ar_percent');prep_pct=published.get('top1_prepay_percent')
    circles=piepercent(ar_pct,'前五名客户的应收与合同资产余额','这不是营业收入的集中度；应收余额口径来自附注。')+piepercent(prep_pct,'第一大预付对象占预付款余额','并非其占全部采购金额的比例。')
    # pair bar common scale 2025H1 / current H1
    groupbars=cmpbars(l,[('营业收入',num(l,'revenue_prior'),rev,factmeta(l,'revenue','revenue_prior')),('营业成本',num(l,'cogs_prior'),cogs,factmeta(l,'cogs','cogs_prior')),('毛利润（计算）',priorgp,gp,'收入－成本'),('经营现金流',num(l,'cfo_prior'),cfo,factmeta(l,'cfo','cfo_prior'))])
    kpis=[('营业收入',money(rev),f'同比 {pc((rev-num(l,"revenue_prior"))/num(l,"revenue_prior"))}' if num(l,'revenue_prior') else '对比数据不足','revenue'),('综合毛利率',pc(gp/rev),f'同比 {pp(gp/rev-priorgp/priorrev)}' if priorgp is not None and priorrev else '同比不可计算','revenue'),('合并净利润',money(net),'合并口径','net_profit'),('经营现金流',money(cfo),f'净利现金转化 {pc(cfo/net)}','cfo')]
    kpihtml=''.join(f'<div class="kpi"><span>{esc(label)}</span><strong>{esc(value)}</strong><small>{esc(delta)}</small></div>' for label,value,delta,_ in kpis)
    forensic=''.join('<div class="forensic-item '+('caution' if x.get('tone')=='caution' else '')+'"><small>'+esc(x.get('label',''))+'</small><strong>'+esc(x.get('metric',''))+'</strong><span>'+esc(x.get('comparison',''))+'</span><p>'+esc(x.get('insight',''))+'</p><em>来源：'+esc(x.get('source',''))+'</em></div>' for x in m.get('forensic_lenses',[]))
    memo_watch=m.get('watchlist',[])
    watch=''.join(f'<div class="watch-card"><small>{i+1:02d} / TESTABLE SIGNAL</small><h3>{esc(x["topic"])}</h3><p>{esc(x["test"])}</p><span>原文 {esc(x.get("page","页码待核"))}</span></div>' for i,x in enumerate(memo_watch))
    support=''.join('<li>'+esc(x)+'</li>' for x in m.get('support',[]))
    counter=''.join('<li>'+esc(x)+'</li>' for x in m.get('counter',[]))
    limits=''.join('<li>'+esc(x)+'</li>' for x in m.get('limits',[]))
    indrows=''.join(f'<tr><td>{esc(x["source_label"])}</td><td class="right {"neg" if D(x["amount"])<0 else "pos"}">{sign(D(x["amount"]))} 亿</td><td>p.{esc(x.get("page","—"))}</td></tr>' for x in adjustments)
    snapshot=''.join(f'<tr><td>{esc(k)}</td><td class="right">{n(D(v["amount"]))} 元</td><td>p.{esc(v.get("page","—"))}</td></tr>' for k,v in f.items() if k in {'revenue','cogs','operating_profit','total_operating_costs','net_profit','cfo','cash_open','cash_close','assets','liabilities','equity','raw_material','top_five_ar','top_prepay'})
    tmpl=Path(__file__).resolve().parents[1]/'template.html'
    pagehtml=tmpl.read_text(encoding='utf-8')
    # No company, report period or source page should exist as a fixed constant in template or script.
    output={
      'company':issuer,'issuer_full':esc(doc['issuer']),'ticker':esc(doc['ticker']), 'period':per,
      'audit_badge':'已审计' if doc['audited'] else '未经审计', 'period_range':esc(doc['period_start']+' — '+doc['period_end']), 'previous_stock_date':esc(doc.get('previous_stock_date','期初')), 'period_end':esc(doc['period_end']),
      'eyebrow':esc(m.get('eyebrow') or doc['ticker']+' / '+doc['period_key']),
      'headline':esc(m.get('headline','公司增长质量研究')),'summary':esc(m.get('summary','')),
      'kpis':kpihtml,'money_flow':flow, 'flow_src':esc(factmeta(l,'revenue','cogs','total_operating_costs')),
      'op_footnote':esc('经营盈余 = 毛利润－营业总成本中除营业成本之外的项目；其他经营净收益另在下方带符号利润桥处理。'),
      'profit_bridge':profitbridge, 'delta_bridge':deltabridge,'profit_s1':esc(factmeta(l,'revenue','total_operating_costs','operating_profit','net_profit')),
      'growth_bars':groupbars,'biz':esc(m.get('business','')),'biz_source':esc(m.get('business_sources','')),
      'growth_explanation':esc(m.get('growth_explanation','')),'growth_counter':esc(m.get('growth_counter','')),
      'cash_bridge':cashbridge, 'cash_full':cashbalance,
      'cash_explanation':esc(m.get('cash_explanation','')),'cash_sources':esc(factmeta(l,'net_profit','cfo','cash_open','cash_close')),
      'cash_adj_table':indrows, 'adj_count':len(adjustments),
      'fcf':money(cfo-capex),'fcf_prior':money(num(l,'cfo_prior')-num(l,'capex_cash_prior')) if None not in (num(l,'cfo_prior'),num(l,'capex_cash_prior')) else '上期未提供',
      'working':stockbars(l,riskpairs),'concentration':circles,'risk_explanation':esc(m.get('risk_explanation','')),
      'balance':balance(l),'capital_explanation':esc(m.get('capital_explanation','')), 'forensic':forensic,
      'support':support,'counter':counter,'watch':watch,'limits':limits,
      'ticker_source':esc(doc['source_sha256']),'ledger_table':snapshot,
      'source_notes':esc(m.get('required_reviewer','')),
      'facts_n':len(f),'flow_n':flowcount,'source_stats':f'{len(adjustments)} 项间接 CFO 调整',
      'status_label':'独立分析 · 原报告数据核验','sources_critical':esc(m.get('source_notes',{}).get('limitations','原报告未提供可验证的销量/价格、同业估值和所有外部行业数据。')),
    }
    # Template keys with special bytes replaced as string for no JS collisions.
    for key,value in output.items(): pagehtml=pagehtml.replace('{{'+key+'}}',str(value))
    unfilled=re.findall(r'{{[a-zA-Z0-9_]+}}',pagehtml)
    if unfilled:raise ValueError('Unfilled template placeholders: '+str(unfilled))
    return pagehtml,{'source_pdf_sha256':doc['source_sha256'],'source_facts':len(f),'indirect_adjustments':len(adjustments),'sankey_groups':len(l.get('segments',[]))+int(rev>add(num(l,g['revenue_key']) for g in l.get('segments',[]) if g.get('dimension')=='product')),'accounting':checks['status'],'output_sha256':hashlib.sha256(pagehtml.encode()).hexdigest(),'html_bytes':len(pagehtml.encode()),'status':'LOCAL_SOURCE_REVIEWED_NEEDS_BROWSER_AND_PUBLIC_HTTP','chart_types':['true_money_flow','signed_profit_waterfall','gross_profit_delta_bridge','same_period_comparison','net_income_to_cfo_bridge','cash_close_bridge','stock_balance_pair','working_capital_compare','concentration_radial']}

def main():
    from audit import audit
    p=argparse.ArgumentParser();p.add_argument('--ledger',required=True);p.add_argument('--memo',required=True);p.add_argument('--out',required=True);p.add_argument('--qa',required=True);p.add_argument('--atlas',action='store_true',help='Include balance-sheet anatomy and two-stage signed cash waterfall')
    a=p.parse_args();l=json.loads(Path(a.ledger).read_text());m=json.loads(Path(a.memo).read_text());doc=l['document']
    if doc.get('business_type') not in ('industrial','manufacturing','services'):
        raise ValueError('Sector-aware fail-closed: financials/property/insurance need different economics')
    qa=audit(l)
    if qa['status']=='BLOCKED':raise ValueError('Accounting audit blocked:'+repr(qa))
    if m.get('review_status')!='ANALYST_REVIEWED':
        raise ValueError('Research memo has not been reviewed. Drafts must not be published without explicit approval')
    result,meta=article(l,m,qa)
    if a.atlas:
        from visual_exhibits import upgrade
        result=upgrade(l,result)
        if not all('id="'+section+'"' in result for section in ('capital-anatomy','cash-architecture')):
            raise ValueError('Missing required atlas financial exhibits')
        meta['chart_types'] += ['balance_anatomy', 'two_tier_signed_cash_bridge']
        meta['output_sha256']=hashlib.sha256(result.encode('utf-8')).hexdigest()
        meta['html_bytes']=len(result.encode('utf-8'))
        meta['atlas']={'assets_reconciled':True,'cfo_reconciled':True,'cash_close_reconciled':True}
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(result,encoding='utf-8')
    Path(a.qa).parent.mkdir(parents=True,exist_ok=True);Path(a.qa).write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'file':str(path),'bytes':meta['html_bytes'],'figures':len(meta['chart_types']),'sha256':meta['output_sha256']},ensure_ascii=False))
if __name__=='__main__':main()