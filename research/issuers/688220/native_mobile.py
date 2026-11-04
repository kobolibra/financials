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
    return f"{D(v)/B:,.2f}亿"

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
    labels=txt("01 收入来源（互斥四组）",16,20)+txt("02 成本 "+money(cost)+" · 毛利 "+money(gp),16,250)
    diagram=svg(labels+paths+nodes+sinks,330,265,"2026H1原始金额严格守恒的四类业务收入对各自营业成本和毛利的手机原生图")
    return shell("nonnegative_conserved_source_cost_gp",diagram+details,"营业收入 "+money(revenue)+"＝营业成本 "+money(cost)+"＋毛利润 "+money(gp)+"。曲带真实宽度与原始元金额成正比，极小类别不人为加宽。")

def signed(l,title,start,changes,end):
    start=D(start);end=D(end);cur=start
    rows=[(title,D(0),start,start,"start")]
    for label,delta in changes:
        delta=D(delta);following=cur+delta
        rows.append((label,cur,following,delta,"step"));cur=following
    assert abs(cur-end)<=D("0.01"),("MOBILE_CAS_SIGNED_BRIDGE_ERROR",title,cur,end)
    rows.append(("会计闭合总额",D(0),end,end,"total"))
    low=min([D(0)]+[min(a,b) for _,a,b,_,_ in rows]);high=max([D(0)]+[max(a,b) for _,a,b,_,_ in rows])
    span=max(D(1),high-low);scale=D(296)/span
    pos=lambda x:D(17)+(x-low)*scale
    height=29+len(rows)*64
    code=f'<path d="M{fmt(pos(0))},18 V{height-8}" stroke="#bdcbc3" stroke-dasharray="3 4"/>'
    for i,(label,before,after,delta,kind) in enumerate(rows):
        y=25+i*64;color=INK if kind in ("start","total") else GREEN if delta>=0 else RUST
        startx=pos(min(before,after));width=abs(after-before)*scale
        code+=txt(label,17,y,11)+txt(plus(delta) if kind=="step" else money(after),313,y,11,"end",color,700)
        code+=f'<rect class="native-asr-signed" data-kind="{kind}" data-step="{i}" data-signed-yuan="{delta}" data-cumulative-yuan="{after}" x="{fmt(startx)}" y="{y+10}" width="{fmt(width)}" height="15" fill="{color}"/>'
        code+=txt("累计 "+money(after),313,y+47,10,"end",GREY,500)
    return shell("signed_cumulative_finance",svg(code,330,height,title+"：原始元金额带符号累计瀑布"),"每一步共用同一人民币元比例轴；绿色增加、铜色减少，负现金也不伪装为正流。")

def compare(l,title,entries,periods):
    vals=[abs(v(l,key)) for _,a,b in entries for key in (a,b)]
    maxnum=max(vals+[D(1)])
    scale=D(295)/maxnum
    y=10;code=""
    for label,one,two in entries:
        code+=txt(label,16,y+14,12)
        for idx,(k,p,color) in enumerate(((one,periods[0],GREY),(two,periods[1],GREEN))):
            value=v(l,k);dy=y+22+idx*32
            code+=txt(p+" "+money(value),16,dy+12,11)
            code+=f'<rect class="native-asr-comparable" data-exact-yuan="{value}" data-source-field="{k}" x="16" y="{dy+18}" width="{fmt(abs(value)*scale)}" height="10" fill="{color}"/>'
        y+=100
    return shell("two_date_stock_comparison",svg(code,330,y+14,title+"；独立日期与相同货币比例尺"),"两期为 2025 年末和 2026 年六月末的资产负债表存量，并非半年期间的经营现金收支。")

