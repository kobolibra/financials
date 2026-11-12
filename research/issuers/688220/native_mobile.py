#!/usr/bin/env python3
"""Source-driven original 688220 narrow-screen financial chart grammar.

This file is an issuer adapter, not a generic chart factory: H1 original
business types, full CAS signed P&L and 17-part indirect CFO determine panels.
No source revenue groups are invented or enlarged. Exportable desktop art and
all original source tables remain untouched. Every original-money SVG element
is constructed at Decimal precision.
"""
from __future__ import annotations
from decimal import Decimal as D
from html import escape as E

B=D("100000000")
GREEN="#087b65"
COPPER="#b27352"
RUST="#a84f40"
INK="#17373b"
GREY="#a6bab1"
BLUE="#447489"

def money(v):
    n=D(v)
    if n==0:
        return "0元"
    if abs(n)<D("10000"):
        return f"{n:,.2f}元"
    if abs(n)<D("10000000"):
        return f"{n/D(10000):,.2f}万"
    return f"{n/B:,.2f}亿"

def plus(v):
    return ("+" if D(v)>0 else "")+money(v)

def fmt(x):
    return format(D(x),".9f")

def txt(text,x,y,size=11,anchor=None,color=INK,weight=600):
    return f'<text x="{fmt(x)}" y="{fmt(y)}" font-size="{size}" fill="{color}" font-weight="{weight}"'+(f' text-anchor="{anchor}"' if anchor else "")+'>'+E(str(text))+'</text>'

def svg(markup,width,height,label):
    return f'<svg class="native-asr-original" xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{E(label)}">'+markup+"</svg>"

def shell(info,diagram,prose=""):
    return '<div class="native-asr" data-finance-grammar="'+E(info)+'"><p class="native-asr-dek">'+E(prose)+'</p>'+diagram+'</div>'

def v(l,k):
    return D(l["facts"][k]["yuan"])

def flow(l):
    groups=l["segments"]
    revenue=v(l,"rev");cost=v(l,"cogs");gp=revenue-cost
    assert revenue>0 and sum((v(l,q["rev"]) for q in groups),D(0))==revenue
    assert sum((v(l,q["cost"]) for q in groups),D(0))==cost
    scale=D(298)/revenue
    source_left=D(16);cost_left=D(16);profit_left=D(16)+cost*scale
    paths="";nodes="";details=""
    for i,g in enumerate(groups):
        r=v(l,g["rev"]);c=v(l,g["cost"]);p=r-c
        assert 0<=c<=r,("NO_NEGATIVE_SANKK",g["label"])
        w=r*scale
        nodes+=f'<rect class="native-asr-source" data-source-key="{E(g["rev"])}" data-exact-yuan="{r}" x="{fmt(source_left)}" y="42" width="{fmt(w)}" height="16" fill="{[BLUE,GREEN,COPPER,GREY][i]}"/>'
        cur=source_left
        for value,side,start,col in ((c,"cost",cost_left,COPPER),(p,"gp",profit_left,GREEN)):
            if value>0:
                thick=value*scale;end=cur+thick;finish=start+thick
                d=f"M{fmt(cur)},58 C{fmt(cur)},112 {fmt(start)},158 {fmt(start)},211 L{fmt(finish)},211 C{fmt(finish)},158 {fmt(end)},112 {fmt(end)},58 Z"
                paths+=f'<path class="native-asr-ribbon" data-source-key="{E(g["rev"])}" data-sink="{side}" data-exact-yuan="{value}" data-width="{fmt(thick)}" d="{d}" fill="{col}" fill-opacity=".58"><title>{E(g["label"])} {side} {money(value)}</title></path>'
                if side=="cost":cost_left+=thick
                else:profit_left+=thick
                cur+=thick
        source_left+=w
        details+='<div class="native-asr-detail"><b>'+E(g["label"])+'</b><span>'+money(r)+'</span><small>营业成本 '+money(c)+' · 毛利 '+money(p)+' · 原报告 p.178</small></div>'
    assert abs(cost_left-(D(16)+cost*scale))<D("0.000000001") and abs(profit_left-D(314))<D("0.000000001")
    sinks=f'<rect class="native-asr-sink" data-sink="cost" data-exact-yuan="{cost}" x="16" y="211" width="{fmt(cost*scale)}" height="16" fill="{COPPER}"/>'+f'<rect class="native-asr-sink" data-sink="gp" data-exact-yuan="{gp}" x="{fmt(D(16)+cost*scale)}" y="211" width="{fmt(gp*scale)}" height="16" fill="{GREEN}"/>'
    labels=txt("01 原收入来源（互斥四组）",16,20)+txt("02 成本 "+money(cost)+" · 毛利 "+money(gp),16,247)+txt("铜色：营业成本     绿色：毛利润",16,268,10,color=GREY)
    diagram=svg(labels+paths+nodes+sinks,330,280,"2026H1原始金额严格守恒的四类业务收入对各自营业成本和毛利的手机原生图")
    return shell("nonnegative_conserved_source_cost_gp",diagram+details,"原始元金额严格满足：营业收入＝营业成本＋毛利润。图上四舍五入显示收入 "+money(revenue)+"、成本 "+money(cost)+"、毛利 "+money(gp)+"；小额业务显示万元或元，不能被显示为零。")

