"""Independent original-yuan V10 narrow-screen financial figure renderer.

Each finance exhibit has a full-width source-bound 330-unit phone SVG and
a separately preserved desktop edition. No desktop 850px SVG scroller.
Data in source ledger is original Decimal CNY yuan; percent facts carry their
reported independent units. Shapes are measured, not cosmetic KPI cards.
"""
from __future__ import annotations
from decimal import Decimal as D
from html import escape as E

W = D(330)
INK = "#17343b"
GREEN = "#087d69"
COPPER = "#b8795b"
BLUE = "#437d95"
MUTED = "#667b78"
PAPER = "#f7f5ef"


def _e(x):
    return E(str(x), quote=True)


def _num(x):
    return format(float(x), ".4f")


def _yi(value):
    return D(str(value)) / D("100000000")


def _fmt(value, unit="亿"):
    value = D(str(value))
    if unit == "%":
        return str(value.quantize(D(".01"))) + "%"
    amount = _yi(value)
    if abs(amount) < D("0.01") and amount != 0:
        return format(amount, ".4f") + "亿"
    return format(amount, ",.2f") + "亿"


def _label(name, limit=17):
    label = str(name)
    return label if len(label) <= limit else label[:limit-1] + "…"


def _text(x, y, txt, size=12, fill=INK, bold=False, anchor="start"):
    return (f'<text x="{_num(x)}" y="{_num(y)}" font-family="Noto Sans CJK SC,PingFang SC,sans-serif" '
            f'font-size="{size}" font-weight="{700 if bold else 450}" fill="{fill}" '
            f'text-anchor="{anchor}">{_e(txt)}</text>')


def _box(x, y, w, h, fill, extra=""):
    return (f'<rect x="{_num(x)}" y="{_num(y)}" width="{_num(max(D(0),D(str(w))))}" '
            f'height="{_num(max(D(0),D(str(h))))}" fill="{fill}" {extra}/>')


def _svg(body, h, title, kind, uid):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 {_num(h)}" '
            f'role="img" data-native-original-yuan="true" data-figure-kind="{_e(kind)}" '
            f'data-figure-id="{_e(uid)}" aria-label="{_e(title)}">'
            f'<title>{_e(title)}</title>' + body + '</svg>')


def _band(x0, top0, bottom0, x1, top1, bottom1):
    c = D(str(x1-x0)) * D(".48")
    return (f'M {_num(x0)} {_num(top0)} C {_num(x0+c)} {_num(top0)} '
            f'{_num(x1-c)} {_num(top1)} {_num(x1)} {_num(top1)} '
            f'L {_num(x1)} {_num(bottom1)} C {_num(x1-c)} {_num(bottom1)} '
            f'{_num(x0+c)} {_num(bottom0)} {_num(x0)} {_num(bottom0)} Z')


def _path_money(d, fill, amount, exact_scale, source_id, revenue, cost, gp):
    return (f'<path d="{d}" fill="{fill}" fill-opacity=".73" '
            f'data-source-id="{_e(source_id)}" '
            f'data-revenue-yuan="{_e(revenue)}" data-cost-yuan="{_e(cost)}" '
            f'data-gp-yuan="{_e(gp)}" data-ribbon-yuan="{_e(amount)}" '
            f'data-scale-yuan-per-svg-unit="{_e(exact_scale)}"/>')


def source_own_sankey(code, typed, names, *, mobile=False):
    """Real source->own COGS and own GP, no group-only borrowing."""
    assert typed["kind"] == "TYPE_A_SOURCE_OWN_COST_GP"
    rows = typed["source_own_cost_gp"]
    total = D(typed["exact_yuan_total"])
    scale = D(70) / total
    if not mobile:
        # Desktop graph uses the same actual-source ribbon decomposition;
        # SVG 330-unit grammar can be placed on a wide canvas without fake flows.
        pass
    h = D(54+len(rows)*132)
    out = _text(12, 23, "业务收入 → 各自成本 + 各自毛利", 14, INK, True)
    out += _text(12, 42, "每条色带的高度＝原始人民币元 × 同一精确比例", 10, MUTED)
    for i,(sid,revenue,cost,gp) in enumerate(rows):
        r,c,g = D(revenue),D(cost),D(gp)
        assert r == c+g and min(r,c,g)>=0
        baseline = D(80+i*132)
        rheight,cheight,gheight = r*scale,c*scale,g*scale
        out += _text(12,baseline-16, names.get(sid,sid),13,INK,True)
        out += _text(317,baseline-16,_fmt(r),12,INK,True,"end")
        y = baseline + D(12)
        out += _box(12,y,7,rheight,GREEN)
        if c>0:
            d=_band(D(19),y,y+cheight,D(235),y,y+cheight)
            out+=_path_money(d,COPPER,c,str(total/D(70)),sid,revenue,cost,gp)
            out+=_box(235,y,7,cheight,COPPER)
        if g>0:
            d=_band(D(19),y+cheight,y+rheight,D(235),y+cheight,y+rheight)
            out+=_path_money(d,GREEN,g,str(total/D(70)),sid,revenue,cost,gp)
            out+=_box(235,y+cheight,7,gheight,GREEN)
        out+=_text(250,y+12,"成本 "+_fmt(c),10,COPPER,False)
        out+=_text(250,y+31,"毛利 "+_fmt(g),10,GREEN,False)
        out+=_text(12,y+rheight+16,"原始元 "+format(r,",.2f"),9,MUTED)
    return _svg(out,h,"各业务独立收入成本毛利真实元级桑基图","TYPE_A_SOURCE_OWN_COST_GP",code+"-2")


