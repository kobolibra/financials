"""Source-driven narrow-screen optical financial editorial figures.

This is a *second rendering* of the existing original income/bridge/stock facts,
not a separate ledger, not downloaded media, and never a synthetic balancing
category. Desktop original 1250-unit SVGs remain editable/exportable.
"""
from __future__ import annotations
from decimal import Decimal as D
from html import escape as E

B=D("100000000")
INK="#16383c"
GREEN="#087e69"
RUST="#af745b"
GREY="#9cafaa"
BLUE="#4e879a"

def money(v):
    return f"{v/B:,.2f}亿"

def v(l,key):
    item=l.get("facts",{}).get(key)
    return D(item["amount"]) if item and item.get("amount") is not None else None

def p(l,key):
    item=l.get("facts",{}).get(key)
    return "p."+str(item.get("page")) if item and item.get("page") else "原报告页码待核"

def card(title, subtitle, body, foot=""):
    return ('<div class="native-finance-inner" role="group" aria-label="'+E(title)+'">'
            '<h4>'+E(title)+'</h4><p class="native-finance-dek">'+E(subtitle)+'</p>'
            +body+('<p class="native-finance-foot">'+E(foot)+'</p>' if foot else '')+'</div>')

def flow(l):
    sources=[]
    for g in l.get("segments",[]):
        if g.get("dimension") not in ("product","other_business"):continue
        r=v(l,g["revenue_key"]);c=v(l,g["cost_key"])
        if r is None or c is None:raise ValueError("NATIVE_SOURCE_MISSING "+g["name"])
        gp=r-c
        if min(r,c,gp)<0:raise ValueError("NATIVE_NEGATIVE_MARGIN_CANNOT_SANKEY "+g["name"])
        sources.append((g["name"],g["revenue_key"],r,c,gp,p(l,g["revenue_key"])))
    rev=v(l,"revenue");cogs=v(l,"cogs");gp=v(l,"gross_profit")
    if rev is None or rev<=0 or sum((q[2] for q in sources),D(0))!=rev:
        raise ValueError("NATIVE_SOURCE_EXCLUSIVE_REVENUE_NOT_CLOSED")
    if sum((q[3] for q in sources),D(0))!=cogs or sum((q[4] for q in sources),D(0))!=gp or cogs+gp!=rev:
        raise ValueError("NATIVE_SOURCE_COST_GP_NOT_CLOSED")
    scale=D(302)/rev
    xs=D(14);xc=D(14);xg=D(14)+cogs*scale
    svg=['<svg class="native-money-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 335" role="img" aria-label="逐真实互斥收入来源等金额拆向原披露营业成本与衍生毛利润；带宽由原始人民币元决定">',
         '<text x="14" y="20" fill="'+INK+'" font-size="12" font-weight="700">01 收入来源 · 每条带保持原金额</text>',
         '<text x="14" y="252" fill="'+INK+'" font-size="12" font-weight="700">02 各自成本 / 毛利 → 合并结果</text>']
    rectangles=[];paths=[]
    for i,(name,key,r,c,g,page) in enumerate(sources):
        w=r*scale
        rectangles.append('<rect class="native-money-source" data-source-key="'+E(key)+'" data-exact-yuan="'+str(r)+'" x="'+str(xs)+'" y="49" width="'+str(w)+'" height="16" fill="'+[BLUE,"#ac9bd0",GREY,"#b3a189"][i%4]+'"/>')
        cur=xs
        for amount,target,begin_dest,color in ((c,"cogs",xc,RUST),(g,"gross_profit",xg,GREEN)):
            if amount>0:
                width=amount*scale
                x1=float(cur);x2=float(cur+width);z1=float(begin_dest);z2=float(begin_dest+width)
                d=(f"M{x1:.9f},65 C{x1:.9f},130 {z1:.9f},200 {z1:.9f},276 "
                   f"L{z2:.9f},276 C{z2:.9f},200 {x2:.9f},130 {x2:.9f},65 Z")
                paths.append('<path class="native-money-ribbon" data-source-key="'+E(key)+'" data-target-key="'+target+'" data-exact-yuan="'+str(amount)+'" d="'+d+'" fill="'+color+'" fill-opacity="0.52"><title>'+E(name+" "+target+" "+str(amount)+" 元")+'</title></path>')
                if target=="cogs":xc+=width
                else:xg+=width
                cur+=width
        xs+=w
    svg.extend(paths)
    svg.extend(rectangles)
    svg.append('<rect class="native-money-sink" data-target-key="cogs" data-exact-yuan="'+str(cogs)+'" x="14" y="276" width="'+str(cogs*scale)+'" height="16" fill="'+RUST+'"/>')
    svg.append('<rect class="native-money-sink" data-target-key="gross_profit" data-exact-yuan="'+str(gp)+'" x="'+str(D(14)+cogs*scale)+'" y="276" width="'+str(gp*scale)+'" height="16" fill="'+GREEN+'"/>')
    svg.append('</svg>')
    rows=['<div class="native-money-total"><strong>合并营业收入</strong><b>'+money(rev)+'</b></div>',
          '<div class="native-money-pair"><span>营业成本 <b>'+money(cogs)+'</b></span><span>毛利润 <b>'+money(gp)+'</b></span></div>',
          '<p class="native-finance-dek">各来源自己的原披露成本与推导毛利严格满足收入＝成本＋毛利；只有同一互斥合并口径才进入图形。</p>']
    for name,key,r,c,g,page in sources:
        rows.append('<button type="button" class="native-source-row" data-source-key="'+E(key)+'" aria-pressed="false" aria-label="选择 '+E(name)+' 的真实成本和毛利路径"><span>'+E(name)+' <small>'+page+'</small></span><strong>'+money(r)+'</strong><span>成本 '+money(c)+' · 毛利 '+money(g)+'</span></button>')
    return card("收入如何分成成本与毛利润？","2026H1 · 合并人民币元 · 同比例真实来源→成本／毛利。不能把股权/现金/其他会计维度合并。",''.join(svg+rows),"两端所有真实 SVG 路径宽度按同一原始金额比例生成，微小来源不设最小可见宽度。")