def signed(l,title,start,changes,end,mobile=True):
    from editorial_bridge import render_bridge
    source='本图完整原始账本及物理PDF页码附表'
    rows=[(title,D(start),'start',source)]+[(label,D(delta),'step',source) for label,delta in changes]+[('会计闭合总额',D(end),'total',source)]
    diagram=render_bridge(rows,title,issuer=l['issuer']['code'],period=l['issuer']['fiscal_period'],
        pdf_sha256=l['source']['original_bytes_sha256'],mobile=mobile)
    return shell('shared_exact_signed_finance',diagram,'同一人民币元比例尺，合计不重复累加；保留负值与跨零累计。')


def compare(l,title,entries,periods,mobile=True):
    from editorial_bridge import render_comparison
    pairs=[(label,v(l,a),v(l,b),a+' / '+b+'；本图源金额及物理页附表') for label,a,b in entries]
    return shell('shared_two_date_comparison',render_comparison(pairs,title,issuer=l['issuer']['code'],
        periods=periods,pdf_sha256=l['source']['original_bytes_sha256'],mobile=mobile),'两个时点的存量比较，不是期间经营现金收支。')


def segment(l,mobile=True):
    from editorial_bridge import render_components
    parts=[]
    for q in l['segments']:
        revenue,cost=v(l,q['rev']),v(l,q['cost']);gp=revenue-cost
        margin=f'{gp/revenue*100:.1f}%' if revenue else '未定义'
        parts.append((q['label']+' · 自身毛利率 '+margin,gp,q['rev']+' / '+q['cost']+'；本图原始事实及物理页附表'))
    total=sum((x[1] for x in parts),D(0))
    if total==0:return shell('zero_gp_components','<p>各业务毛利均为零，不绘制非零金额比例尺。</p>')
    return shell('shared_gp_components',render_components(parts,total,'各业务毛利贡献与自身毛利率',
        issuer=l['issuer']['code'],period=l['issuer']['fiscal_period'],pdf_sha256=l['source']['original_bytes_sha256'],mobile=mobile),
        '占合计为各业务毛利占集团毛利的比例；自身毛利率以各业务收入为分母，二者不能混同。')


def balance(l,mobile=True):
    from editorial_bridge import render_balance
    dates=[]
    for period,suffix in (('2025-12-31','_prior'),('2026-06-30','')):
        a,liab,e=[k+suffix for k in ('assets','liabilities','equity')]
        dates.append((l['facts'][a]['period'],v(l,a),v(l,liab),v(l,e),'本图资产负债表原始事实及页码附表'))
    return shell('shared_equal_stock_identity',render_balance(dates,'同日资产与负债权益结构',
        issuer=l['issuer']['code'],pdf_sha256=l['source']['original_bytes_sha256'],mobile=mobile),'同一日期资产等于负债加全部权益，不是现金流向。')


def make(l,mobile=True):
    bridge=lambda *args:signed(*args,mobile=mobile)
    f=lambda k:v(l,k)
    prior=f("rev_prior")-f("cogs_prior");gp=f("rev")-f("cogs")
    op_exp=f("rnd_expense")+sum((f(k) for k in ("tax_surcharge","sell","admin","finance_expense")),D(0))
    extra=sum((f(k) for k in ("other_income","investment_income","fair_value_income","credit_impairment","asset_impairment","asset_disposal_gain")),D(0))
    cfo=l["cfo_indirect"]["parts"]
    assert len(cfo)==17
    c=lambda n:D(cfo[n]["yuan"])
    other=sum((c(i) for i in range(13)),D(0))
    return {
       "flow":flow(l),
       "segment":segment(l,mobile=mobile),
       "gp":bridge(l,"上年同期毛利润",prior,[("营业收入变化",f("rev")-f("rev_prior")),("减：营业成本变化",f("cogs_prior")-f("cogs"))],gp),
       "pnl":bridge(l,"2026H1 合并毛利润",gp,[("研发费用",-f("rnd_expense")),("其他期间费用及税金",-(op_exp-f("rnd_expense"))),("其他经营损益净额",extra),("营业外收支净额",f("nonoperating_income")-f("nonoperating_expense")),("所得税影响",-f("income_tax_expense"))],f("consolidated_net_profit")),
       "earnings":bridge(l,"扣非归母净利润",f("deducted_parent_ni"),[("非经常项目（归母税后）",f("nonrec_parent_net"))],f("parent_ni")),
       "cfo":bridge(l,"合并净利润",f("consolidated_net_profit"),[(part["label"],D(part["yuan"])) for part in cfo],f("cash_cfo")),
       "cash":bridge(l,"期初现金及等价物",f("cash_start"),[("经营现金流",f("cash_cfo")),("投资现金流",f("cash_cfi")),("筹资现金流",f("cash_cff")),("汇率对现金影响",f("cash_fx"))],f("cash_end")),
       "balance":balance(l,mobile=mobile),
       "capital":compare(l,"营运资产与合同负债两日期比较",[
         ("存货净额","inventory_net_prior","inventory_net"),
         ("应收账款净额","ar_prior","ar"),
         ("预付款项","prepayments_prior","prepayments"),
         ("合同负债","contract_liabilities_prior","contract_liabilities")
       ],(l["facts"]["inventory_net_prior"]["period"],l["facts"]["inventory_net"]["period"]),mobile=mobile)
    }