def group_sankey(code, typed, names):
    """Sources->actual GROUP total->total COGS and GP, no own GP claim."""
    assert typed["kind"] == "TYPE_B_GROUP_ONLY_GROSS_ALLOCATION"
    total=D(typed["exact_yuan_total"]);cost=D(typed["exact_yuan_cogs"]);gp=D(typed["exact_yuan_group_gp"])
    assert total==cost+gp
    rows=[(sid,D(val)) for sid,val in _source_rows(code,typed)]
    assert sum((x[1] for x in rows),D(0))==total
    scale=D(92)/total
    h=D(145+len(rows)*47)
    out=_text(12,22,"收入分类 → 集团总成本 / 毛利",13,INK,True)
    out+=_text(12,40,"PRODUCT_LEVEL_GP_NOT_ESTABLISHED",10,COPPER,True)
    out+=_text(12,56,"未披露各业务毛利；右侧仅为集团合计分配",10,MUTED)
    cursor=D(78);mid=D(78)
    for sid,amount in rows:
        thick=amount*scale
        out+=_text(12,cursor-8,names.get(sid,sid),11,INK,True)
        out+=_text(12,cursor+thick+12,_fmt(amount),10,MUTED)
        out+=_box(12,cursor,7,thick,BLUE)
        out+=_path_money(_band(D(19),cursor,cursor+thick,D(180),mid,mid+thick),BLUE,
                         amount,str(total/D(92)),sid,str(amount),"0","0")
        cursor+=thick+D(47);mid+=thick
    out+=_box(180,78,9,D(92),INK)
    out+=_text(184,68,_fmt(total),12,INK,True,"middle")
    out+=_path_money(_band(D(189),78,78+cost*scale,D(246),78,78+cost*scale),COPPER,
                     cost,str(total/D(92)),"GROUP",str(total),str(cost),str(gp))
    out+=_path_money(_band(D(189),78+cost*scale,170,D(246),78+cost*scale,170),GREEN,
                     gp,str(total/D(92)),"GROUP",str(total),str(cost),str(gp))
    out+=_box(246,78,7,cost*scale,COPPER)
    out+=_box(246,78+cost*scale,7,gp*scale,GREEN)
    out+=_text(260,91,"成本",11,COPPER,True)
    out+=_text(260,106,_fmt(cost),10,COPPER)
    out+=_text(260,149,"毛利",11,GREEN,True)
    out+=_text(260,164,_fmt(gp),10,GREEN)
    return _svg(out,h,"集团层财务桑基图（不代表各分部毛利）","TYPE_B_GROUP_ONLY_GROSS_ALLOCATION",code+"-2")


def _source_rows(code, typed):
    from pathlib import Path
    import json
    here=Path(__file__).resolve().parent
    facts=json.loads((here/"input-ledgers"/(code+".json")).read_text())["facts"]
    return [(sid,facts[sid]["yuan"]) for sid in typed["source_keys"]]


