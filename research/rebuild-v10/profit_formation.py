"""Source-typed, independently legible signed income-to-net formation.

An explicitly NAMED residual is not an invented operating expense. The
industrial margin must not swallow financial-subsidiary interest/fees. Do not
borrow an industrial profit flow for bank/insurer, or force a negative segment
into a positive connected income Sankey.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal as D
from html import escape as E
import re

YI=D("100000000")
INK="#193940"
SOURCE="#597A87"
COST="#BF7564"
GAIN="#23876E"
LINE="#CCDBD4"
MUTED="#536B67"

@dataclass(frozen=True)
class MoneyRow:
    key:str
    yuan:D
    page:int
    period:str

@dataclass(frozen=True)
class SignedStep:
    id:str
    title:str
    delta:D
    before:D
    after:D
    role:str
    evidence:str
    source_ids:tuple[str,...]=()

@dataclass(frozen=True)
class ProfitFormation:
    issuer:str
    sha:str
    sources:tuple[MoneyRow,...]
    steps:tuple[SignedStep,...]
    gross_profit:D
    group_total_revenue:D|None

def _yuan(value):
    value=D(str(value))
    if not value.is_finite():
        raise ValueError("NONFINITE_FINANCE_FACT")
    return value

def form_plan(code:str, facts:dict, source_sha:str)->ProfitFormation:
    if code not in {"688111","000333","600900","600276"}:
        raise ValueError("INDUSTRY_PROFIT_BRIDGE_INCOMPATIBLE_OR_UNSOURCED "+str(code))
    if not re.fullmatch(r"[0-9a-f]{64}",source_sha):
        raise ValueError("MISSING_COMPLETE_ORIGINAL_PDF_SHA")
    names=["rev","cogs","operating_profit",{"688111":"net_consolidated","000333":"consolidated_ni","600900":"net_profit","600276":"net_profit"}[code]]
    if code=="000333":
        names+=["total_rev","interest_income","fee_income"]
    sources=[]
    for key in names:
        item=facts.get(key)
        if not isinstance(item,dict) or "yuan" not in item:
            raise ValueError("SOURCE_FACT_NOT_DISCLOSED "+str(key))
        value=_yuan(item["yuan"])
        if not isinstance(item.get("page"),int) or item["page"]<=0 or item.get("period")!="2026H1":
            raise ValueError("SOURCE_FACT_PAGE_OR_FLOW_PERIOD_WRONG "+key)
        if item.get("status")=="DERIVED":
            raise ValueError("NOT_AN_ORIGINAL_DISCLOSED_LINE "+key)
        sources.append(MoneyRow(key,value,item["page"],item["period"]))
    v={row.key:row.yuan for row in sources}
    revenue,cogs,op,net=(v[n] for n in names[:4])
    if not (revenue>0 and D(0)<=cogs<=revenue and op>0 and net>0):
        raise ValueError("SIGNED_OR_INCOMPATIBLE_INDUSTRY_PROFILE")
    gross=revenue-cogs
    finance=D(0)
    group_total=None
    if code=="000333":
        finance=v["interest_income"]+v["fee_income"]
        group_total=v["total_rev"]
        if revenue+finance!=group_total or finance<0:
            raise ValueError("MIDEA_FINANCIAL_SUBSIDIARY_GROUP_REVENUE_NOT_CLOSED")
    rows=[
        SignedStep("income","营业收入（不含金融利息）" if code=="000333" else "营业收入",
                   revenue,D(0),revenue,"source","DISCLOSED",("rev",)),
        SignedStep("cost","减：披露营业成本",-cogs,revenue,gross,"cost","DISCLOSED",("cogs",)),
    ]
    running=gross
    if code=="000333":
        rows.append(SignedStep("finance_income","加：金融利息/手续费",finance,
                               running,running+finance,"source","DISCLOSED_SEPARATE_INCOME",
                               ("interest_income","fee_income","total_rev")))
        running+=finance
    # Explicit consolidated residuals. No issuer-level source allocation, no
    # unsupported labels such as "R&D expense" or "derivative hedge profit".
    residual=op-running
    rows.append(SignedStep("unallocated_operating",
                           "其余净影响（不能逐项归因）",residual,running,op,
                           "residual","DERIVED_UNATTRIBUTED_GROUP_NET_DIFFERENCE",
                           ("operating_profit",)))
    rows.append(SignedStep("nonoperating_tax",
                           "营业外/所得税净影响（合并）",net-op,op,net,
                           "residual","DERIVED_UNATTRIBUTED_NET_DIFFERENCE",
                           (names[3],)))
    rows.append(SignedStep("net_income","合并净利润",net,D(0),net,
                           "profit","DISCLOSED",(names[3],)))
    for row in rows:
        if row.before+row.delta!=row.after:
            raise ValueError("INVALID_SIGNED_CONSOLIDATED_PROFIT_CHAIN "+row.id)
        if min(row.before,row.after)<0:
            raise ValueError("NEGATIVE_CUMULATIVE_PROFIT_REQUIRES_SIGNED_ALTERNATIVE "+row.id)
    if rows[-2].after!=rows[-1].after or rows[1].after!=gross:
        raise ValueError("UNRECONCILED_GROUP_PROFIT_FORMATION")
    return ProfitFormation(code,source_sha,tuple(sources),tuple(rows),gross,group_total)

def _q(v):
    return format(v.quantize(D(".0001")),"f")
def _fmt(v):
    value=v/YI
    return f"{'+' if value>0 else ''}{value:,.2f}亿"
def _tag_text(x,y,s,*,size,fill=INK,anchor="start",weight=500,role=""):
    return (f'<text x="{_q(x)}" y="{_q(y)}" fill="{fill}" '
            f'font-family="Noto Sans CJK SC,PingFang SC,Arial,sans-serif" '
            f'font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" '
            f'data-editorial-role="{role}">{E(str(s))}</text>')

def render_svg(plan:ProfitFormation, *,mobile:bool=False)->str:
    width=D(330 if mobile else 1040)
    pad=D(13 if mobile else 32)
    area=width-2*pad
    max_value=max((max(s.before,s.after) for s in plan.steps),default=D(1))
    if max_value<=0:
        raise ValueError("ZERO_MONEY_AXIS")
    scale=max_value/area
    row_height=D(100 if mobile else 88)
    head=D(76 if mobile else 72)
    height=head+row_height*len(plan.steps)+D(18)
    out=[_tag_text(pad,D(27),"合并利润 · 有符号金额桥",
                   size=14 if mobile else 13,fill=MUTED,weight=700,role="figure-kicker"),
         _tag_text(pad,D(47),"同一金额比例尺；小额净差不人为放大",
                   size=12 if mobile else 13,fill=MUTED,role="scale-disclosure")]
    for i,row in enumerate(plan.steps):
        y=head+D(i)*row_height
        label=row.title
        if mobile and row.id=="unallocated_operating":
            label="其余净影响（未逐项归因）"
        if mobile and row.id=="nonoperating_tax":
            label="营业外/税项合并净影响"
        amount=_fmt(row.delta)
        out.append(_tag_text(pad,y,label,size=13 if mobile else 16,weight=700,role="step-label"))
        out.append(_tag_text(width-pad,y+D(21 if mobile else 0),amount,
                             size=13 if mobile else 15,anchor="end",
                             fill=COST if row.delta<0 else GAIN if row.role=="profit" else INK,
                             weight=700,role="step-money"))
        bar_y=y+D(39 if mobile else 17)
        out.append(f'<line x1="{_q(pad)}" y1="{_q(bar_y+D(8))}" x2="{_q(width-pad)}" '
                   f'y2="{_q(bar_y+D(8))}" stroke="{LINE}" stroke-width=".7"/>')
        left=pad+min(row.before,row.after)/scale
        bar_width=abs(row.delta)/scale
        fill=SOURCE if row.role=="source" else COST if row.delta<0 else GAIN
        if row.role=="residual" and row.delta>=0:
            fill=GAIN
        # A genuinely tiny delta may be subpixel. The adjacent number always
        # carries the exact amount, without decorative minimum ribbon widths.
        out.append(f'<rect x="{_q(left)}" y="{_q(bar_y)}" width="{_q(bar_width)}" '
                   f'height="16" rx="1" fill="{fill}" '
                   f'data-step-id="{E(row.id)}" data-delta-yuan="{row.delta}" '
                   f'data-before-yuan="{row.before}" data-after-yuan="{row.after}" '
                   f'data-money-scale-yuan-per-unit="{scale}" '
                   f'data-step-evidence="{row.evidence}" '
                   f'data-source-fact-ids="{E(",".join(row.source_ids))}"/>')
        out.append(_tag_text(pad,y+D(78 if mobile else 63),
                             "累积 "+_fmt(row.after) if row.id!="net_income" else "终值 "+_fmt(row.after),
                             size=12 if mobile else 12,fill=MUTED,role="cumulative"))
    layout="native-mobile-330" if mobile else "desktop-1040"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_q(width)} {_q(height)}" '
            f'role="img" aria-label="披露收入、成本与合并净利润的可勾稽有符号桥；未披露单项仅显示净差额" '
            f'data-profit-grammar="DISCLOSED_INCOME_TO_NET_SIGNED_CONSOLIDATED_BRIDGE" '
            f'data-issuer="{plan.issuer}" data-period="2026H1" data-layout="{layout}" '
            f'data-revenue-yuan="{plan.steps[0].after}" '
            f'data-gross-yuan="{plan.gross_profit}" '
            f'data-net-yuan="{plan.steps[-1].after}" '
            f'data-source-pdf-sha256="{plan.sha}" '
            f'data-residual-status="DERIVED_UNATTRIBUTED_NOT_CAUSAL" '
            f'data-yuan-per-svg-unit="{scale}">'
            f'<title>营业收入至合并净利润 · 保留披露与残差边界</title>'
            f'<desc>报告财务元金额真实比例，任何残差均只表示已披露合计之间的净差，不是具体费用、金融子公司利润或因果归因。</desc>'
            +''.join(out)+'</svg>')

def render_profit_formation(code:str, facts:dict, source_sha:str, pdf_url:str)->str:
    plan=form_plan(code,facts,source_sha)
    if not pdf_url.startswith("https://"):
        raise ValueError("ORIGINAL_DISCLOSURE_PDF_LINK_REQUIRED")
    source_rows=[]
    source_labels={"rev":"营业收入", "cogs":"营业成本", "operating_profit":"营业利润",
                   "net_consolidated":"合并净利润", "consolidated_ni":"合并净利润",
                   "net_profit":"合并净利润", "total_rev":"营业总收入",
                   "interest_income":"金融利息收入", "fee_income":"金融手续费收入"}
    for row in plan.sources:
        source_rows.append(
            f'<tr data-fact-id="{E(row.key)}" data-exact-yuan="{row.yuan}" '
            f'data-period="{row.period}" data-physical-page="{row.page}">'
            f'<td>{E(source_labels[row.key])}</td><td>{row.yuan:,.2f} 元</td>'
            f'<td><a href="{E(pdf_url,quote=True)}#page={row.page}" target="_blank" '
            f'rel="noopener">原始 PDF p.{row.page}</a></td></tr>')
    finance_note=('美的的财务子公司利息与手续费收入先单独加回到集团总收入；'
                  '这不是工业毛利，集团其余成本和利润影响不得假设全部来自工业主业。'
                  if code=="000333" else
                  "水电业务的财务费用与投资收益须按披露符号复核，不能把毛利到营业利润净差额全标成发电成本。" if code=="600900" else
                  "医药业务销售、研发和管理开支及许可收入需分别理解，净差额并不证明某一款药物贡献了集团利润。" if code=="600276" else
                  '金山办公投资收益可能进入营业利润，不可把毛利到营业利润的净差额简单标成期间费用。')
    return (f'<section class="profit-formation" id="profit-formation-{code}" '
            f'data-profit-formation="SOURCE_BOUND_SIGNED_V1" '
            f'data-issuer="{code}" data-source-pdf-sha256="{source_sha}" '
            f'data-unattributed-steps="2">'
            f'<div class="tag">利润形成 · 来源可核对</div>'
            f'<h3>收入怎样经过成本，最终成为合并净利润？</h3>'
            f'<p class="profit-formation-lead">这是同一报告期间的有符号会计累计桥，不是把所有金额强制画成一条桑基流。'
            f'每步按实际人民币元比例绘制；未取得逐项明细的两段仅显示有明确标注的净差额，不虚构归因。</p>'
            f'<div class="profit-viz profit-viz-desktop">{render_svg(plan,mobile=False)}</div>'
            f'<div class="profit-viz profit-viz-phone">{render_svg(plan,mobile=True)}</div>'
            f'<p class="profit-formation-caveat">{E(finance_note)} 营业利润至合并净利润净差额不代表单独的所得税金额，'
            f'还包含营业外净损益。源事实经选定 PDF 页码核验；具体净残差构成与因果归因仍须专项附注复核。</p>'
            f'<details class="profit-source-table"><summary>查看全部原始元金额、报告页码及会计残差口径</summary>'
            f'<table><thead><tr><th>原报表行项</th><th>精确元金额</th><th>原始来源</th></tr></thead>'
            f'<tbody>{"".join(source_rows)}</tbody></table>'
            f'<p>集团毛利（营业收入－营业成本）：{plan.gross_profit:,.2f} 元；'
            f'营业利润：{next(s.after for s in plan.steps if s.id=="unallocated_operating"):,.2f} 元；'
            f'合并净利润：{plan.steps[-1].after:,.2f} 元。</p>'
            f'<p>原始 PDF SHA-256：<code>{source_sha}</code>；独立财务分析师/视觉总编验收：尚未核验。</p>'
            f'</details></section>')
