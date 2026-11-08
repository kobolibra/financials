"""One finance-first visual grammar for every positive, conserved income flow.

This is a TRUE Sankey: individual source amounts physically merge into a
single revenue node and then branch into separately identified outcomes.
Every ribbon is source-accounting-bound, has exact Decimal yuan, and shares
one linear yuan-to-SVG scale within its own chart. Do NOT feed negative
profits, overlapping segments, period-mismatched facts or balance stocks.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal as D
from html import escape
from collections import defaultdict

PALETTE = {
    "page":"#F8F7F2", "ink":"#19333C", "muted":"#63747A",
    "source":"#9CABB2", "source_dark":"#657E89",
    "trunk":"#263F47", "cost":"#CD7271", "profit":"#239878",
    "rule":"#E4E4DE"
}

def yuan(v):
    x=D(str(v))
    if not x.is_finite():
        raise ValueError("NON_FINITE_MONEY")
    return x

def fmt(x):
    # Compact editorial labels only; full exact yuan lives in DOM attributes.
    y=yuan(x)/D(100000000)
    if y == 0:
        return "0"
    if abs(y)<D(".01"):
        # Never turn 79,769.92 original yuan into a misleading "0.001亿"
        # (approximately CNY 100,000). Use a suitable truthful small unit.
        return format(yuan(x)/D(10000),".2f")+"万"
    if abs(y)<D(1):
        return format(y,".3f")+"亿"
    return format(y,",.2f")+"亿"

def nu(x):
    return format(float(x),".4f")

def esc(x):
    return escape(str(x),quote=True)

def text(x,y,label,size=12,color=None,weight=500,anchor="start",role=""):
    return (f'<text x="{nu(x)}" y="{nu(y)}" fill="{color or PALETTE["ink"]}" '
            f'font-family="Noto Sans CJK SC,PingFang SC,Arial,sans-serif" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" '
            f'data-editorial-role="{esc(role)}">'
            f'{esc(label)}</text>')

def rect(x,y,w,h,color,metadata=""):
    if yuan(w)<0 or yuan(h)<0:
        raise ValueError("NEGATIVE_SIZE")
    return f'<rect x="{nu(x)}" y="{nu(y)}" width="{nu(w)}" height="{nu(h)}" fill="{color}" {metadata}/>'

def path(x0,top0,bot0,x1,top1,bot1,color,amount,scale,source_id,stage,**attrs):
    amount, scale = yuan(amount), yuan(scale)
    if amount < 0 or scale <= 0:
        raise ValueError("INVALID_SANKEY_PATH_AMOUNT_OR_SCALE")
    expected = amount / scale
    if (abs((yuan(bot0)-yuan(top0))-expected) >= D(".00000001")
            or abs((yuan(bot1)-yuan(top1))-expected) >= D(".00000001")):
        raise ValueError("SANKEY_PATH_GEOMETRY_DOES_NOT_CONSERVE")
    dx=(x1-x0)*D(".48")
    d=(f'M {nu(x0)} {nu(top0)} C {nu(x0+dx)} {nu(top0)} '
       f'{nu(x1-dx)} {nu(top1)} {nu(x1)} {nu(top1)} '
       f'L {nu(x1)} {nu(bot1)} C {nu(x1-dx)} {nu(bot1)} '
       f'{nu(x0+dx)} {nu(bot0)} {nu(x0)} {nu(bot0)} Z')
    extra=" ".join(f'data-{esc(k.replace("_","-"))}="{esc(v)}"' for k,v in attrs.items())
    return (f'<path d="{d}" fill="{color}" fill-opacity=".68" '
            f'data-source-id="{esc(source_id)}" data-stage="{esc(stage)}" '
            f'data-ribbon-yuan="{esc(amount)}" '
            f'data-scale-yuan-per-svg-unit="{esc(scale)}" {extra}/>')

@dataclass(frozen=True)
class FlowPlan:
    issuer:str
    kind:str
    title:str
    source_label:str
    outcome_label:str
    sources:tuple  # ((fact_id, display_name, amount_yuan), ...)
    outcomes:tuple # ((fact_id, display_name, amount_yuan, semantic: cost|profit),...)
    allocations:tuple=() # ((source_id, outcome_id, amount_yuan), ...); only TYPE_A
    footnote:str=""
    period:str="2026H1"

    def check(self):
        if self.kind not in ("TYPE_A_SOURCE_OWN_COST_GP","TYPE_B_GROUP_ONLY_GROSS_ALLOCATION",
                             "BANK_NET_INCOME_TO_OPERATING_PROFIT"):
            raise ValueError("WRONG_GRAMMAR_FOR_POSITIVE_MONEY_SANKEY")
        if not 2<=len(self.sources)<=8 or not 2<=len(self.outcomes)<=8:
            raise ValueError("SOURCES_AND_OUTCOMES_REQUIRED")
        sources={str(k):yuan(v) for k,_,v in self.sources}
        outcomes={str(k):yuan(v) for k,_,v,_ in self.outcomes}
        if len(sources)!=len(self.sources) or len(outcomes)!=len(self.outcomes):
            raise ValueError("DUPLICATE_NODE_IDENTIFIER")
        if any(v<0 for v in [*sources.values(),*outcomes.values()]):
            raise ValueError("NEGATIVE_IN_POSITIVE_FLOW")
        total=sum(sources.values(),D(0))
        if total<=0 or total!=sum(outcomes.values(),D(0)):
            raise ValueError("SOURCE_AND_OUTCOME_TOTAL_MISMATCH")
        if any(role not in ("cost","profit") for _,_,_,role in self.outcomes):
            raise ValueError("INVALID_OUTCOME_ROLE")
        if self.kind=="TYPE_A_SOURCE_OWN_COST_GP":
            if not self.allocations:
                raise ValueError("SOURCE_OWN_COST_CANNOT_BE_INFERRED_FROM_GROUP")
            seen=set()
            src_sums=defaultdict(lambda:D(0))
            sink_sums=defaultdict(lambda:D(0))
            for sid,oid,value in self.allocations:
                v=yuan(value)
                if str(sid) not in sources or str(oid) not in outcomes or v<0:
                    raise ValueError("INVALID_SOURCE_OWN_COST_LINK")
                if (sid,oid) in seen:
                    raise ValueError("DUPLICATE_SOURCE_OUTCOME")
                seen.add((sid,oid))
                src_sums[sid]+=v; sink_sums[oid]+=v
            if any(src_sums[sid]!=v for sid,v in sources.items()):
                raise ValueError("SOURCE_OWN_ALLOCATION_DOES_NOT_RECONCILE")
            if any(sink_sums[oid]!=v for oid,v in outcomes.items()):
                raise ValueError("OUTCOME_OWN_ALLOCATION_DOES_NOT_RECONCILE")
        elif self.allocations:
            raise ValueError("MUST_NOT_INVENT_PRODUCT_GP_OR_BANK_SUBSOURCE_EXPENSES")
        if not self.period or not self.issuer or not self.footnote:
            raise ValueError("UNSOURCED_OR_CONTEXTLESS_FINANCE")
        return total

def render_income_sankey(plan:FlowPlan, *, mobile:bool=False, embedded:bool=False):
    total=plan.check()
    W=D(330 if mobile else 1100)
    HVAL=D(142 if mobile else 286)
    scale=total/HVAL
    # Desktop has three distinct editorial rows per source (name/amount/GP).
    # 43-unit spacing makes near-zero disclosed sources collide with the prior
    # business label even though zero-width ribbon geometry remains correct.
    gap_src=D(25 if mobile else 70)
    gap_out=D(31 if mobile else 55)
    if mobile:
        xsrc,xrev,xout=D(15),D(149),D(260)
        left_width=6
        rev_width=D(10)
        # The source legend has one line per real source. Give it its
        # own height instead of drawing the fourth company over the header.
        top=D(173)+D(32)*D(max(0,len(plan.sources)-2))
        src_base=top; mid_base=top+D(7); sink_base=top+D(7)
        title_size=14
    else:
        xsrc,xrev,xout=D(310),D(603),D(859)
        left_width=12
        rev_width=D(16)
        top=D(195)
        src_base=top; mid_base=top+D(9); sink_base=top+D(9)
        title_size=25
    src_nodes=[]
    sink_nodes=[]
    pointer=src_base
    for sid,name,value in plan.sources:
        value=yuan(value)
        h=value/scale
        src_nodes.append((sid,name,value,pointer,h))
        pointer+=h+gap_src
    pointer=sink_base
    for oid,name,value,role in plan.outcomes:
        value=yuan(value)
        h=value/scale
        sink_nodes.append((oid,name,value,role,pointer,h))
        pointer+=h+gap_out
    chart_bottom=max(src_base+HVAL+gap_src*(len(plan.sources)-1),
                     sink_base+HVAL+gap_out*(len(plan.outcomes)-1))
    H=chart_bottom+D(120 if mobile else 140)
    out=[]
    title=plan.title
    if mobile:
        if not embedded:
            out.append(text(12,24,title[:23],title_size,weight=700))
        out.append(text(12,43,f'{plan.period} · 人民币亿元 · 金额按同一比例',10,PALETTE["muted"]))
        out.append(text(12,64,"灰色：收入来源    红色：成本    绿色：利润",10,PALETTE["muted"]))
        for i,(sid,name,v,_,__) in enumerate(src_nodes):
            leg_y=D(89+i*32)
            # Own line for the source and own line for money: never collide
            # with long Chinese names or the directly readable gross margin.
            out.append(text(12,leg_y,f'{i+1:02d}  {name}',11,PALETTE["ink"],600,role="source-summary"))
            label=fmt(v)
            if plan.allocations:
                own_gp=sum((yuan(value) for source,outcome,value in plan.allocations
                            if source==sid and any(key==outcome and role=="profit"
                                                   for key,_,_,role in plan.outcomes)),D(0))
                label+=f' · 毛利{own_gp/v*100:.1f}%'
            out.append(text(28,leg_y+D(15),label,11,PALETTE["source_dark"],600,role="source-summary"))
        out.append(text(12,top-D(16),"来源",10,PALETTE["muted"],600,role="source-stage-header"))
        out.append(text(xrev,top-D(16),"净收入合计" if plan.kind=="BANK_NET_INCOME_TO_OPERATING_PROFIT" else "总收入",10,PALETTE["muted"],600,"middle",role="total-stage-header"))
        out.append(text(xout,top-D(16),"去向",10,PALETTE["muted"],600,"middle"))
    else:
        if not embedded:
            out.append(text(26,46,title,28,PALETTE["ink"],700))
        out.append(text(26,76,f'{plan.period}  ·  CNY 亿元  ·  真实原始元面积守恒',15,PALETTE["muted"]))
        out.append(text(26,103,"收入来源汇总到一个总收入节点，然后流向合法的成本与利润去向；色带不设置虚假的最小金额宽度",12,PALETTE["muted"]))
        out.append(text(xsrc,160,plan.source_label,17,PALETTE["ink"],700,"middle"))
        out.append(text(xrev+rev_width/2,160,"合计收入",17,PALETTE["ink"],700,"middle"))
        out.append(text(xout,160,plan.outcome_label,17,PALETTE["ink"],700,"middle"))
    # SOURCE -> ONE shared revenue trunk. Inflow segments are continuous
    # inside that one trunk even when individual left sources have gaps.
    rev_cursor=mid_base
    src_center={}
    for i,(sid,name,value,sy,thick) in enumerate(src_nodes):
        src_center[sid]=(rev_cursor,thick)
        if value>0:
            out.append(path(xsrc+left_width,sy,sy+thick,
                            xrev,rev_cursor,rev_cursor+thick,PALETTE["source"],
                            value,scale,sid,"source-to-revenue"))
        rev_cursor+=thick
    # REVENUE -> COST/GP in exact source-aware allocations when known;
    # otherwise the GRAPH is truly group-only and must not tag fake per-source GP.
    sink_offsets={sid:yy for sid,_,_,_,yy,_ in sink_nodes}
    if plan.allocations:
        by_source={(s,o):yuan(v) for s,o,v in plan.allocations}
        for sid,_,value,_,_ in src_nodes:
            seg_start,thick=src_center[sid]
            row_offset=seg_start
            for oid,_,val,role,yy,_ in sink_nodes:
                v=by_source.get((sid,oid),D(0))
                if v==0:
                    continue
                target=sink_offsets[oid]
                color=PALETTE["profit"] if role=="profit" else PALETTE["cost"]
                # Additional audit hooks preserve exactly which own product
                # COGS/GP made each branch, never group-average attribution.
                own_cost=sum((by_source.get((sid,k),D(0)) for k,_,_,r in plan.outcomes if r=="cost"),D(0))
                own_gp=sum((by_source.get((sid,k),D(0)) for k,_,_,r in plan.outcomes if r=="profit"),D(0))
                out.append(path(xrev+rev_width,row_offset,row_offset+v/scale,
                                xout,target,target+v/scale,color,v,scale,sid,
                                "revenue-to-outcome", revenue_yuan=value,
                                cost_yuan=own_cost,gp_yuan=own_gp,outcome_id=oid))
                row_offset+=v/scale
                sink_offsets[oid]+=v/scale
            if abs(row_offset-(seg_start+thick))>D(".00000001"):
                raise ValueError("SOURCE_RIBBON_NOT_CONSERVED_GEOMETRICALLY")
    else:
        cursor=mid_base
        for oid,name,value,role,sy,thick in sink_nodes:
            if value>0:
                color=PALETTE["profit"] if role=="profit" else PALETTE["cost"]
                out.append(path(xrev+rev_width,cursor,cursor+thick,
                                xout,sy,sy+thick,color,value,scale,"GROUP",
                                "revenue-to-outcome",outcome_id=oid))
            cursor+=thick
    # Overlay exact, semantically meaningful three-column nodes.
    for i,(sid,name,v,sy,thick) in enumerate(src_nodes):
        out.append(rect(xsrc,sy,left_width,thick,PALETTE["source_dark"],
                        f'data-node-id="{esc(sid)}" data-node-yuan="{esc(v)}" data-node-role="source"'))
        if not mobile:
            out.append(text(24,sy-10,name,16,PALETTE["ink"],700,role="source-item-title"))
            out.append(text(24,sy+13,fmt(v),15,PALETTE["muted"],600,role="source-item-money"))
            if plan.allocations:
                own=[(o,yuan(a)) for s,o,a in plan.allocations if s==sid]
                profit=sum((a for oid,a in own if next(r for k,_,_,r in plan.outcomes if k==oid)=="profit"),D(0))
                out.append(text(24,sy+34,f'毛利率 {profit/v*100:.1f}%',13,PALETTE["profit"],700,role="source-item-margin"))
    out.append(rect(xrev,mid_base,rev_width,HVAL,PALETTE["trunk"],
                    f'data-node-id="revenue-total" data-node-yuan="{esc(total)}" data-node-role="total"'))
    if not mobile:
        out.append(text(xrev-7,mid_base-14,fmt(total),21,PALETTE["ink"],700,"end"))
    for oid,name,v,role,sy,thick in sink_nodes:
        color=PALETTE["profit"] if role=="profit" else PALETTE["cost"]
        out.append(rect(xout,sy,12 if not mobile else 9,thick,color,
                        f'data-node-id="{esc(oid)}" data-node-yuan="{esc(v)}" data-node-role="{role}"'))
        if not mobile:
            out.append(text(xout+29,sy+17,name,17,PALETTE["ink"],700))
            out.append(text(xout+29,sy+39,fmt(v),17,color,700))
        else:
            short=name.replace("营业","").replace("及管理","")
            if len(short)>4: short=short[:4]
            out.append(text(274,sy+10,short,10,color,700))
    if mobile:
        # The financial outcome list, accounting warning and source note are
        # stacked using ACTUAL row count, never fixed H offsets (which caused
        # the CMB amount + bank caveat + source note to overlap).
        footer=chart_bottom+D(27)
        out.append(text(12,footer,"成本与利润 · 对应原报表",11,PALETTE["ink"],700,role="outcome-list-title"))
        for i,(oid,name,v,role,_,__) in enumerate(sink_nodes):
            ypos=footer+D(20+i*20)
            out.append(text(12,ypos,name,10,PALETTE["ink"],500,role="outcome-value"))
            out.append(text(315,ypos,fmt(v),10,
                            PALETTE["profit"] if role=="profit" else PALETTE["cost"],
                            700,"end",role="outcome-value"))
        last_value_y=footer+D(20+(len(sink_nodes)-1)*20)
        hint_y=last_value_y+D(28)
        source_y=hint_y+D(20)
        if plan.kind=="TYPE_B_GROUP_ONLY_GROSS_ALLOCATION":
            out.append(text(12,hint_y,"未披露各业务毛利，不能倒推分部盈利",
                            10,PALETTE["cost"],700,role="accounting-limitation"))
        elif plan.kind=="BANK_NET_INCOME_TO_OPERATING_PROFIT":
            out.append(text(12,hint_y,"净利息已扣息，信用成本另列",
                            10,PALETTE["cost"],700,role="accounting-limitation"))
        else:
            out.append(text(12,hint_y,"各业务成本来自本业务披露",
                            10,PALETTE["muted"],700,role="accounting-limitation"))
        out.append(text(12,source_y,"详细来源和会计口径见下方数据表",
                        9,PALETTE["muted"],role="source-caveat"))
        H=max(H,source_y+D(21))
    else:
        # Give the last small source's directly labeled margin enough air
        # before a second hierarchy of accounting/editorial caveats.
        y=chart_bottom+D(67 if embedded else 47)
        if plan.kind=="TYPE_B_GROUP_ONLY_GROSS_ALLOCATION":
            out.append(text(26,y,"重要边界：仅集团合计成本和毛利，无法由此倒推各分部毛利率",16,PALETTE["cost"],700))
        elif plan.kind=="BANK_NET_INCOME_TO_OPERATING_PROFIT":
            out.append(text(26,y,"银行净利息收入已扣利息支出；仅分流经营费用、信用成本和营业利润",15,PALETTE["cost"],700))
        else:
            out.append(text(26,y,"各业务成本直接来自本业务披露；集团总毛利不等于归母净利润",15,PALETTE["muted"],600))
        if not embedded:
            out.append(text(26,y+28,plan.footnote[:78],12,PALETTE["muted"]))
        else:
            # Never silently truncate the reader's original-PDF source caveat
            # or print half an English sentence beyond the 1100 viewBox.
            # Approximate full-width Chinese as two display columns, Latin
            # as one; real Chromium bounding boxes remain the final gate.
            units=0
            pieces=[]
            part=""
            for ch in plan.footnote:
                next_units=2 if ord(ch)>127 else 1
                if part and units+next_units>140:
                    pieces.append(part)
                    part="";units=0
                part+=ch;units+=next_units
            if part:
                pieces.append(part)
            for i,line in enumerate(pieces):
                out.append(text(26,y+D(28)+D(20)*i,line,12,
                                PALETTE["muted"],role="source-footnote"))
            H=max(H,y+D(54)+D(20)*D(max(0,len(pieces)-1)))
    extra={
        "TYPE_A_SOURCE_OWN_COST_GP":'data-allocation-evidence="SOURCE_OWN_COST_GP"',
        "TYPE_B_GROUP_ONLY_GROSS_ALLOCATION":'data-gp-limitation="PRODUCT_LEVEL_GP_NOT_ESTABLISHED"',
        "BANK_NET_INCOME_TO_OPERATING_PROFIT":'data-bank-interest-already-net="true"',
    }[plan.kind]
    description=(f"{plan.issuer} {plan.period}. {plan.title}. "
                 f"收入合计{fmt(total)}. {plan.footnote}. "
                 f"全部原始人民币元金额在数据节点和色带属性中.")
    body="".join(out)
    if embedded:
        # The surrounding report already has its own editorial H3. Keep
        # meaningful period/margins, but do not repeat a competing title.
        # Compact only this embedded layout; no changes to source/path scale.
        shift=D(22 if mobile else 50)
        H-=shift
        body=f'<g transform="translate(0,-{nu(shift)})">{body}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {nu(W)} {nu(H)}" role="img" '
            f'data-design-system="FINANCIALS_UNIFIED_STORY_V1" '
            f'data-editorial-placement="{"embedded-article" if embedded else "standalone"}" '
            f'data-chart-grammar="SOURCE_REVENUE_OUTCOME_CONNECTED_SANKEY" '
            f'data-layout="{"mobile-editorial" if mobile else "desktop-editorial"}" '
            f'data-figure-kind="{esc(plan.kind)}" data-figure-id="{esc(plan.issuer)}-2" '
            f'data-issuer="{esc(plan.issuer)}" data-period="{esc(plan.period)}" '
            f'data-revenue-yuan="{esc(total)}" data-scale-yuan-per-svg-unit="{esc(scale)}" '
            f'{extra} aria-label="{esc(description)}"><title>{esc(plan.title)}</title>'
            f'<desc>{esc(description)}</desc>{body}</svg>')