def bank_sankey(code, typed, get, names):
    """Net bank revenue is already AFTER interest expenses."""
    assert typed["kind"]=="BANK_NET_INCOME_TO_OPERATING_PROFIT"
    src=[("nii",D(get(code,"nii"))),("fees_net",D(get(code,"fees_net"))),("other_net",D(get(code,"other_net")))]
    costs=[("administrative_expense",D(get(code,"administrative_expense"))),
           ("credit_impairment_expense",D(get(code,"credit_impairment_expense"))),
           ("other_operating_cost",D(get(code,"other_operating_cost")))]
    total=D(typed["exact_yuan_total"]);profit=D(typed["exact_yuan_result"])
    assert sum((v for _,v in src),D(0))==total and total==sum((v for _,v in costs),D(0))+profit
    scale=D(90)/total
    out=_text(10,21,"净利息收入已扣利息支出",13,INK,True)
    out+=_text(10,37,"银行净收入 → 运营、信用成本 → 营业利润",10,MUTED)
    cursor=D(76)
    for k,amt in src:
        h=amt*scale
        out+=_text(12,cursor-5,names.get(k,k),11,INK)
        out+=_box(14,cursor,7,h,BLUE)
        out+=_path_money(_band(D(21),cursor,cursor+h,D(172),D(76)+sum((v for _,v in src[:src.index((k,amt))]),D(0))*scale,D(76)+sum((v for _,v in src[:src.index((k,amt))+1]),D(0))*scale),BLUE,amt,str(total/D(90)),k,str(amt),"0","0")
        cursor+=h+D(41)
    out+=_box(172,76,9,90,INK)
    out+=_text(176,64,_fmt(total),12,INK,True,"middle")
    right=D(76)
    for k,amt in costs+[("operating_profit",profit)]:
        h=amt*scale
        out+=_path_money(_band(D(181),right,right+h,D(235),right,right+h),GREEN if k=="operating_profit" else COPPER,amt,str(total/D(90)),k,str(amt),"0","0")
        out+=_box(235,right,6,h,GREEN if k=="operating_profit" else COPPER)
        out+=_text(248,right-4,names.get(k,k),10,INK,True)
        out+=_text(248,right+9,_fmt(amt),10,GREEN if k=="operating_profit" else COPPER)
        right+=h+D(35)
    return _svg(out,350,"银行净利息及手续费收入分配到营业支出与营业利润","BANK_NET_INCOME_TO_OPERATING_PROFIT",code+"-2")


def signed_product_profit(code, typed, get, names):
    """No positive profit ribbons when a reported product has negative GP."""
    assert typed["kind"]=="TYPE_C_SANKEY_OMITTED"
    keys=[("maotai_rev","maotai_cogs"),("series_rev","series_cogs"),("other_rev","other_cogs")]
    gps=[(k,D(get(code,k))-D(get(code,c))) for k,c in keys]
    maxabs=max(abs(v) for _,v in gps)
    zero=D(44)
    out=_text(12,22,"真实业务毛利（含负数）",13,INK,True)
    out+=_text(12,42,"FINANCIAL_SANKEY_OMITTED_WITH_SOURCE_REASON",9,COPPER,True)
    out+=_text(12,58,typed["reason"],9,MUTED)
    for i,(sid,amt) in enumerate(gps):
        y=D(91+i*91);w=abs(amt)/maxabs*D(240)
        out+=_text(12,y-11,names.get(sid,sid),12,INK,True)
        out+=_box(44,y,D(1),37,MUTED)
        out+=_box(zero if amt>=0 else zero-w,y+3,w,25,GREEN if amt>=0 else COPPER,
                  f'data-signed-yuan="{amt}"')
        out+=_text(12,y+47,("+" if amt>0 else "")+_fmt(amt),12,GREEN if amt>=0 else COPPER,True)
    return _svg(out,395,"逐产品真实有符号毛利：负毛利不是正向资金流","TYPE_C_SANKEY_OMITTED",code+"-2")


def signed_source_bars(code, index, keys, get, facts, label="原始财务金额与真实符号"):
    """Competing source amounts on one signed zero axis, never additive claim."""
    rows=[]
    for k in keys:
        item=facts.get(k)
        if item is None:
            continue
        unit=item.get("reported_unit",item.get("unit","元"))
        if unit == "%" or k.endswith("_pct") or "_pct_" in k:
            continue
        val=D(get(code,k))
        rows.append((k,item["label"],val))
    rows=rows[:14]
    if not rows:
        return ratio_bars(code,index,keys,get,facts)
    maximum=max((abs(r[2]) for r in rows),default=D(1)) or D(1)
    h=D(62+len(rows)*70)
    out=_text(12,23,label,13,INK,True)
    out+=_text(12,40,"各指标同一金额坐标；不同定义的金额不可相加",10,MUTED)
    axis=D(158)
    for i,(key,title,val) in enumerate(rows):
        y=D(73+i*70);width=abs(val)/maximum*D(134)
        out+=_text(12,y-9,_label(title,24),11,INK,True)
        out+=_box(axis,y,D(1),25,MUTED)
        out+=_box(axis if val>=0 else axis-width,y+3,width,19,GREEN if val>=0 else COPPER,
                  f'data-source-id="{_e(key)}" data-exact-yuan="{_e(val)}"')
        out+=_text(12,y+40,("+" if val>0 else "")+_fmt(val),11,GREEN if val>=0 else COPPER,True)
    return _svg(out,h,label,"SIGNED_SOURCE_VALUES",code+"-"+str(index))