def segment(l):
    pairs=[(q["label"],v(l,q["rev"]),v(l,q["cost"])) for q in l["segments"]]
    maximum=max([x-y for _,x,y in pairs]+[D(1)])
    code=""
    for i,(name,rev,cost) in enumerate(pairs):
        gp=rev-cost;y=23+i*62
        code+=txt(name,16,y,12)+txt(money(gp)+" · "+f"{gp/rev*100:.1f}%",314,y,10,"end")
        code+=f'<rect class="native-asr-gp" data-gp-yuan="{gp}" x="16" y="{y+12}" width="{fmt(gp/maximum*D(298))}" height="18" fill="{[GREEN,BLUE,COPPER,GREY][i]}"/>'
    return shell("source_gp_contribution_with_rate",svg(code,330,285,"翱捷科技四类业务毛利润原始元比例与不同分母的毛利率"),"“半导体 IP 授权”毛利率接近100%，但分母很小，不应把高毛利率误认为主要集团盈利贡献。")

def balance(l):
    total=max(v(l,"assets"),v(l,"assets_prior"));scale=D(294)/total
    out=""
    for i,(when,a,lkey,e) in enumerate((("2025-12-31","assets_prior","liabilities_prior","equity_prior"),("2026-06-30","assets","liabilities","equity"))):
        a0=v(l,a);liab=v(l,lkey);equity=v(l,e)
        assert a0==liab+equity
        y=26+i*95
        out+=txt(when+" 合并资产 "+money(a0),18,y,12)
        out+=f'<rect data-assets-yuan="{a0}" x="18" y="{y+10}" width="{fmt(a0*scale)}" height="16" fill="#bdcbc4"/>'
        out+=f'<rect data-liabilities-yuan="{liab}" x="18" y="{y+34}" width="{fmt(liab*scale)}" height="17" fill="{COPPER}"/>'
        out+=f'<rect data-equity-yuan="{equity}" x="{fmt(D(18)+liab*scale)}" y="{y+34}" width="{fmt(equity*scale)}" height="17" fill="{GREEN}"/>'
        out+=txt("负债 "+money(liab)+" · 权益 "+money(equity),18,y+75,11)
    return shell("same_date_balanced_stock",svg(out,330,220,"两个时点资产=负债+所有者权益且人民币元比例一致"),"资产＝负债＋总权益为同一日期的存量恒等式；不是“资产现金流入负债”。")

def make(l):
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
       "segment":segment(l),
       "gp":signed(l,"上年同期毛利润",prior,[("营业收入变化",f("rev")-f("rev_prior")),("减：营业成本变化",f("cogs_prior")-f("cogs"))],gp),
       "pnl":signed(l,"2026H1 合并毛利润",gp,[("研发费用",-f("rnd_expense")),("其他期间费用及税金",-(op_exp-f("rnd_expense"))),("其他经营损益净额",extra),("营业外收支净额",f("nonoperating_income")-f("nonoperating_expense")),("所得税影响",-f("income_tax_expense"))],f("consolidated_net_profit")),
       "earnings":signed(l,"扣非归母净利润",f("deducted_parent_ni"),[("非经常项目（归母税后）",f("nonrec_parent_net"))],f("parent_ni")),
       "cfo":signed(l,"合并净利润",f("consolidated_net_profit"),[("前13项附注调整（逐项留在下方表格）",other),("存货调整",c(13)),("经营性应收调整",c(14)),("经营性应付调整",c(15)),("其他调整",c(16))],f("cash_cfo")),
       "cash":signed(l,"期初现金及等价物",f("cash_start"),[("经营现金流",f("cash_cfo")),("投资现金流",f("cash_cfi")),("筹资现金流",f("cash_cff")),("汇率对现金影响",f("cash_fx"))],f("cash_end")),
       "balance":balance(l),
       "capital":compare(l,"营运资产与合同负债两日期比较",[
         ("存货净额","inventory_net_prior","inventory_net"),
         ("应收账款净额","ar_prior","ar"),
         ("预付款项","prepayments_prior","prepayments"),
         ("合同负债","contract_liabilities_prior","contract_liabilities")
       ],("2025-12-31","2026-06-30"))
    }
