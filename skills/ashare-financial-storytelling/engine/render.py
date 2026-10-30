#!/usr/bin/env python3
"""Cross-issuer evidence-ledger -> self-contained Chinese financial research HTML.

Industry type industrial/services; bank/insurance automatically fail closed. Ledger is
source-reviewed, memo must be human-reviewed to leave DRAFT. Not an autonomous analyst.
"""
from __future__ import annotations
import argparse, json, html, hashlib, math
from pathlib import Path
from decimal import Decimal as D
from audit import audit

def escape(x):return html.escape(str(x),quote=True)
def Y(x):return f'{float(x)/1e8:.2f}'
def pct(x,decimal=1):return f'{float(x):.{decimal}f}%'
def n(x):return f'{float(x):,.2f}'
def num(ledger,key):
    try:return D(ledger['facts'][key]['amount'])
    except (KeyError,ValueError):return None

def svg_sankey(ledger,memo):
    f=ledger['facts'];base=num(ledger,'revenue');cost_total=num(ledger,'cogs')
    if not base or base<=0 or cost_total is None:return '<p class="nochart">分部收入与营业成本资料不足，不能生成真实比例流向图。</p>'
    if ledger['document'].get('business_type') in ('bank','insurance','brokerage'):
        return '<p class="nochart">该行业不适用工业成本桑基图。</p>'
    groups=[]
    for seg in ledger.get('segments',[]):
        if seg.get('dimension')!='product' or not seg.get('cost_key'):continue
        rv=num(ledger,seg['revenue_key']);cv=num(ledger,seg['cost_key'])
        if rv is None or cv is None or rv<cv or cv<0:raise ValueError('Non-conserving or negative product source')
        groups.append((seg['name'],rv,cv,rv-cv,seg['revenue_key'],seg['cost_key'],False))
    if not groups:return '<p class="nochart">未披露可勾稽的产品收入与成本，流向图不适用。</p>'
    rev_left=base-sum((r for _,r,*_ in groups),D(0))
    cost_left=cost_total-sum((c for _,_,c,*_ in groups),D(0))
    if rev_left<D(0) or cost_left<D(0) or cost_left>rev_left:raise ValueError('Unreconciled segment revenue or COGS cannot be Sankeyed')
    if rev_left>0:groups.append(('未分配披露差额（计算）',rev_left,cost_left,rev_left-cost_left,'revenue','cogs',True))
    total_gp=base-cost_total;ratio=355/float(base/D(1e8))
    # All source & destination ribbon heights are common scale: (亿元 × ratio)
    heights=[float(r/D(1e8))*ratio for _,r,*_ in groups]
    start_y=91; src_cursor=start_y; gp_y=91; cost_y=91+float(total_gp/D(1e8))*ratio+43
    names=[];bands=[];colors=['#187d6b','#507f99','#a3a196','#7a8a7d','#867ca2']
    for j,(title,r,c,g,rk,ck,isres) in enumerate(groups):
        src_y=src_cursor;src_cursor+=heights[j]+16
        color=colors[min(j,len(colors)-1)]; gheight=float(g/D(1e8))*ratio;cheight=float(c/D(1e8))*ratio
        gp_tool=f'{title} · 毛利润|{n(g)} 元 · 来源 p22（成本及收入计算）'
        cost_tool=f'{title} · 营业成本|{n(c)} 元 · 来源 p22／p61'
        def ribbon(y1,y2,height,shade,tool,idx):
            x1,x2=360,893
            return f'<path class="ribbon" tabindex="0" role="img" aria-label="{escape(tool.replace("|","；"))}" data-tip="{escape(tool)}" data-group="{idx}" style="fill:{shade}" d="M{x1},{y1:.2f} C550,{y1:.2f} 705,{y2:.2f} {x2},{y2:.2f} L{x2},{y2+height:.2f} C705,{y2+height:.2f} 550,{y1+height:.2f} {x1},{y1+height:.2f} Z"/>'
        bands.append(ribbon(src_y,gp_y,gheight,color+'BD',gp_tool,j))
        bands.append(ribbon(src_y+gheight,cost_y,cheight,'#b57c66AE',cost_tool,j))
        names.append(f'<rect x="331" y="{src_y:.1f}" width="18" height="{heights[j]:.1f}" rx="3" fill="{color}"/><text class="svg-label" x="24" y="{src_y+13:.1f}">{escape(title[:17])}</text><text class="svg-amount" x="24" y="{src_y+40:.1f}">{Y(r)} 亿</text>')
        gp_y+=gheight;cost_y+=cheight
    if abs((gp_y-91)-float(total_gp/D(1e8))*ratio)>0.1 or abs((cost_y-(91+float(total_gp/D(1e8))*ratio+43))-float(cost_total/D(1e8))*ratio)>0.1:raise ValueError('Sankey geometry nonconservation')
    view_h=max(635,math.ceil(src_cursor+52),math.ceil(cost_y+65))
    dest=f'<rect x="905" y="91" width="21" height="{float(total_gp/D(1e8))*ratio:.1f}" rx="4" fill="#18806a"/><rect x="905" y="{91+float(total_gp/D(1e8))*ratio+43:.1f}" width="21" height="{float(cost_total/D(1e8))*ratio:.1f}" rx="4" fill="#bc7965"/><text class="svg-label" x="948" y="114">毛利润</text><text class="svg-amount" x="948" y="146">{Y(total_gp)} 亿</text><text class="svg-label" x="948" y="{91+float(total_gp/D(1e8))*ratio+62:.1f}">营业成本</text><text class="svg-amount" x="948" y="{91+float(total_gp/D(1e8))*ratio+94:.1f}">{Y(cost_total)} 亿</text>'
    return f'<svg class="money-svg" role="group" aria-label="按实际收入金额比例计算的产品营业成本与毛利润桑基流图，数字来自半年报披露" viewBox="0 0 1190 {view_h}"><text class="svg-kicker" x="24" y="52">产品 / 收入</text><text class="svg-kicker" x="946" y="52">分配 / 结果</text>{"".join(bands)}{"".join(names)}{dest}</svg>'