def ratio_bars(code,index,keys,get,facts):
    rows=[(k,v) for k,v in ((key,facts.get(key)) for key in keys)
          if v is not None and (v.get("reported_unit",v.get("unit"))=="%" or "pct" in k)]
    out=_text(12,22,"同类风险与比率指标（分别列示）",13,INK,True)
    for i,(key,fact) in enumerate(rows):
        y=D(66+i*84);v=D(get(code,key))
        out+=_text(12,y-9,_label(fact["label"],24),11,INK,True)
        out+=_box(12,y,265,14,PAPER)
        out+=_box(12,y,max(D(0),min(D(265),abs(v)*D("2.4"))),14,GREEN if v>=0 else COPPER,
                  f'data-source-id="{_e(key)}" data-source-percent="{_e(v)}"')
        out+=_text(12,y+33,str(v.quantize(D(".01")))+"%",12,GREEN,True)
    return _svg(out,55+84*len(rows),"分别列示的实际风险比率","INDEPENDENT_RATIOS",code+"-"+str(index))


def two_stock_comparison(code,index,keys,get,facts):
    pairs=[]
    present=set(keys)
    for k in keys:
        prior=next((x for x in (k+"_prior",k+"_prior_bs",k.replace("_bs","_prior_bs"),k.replace("_bs","_prior")) if x in present),None)
        if prior is None or k==prior or ("prior" in k):
            continue
        pairs.append((k,prior))
    if not pairs:
        return signed_source_bars(code,index,keys,get,facts,"同期同口径财务比较")
    mx=max((D(get(code,k)) for pair in pairs for k in pair),default=D(1)) or D(1)
    h=D(72+len(pairs)*105)
    out=_text(12,22,"两时点 / 两期间可比金额",13,INK,True)
    out+=_text(12,40,"同一公司同一项目，对照不等于现金流",10,MUTED)
    for i,(cur,prior) in enumerate(pairs):
        y=D(69+i*105)
        out+=_text(12,y,_label(facts[cur]["label"],22),12,INK,True)
        for j,k in enumerate((prior,cur)):
            v=D(get(code,k));w=abs(v)/mx*D(212)
            yy=y+D(10+j*29)
            out+=_box(12,yy,w,17,BLUE if j==0 else GREEN,
                      f'data-source-id="{_e(k)}" data-exact-yuan="{_e(v)}"')
            out+=_text(229,yy+12,("上期 " if j==0 else "本期 ")+_fmt(v),10,MUTED if j==0 else GREEN)
    return _svg(out,h,"原报表可比期间的真实财务金额","TWO_PERIOD_OR_STOCK",code+"-"+str(index))