def signed(l, title, subtitle, rows, foot):
    """Same money x-axis, source-true signed cumulative step geometry."""
    if not rows or rows[0][2]!="start":raise ValueError("SIGNED_MOBILE_START_REQUIRED")
    cum=rows[0][1];segments=[(rows[0][0],D(0),cum,cum,"start",rows[0][3])]
    for name,delta,kind,src in rows[1:]:
        if kind=="total":
            if delta!=cum:raise ValueError("SIGNED_MOBILE_SUBTOTAL_DIFFERENCE "+name)
            segments.append((name,D(0),cum,cum,kind,src))
        else:
            old=cum;cum+=delta;segments.append((name,old,cum,delta,kind,src))
    lo=min([D(0)]+[min(a,b) for _,a,b,_,_,_ in segments])
    hi=max([D(0)]+[max(a,b) for _,a,b,_,_,_ in segments])
    if hi==lo:hi=lo+D(1)
    scale=D(298)/(hi-lo)
    x=lambda k:float(D(16)+(k-lo)*scale)
    svg=['<svg class="native-signed-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 '+str(32+len(segments)*68)+'" role="img" aria-label="'+E(title)+'，每行精确人民币元累计，同一线性货币坐标，有符号连贯瀑布">']
    zero=x(D(0))
    svg.append(f'<path d="M{zero:.6f},24 L{zero:.6f},{24+len(segments)*68}" stroke="#c5d3cc" stroke-dasharray="3 5"/>')
    for i,(name,a,b,amt,kind,source) in enumerate(segments):
        y=32+i*68
        shown=amt if kind not in ("start","total") else b
        col=INK if kind in ("start","total") else GREEN if amt>=0 else RUST
        x0=x(min(a,b));w=x(max(a,b))-x0
        svg.append('<g><text x="14" y="'+str(y)+'" font-size="12" fill="'+INK+'" font-weight="600">'+E((name[:17]+"…" if len(name)>18 else name))+'</text>')
        svg.append('<text x="317" y="'+str(y)+'" text-anchor="end" font-size="12" fill="'+col+'" font-weight="700">'+E(("+" if amt>0 and kind=="step" else "")+money(shown))+'</text>')
        svg.append(f'<rect class="native-signed-money" data-step="{i}" data-kind="{kind}" data-signed-yuan="{str(amt)}" data-cumulative-yuan="{str(b)}" x="{x0:.8f}" y="{y+10}" width="{w:.8f}" height="16" fill="{col}"/>')
        svg.append('<text x="317" y="'+str(y+44)+'" text-anchor="end" font-size="10" fill="#637b76">累计 '+E(money(b))+'</text></g>')
    svg.append('</svg>')
    return card(title,subtitle,''.join(svg),foot)