def bar(label,value,maxvalue,color='#177d6b',detail=''):
    w=max(0,min(100,float(value/maxvalue)*100)) if maxvalue else 0
    return f'<div class="compare-row" data-tip="{escape(detail)}" tabindex="0"><div class="bar-line"><span>{escape(label)}</span><strong>{Y(value)} 亿</strong></div><div class="track"><div class="track-fill" style="--w:{w:.3f}%;background:{color}"></div></div></div>'

def cash_adjustments(ledger):
    adj=ledger.get('indirect_cfo_adjustments') or []
    if not adj or num(ledger,'net_profit') is None:return '<p>未披露完整净利润到 CFO 调节表，本图省略。</p>'
    positives=[];negatives=[]
    for i,x in enumerate(adj):
        v=D(x['amount']);(positives if v>=0 else negatives).append((x['source_label'],v,x.get('page')))
    maxval=max(abs(v) for _,v,_ in positives+negatives)
    html_rows=[]
    for sign,section in [('增加现金方向',positives),('减少现金方向',negatives)]:
        html_rows.append(f'<div class="cash-group"><div class="cash-group-head">{escape(sign)}</div>')
        for k,v,p in section:
            w=float(abs(v)/maxval*100)
            color='#23866e' if v>=0 else '#bd7965'
            txt=f'{escape(k)} | {n(v)} 元 · p{p} · CFO 间接调整项'
            html_rows.append(f'<div class="cash-line" tabindex="0" data-tip="{escape(txt)}"><span class="cash-name">{escape(k)}</span><span class="cash-track"><i style="width:{w:.2f}%;background:{color}"></i></span><b class="num">{Y(v):s} 亿</b></div>')
        html_rows.append('</div>')
    return ''.join(html_rows)

