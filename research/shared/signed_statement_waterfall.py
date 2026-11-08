"""Shared, source-typed signed statement graphic (not a positive-money Sankey).

A single Decimal accounting plan yields both desktop and native phone vector art.
The workhorse intentionally allows negative interim profit and zero source rows.
No decorative minimum-width bars, fabricated cash edges, or silent relabeling
of source pages. Industry adapters supply their own lawful stage composition.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal as D
from html import escape as E

from unified_income_sankey import PALETTE

COLORS={"ink":PALETTE["ink"],"positive":PALETTE["profit"],
        "negative":PALETTE["cost"],"base":PALETTE["source_dark"],
        "muted":PALETTE["muted"],"rule":PALETTE["rule"]}
YI=D("100000000")


def money(v):
    z=D(str(v))
    if not z.is_finite():raise ValueError("SIGNED_NONFINITE_MONEY")
    return z


def _fmt(z,dp=4):
    return format(money(z).quantize(D(1).scaleb(-dp)),"f")


def _label(z):
    x=money(z)/YI
    return f"{'+' if x>0 else ''}{x:,.2f} 亿"


@dataclass(frozen=True)
class SignedStage:
    id:str
    name:str
    delta:D
    source_ids:tuple[str,...]
    role:str="ordinary"   # base, ordinary, checkpoint
    provenance:str="DISCLOSED_OR_EXACT_ARITHMETIC"


@dataclass(frozen=True)
class SignedStatement:
    issuer:str
    statement:str
    source_sha256:str
    source_status:str
    start_label:str
    start_yuan:D
    start_fact_ids:tuple[str,...]
    stages:tuple[SignedStage,...]
    checkpoints:tuple[tuple[str,str],...]  # (stage id, disclosed fact key)
    end_fact_id:str
    end_yuan:D

    def check(self,facts:dict)->tuple[tuple[SignedStage,D,D,tuple[int,...]],...]:
        if len(self.source_sha256)!=64 or any(ch not in "0123456789abcdef" for ch in self.source_sha256):
            raise ValueError("SIGNED_SOURCE_SHA_NOT_PROVEN")
        if self.source_status not in ("MIRROR_COMPLETE_PDF_SHA_PASS__OFFICIAL_EQUIVALENCE_NOT_CHECKED",
                                     "ORIGINAL_PDF_SHA256_VERIFIED"):
            raise ValueError("SIGNED_UNVERIFIED_ORIGIN_STATUS")
        if not self.stages or self.stages[0].role!="base" or len(set(z.id for z in self.stages))!=len(self.stages):
            raise ValueError("SIGNED_MISSING_OR_DUPLICATED_STAGES")
        if self.stages[0].delta!=self.start_yuan:
            raise ValueError("SIGNED_BASE_AMOUNT_MISMATCH")
        for z in self.stages:
            if not z.id or not z.name or not z.source_ids or z.role not in ("base","ordinary","checkpoint"):
                raise ValueError("SIGNED_UNEXPLAINED_STAGE "+z.id)
        all_ids=set(self.start_fact_ids)|{self.end_fact_id}
        for z in self.stages:all_ids.update(z.source_ids)
        all_ids.update(fact for _,fact in self.checkpoints)
        for key in all_ids:
            v=facts.get(key)
            if not isinstance(v,dict):
                raise ValueError("SIGNED_DISCONNECTED_FACT "+key)
            if v.get("scope")!="consolidated" or v.get("period")!="2026H1" or v.get("unit")!="元":
                raise ValueError("SIGNED_CROSS_PERIOD_SCOPE_UNIT "+key)
            if not isinstance(v.get("page"),int) or v["page"]<=0:
                raise ValueError("SIGNED_MISSING_SOURCE_PAGE "+key)
            money(v["yuan"])
        current=D(0)
        rows=[]
        checks=dict(self.checkpoints)
        for z in self.stages:
            start=current
            current+=money(z.delta)
            if z.id in checks and current!=money(facts[checks[z.id]]["yuan"]):
                raise ValueError("SIGNED_CHECKPOINT_ACCOUNTING_WRONG "+z.id)
            pages=tuple(sorted({facts[k]["page"] for k in z.source_ids}))
            rows.append((z,start,current,pages))
        if current!=self.end_yuan or current!=money(facts[self.end_fact_id]["yuan"]):
            raise ValueError("SIGNED_END_NET_PROFIT_NOT_CLOSED")
        if self.start_yuan!=money(facts[self.start_fact_ids[0]]["yuan"])-money(facts[self.start_fact_ids[1]]["yuan"]):
            raise ValueError("SIGNED_SOURCE_GROSS_NOT_CLOSED")
        if any(key not in {x.id for x in self.stages} for key in checks):
            raise ValueError("SIGNED_UNKNOWN_CHECKPOINT")
        return tuple(rows)


def render_signed_statement(plan:SignedStatement,facts:dict,*,mobile:bool)->str:
    rows=plan.check(facts)
    width=D(330 if mobile else 1040)
    left=D(16 if mobile else 35)
    right=width-left
    row_h=D(94 if mobile else 89)
    top=D(82 if mobile else 100)
    height=top+row_h*len(rows)+D(26)
    lo=min([D(0)]+[min(a,b) for _,a,b,_ in rows])
    hi=max([D(0)]+[max(a,b) for _,a,b,_ in rows])
    span=hi-lo
    if span<=0:raise ValueError("SIGNED_EMPTY_DOMAIN")
    scale=span/(right-left)
    axis=left+(D(0)-lo)/scale
    def t(x,y,words,size,*,fill=COLORS["ink"],weight=600,anchor="start",role=""):
        return (f'<text x="{_fmt(x)}" y="{_fmt(y)}" font-size="{size}" '
                f'fill="{fill}" font-weight="{weight}" text-anchor="{anchor}" '
                f'font-family="Noto Sans CJK SC,PingFang SC,Arial,sans-serif" '
                f'data-editorial-role="{role}">{E(str(words))}</text>')
    out=[t(left,24,"SIGNED PROFIT FORMATION / ORIGINAL CNY",10 if mobile else 14,
           fill=COLORS["muted"],weight=750,role="kicker"),
         t(left,47,"零点与每一步金额使用同一比例尺；负值保留方向",
           10 if mobile else 13,fill=COLORS["muted"],role="scale-law"),
         f'<line x1="{_fmt(axis)}" x2="{_fmt(axis)}" y1="{_fmt(top-9)}" '
         f'y2="{_fmt(height-35)}" stroke="{COLORS["muted"]}" '
         f'opacity=".6" stroke-dasharray="4 5" stroke-width="1" data-axis-yuan="0"/>']
    for i,(z,before,after,pages) in enumerate(rows):
        y=top+row_h*i
        x=left+(min(before,after)-lo)/scale
        w=abs(z.delta)/scale
        positive=z.delta>0
        color=COLORS["base"] if z.role=="base" else COLORS["positive"] if positive else COLORS["negative"]
        print_name=z.name
        if mobile and print_name=="扣减：销售、管理费用":
            print_name="销售与管理费用"
        if mobile and print_name=="扣减：税金及财务费用":
            print_name="税金及财务费用"
        out.append(t(left,y,print_name,11 if mobile else 16,weight=700,role="signed-stage-label"))
        out.append(t(right,y+D(19 if mobile else 0),_label(z.delta),
                     11 if mobile else 16,fill=color,weight=750,anchor="end",role="signed-exact-change"))
        bar_y=y+D(35 if mobile else 21)
        out.append(f'<line x1="{_fmt(left)}" y1="{_fmt(bar_y+9)}" '
                   f'x2="{_fmt(right)}" y2="{_fmt(bar_y+9)}" '
                   f'stroke="{COLORS["rule"]}" stroke-width="0.65"/>')
        ids=",".join(z.source_ids)
        out.append(f'<rect x="{_fmt(x)}" y="{_fmt(bar_y)}" width="{_fmt(w,7)}" height="18" rx="1" '
                   f'fill="{color}" class="unified-signed-statement-step" '
                   f'data-stage-id="{E(z.id)}" data-before-yuan="{before}" '
                   f'data-signed-yuan="{z.delta}" data-after-yuan="{after}" '
                   f'data-money-scale-yuan-per-unit="{scale}" '
                   f'data-source-fact-ids="{E(ids)}" data-physical-pages="{",".join(map(str,pages))}" '
                   f'data-money-provenance="{E(z.provenance)}"><title>'
                   f'{E(z.name)}：{E(str(z.delta))}元，累计{E(str(after))}元；原始PDF物理页'
                   f'{",".join(map(str,pages))}</title></rect>')
        out.append(t(left,y+D(73 if mobile else 68),
                     "累计 "+_label(after),10 if mobile else 13,
                     fill=COLORS["muted"],role="cumulative-net-position"))
    source_scope=("完整原始 PDF 副本 SHA 已核验；交易所官网与副本字节同一性尚未验证"
                  if "MIRROR" in plan.source_status else "原始 PDF SHA 核验")
    desc=("合并利润表金额带符号同轴呈现；累计利润允许短暂转负。"
          "研发、费用、公允价值与减值、营业外和税项各自保留会计符号；"
          "这不是经营现金流或分部利润来源桑基图。"+source_scope)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {_fmt(width,0)} {_fmt(height,0)}" '
            f'role="img" aria-label="{E(desc)}" '
            f'data-signed-statement-grammar="FINANCIALS_TYPED_FULL_PNL_SIGNED_V1" '
            f'data-issuer="{E(plan.issuer)}" data-accounting-scope="consolidated" '
            f'data-period="2026H1" data-layout="{"native-330" if mobile else "editorial-1040"}" '
            f'data-original-pdf-sha256="{E(plan.source_sha256)}" '
            f'data-source-status="{E(plan.source_status)}" '
            f'data-start-gross-yuan="{plan.start_yuan}" data-end-net-yuan="{plan.end_yuan}" '
            f'data-money-scale-yuan-per-unit="{scale}" '
            f'data-negative-intervals-preserved="true"><title>完整合并利润表有符号逐步拆解</title>'
            f'<desc>{E(desc)}</desc>{"".join(out)}</svg>')
