"""Source-typed migration adapter for the two original V7 optical issuer ledgers.

No HTML renderer is silently swapped. Build original-yuan connected candidate
figures and reject bad facts before a future visual/source-SHA publication gate.
A new V7 issuer must prove a disjoint exhaustive revenue/cost partition.
"""
from __future__ import annotations
from decimal import Decimal as D
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from unified_income_sankey import FlowPlan,render_income_sankey


def optical_flow_plan(ledger: dict) -> FlowPlan:
    d=ledger.get("document",{})
    coverage=ledger.get("revenue_partition_assertion",{})
    facts=ledger.get("facts",{})
    segments=ledger.get("segments",[])
    issuer=d.get("ticker","").split(".")[0]
    period=d.get("period_key")
    if not issuer or not period or d.get("currency")!="CNY" or d.get("scope")!="consolidated":
        raise ValueError("OPTICAL_INCOMPATIBLE_ISSUER_PERIOD_CURRENCY_OR_SCOPE")
    if (coverage.get("completeness")!="exact_original_reported"
            or coverage.get("source_amounts")!="original yuan"
            or not coverage.get("source_page") or not coverage.get("scope")
            or not coverage.get("source_section")):
        raise ValueError("OPTICAL_EXHAUSTIVE_SOURCE_PARTITION_NOT_PROVEN")
    if not 2<=len(segments)<=8:
        raise ValueError("OPTICAL_VALID_DISJOINT_SOURCE_ROWS_REQUIRED")
    def value(key: str) -> D:
        f=facts.get(key)
        if not f or f.get("period")!=period or f.get("scope")!=d["scope"] or f.get("kind")!="flow":
            raise ValueError("OPTICAL_FACT_PERIOD_SCOPE_OR_KIND_MISMATCH "+str(key))
        if not isinstance(f.get("page"),int) or f["page"]<1:
            raise ValueError("OPTICAL_PHYSICAL_SOURCE_PAGE_MISSING "+str(key))
        v=D(str(f.get("amount","NaN")))
        if not v.is_finite():
            raise ValueError("OPTICAL_NONFINITE_OR_MISSING_YUAN "+str(key))
        return v
    revenue=value("revenue"); cogs=value("cogs")
    seen=set()
    sources=[]; alloc=[]; own_cost_total=D(0); own_revenue_total=D(0)
    for s in segments:
        key=s.get("revenue_key"); ck=s.get("cost_key")
        if not key or not ck or key==ck or key in seen or ck in seen:
            raise ValueError("OPTICAL_OVERLAPPING_OR_DUPLICATE_SOURCE_FACTS")
        seen.update((key,ck))
        if s.get("dimension") not in ("product","other_business"):
            raise ValueError("OPTICAL_CROSS_AXIS_SOURCE_MUST_BE_ADJUDICATED")
        name=s.get("name")
        if not name:
            raise ValueError("OPTICAL_UNNAMED_BUSINESS_SOURCE")
        r=value(key); c=value(ck)
        if r<=0 or c<0 or c>r:
            raise ValueError("OPTICAL_NEGATIVE_OR_NONPOSITIVE_SEGMENT_REQUIRES_SIGNED_ALTERNATIVE")
        own_revenue_total+=r; own_cost_total+=c
        sources.append((key,name,str(r)))
        alloc.extend(((key,"group_cogs",str(c)),(key,"group_gp",str(r-c))))
    if own_revenue_total!=revenue:
        raise ValueError("OPTICAL_SEGMENT_REVENUE_NOT_EXHAUSTIVE")
    if own_cost_total!=cogs:
        raise ValueError("OPTICAL_SEGMENT_COGS_NOT_EXHAUSTIVE")
    if revenue<=0 or cogs>revenue:
        raise ValueError("OPTICAL_TOTAL_CANNOT_RENDER_POSITIVE_SANKEY")
    return FlowPlan(issuer=issuer,period=period,kind="TYPE_A_SOURCE_OWN_COST_GP",
        title="业务收入如何形成真实披露的成本与毛利？",
        source_label="互斥披露业务收入",outcome_label="成本与毛利",
        sources=tuple(sources),
        outcomes=(("group_cogs","营业成本",str(cogs),"cost"),
                  ("group_gp","营业毛利",str(revenue-cogs),"profit")),
        allocations=tuple(alloc),
        footnote=(f"业务分组与成本来自原报告附注物理页 {coverage['source_page']}；"
                  f"{coverage['scope']}；不得跨业务类型和主营/其他分类重复加总。"))


def render_optical_candidate(ledger: dict, *, mobile:bool=False) -> str:
    return render_income_sankey(optical_flow_plan(ledger),mobile=mobile)