def render(ledger,memo):
    doc=ledger['document'];qa=audit(ledger)
    if doc.get('business_type') in ('bank','insurance','brokerage'):raise ValueError('Financial institutions require distinct financial-sector renderer; fail closed, do not use manufacturing P&L')
    if qa['status']=='BLOCKED':raise ValueError('Ledger audit blocked: '+repr(qa['issues'])+repr([x for x in qa['checks'] if x['status']=='FAIL']))
    issuer=escape(memo.get('issuer_short',doc['issuer']));title=escape(memo.get('headline','财报研究：事实、机制与不确定性'))
    status=memo.get('review_status','DRAFT');draft=status!='ANALYST_REVIEWED' or qa['status'] not in ('CALCULATION_PASS_MANUAL_REVIEW_REQUIRED','CONDITIONAL_DRAFT')
    rev=num(ledger,'revenue'); gp=rev-num(ledger,'cogs') if rev and num(ledger,'cogs') is not None else None
    cfo=num(ledger,'cfo'); np=num(ledger,'net_profit');rr=num(ledger,'revenue_prior');cc=num(ledger,'cogs_prior')
    if rev is None:raise ValueError('Revenue required for current industrial sample')
    growth=((rev-rr)/rr*100) if rr else D(0)
    gpold=(rr-cc) if rr and cc is not None else None
    gp_delta=gp-gpold if gpold else None
    gs=((gp_delta)/gpold*100) if gpold else None
    src='半年度报告';asset=num(ledger,'assets');liab=num(ledger,'liabilities');eq=num(ledger,'equity'); capex=num(ledger,'capex_cash')
    segments=ledger.get('segments',[])
    facts=ledger['facts']
    def mfact(k):
        return ('p'+str(facts[k]['page'])) if k in facts else '无披露页码'
    KPIs=[('营业收入',Y(rev)+' 亿',f'同比 {pct(growth,2)}',mfact('revenue')),
          ('毛利润',Y(gp)+' 亿',f'同比 +{pct(gs,1)}' if gs else '本期',mfact('revenue')+' · '+mfact('cogs')),
          ('合并净利润',Y(np)+' 亿' if np else '—','与归母利润不同',mfact('net_profit')),
          ('经营现金流',Y(cfo)+' 亿' if cfo else '—','现金调节须看附注',mfact('cfo'))]
    kphtml=''.join(f'<div class="stat"><div class="stat-title">{escape(a)}<small>{escape(d)}</small></div><div class="stat-num">{escape(b)}</div><div class="stat-meta">{escape(c)}</div></div>' for a,b,c,d in KPIs)
    sank=svg_sankey(ledger,memo)
    growthbars=''.join(bar(lab,val,max([gp,gpold,rev,rr]),col,'来自合并利润表：p61（毛利润为计算值）') for lab,val,col in [('上年毛利润',gpold,'#88b5ac'),('本期毛利润',gp,'#177d6b'),('上年收入',rr,'#c5b7a4'),('本期收入',rev,'#4f6f79')] if val is not None)
    inv=num(ledger,'inventory'); invprior=num(ledger,'inventory_prior');ar=num(ledger,'accounts_receivable');arprior=num(ledger,'accounts_receivable_prior')
    watch=''.join(f'<li><div class="watch-no">{str(i).zfill(2)}</div><div><b>{escape(x["topic"])}</b><p>{escape(x["test"])}</p><small>{escape(x.get("page",""))}</small></div></li>' for i,x in enumerate(memo.get('watchlist',[]),1))
    supp=''.join('<li>'+escape(x)+'</li>' for x in memo.get('support',[]));counter=''.join('<li>'+escape(x)+'</li>' for x in memo.get('counter',[]))
    limits=''.join('<li>'+escape(x)+'</li>' for x in memo.get('limits',[]))
    prod=''.join(f'<div class="source-row"><span>{escape(k)}</span><b>{escape(v["source_label"])} · p{v["page"]}</b><span>{escape(v["amount"])} 元</span></div>' for k,v in list(facts.items())[:48])
    auditlist=''.join(f'<tr><td>{escape(v["id"])}</td><td class="{escape(v["status"].lower())}">{escape(v["status"])}</td><td>{escape(v.get("residual", v.get("note","")))}</td></tr>' for v in qa['checks'])
    cashflow=f'<div class="equation"><div>合并净利润<strong>{Y(np)} 亿</strong></div><span>＋ 15 项逐项调整</span><div>经营现金流<strong>{Y(cfo)} 亿</strong></div></div>' if np is not None and cfo is not None else ''
    capfacts=f'<div class="triple"><div><span>经营现金流</span><b>{Y(cfo)} 亿</b></div><div><span>长期资产购建现金支出</span><b>{Y(capex)} 亿</b></div><div><span>简化 FCF¹</span><b>{Y(cfo-capex)} 亿</b></div></div>' if cfo is not None and capex is not None else ''
    capchart=''.join(bar(label,val,asset,color,detail) for label,val,color,detail in [('期末资产',asset,'#59737a','资产 p57'),('负债',liab,'#bb836d','负债 p58'),('股东权益',eq,'#16816a','权益 p58')] if val is not None)
    raw=num(ledger,'raw_material');raw_prev=num(ledger,'raw_material_prior')
    top5=num(ledger,'top_five_ar');ar_gross=num(ledger,'ar_gross');allowance=num(ledger,'ar_allowance')
    prepaid=num(ledger,'prepayment');prepaid_prior=num(ledger,'prepayment_prior');top_prepaid=num(ledger,'top_prepay')
    rawinsight=''
    if raw is not None and raw_prev is not None and inv is not None and invprior is not None:
        maxraw=max(inv,invprior)
        rawinsight=f'<div class="contentbox"><h3>原材料积累是否正在占用现金？</h3><div class="triple"><div><span>原材料净额 · 2025年末</span><b>{Y(raw_prev)} 亿</b></div><div><span>原材料净额 · 2026H1 末</span><b>{Y(raw)} 亿</b></div><div><span>原材料占库存增量</span><b>{pct((raw-raw_prev)/(inv-invprior)*100,1)}</b></div></div>{bar("2025 年末原材料净额",raw_prev,maxraw,"#b8ada4","原材料净额 p112")}{bar("2026 H1 期末原材料净额",raw,maxraw,"#147f6b","原材料净额 p112")}<p class="caption">来源：存货分类附注 p112。原材料净额增长约 {Y(raw-raw_prev)} 亿，不能直接推断已成为滞销或全部用于战略备货；需结合存货跌价和后续生产转化复核。</p></div>'
    concinsight=''
    if top5 is not None and ar_gross is not None and ar_gross>0:
        actualpct=top5/ar_gross*100
        concinsight=f'<div class="contentbox"><h3>客户应收集中 ≠ 客户收入集中</h3><div class="focus-line"><div class="donut" style="--p:{float(actualpct):.2f}%" role="img" aria-label="前五名应收及合同资产余额合计约占84.27%"><b>{pct(actualpct,2)}</b><small>前五名应收余额</small></div><div><p>前五名客户应收账款及合同资产余额合计约 {Y(top5)} 亿元，占相关余额约 {pct(actualpct,2)}。<strong>此比例不是营业收入份额，也不是逾期率。</strong></p><p>应收总账面余额 {Y(ar_gross)} 亿元，计提坏账准备 {Y(allowance)} 亿元。客户名称未披露，不能据此推断信用违约。</p></div></div><p class="caption">来源：应收附注 p102–103。应收占比为原披露约84.27%；计算中可能存在小数位四舍五入差。</p></div>'
    prepayinsight=''
    if prepaid is not None and top_prepaid is not None:
        prepayinsight=f'<div class="contentbox"><h3>供应链预付款集中度</h3><div class="triple"><div><span>期末预付款</span><b>{Y(prepaid)} 亿</b></div><div><span>年初预付款</span><b>{Y(prepaid_prior)} 亿</b></div><div><span>第一大预付对象份额</span><b>{pct(top_prepaid/prepaid*100,1)}</b></div></div><p class="caption">来源：预付款附注 p111–112。占比仅针对预付款余额，绝不能当成总采购金额份额，也不能由此确认供应商身份。</p></div>'
    invdisplay=bar('年初存货净额' ,invprior,inv,'#c5b4a9','年初存货 p23')+bar('期末存货净额',inv,inv,'#2a8373','期末存货 p23') if inv and invprior else ''
    ardisplay=bar('年初应收净额',arprior,ar,'#c5b4a9','p23')+bar('期末应收净额',ar,ar,'#bd7461','p23') if ar and arprior else ''
    css=r'''<style>
:root{--ink:#132b31;--muted:#627574;--paper:#f7f6f1;--white:#fffefb;--line:#d8e0d9;--jade:#0d8069;--coral:#bd7965;--navy:#11252e;--serif:Georgia,'Songti SC','Noto Serif SC',serif;--sans:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif}*{box-sizing:border-box}html{scroll-behavior:smooth;overflow-x:clip;max-width:100%}body{margin:0;overflow-x:clip;max-width:100%;background:var(--paper);color:var(--ink);font-family:var(--sans);-webkit-font-smoothing:antialiased}a{color:inherit}button{font:inherit;cursor:pointer}:focus-visible{outline:3px solid #eaaf71!important;outline-offset:4px}header{background:var(--navy);color:#f6f9f3}.container{max-width:1180px;margin:auto;padding-left:28px;padding-right:28px}.mast{height:76px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #45606170}.logo{font-size:15px;font-weight:800;letter-spacing:.2em}.mast small{font-size:12px;letter-spacing:.08em;color:#b6cac4}.nav{display:flex;gap:21px}.nav a{font-size:12px;text-decoration:none;color:#c7d6cf}.nav a:hover{color:white}.hero{padding:80px 0 92px}.eyebrow{font-size:12px;color:#93bdac;letter-spacing:.21em;font-weight:800;text-transform:uppercase}.hero h1{max-width:1000px;line-height:1.18;font-weight:600;font-size:clamp(44px,6vw,73px);letter-spacing:-.05em;margin:24px 0}.hero h1 span{color:#82d3b4}.subtitle{max-width:870px;font-size:18px;line-height:1.95;color:#cbdbd4}.taglist{display:flex;gap:9px;flex-wrap:wrap;margin-top:34px}.tag{font-size:11px;padding:9px 12px;border-radius:50px;border:1px solid #638179;color:#d4e0d9}.draft{background:#f5dfbb;color:#77420a;padding:9px 15px;margin-top:12px;font-size:13px}.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));margin-top:-32px;position:relative;box-shadow:0 18px 46px #152d2c12;background:var(--line);gap:1px}.stat{padding:27px 22px;background:var(--white)}.stat-title{font-size:12px;font-weight:700;color:#476760;display:flex;justify-content:space-between;gap:8px}.stat-title small{color:#869895}.stat-num{font-family:var(--serif);font-size:31px;font-weight:700;margin:12px 0;white-space:nowrap}.stat-meta{font-size:12px;color:#188268}.lede{display:grid;grid-template-columns:1fr 1fr;gap:60px;padding:78px 0}.lede h2{font:500 clamp(29px,3.3vw,45px)/1.28 var(--serif);letter-spacing:-.035em;margin:0}.lede p{font-size:16px;line-height:2;color:#4d6362;margin:0}.chapter{padding:56px 0 65px;border-top:1px solid #cfd8d2;scroll-margin-top:26px}.chapterhead{display:grid;grid-template-columns:120px 1fr;gap:20px;margin-bottom:32px}.ch-num{font:700 13px var(--sans);letter-spacing:.12em;color:var(--jade)}h2{font:500 clamp(30px,3.7vw,46px)/1.26 var(--serif);margin:0;letter-spacing:-.035em}h3{font-size:19px;margin:0 0 13px;line-height:1.5}.under{font-size:16px;color:#5c7470;max-width:800px;line-height:1.85;margin:15px 0 0}.figure{background:var(--white);padding:26px;border:1px solid #e1e5e0;border-radius:6px;box-shadow:0 10px 36px #152d2a0a}.figtop{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:10px}.figtop small{font-size:12px;color:#617571;letter-spacing:.1em;font-weight:800}.figtop button{padding:9px 13px;border:1px solid #dae2da;color:#176d5a;background:#fff;border-radius:5px;font-size:12px}.svg-scroller{overflow-x:auto;overscroll-behavior-inline:contain}.money-svg{width:100%;min-width:930px;display:block;font-family:var(--sans)}.svg-kicker{font-size:16px;fill:#6b807a;font-weight:700;letter-spacing:1px}.svg-label{font-size:17px;fill:#1a3b3e;font-weight:750}.svg-amount{font-size:23px;fill:#143c3c;font-weight:750}.ribbon{opacity:.81;stroke:#fff8;stroke-width:1.5;cursor:help}.ribbon:hover,.ribbon:focus{stroke:#082f33;stroke-width:2.5;opacity:1}.ribbon.dim{opacity:.12}.caption{color:#6b7e77;font-size:12px;line-height:1.8;margin:18px 1px 0}.analysis-pair{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:21px}.analysis-pair>div{padding:25px 25px;background:#eaf1eb;border-top:3px solid var(--jade)}.analysis-pair>div:nth-child(2){background:#f0eae3;border-top-color:#c1876b}.analysis-pair h3{font-size:15px}.analysis-pair p{font-size:14px;color:#49615e;line-height:1.85;margin:0}.contentbox{padding:30px;background:var(--white);border:1px solid #e2e6de;margin:18px 0}.contentbox p{color:#4c6160;font-size:15px;line-height:1.96}.compare-row{margin:18px 0;cursor:help}.bar-line{display:flex;justify-content:space-between;gap:12px;font-size:13px;color:#456360}.bar-line strong{font-variant-numeric:tabular-nums}.track{height:22px;background:#e9eee8;margin-top:8px;border-radius:4px;overflow:hidden}.track-fill{width:var(--w);height:100%;border-radius:4px}.cash-grid{display:grid;grid-template-columns:1fr 1fr;gap:25px}.cash-group{padding:23px;background:#fffefb;border:1px solid #e0e5df}.cash-group-head{font-weight:750;font-size:14px;color:#33544b;margin-bottom:20px}.cash-line{display:grid;grid-template-columns:160px minmax(40px,1fr) 77px;align-items:center;gap:12px;margin:12px 0;font-size:12px}.cash-name{font-size:12px;line-height:1.35}.cash-track{height:13px;background:#e9eee8;display:block;overflow:hidden;border-radius:2px}.cash-track i{display:block;height:100%;border-radius:2px}.cash-line .num{text-align:right;white-space:nowrap}.equation{display:flex;gap:16px;align-items:center;flex-wrap:wrap;padding:24px;background:#e9eee8;margin-bottom:18px}.equation>div{display:grid;gap:5px;font-size:12px}.equation strong{font:700 25px var(--serif)}.equation>span{font-size:12px;color:#4b6760}.triple{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:#dfe5dd}.triple div{padding:22px;background:#fffefb}.triple span{font-size:12px;color:#697d77}.triple b{display:block;margin-top:12px;font:700 26px var(--serif)}.watchlist{padding:0;list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:14px}.watchlist li{display:flex;gap:15px;padding:23px;background:#edf1eb;border:1px solid #dde5dc}.watch-no{font:700 22px var(--serif);color:#0c876a}.watchlist b{font-size:14px}.watchlist p{font-size:13px;line-height:1.8;color:#56706b;margin:9px 0}.watchlist small{color:#7b9188}.method{padding:30px;background:#13313a;color:#ecf0ea}.method h3{font:500 30px var(--serif)}.method p,.method li{color:#c8d8d0;font-size:13px;line-height:1.8}.method ul{padding-left:22px}.method details{border-top:1px solid #668077;margin-top:14px;padding-top:15px}.method summary{cursor:pointer;font-weight:700}.method table{width:100%;border-collapse:collapse;font-size:12px;margin-top:15px;text-align:left}.method th,.method td{padding:11px;border-bottom:1px solid #45665e}.method .pass{color:#87dfb9}.method .fail{color:#ff9a8b}.source-row{display:grid;grid-template-columns:180px 1fr 180px;gap:10px;border-bottom:1px solid #476760;font-size:11px;padding:9px 0}.source-row b{font-weight:500}.source-row span:last-child{text-align:right}footer{background:#142d35;color:#c5d6d0;padding:30px 0;font-size:12px}.footer-inner{display:flex;justify-content:space-between;gap:15px}.tooltip{position:fixed;z-index:99;pointer-events:none;display:none;background:#132f37;color:white;border-radius:5px;padding:13px 15px;max-width:320px;box-shadow:0 10px 28px #0003;font-size:12px;line-height:1.65}.tooltip b{display:block;color:#99dec3;font-size:13px;margin-bottom:4px}.tooltip p{margin:0}.focus-line{display:grid;grid-template-columns:190px 1fr;gap:24px;align-items:center}.donut{width:176px;height:176px;border-radius:50%;background:conic-gradient(#137e69 var(--p),#dfe9e0 var(--p));display:flex;align-items:center;justify-content:center;flex-direction:column;position:relative}.donut:before{content:'';position:absolute;background:#fffefb;border-radius:50%;inset:22px}.donut b,.donut small{position:relative}.donut b{font:700 30px var(--serif)}.donut small{font-size:11px;color:#667970}.nochart{padding:20px;background:#f0e7e0}.chip{font-size:11px;color:#1a836d;border:1px solid #bfd4ca;border-radius:20px;padding:6px 10px}@media(max-width:1000px){.nav{display:none}.metrics{grid-template-columns:repeat(2,1fr)}.cash-grid{grid-template-columns:1fr}.lede{gap:22px}}@media(max-width:680px){.container{padding-left:17px;padding-right:17px}.hero{padding:55px 0 80px}.hero h1{font-size:42px}.subtitle{font-size:15px}.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.stat{padding:20px 14px}.stat-num{font-size:24px}.stat-title{display:block}.stat-title small{display:block;margin-top:6px}.lede,.analysis-pair,.watchlist{grid-template-columns:1fr}.lede{padding:58px 0}.chapterhead{grid-template-columns:1fr;gap:12px}.chapter{padding:45px 0}.figure{padding:13px 13px}.cash-line{grid-template-columns:125px minmax(40px,1fr) 75px;gap:8px}.triple{grid-template-columns:1fr}.source-row{grid-template-columns:1fr}.source-row span:last-child{text-align:left}.footer-inner{display:block}.cash-group{padding:14px}.contentbox{padding:22px}.focus-line{grid-template-columns:1fr;justify-items:center}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}</style>'''
    js=r'''<script>(()=>{const tooltip=document.querySelector('.tooltip');const tooltipTitle=tooltip.querySelector('b');const tooltipBody=tooltip.querySelector('p');function hide(){tooltip.style.display='none'}function show(el,e){const pair=(el.dataset.tip||'').split('|');tooltipTitle.textContent=pair[0]||'';tooltipBody.textContent=pair.slice(1).join(' | ');tooltip.style.display='block';const r=el.getBoundingClientRect();let x=e&&Number.isFinite(e.clientX)?e.clientX+14:r.left+16,y=e&&Number.isFinite(e.clientY)?e.clientY+18:r.top-84;tooltip.style.left=Math.max(8,Math.min(window.innerWidth-330,x))+'px';tooltip.style.top=Math.max(8,Math.min(window.innerHeight-120,y))+'px'}document.querySelectorAll('[data-tip]').forEach(el=>{el.addEventListener('pointerenter',e=>show(el,e));el.addEventListener('pointermove',e=>show(el,e));el.addEventListener('pointerleave',hide);el.addEventListener('focus',()=>show(el));el.addEventListener('blur',hide)});document.querySelectorAll('.ribbon').forEach(r=>{r.addEventListener('pointerenter',()=>document.querySelectorAll('.ribbon').forEach(x=>x.classList.toggle('dim',x.dataset.group!==r.dataset.group)));r.addEventListener('pointerleave',()=>document.querySelectorAll('.ribbon').forEach(x=>x.classList.remove('dim')))});document.querySelectorAll('button[data-export]').forEach(b=>b.addEventListener('click',()=>{const svg=document.querySelector('#sankey svg');if(!svg)return;const blob=new Blob([new XMLSerializer().serializeToString(svg)],{type:'image/svg+xml'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='financials-money-flow.svg';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}));document.addEventListener('keydown',e=>{if(e.key==='Escape')hide()})})();</script>'''
    hero=f'<header><div class="container"><div class="mast"><div class="logo">FINANCIALS <span style="color:#93cbb6">/ RESEARCH</span></div><div class="nav"><a href="#model">商业模式</a><a href="#growth">增长引擎</a><a href="#cash">现金质量</a><a href="#risk">资本风险</a><a href="#watch">追踪指标</a><a href="#sources">来源</a></div><small>ISSUER FILINGS · 研究记录</small></div><div class="hero"><div class="eyebrow">{escape(memo.get("eyebrow",doc.get("period_key","")))}</div><h1>{title}</h1><p class="subtitle">{escape(memo.get("summary",""))}</p><div class="taglist"><span class="tag">{issuer} · {escape(doc["ticker"])}</span><span class="tag">{escape(doc["period_start"])} — {escape(doc["period_end"])}</span><span class="tag">{("未经审计" if not doc["audited"] else "已审计")}</span><span class="tag">报告原文为唯一公司数据来源</span></div></div></div></header>'
    disclaimer=f'<div class="draft"><div class="container">研究草稿：来源/分析复核或应用性门槛未完成，不得当成正式投资研究产品。</div></div>' if draft else ''
    main=f'''<main class="container">
 <section class="lede" id="model"><h2>从价值链开始，而不是从一个利润率数字开始。</h2><p>{escape(memo.get('business',''))}<br><small style="color:#6b8078">{escape(memo.get('business_sources',''))}</small></p></section>
 <section class="chapter" id="growth"><div class="chapterhead"><span class="ch-num">01 / THE MONEY</span><div><h2>无源和有源，各自贡献了多少毛利润？</h2><p class="under">按金额比例拆解收入：每条连续流带都有独立的金额与利润/成本去向。分部披露差额仅作为<strong>计算差额</strong>，绝不是虚构业务。</p></div></div>
 <div class="figure" id="sankey"><div class="figtop"><small>2026 H1 / 收入 → 毛利润 + 营业成本 / RMB 亿</small><button data-export="sankey" type="button">导出矢量图 · SVG</button></div><div class="svg-scroller">{sank}</div><p class="caption">来源：{issuer} 2026H1 半年度报告 p22、p61。原值以元精确处理、绘图时按亿展示；各条流带面积与金额严格同比例，非实际收付现金流向。鼠标或键盘聚焦可查看原始数值。</p></div>
 <div class="analysis-pair"><div><h3>观察：增长结构明显分化</h3><p>{escape(memo.get('growth_explanation',''))}</p></div><div><h3>反面解释：供给与需求需要分开验证</h3><p>{escape(memo.get('growth_counter',''))}</p></div></div>
 </section>
 <section class="chapter"><div class="chapterhead"><span class="ch-num">02 / EARNINGS ENGINE</span><div><h2>毛利润增长为何远快于收入？</h2><p class="under">毛利润增加 {Y(gp_delta)} 亿元，来自合并营收与营业成本的共同变化。这是严格的会计差额，不是对销量/定价的因果归因。</p></div></div><div class="contentbox"><h3>两年同期 · 总收入与毛利润</h3>{growthbars}<p class="caption">合并报表 p61，2025H1 与 2026H1，金额均按同一尺度绘制。毛利润=收入−营业成本。</p></div></section>
 <section class="chapter" id="cash"><div class="chapterhead"><span class="ch-num">03 / CASH CONVERSION</span><div><h2>利润兑现现金，中间经历了什么？</h2><p class="under">没有把资产负债表的期末差额当现金流，而是直接使用现金流量表补充资料披露的全部签名调整项。</p></div></div>{cashflow}<div class="cash-grid">{cash_adjustments(ledger)}</div><p class="caption">来源：合并利润表 p62、现金流量表及间接法补充资料 p147–148。15 项原始金额以元精确勾稽；正负号反映对 CFO 的调整，不代表支出的会计分类。</p><div class="contentbox"><h3>现金增长与营运资本占用同时存在</h3><p>{escape(memo.get('cash_explanation',''))}</p></div></section>
 <section class="chapter" id="risk"><div class="chapterhead"><span class="ch-num">04 / FINANCIAL QUALITY</span><div><h2>增长的另一面：库存、应收与资金配置。</h2><p class="under">这三组风险不是对管理层的指控，而是需要继续通过附注与现金回收验证的经营约束。</p></div></div><div class="contentbox"><h3>存货净额 · 2025年末 → 2026年6月末</h3>{invdisplay}{rawinsight}<p class="caption">来源：半年度报告 p23（时点比较）。两条使用同一尺度，不应与 H1 同比营收直接视作同周期增幅。</p></div><div class="contentbox"><h3>应收账款净额 · 2025年末 → 2026年6月末</h3>{ardisplay}<p class="caption">来源：p23、p102–103。前五名客户占应收及合同资产余额 84.27%，<strong>并非收入占比</strong>。</p><p>{escape(memo.get('risk_explanation',''))}</p></div>{concinsight}{prepayinsight}<div class="contentbox"><h3>资产负债与资本配置</h3>{capchart}{capfacts}<p class="caption">来源：资产负债表 p56–58，现金流量表 p65。¹ 分析师定义的简化 FCF=CFO−购建长期资产支付现金；并非管理层定义或股东可分配现金。</p><p>{escape(memo.get('capital_explanation',''))}</p></div></section>
 <section class="chapter"><div class="chapterhead"><span class="ch-num">05 / TWO-SIDED VIEW</span><div><h2>最强的支持证据，也必须接受最强的反面假设。</h2><p class="under">财报研究不应把公司的解释和分析师的推断混为已被证明的经营因果。</p></div></div><div class="analysis-pair"><div><h3>支持 / Supported</h3><ul>{supp}</ul></div><div><h3>风险 / Challenged</h3><ul>{counter}</ul></div></div></section>
 <section class="chapter" id="watch"><div class="chapterhead"><span class="ch-num">06 / FALSIFICATION</span><div><h2>下一份财报，什么数据能够推翻今天的判断？</h2><p class="under">只有可证伪、可重复的追踪指标，才算真正完成一次研究。</p></div></div><ul class="watchlist">{watch}</ul></section>
 <section class="chapter" id="sources"><div class="method"><h3>来源、核算、假设与边界</h3><p>源文件：{escape(doc['issuer'])} {escape(doc['period_key'])} 半年度报告。源 SHA-256：<code style="overflow-wrap:anywhere">{escape(doc['source_sha256'])}</code>。合并报表，{('已审计' if doc['audited'] else '未经审计')}。</p><p>证据复核：{escape(memo.get('required_reviewer',''))}</p><ul>{limits}</ul><p>脚本核算状态：<strong>{escape(qa['status'])}</strong>，适用检查 PASS={qa['summary']['PASS']}，FAIL={qa['summary']['FAIL']}，NOT_CHECKED={qa['summary']['NOT_CHECKED']}。计算通过不等于行业预测被验证或公网已发布验收。</p><details><summary>完整会计勾稽记录 / Financial checks</summary><table><thead><tr><th>检查</th><th>结果</th><th>偏差 / 备注</th></tr></thead><tbody>{auditlist}</tbody></table></details><details><summary>主要原始金额与报告页码 / Ledger trace</summary><div>{prod}</div></details></div></section>
 </main>'''
    return f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="可核对原始财报页码的A股上市公司商业模式、盈利、现金转换与研究判断。"><title>{issuer}｜{escape(doc["period_key"])}｜Financials Research Desk</title>{css}</head><body><div class="tooltip" role="status" aria-live="polite"><b></b><p></p></div>{hero}{disclaimer}<div class="container"><section class="metrics">{kphtml}</section></div>{main}<footer><div class="container footer-inner"><b>FINANCIALS / INDEPENDENT RESEARCH</b><span>证据优先 · 原创设计 · 不构成投资建议</span></div></footer>{js}</body></html>'

def main():
    p=argparse.ArgumentParser();p.add_argument('--ledger',required=True);p.add_argument('--memo',required=True);p.add_argument('--out',required=True);p.add_argument('--qa',default=None)
    a=p.parse_args();ledger=json.loads(Path(a.ledger).read_text());memo=json.loads(Path(a.memo).read_text())
    content=render(ledger,memo);out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(content,encoding='utf-8')
    status=audit(ledger);summary={'source_pdf_sha256':ledger['document']['source_sha256'],'artifact_sha256':hashlib.sha256(content.encode()).hexdigest(),'html_bytes':len(content.encode()),'status':'DRAFT' if memo.get('review_status')!='ANALYST_REVIEWED' else 'EVIDENCE_AUDITED_BROWSER_PENDING','accounting':status,'figures':{'sankey_ribbons':content.count('class="ribbon"'),'indirect_adjustments':len(ledger.get('indirect_cfo_adjustments',[]))}}
    if a.qa:Path(a.qa).write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'out':str(out),'bytes':len(content.encode()),'sankey_ribbons':content.count('class="ribbon"'),'accounting':status['status']},ensure_ascii=False))
if __name__=='__main__':main()