def pnl(l):
    q=lambda k:v(l,k)
    gp=q("gross_profit");cogs=q("cogs");rev=q("revenue")
    extra=-(q("total_operating_costs")-cogs)
    operating_gain=q("operating_profit")-(gp+extra)
    nonop=q("nonop_income")-q("nonop_expense")
    return signed(l,"毛利润怎样成为净利润？","合并利润表；蓝色首尾是会计总额，绿色/铜色为真实正负调整。",[
       ("毛利润",gp,"start",p(l,"gross_profit")),
       ("其余营业总成本",extra,"step",p(l,"total_operating_costs")),
       ("其他经营净损益",operating_gain,"step",p(l,"operating_profit")),
       ("营业利润",q("operating_profit"),"total",p(l,"operating_profit")),
       ("营业外净额",nonop,"step",p(l,"nonop_income")),
       ("所得税",-q("income_tax"),"step",p(l,"income_tax")),
       ("合并净利润",q("net_profit"),"total",p(l,"net_profit"))
    ],"其他经营净损益是从原营业利润反算的*明确命名会计汇总项*，并非虚构业务；明细和原始页在原财报来源表中。")

def delta_gp(l):
    q=lambda k:v(l,k)
    prev=q("revenue_prior")-q("cogs_prior");new=q("gross_profit")
    return signed(l,"毛利润变化来自什么算术关系？","2025H1 → 2026H1；收入与成本变动是会计恒等，不足以证明售价/数量/良率因果。",[
      ("2025H1 毛利润",prev,"start",p(l,"revenue_prior")),
      ("收入的变动",q("revenue")-q("revenue_prior"),"step",p(l,"revenue")),
      ("减：成本变动",q("cogs_prior")-q("cogs"),"step",p(l,"cogs")),
      ("2026H1 毛利润",new,"total",p(l,"gross_profit"))
    ],"只有可比期间/合并口径才能做桥；不是价格×销量贡献。")

def cfo(l):
    q=lambda k:v(l,k)
    wc={};other=D(0);count=0
    for z in l["indirect_cfo_adjustments"]:
        name=z["source_label"];amount=D(z["amount"])
        if "存货减少" in name or "存货的减少" in name:key="存货变化"
        elif "经营性应收" in name:key="经营性应收"
        elif "经营性应付" in name:key="经营性应付"
        else:key=None
        if key:
            if key in wc:raise ValueError("NATIVE_DUPLICATED_CFO_GROUP")
            wc[key]=amount
        else:other+=amount;count+=1
    if set(wc)!={"存货变化","经营性应收","经营性应付"}:raise ValueError("NATIVE_CFO_MISSING_WC")
    return signed(l,"净利润为何没有完全转为现金？","真实净利润 + 原始全部间接调节（其余逐项保留在原报表表格中）→ CFO。",[
       ("合并净利润",q("net_profit"),"start",p(l,"net_profit")),
       (str(count)+"项非营运资本调整",other,"step","原附注"),
       ("存货调整",wc["存货变化"],"step","原附注"),
       ("应收调整",wc["经营性应收"],"step","原附注"),
       ("应付调整",wc["经营性应付"],"step","原附注"),
       ("经营活动现金净额",q("cfo"),"total",p(l,"cfo"))
    ],"不能使用资产负债表存货/应收余额的简单变化替代法定现金流量表间接调节。")

def cash(l):
    q=lambda k:v(l,k)
    return signed(l,"现金及现金等价物怎样变化？","同一现金等价物口径，经营/投资/筹资/汇率带符号结账。",[
       ("期初现金及等价物",q("cash_open"),"start",p(l,"cash_open")),
       ("经营现金流",q("cfo"),"step",p(l,"cfo")),
       ("投资现金流",q("cfi"),"step",p(l,"cfi")),
       ("筹资现金流",q("cff"),"step",p(l,"cff")),
       ("现金汇率影响",q("fx_effect"),"step",p(l,"fx_effect")),
       ("期末现金及等价物",q("cash_close"),"total",p(l,"cash_close"))
    ],"现金等价物不等于资产负债表货币资金，受限资金及其他币种损益不得混用。")

def fcf(l):
    q=lambda k:v(l,k)
    return signed(l,"经营现金扣除现金资本开支剩多少？","简化 FCF = CFO − 原报告实际购建长期资产支付的现金。",[
        ("经营现金流",q("cfo"),"start",p(l,"cfo")),
        ("现金购建长期资产",-q("capex_cash"),"step",p(l,"capex_cash")),
        ("简化现金 FCF",q("cfo")-q("capex_cash"),"total",p(l,"cfo"))
    ],"仅为指定现金指标，不等同可分配现金；不用固定资产账面变动推导现金资本开支。")

def paired(l,title,pairs,note,percent=False):
    parts=[]
    for label,prior,now,source in pairs:
        if prior is None or now is None:continue
        top=max(abs(prior),abs(now),D("0.00001"))
        for period,value,color in (("2025H1" if percent else "2025-12-31",prior,GREY),("2026H1" if percent else "2026-06-30",now,GREEN)):
            width=max(D(0),abs(value)/top*D(100))
            if percent:
                formatted=f"{value:.2f}%"
            else:formatted=money(value)
            parts.append('<div class="native-pair-row"><span>'+E(label)+' <small>'+period+'</small></span><strong>'+formatted+'</strong><div class="native-pair-track"><i style="width:'+str(width)+'%;background:'+color+'"></i></div></div>')
    return card(title,note,''.join(parts),"每对数据独立标定零起点；不把不同金额/百分比类别的图条作为同一绝对尺度对比。")

