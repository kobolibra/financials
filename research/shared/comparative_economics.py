"""Evidence-bound two-period industrial economics, independent of issuer codes.

Revenue/margin contributions are a symmetric accounting decomposition, NOT
identified price/volume/mix/FX effects. Exact rational arithmetic prevents a
repeating margin or the host Decimal context creating a hidden balancing item.
This module does not render bank/insurance income as industrial gross profit.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext, ROUND_HALF_EVEN
from fractions import Fraction
import re


def money(raw: str) -> Fraction:
    if not isinstance(raw, str) or not re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]{1,2})?", raw):
        raise ValueError("EXACT_YUAN_STRING_REQUIRED")
    try:
        return Fraction(Decimal(raw))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("INVALID_YUAN") from exc


def decimal_text(value: Fraction, places: int = 2) -> str:
    with localcontext() as ctx:
        ctx.prec=max(60,len(str(abs(value.numerator)))+len(str(value.denominator))+10)
        return format((Decimal(value.numerator)/Decimal(value.denominator)).quantize(
            Decimal(1).scaleb(-places),rounding=ROUND_HALF_EVEN), f".{places}f")


@dataclass(frozen=True)
class EconomicsPeriod:
    issuer: str
    period: str
    revenue_yuan: str
    cost_yuan: str
    revenue_fact: str
    cost_fact: str
    revenue_page: int
    cost_page: int
    pdf_sha256: str
    pdf_pages: int
    scope: str
    currency: str
    unit: str
    statement: str
    definition: str
    classification: str
    period_start: str
    period_end: str

    def check(self):
        from datetime import date
        if any(not isinstance(v,str) or not v.strip() for v in
               (self.issuer,self.period,self.revenue_fact,self.cost_fact,self.definition)):
            raise ValueError("ECONOMIC_EVIDENCE_IDENTITY_REQUIRED")
        if self.revenue_fact==self.cost_fact:
            raise ValueError("REVENUE_AND_COST_CANNOT_REUSE_ONE_FACT")
        if self.statement!="industrial_operating_income":
            raise ValueError("INDUSTRIAL_GP_ROUTE_REQUIRED")
        if self.scope!="consolidated" or self.currency!="CNY" or self.unit!="yuan":
            raise ValueError("ECONOMIC_SCOPE_CURRENCY_UNIT_MISMATCH")
        if self.classification not in ("DISCLOSED","DISCLOSED_RESTATED"):
            raise ValueError("DISCLOSED_COMPARABLE_STATEMENT_REQUIRED")
        if not re.fullmatch(r"[a-f0-9]{64}",self.pdf_sha256):
            raise ValueError("ORIGINAL_PDF_FINGERPRINT_REQUIRED")
        if type(self.pdf_pages) is not int or self.pdf_pages<1:
            raise ValueError("ORIGINAL_PDF_PAGECOUNT_REQUIRED")
        if any(type(p) is not int or not 1<=p<=self.pdf_pages
               for p in (self.revenue_page,self.cost_page)):
            raise ValueError("ORIGINAL_PDF_PHYSICAL_PAGE_OUT_OF_RANGE")
        start,end=date.fromisoformat(self.period_start),date.fromisoformat(self.period_end)
        if start>end or start.year!=end.year:
            raise ValueError("VALID_REPORT_FLOW_INTERVAL_REQUIRED")
        intervals={"H1":(1,1,6,30),"FY":(1,1,12,31),"9M":(1,1,9,30),
                   "Q1":(1,1,3,31),"Q2":(4,1,6,30),"Q3":(7,1,9,30),"Q4":(10,1,12,31)}
        key=self.period.removeprefix(str(start.year))
        if (not self.period.startswith(str(start.year)) or
                intervals.get(key)!=(start.month,start.day,end.month,end.day)):
            raise ValueError("PERIOD_LABEL_DOES_NOT_MATCH_FLOW_INTERVAL")
        revenue,cost=money(self.revenue_yuan),money(self.cost_yuan)
        if revenue<=0 or cost<0:
            raise ValueError("POSITIVE_REVENUE_NONNEGATIVE_COST_REQUIRED")
        return revenue,cost


def gross_profit_bridge(prior: EconomicsPeriod, current: EconomicsPeriod, *,
                        comparability_evidence: str) -> dict:
    """Return symmetric GP change and exact fraction proof, including losses.

    ΔGP = ΔR × (m0+m1)/2 + Δm × (R0+R1)/2.
    Both factors include half the interaction; reversing the periods reverses
    both effects. A loss is legal here because the output is a SIGNED bridge.
    """
    r0,c0=prior.check();r1,c1=current.check()
    if any(getattr(prior,k)!=getattr(current,k) for k in
           ("issuer","scope","currency","unit","statement","definition")):
        raise ValueError("INCOMPARABLE_ISSUER_OR_ECONOMIC_BASIS")
    from datetime import date
    a0,b0,a1,b1=map(date.fromisoformat,(prior.period_start,prior.period_end,current.period_start,current.period_end))
    if (a1.year!=a0.year+1 or b0>=a1 or prior.period==current.period
            or (a0.month,a0.day,b0.month,b0.day)!=(a1.month,a1.day,b1.month,b1.day)):
        raise ValueError("LIKE_FOR_LIKE_NONOVERLAPPING_FLOW_PERIODS_REQUIRED")
    if not isinstance(comparability_evidence,str) or len(comparability_evidence.strip())<20:
        raise ValueError("EXPLICIT_COMPARABILITY_EVIDENCE_REQUIRED")
    gp0,gp1=r0-c0,r1-c1
    m0,m1=gp0/r0,gp1/r1
    scale=(r1-r0)*(m0+m1)/2
    margin=(m1-m0)*(r0+r1)/2
    delta=gp1-gp0
    if scale+margin!=delta:
        raise ValueError("EXACT_SYMMETRIC_DECOMPOSITION_NOT_CLOSED")
    rounded_scale,rounded_margin=money(decimal_text(scale)),money(decimal_text(margin))
    # Visible rounding row is explicitly numerical, never an invented business.
    rounding=delta-rounded_scale-rounded_margin
    def exact(x):return {"numerator":str(x.numerator),"denominator":str(x.denominator)}
    def source(p):
        return {"period":p.period,"interval":[p.period_start,p.period_end],
                "pdf_sha256":p.pdf_sha256,"physical_pages":[p.revenue_page,p.cost_page],
                "fact_ids":[p.revenue_fact,p.cost_fact],
                "revenue_yuan":p.revenue_yuan,"cost_yuan":p.cost_yuan,
                "classification":p.classification}
    return {"schema":"financials.symmetric_gp_bridge.v1","issuer":current.issuer,
            "prior":source(prior),"current":source(current),
            "definition":current.definition,"comparability_evidence":comparability_evidence,
            "prior_gp_yuan":decimal_text(gp0),"current_gp_yuan":decimal_text(gp1),
            "delta_gp_yuan":decimal_text(delta),
            "prior_margin_pct":decimal_text(m0*100,4),"current_margin_pct":decimal_text(m1*100,4),
            "margin_change_pp":decimal_text((m1-m0)*100,4),
            "effects":[{"id":"revenue_base","label":"收入基数贡献","yuan":decimal_text(scale),"exact":exact(scale)},
                       {"id":"margin","label":"综合毛利率贡献","yuan":decimal_text(margin),"exact":exact(margin)}],
            "display_rounding_yuan":decimal_text(rounding),
            "interpretation":"ACCOUNTING_DECOMPOSITION_NOT_CAUSAL",
            "unidentified_drivers":["price","volume","mix","FX","consolidation"],
            "independent_financial_review":"NOT_CHECKED"}
