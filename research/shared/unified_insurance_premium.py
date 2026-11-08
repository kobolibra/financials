"""One visual system, separate lawful insurance premium accounting grammar.

This is a real three-stage premium Sankey: four mutually exclusive original
insurance management premium categories -> new/renewal -> gross total.
It has NO path to CAS25 insurance service revenue, net profit, cash or CSM.
"""
from __future__ import annotations
from decimal import Decimal as D
from html import escape
import re
from unified_income_sankey import PALETTE,path,rect,text,fmt,nu

SOURCES=(("premium_first_regular","首年期交"),("premium_single","趸交"),
         ("premium_short","短期险"),("premium_renew","续期"))
NEW=("premium_first_regular","premium_single","premium_short")
GOLD="#B88642"

def _checked(ledger:dict):
    issuer=ledger.get("issuer",{})
    source=ledger.get("source",{})
    if (issuer.get("code")!="601628" or issuer.get("industry")!="life_insurance"
        or issuer.get("fiscal_period")!="2026H1" or issuer.get("base_unit")!="人民币元"
        or not re.fullmatch(r"[a-f0-9]{64}",str(source.get("original_bytes_sha256","")))
        or "SHA_PASS" not in str(source.get("original_bytes_gate",""))
        or source.get("physical_pages_observed")!=104):
        raise ValueError("INSURANCE_P104_SOURCE_BYTES_PERIOD_OR_SCOPE_NOT_PROVEN")
    facts=ledger.get("facts",{})
    def amt(key):
        f=facts.get(key,{})
        if (f.get("page")!=10 or f.get("scope")!="consolidated"
            or f.get("period")!="2026H1" or f.get("classification")!="DISCLOSED"
            or f.get("type")!="flow" or f.get("unit")!="元" or f.get("currency")!="CNY"
            or "旧保险合同" not in str(f.get("source_limit",""))):
            raise ValueError("INSURANCE_P10_MANAGEMENT_PREMIUM_TYPED_FACT_MISMATCH "+key)
        n=D(str(f.get("yuan","NaN")))
        if not n.is_finite() or n<0 or n.as_tuple().exponent < -2:
            raise ValueError("INSURANCE_NONFINITE_NEGATIVE_OR_INEXACT_PREMIUM "+key)
        return n
    vals={key:amt(key) for key,_ in SOURCES}
    new=amt("premium_new")
    total=amt("premium_total")
    renew=vals["premium_renew"]
    if (sum(vals.values(),D(0))!=total
        or sum((vals[k] for k in NEW),D(0))!=new
        or new+renew!=total or not new or not total):
        raise ValueError("INSURANCE_PREMIUM_4_TO_2_TO_1_ORIGINAL_P10_DOES_NOT_CLOSE")
    # Recorded CAS25 insurance-service income must not be presented as part
    # of an older-basis premium statistical total (p47 vs p10).
    service=facts.get("service_revenue",{})
    if (service.get("page")!=47 or service.get("period")!="2026H1"
        or service.get("type")!="flow" or service.get("currency")!="CNY"
        or D(str(service.get("yuan","NaN")))==total):
        raise ValueError("INSURANCE_SERVICE_REVENUE_MUST_STAY_SEPARATE_FROM_PREMIUM")
    return vals,new,renew,total