def margin(l):
    q=lambda k:v(l,k)
    a=q("revenue_prior");b=q("revenue")
    if not a or not b:return card("盈利率比较","可比期间缺失",'<p>NOT_CHECKED</p>')
    pairs=[("毛利率",((q("revenue_prior")-q("cogs_prior"))/a*100),(q("gross_profit")/b*100),"gross")]
    if q("cfo_prior") is not None:pairs.append(("经营现金流/收入",q("cfo_prior")/a*100,q("cfo")/b*100,"cfo"))
    if q("capex_cash_prior") is not None and q("cfo_prior") is not None:
        pairs.append(("简化现金FCF/收入",(q("cfo_prior")-q("capex_cash_prior"))/a*100,(q("cfo")-q("capex_cash"))/b*100,"fcf"))
    return paired(l,"毛利率与现金率：不同指标不能混成利润率",pairs,"两个半年同期，数值使用百分比；不是8–12季度趋势。",True)

def volume(l):
    q=lambda k:v(l,k)
    keys=["revenue_optics","product_revenue_prior","product_volume_wan","product_volume_wan_prior"]
    if any(q(k) is None for k in keys):return ""
    r0=q("product_revenue_prior");r1=q("revenue_optics")
    n0=q("product_volume_wan_prior");n1=q("product_volume_wan")
    if min(r0,r1,n0,n1)<=0:return ""
    metrics=[("产品收入(亿元)",r0/B,r1/B),("销量(万只)",n0,n1),("平均收入/只(元)",r0/n0/D(10000),r1/n1/D(10000))]
    items=[]
    for name,a,b in metrics:
        maximum=max(a,b,D("0.0001"))
        items.append('<div class="native-metric-pair"><strong>'+E(name)+'</strong><div>2025H1 '+f"{a:,.2f}"+'</div><i style="width:'+str(a/maximum*100)+'%;background:'+GREY+'"></i><div>2026H1 '+f"{b:,.2f}"+'</div><i style="width:'+str(b/maximum*100)+'%;background:'+GREEN+'"></i></div>')
    return card("产品收入、销量、混合单位收入","三个面板各自零基准；单位收入仅为不同产品组合的总体均值。",''.join(items),"不得将总体收入÷不同型号总销量解释为固定规格产品价格或价格上涨因果。")

def balance(l):
    q=lambda k:v(l,k)
    total=q("assets");liab=q("liabilities");equity=q("equity")
    if total!=liab+equity:raise ValueError("NATIVE_BALANCE_NOT_CLOSED")
    w1=liab/total*D(100);w2=equity/total*D(100)
    html='<div class="native-money-total"><strong>2026-06-30 合并总资产</strong><b>'+money(total)+'</b></div>'
    html+='<div class="native-stock-track"><i style="width:'+str(w1)+'%;background:'+RUST+'"></i><i style="width:'+str(w2)+'%;background:'+GREEN+'"></i></div>'
    html+='<div class="native-money-pair"><span>负债 '+money(liab)+'</span><span>权益 '+money(equity)+'</span></div>'
    return card("同日资产如何由负债和权益支撑？","资产＝负债＋所有者权益，是存量恒等式，不是现金转移。",html,"不得混入不同日期或经营现金流期间。")

def working_capital(l):
    pairs=[]
    for label,prior,current in (("存货","inventory_prior","inventory"),("应收净额","accounts_receivable_prior","accounts_receivable"),("预付款项","prepayment_prior","prepayment")):
        a=v(l,prior);b=v(l,current)
        if a is not None and b is not None:pairs.append((label,a,b,p(l,current)))
    return paired(l,"期初至六月末的营运资产存量比较",pairs,"2025-12-31 vs 2026-06-30；这不是半年同比，也不是CFO间接现金调整。")

def make(l):
    required=("revenue","cogs","gross_profit","assets","liabilities","equity","cfo","net_profit")
    if any(v(l,k) is None for k in required):raise ValueError("NATIVE_INCOMPLETE_FINANCIAL_LEDGER")
    panels={"01":flow(l),"03":pnl(l),"04":delta_gp(l),"05":margin(l),"06":cfo(l),"07":cash(l),"08":fcf(l),"09":balance(l),"10":working_capital(l)}
    vol=volume(l)
    if vol:panels["02"]=vol
    return panels