def cash_waterfall(code,index,get,facts,cfo_components):
    if index in (8,9,10) and code in cfo_components:
        z=cfo_components[code]
        values=[("合并净利润",D(z["start"][1]))]
        groups={}
        for name,val,page,cat in z["parts"]:
            groups[cat]=groups.get(cat,D(0))+D(val)
        adjustments=[(k,v) for k,v in groups.items()]
        final=D(z["end"][1])
        assert values[0][1]+sum((v for _,v in adjustments),D(0))==final
        subtitle="完整间接法调整，原始分项见审计表"
    else:
        maps={
          "688111":("cash_begin","cfo","cfi","cff","cash_fx","cash_close"),
          "000333":("cash_begin_bs","cfo","cfi_bs","cff_bs","fx_bs","cash_close_bs"),
          "600036":("cash_begin_bs","cfo","cfi_bs","cff_bs","fx_bs","cash_close_bs"),
        }
        if code not in maps:
            return None
        a,b,c,d,e,f=maps[code]
        values=[("期初现金",D(get(code,a)))]
        adjustments=[("经营",D(get(code,b))),("投资",D(get(code,c))),
                     ("筹资",D(get(code,d))),("汇兑",D(get(code,e)))]
        final=D(get(code,f))
        assert values[0][1]+sum((v for _,v in adjustments),D(0))==final
        subtitle="真正现金等价物期初 + 四类有符号现金流 = 期末"
    running=values[0][1]
    history=[running]
    for _,v in adjustments:
        running+=v;history.append(running)
    assert running==final
    domain=max(abs(v) for v in history+[D(0)]) or D(1)
    # Horizontal bar endpoints preserve signed amount and cumulative endpoints.
    h=D(105+len(adjustments)*86+64)
    out=_text(12,23,"真实有符号会计桥",13,INK,True)
    out+=_text(12,41,subtitle,10,MUTED)
    out+=_text(12,68,"起点 "+_fmt(values[0][1]),12,INK,True)
    running=values[0][1]
    for i,(label,delta) in enumerate(adjustments):
        nextval=running+delta
        y=D(98+i*86)
        lo=min(running,nextval);hi=max(running,nextval)
        x0=D(12)+(lo-min(min(history),D(0)))/(max(history)-min(min(history),D(0))+D("0.00000001"))*D(270)
        x1=D(12)+(hi-min(min(history),D(0)))/(max(history)-min(min(history),D(0))+D("0.00000001"))*D(270)
        out+=_text(12,y-12,label+" "+("+" if delta>0 else "")+_fmt(delta),12,GREEN if delta>=0 else COPPER,True)
        out+=_box(x0,y,x1-x0,24,GREEN if delta>=0 else COPPER,
                  f'data-exact-signed-yuan="{_e(delta)}" data-start-yuan="{_e(running)}" data-end-yuan="{_e(nextval)}"')
        out+=_text(12,y+43,"累计 "+_fmt(nextval),10,MUTED)
        running=nextval
    out+=_text(12,D(104+len(adjustments)*86),"终点 "+_fmt(final),13,INK,True)
    return _svg(out,h,"净利润或期初现金到报告现金流的逐项有符号会计桥","SIGNED_CASH_OR_INDIRECT_CFO",code+"-"+str(index))


# Exact per-company exhibit family and use of full source rows.
FAMILY={
 "688111":{1:"compare",2:"type",3:"rows",4:"rows",5:"stock",6:"compare",7:"cash",8:"indirect",9:"rows"},
 "600519":{1:"compare",2:"type",3:"rows",4:"rows",5:"rows",6:"compare",7:"stock",8:"indirect",9:"rows"},
 "000333":{1:"compare",2:"type",3:"compare",4:"rows",5:"rows",6:"compare",7:"rows",8:"stock",9:"cash",10:"indirect"},
 "600036":{1:"bank_interest",2:"type",3:"bank_profit",4:"compare",5:"ratio",6:"stock",7:"rows",8:"cash"},
}
NAME={
 "688111":{"wps_personal":"WPS个人","wps365":"WPS365","wps_software":"WPS软件","other_rev":"其他业务"},
 "600519":{"maotai_rev":"茅台酒","series_rev":"系列酒","other_rev":"其他业务"},
 "000333":{"home":"智能家居","industrial_solution":"商业及工业","other_total":"其他业务"},
 "600036":{"nii":"净利息收入","fees_net":"净手续费","other_net":"其他净收入",
           "administrative_expense":"业务及管理费","credit_impairment_expense":"信用减值","other_operating_cost":"其他营业成本",
           "operating_profit":"营业利润"},
}


def mobile_for(code,index,keys,get,facts,cfo_components,typed):
    family=FAMILY[code].get(index,"rows")
    names=NAME[code]
    if family=="type":
        if code=="688111":
            return source_own_sankey(code,typed,names,mobile=True)
        if code=="600519":
            return signed_product_profit(code,typed,get,names)
        if code=="000333":
            return group_sankey(code,typed,names)
        return bank_sankey(code,typed,get,names)
    if family=="indirect":
        return cash_waterfall(code,index,get,facts,cfo_components)
    if family=="cash":
        return cash_waterfall(code,index,get,facts,cfo_components)
    if family=="bank_profit":
        return signed_source_bars(code,index,keys,get,facts,"银行净收入、信用成本及利润各口径")
    if family=="bank_interest":
        return signed_source_bars(code,index,keys,get,facts,"利息收入、利息支出与净额（均为原始金额）")
    if family=="ratio":
        return ratio_bars(code,index,keys,get,facts)
    if family=="compare":
        return two_stock_comparison(code,index,keys,get,facts)
    if family=="stock":
        return two_stock_comparison(code,index,keys,get,facts)
    return signed_source_bars(code,index,keys,get,facts)
