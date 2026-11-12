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

def signed(l, title, subtitle, rows, foot,mobile=True):
    from pathlib import Path
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[4]/'research/shared'))
    from editorial_bridge import render_bridge
    doc=l['document']
    ordered=[(label,value,kind,source) for label,value,kind,source in rows]
    diagram=render_bridge(ordered,title,issuer=doc['ticker'].split('.')[0],
        period=doc['period_key'],pdf_sha256=doc['source_sha256'],mobile=mobile)
    diagram=diagram.replace('<svg ','<svg class="native-signed-svg" ',1)
    return card(title,subtitle,diagram,foot)


def pnl(l,mobile=True):
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
    ],"其他经营净损益是从原营业利润反算的*明确命名会计汇总项*，并非虚构业务；明细和原始页在原财报来源表中。",mobile=mobile)

def delta_gp(l,mobile=True):
    q=lambda k:v(l,k)
    if q("revenue_prior") is None or q("cogs_prior") is None:
        return card("毛利润变化", "缺少可比两期财务数据", '<p>不生成虚构的毛利润同比桥。</p>')
    prev=q("revenue_prior")-q("cogs_prior");new=q("gross_profit")
    return signed(l,"毛利润变化来自什么算术关系？","2025H1 → 2026H1；收入与成本变动是会计恒等，不足以证明售价/数量/良率因果。",[
      ("2025H1 毛利润",prev,"start",p(l,"revenue_prior")),
      ("收入的变动",q("revenue")-q("revenue_prior"),"step",p(l,"revenue")),
      ("减：成本变动",q("cogs_prior")-q("cogs"),"step",p(l,"cogs")),
      ("2026H1 毛利润",new,"total",p(l,"gross_profit"))
    ],"只有可比期间/合并口径才能做桥；不是价格×销量贡献。",mobile=mobile)

def cfo(l,mobile=True):
    adjustments=l.get('indirect_cfo_adjustments',[])
    if not adjustments:raise ValueError('NATIVE_CFO_MISSING_SOURCE_ADJUSTMENTS')
    rows=[('合并净利润',v(l,'net_profit'),'start',p(l,'net_profit'))]
    seen=set()
    for item in adjustments:
        label=item['source_label'];page=item.get('page')
        if type(page) is not int or not 1<=page<=l['document']['pages']:raise ValueError('NATIVE_CFO_SOURCE_PHYSICAL_PAGE_REQUIRED')
        identity=(label,page)
        if identity in seen:raise ValueError('NATIVE_DUPLICATED_CFO_GROUP')
        seen.add(identity)
        rows.append((label,D(item['amount']),'step','p.'+str(page)))
    rows.append(('经营活动现金净额',v(l,'cfo'),'total',p(l,'cfo')))
    return signed(l,'净利润为何没有完全转为现金？','全部原始间接现金调节逐项保留，按同一金额轴累计。',rows,
        '不得用资产负债表余额变化替代真实间接现金调节；所有原始行与页码保留。',mobile=mobile)


def cash(l,mobile=True):
    q=lambda k:v(l,k)
    return signed(l,"现金及现金等价物怎样变化？","同一现金等价物口径，经营/投资/筹资/汇率带符号结账。",[
       ("期初现金及等价物",q("cash_open"),"start",p(l,"cash_open")),
       ("经营现金流",q("cfo"),"step",p(l,"cfo")),
       ("投资现金流",q("cfi"),"step",p(l,"cfi")),
       ("筹资现金流",q("cff"),"step",p(l,"cff")),
       ("现金汇率影响",q("fx_effect"),"step",p(l,"fx_effect")),
       ("期末现金及等价物",q("cash_close"),"total",p(l,"cash_close"))
    ],"现金等价物不等于资产负债表货币资金，受限资金及其他币种损益不得混用。",mobile=mobile)

def fcf(l,mobile=True):
    q=lambda k:v(l,k)
    return signed(l,"经营现金扣除现金资本开支剩多少？","简化 FCF = CFO − 原报告实际购建长期资产支付的现金。",[
        ("经营现金流",q("cfo"),"start",p(l,"cfo")),
        ("现金购建长期资产",-q("capex_cash"),"step",p(l,"capex_cash")),
        ("简化现金 FCF",q("cfo")-q("capex_cash"),"total",p(l,"cfo"))
    ],"仅为指定现金指标，不等同可分配现金；不用固定资产账面变动推导现金资本开支。",mobile=mobile)

def paired(l,title,pairs,note,percent=False,mobile=True):
    from pathlib import Path
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[4]/'research/shared'))
    from editorial_bridge import render_comparison
    doc=l['document']
    periods=(doc['comparative_period_key'],doc['period_key']) if percent else (doc['previous_stock_date'],doc['period_end'])
    valid=[(label,prior,now,source) for label,prior,now,source in pairs if prior is not None and now is not None]
    if not valid:return card(title,note,'<p>缺少可比原始数据，暂不绘图。</p>')
    diagram=render_comparison(valid,title,issuer=doc['ticker'].split('.')[0],periods=periods,
        pdf_sha256=doc['source_sha256'],mobile=mobile,percent=percent)
    return card(title,note,diagram,'每项独立零基准；负值保留方向，不把不同指标的条长比较。')