def render_insurance_premium(ledger:dict,*,mobile:bool=False)->str:
    vals,new,renew,total=_checked(ledger)
    W=D(330 if mobile else 1100)
    HVAL=D(143 if mobile else 268)
    scale=total/HVAL
    xsrc,xmid,xout=(D(17),D(143),D(262)) if mobile else (D(305),D(602),D(855))
    sw,mw,ow=(D(6),D(9),D(9)) if mobile else (D(14),D(16),D(15))
    src_gap=D(42 if mobile else 66)
    middle_gap=D(30 if mobile else 46)
    top=D(218 if mobile else 185)
    src=[]
    yy=top
    for key,name in SOURCES:
        h=vals[key]/scale
        src.append((key,name,vals[key],yy,h))
        yy+=h+src_gap
    new_y=top+D(3);renew_y=new_y+new/scale+middle_gap
    total_y=top+D(5)
    mid=[("premium_new","新单保费",new,new_y,PALETTE["profit"]),
         ("premium_renew","续期保费",renew,renew_y,GOLD)]
    bottom=max(yy-src_gap,renew_y+renew/scale,total_y+HVAL)
    H=bottom+D(153 if mobile else 175)
    out=[]
    if mobile:
        out.extend([
            text(13,23,"2026H1 · 中国人寿 · 保费统计原口径",11,PALETTE["ink"],700),
            text(13,43,"原始第10页 · 金额人民币亿元 · 流带同一比例",9,PALETTE["muted"]),
            text(13,63,"首年期交+趸交+短期险=新单；续期独立",9,PALETTE["muted"]),
            text(13,82,"注意：总保费不是CAS保险服务收入或实际收现",9,GOLD,700),
        ])
        for idx,(key,name,v,_,__) in enumerate(src):
            y=D(110)+D(idx)*D(22)
            out.append(text(13,y,name,10,PALETTE["ink"],600,role="premium-source-name"))
            out.append(text(315,y,fmt(v),10,PALETTE["source_dark"],600,"end",role="premium-source-money"))
        out.extend([text(13,top-14,"保费来源",10,PALETTE["muted"],600),
                    text(xmid+mw/2,top-14,"新单 / 续期",10,PALETTE["muted"],600,"middle"),
                    text(xout+ow/2,top-14,"总保费",10,PALETTE["muted"],600,"middle")])
    else:
        out.extend([text(25,36,"保费不等于保险服务收入 · 管理层旧合同统计 · 财报原文 p.10",16,PALETTE["ink"],700),
                    text(25,65,"四条保费来源先分为新单与续期，再汇成总保费；不连接现金、CSM及CAS25损益",13,PALETTE["muted"]),
                    text(xsrc,148,"四类互斥保费来源",17,PALETTE["ink"],700,"middle"),
                    text(xmid,148,"新单 / 续期",17,PALETTE["ink"],700,"middle"),
                    text(xout,148,"总保费",17,PALETTE["ink"],700,"middle")])
    # Draw exact original RMB-yuan width of both stages, no min-width padding.
    offsets={"premium_new":new_y,"premium_renew":renew_y}
    for key,name,value,sy,h in src:
        target="premium_renew" if key=="premium_renew" else "premium_new"
        target_y=offsets[target]
        color=GOLD if target=="premium_renew" else PALETTE["source"]
        out.append(path(xsrc+sw,sy,sy+h,xmid,target_y,target_y+h,color,value,scale,key,
                        "premium-source-to-new-or-renew",premium_bucket=target))
        offsets[target]+=h
    total_cursor=total_y
    for key,name,value,sy,color in mid:
        h=value/scale
        out.append(path(xmid+mw,sy,sy+h,xout,total_cursor,total_cursor+h,color,value,
                        scale,key,"new-or-renew-to-premium-total"))
        total_cursor+=h
    if abs(total_cursor-(total_y+HVAL))>=D(".00000001"):
        raise ValueError("INSURANCE_P10_RIBBON_GEOMETRIC_CLOSURE")
    for key,name,value,sy,h in src:
        out.append(rect(xsrc,sy,sw,h,PALETTE["source_dark"],
                        f'data-node-id="{key}" data-node-role="premium-source" data-node-yuan="{value}"'))
        if not mobile:
            out.append(text(25,sy-8,name,15,PALETTE["ink"],700,role="premium-source-name"))
            out.append(text(25,sy+12,fmt(value),14,PALETTE["muted"],600,role="premium-source-money"))
    for key,name,value,sy,color in mid:
        out.append(rect(xmid,sy,mw,value/scale,color,
                        f'data-node-id="{key}" data-node-role="premium-bucket" data-node-yuan="{value}"'))
        if not mobile:
            out.append(text(xmid+mw+D(12),sy+20,name,15,PALETTE["ink"],700))
            out.append(text(xmid+mw+D(12),sy+39,fmt(value),15,color,700))
    out.append(rect(xout,total_y,ow,HVAL,PALETTE["trunk"],
                    f'data-node-id="premium-total" data-node-role="premium-total" data-node-yuan="{total}"'))
    if not mobile:
        out.append(text(xout+ow+D(14),total_y+30,"管理层总保费",16,PALETTE["ink"],700))
        out.append(text(xout+ow+D(14),total_y+55,fmt(total),19,PALETTE["profit"],700))
    else:
        out.append(text(13,bottom+D(31),"保费统计组成（非保险服务收入）",11,PALETTE["ink"],700))
        out.append(text(13,bottom+D(53),"新单保费",10,PALETTE["ink"]))
        out.append(text(315,bottom+D(53),fmt(new),10,PALETTE["profit"],700,"end"))
        out.append(text(13,bottom+D(75),"续期保费",10,PALETTE["ink"]))
        out.append(text(315,bottom+D(75),fmt(renew),10,GOLD,700,"end"))
        out.append(text(13,bottom+D(97),"管理层合计",10,PALETTE["ink"],700))
        out.append(text(315,bottom+D(97),fmt(total),10,PALETTE["trunk"],700,"end"))
    note="原始2026半年报物理页10：四类保费、新单和续期（旧保险合同管理层统计）。不等于法定CAS25保险服务收入、现金收款、利润或保险合同负债。"
    if not mobile:
        out.append(text(25,bottom+D(42),"管理层总保费（旧保险合同统计）≠ CAS25保险服务收入 ≠ 实际现金收款",14,GOLD,700))
        out.append(text(25,bottom+D(67),note,11,PALETTE["muted"]))
    else:
        out.append(text(13,bottom+D(120),"物理页10来源与会计口径见下方逐图原始数据表",9,PALETTE["muted"]))
    desc=f"中国人寿2026H1旧保险合同保费四类来源合计{fmt(total)}，新单{fmt(new)}，续期{fmt(renew)}。{note}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        f'viewBox="0 0 {nu(W)} {nu(H)}" '
        f'data-design-system="FINANCIALS_UNIFIED_STORY_V1" '
        f'data-chart-grammar="INSURANCE_PREMIUM_SOURCE_NEW_RENEW_TOTAL" '
        f'data-accounting-basis="MANAGEMENT_LEGACY_PREMIUM_STATISTICS_NOT_CAS25" '
        f'data-issuer="601628" data-period="2026H1" data-premium-yuan="{total}" '
        f'data-scale-yuan-per-svg-unit="{scale}" '
        f'data-layout="{"mobile-editorial" if mobile else "desktop-editorial"}" '
        f'aria-label="{escape(desc,quote=True)}"><title>管理层总保费的真实原始来源与新续期汇总</title>'
        f'<desc>{escape(desc)}</desc>{"".join(out)}</svg>')