def margin(l,mobile=True):
    q=lambda k:v(l,k)
    a=q("revenue_prior");b=q("revenue")
    if not a or not b:return card("盈利率比较","可比期间缺失",'<p>尚未核验</p>')
    pairs=[("毛利率",((q("revenue_prior")-q("cogs_prior"))/a*100),(q("gross_profit")/b*100),"gross")]
    if q("cfo_prior") is not None:pairs.append(("经营现金流/收入",q("cfo_prior")/a*100,q("cfo")/b*100,"cfo"))
    if q("capex_cash_prior") is not None and q("cfo_prior") is not None:
        pairs.append(("简化现金FCF/收入",(q("cfo_prior")-q("capex_cash_prior"))/a*100,(q("cfo")-q("capex_cash"))/b*100,"fcf"))
    return paired(l,"毛利率与现金率：不同指标不能混成利润率",pairs,"两个半年同期，数值使用百分比；不是8–12季度趋势。",True,mobile=mobile)

def volume(l,mobile=True):
    q=lambda k:v(l,k)
    keys=["revenue_optics","product_revenue_prior","product_volume_wan","product_volume_wan_prior"]
    if any(q(k) is None for k in keys):return ""
    r0=q("product_revenue_prior");r1=q("revenue_optics")
    n0=q("product_volume_wan_prior");n1=q("product_volume_wan")
    if min(r0,r1,n0,n1)<=0:return ""
    from pathlib import Path
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[4]/'research/shared'))
    from editorial_bridge import render_comparison
    doc=l['document']
    metrics=[('产品收入',r0/B,r1/B,p(l,'revenue_optics'),'亿元'),
             ('产品销量',n0,n1,p(l,'product_volume_wan'),'万只'),
             ('混合单位收入',r0/n0/D(10000),r1/n1/D(10000),p(l,'product_volume_wan'),'元/只')]
    diagram=render_comparison(metrics,'产品收入、销量与混合单位收入',issuer=doc['ticker'].split('.')[0],
        periods=(doc['comparative_period_key'],doc['period_key']),pdf_sha256=doc['source_sha256'],mobile=mobile)
    return card('产品收入、销量、混合单位收入','三个指标分别标明单位，各自零基准。',diagram,'混合单位收入不是固定规格产品售价；不得据此识别价格变化因果。')


def balance(l,mobile=True):
    from pathlib import Path
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[4]/'research/shared'))
    from editorial_bridge import render_balance,render_components,combine_panels
    doc=l['document']
    common=dict(issuer=doc['ticker'].split('.')[0],pdf_sha256=doc['source_sha256'],mobile=mobile)
    identity=render_balance([(doc['period_end'],v(l,'assets'),v(l,'liabilities'),v(l,'equity'),p(l,'assets'))],
        '资产与负债权益同日相等',**common)
    pieces=[]
    for name,key in [('货币资金，不等于现金等价物','monetary_funds'),('应收账款净额','accounts_receivable'),('存货净额','inventory'),('预付款项','prepayment')]:
        amount=v(l,key)
        if amount is not None:pieces.append((name,amount,p(l,key)))
    residual=v(l,'current_assets')-sum((r[1] for r in pieces),D(0))
    if residual<0:raise ValueError('SOURCE_ASSET_COMPONENTS_OVERLAP')
    pieces.extend([('其他流动资产，计算差额',residual,p(l,'current_assets')),('非流动资产',v(l,'noncurrent_assets'),p(l,'noncurrent_assets'))])
    detail=render_components(pieces,v(l,'assets'),'完整资产结构，不是现金流向',period=doc['period_end'],**common)
    return card('同日资产如何由负债和权益支撑？','同日存量恒等式；各类资产及资金结构分别绘制。',combine_panels([identity,detail],'资产结构与同日资金来源'),'货币资金与现金等价物、资产存量与期间现金流必须区分。')


def working_capital(l,mobile=True):
    pairs=[]
    for label,prior,current in (("原材料","raw_material_prior","raw_material"),("存货","inventory_prior","inventory"),("应收净额","accounts_receivable_prior","accounts_receivable"),("预付款项","prepayment_prior","prepayment")):
        a=v(l,prior);b=v(l,current)
        if a is not None and b is not None:pairs.append((label,a,b,p(l,current)))
    return paired(l,"期初至六月末的营运资产存量比较",pairs,"2025-12-31 vs 2026-06-30；这不是半年同比，也不是CFO间接现金调整。",mobile=mobile)

def make(l,mobile=True):
    required=("revenue","cogs","gross_profit","assets","liabilities","equity","cfo","net_profit")
    if any(v(l,k) is None for k in required):raise ValueError("NATIVE_INCOMPLETE_FINANCIAL_LEDGER")
    panels={"01":flow(l),"03":pnl(l,mobile=mobile),"04":delta_gp(l,mobile=mobile),"05":margin(l,mobile=mobile),"06":cfo(l,mobile=mobile),"07":cash(l,mobile=mobile),"08":fcf(l,mobile=mobile),"09":balance(l,mobile=mobile),"10":working_capital(l,mobile=mobile)}
    vol=volume(l,mobile=mobile)
    if vol:panels["02"]=vol
    return panels
