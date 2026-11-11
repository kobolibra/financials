"""Adapt original 2026H1 ledger classifications to ONE Sankey design grammar.

No per-issuer drawing code. Per-industry accounting type is selected by the
source-audited classifier; this layer only attaches original-fact ID, labels
and amounts. Own-cost allocations must be explicitly disclosed. Every
new positive Sankey uses unified_income_sankey.render_income_sankey().
"""
from __future__ import annotations

from decimal import Decimal as D
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"shared"))
from unified_income_sankey import FlowPlan, render_income_sankey


def plan_for(code:str, typed:dict, get, names:dict):
    kind=typed["kind"]
    if kind not in ("TYPE_A_SOURCE_OWN_COST_GP",
                    "TYPE_B_GROUP_ONLY_GROSS_ALLOCATION",
                    "BANK_NET_INCOME_TO_OPERATING_PROFIT"):
        raise ValueError("SIGNED_NEGATIVE_OR_INCOMPATIBLE_NOT_POSITIVE_SANKEY")
    original_sources=tuple(
        (key,names.get(key,key),str(get(code,key))) for key in typed["source_keys"]
    )
    total=D(typed["exact_yuan_total"])
    if sum((D(row[2]) for row in original_sources),D(0)) != total:
        raise ValueError("SOURCE_LEDGER_TOTAL_MISMATCH " + code)
    if kind=="TYPE_A_SOURCE_OWN_COST_GP":
        rows=typed["source_own_cost_gp"]
        expected_source={sid:D(amount) for sid,_,amount in original_sources}
        if len(rows)!=len(expected_source) or {sid for sid,_,_,_ in rows}!=set(expected_source):
            raise ValueError("SOURCE_OWN_ROW_IDENTITIES_MISMATCH " + code)
        for sid,revenue,cost,gross in rows:
            if D(revenue)!=expected_source[sid]:
                raise ValueError("SOURCE_OWN_REVENUE_ROW_MISMATCH " + sid)
            cost_key=typed.get("source_cost_keys",{}).get(sid)
            if cost_key and D(cost)!=D(get(code,cost_key)):
                raise ValueError("SOURCE_OWN_COST_ORIGINAL_FACT_MISMATCH " + sid)
            if D(cost)+D(gross)!=D(revenue):
                raise ValueError("SOURCE_OWN_COST_GP_ARITHMETIC_MISMATCH " + sid)
        costs=sum((D(c) for _,_,c,_ in rows),D(0))
        gp=sum((D(g) for _,_,_,g in rows),D(0))
        if costs!=D(typed["exact_yuan_cogs"]):
            raise ValueError("SOURCE_OWN_COST_TOTAL_MISMATCH " + code)
        if gp!=D(typed["exact_yuan_group_gp"]):
            raise ValueError("SOURCE_OWN_GP_TOTAL_MISMATCH " + code)
        # The group cost/GP sink is backed by separate independently
        # disclosed own-product cost/GP values, NOT by corporate average.
        allocations=tuple(
            pair
            for sid,revenue,cost,gross in rows
            for pair in ((sid,"group_cogs",str(cost)),
                         (sid,"group_gp",str(gross)))
        )
        return FlowPlan(
            issuer=code,kind=kind,
            title="哪些业务收入真正创造了集团毛利？",
            source_label=f"{len(original_sources)}项披露业务收入",outcome_label="集团毛利归因",
            sources=original_sources,
            outcomes=(("group_cogs","营业成本",str(costs),"cost"),
                      ("group_gp","营业毛利",str(gp),"profit")),
            allocations=allocations,
            footnote="每一项成本都属于该业务原始披露；毛利未扣销售研发费用、税费及投资收益",
        )
    if kind=="TYPE_B_GROUP_ONLY_GROSS_ALLOCATION":
        cost=D(typed["exact_yuan_cogs"])
        gp=D(typed["exact_yuan_group_gp"])
        if cost+gp!=total:
            raise ValueError("GROUP_COST_GP_TOTAL_MISMATCH " + code)
        return FlowPlan(
            issuer=code,kind=kind,
            title="哪些业务贡献收入，集团留下多少毛利？",
            source_label="同层级互斥业务收入",outcome_label="集团成本与毛利",
            sources=original_sources,
            outcomes=(("group_cogs","集团营业成本",str(cost),"cost"),
                      ("group_gp","集团营业毛利",str(gp),"profit")),
            footnote="未披露各业务自身毛利，不能根据集团合计倒推出每个业务的毛利率",
        )
    # Bank income is already NET interest / net fee / other net income:
    # NEVER subtract gross interest expense a second time.
    exp_keys=typed["expense_keys"]
    costs=tuple((key,names.get(key,key),str(get(code,key)),"cost")
                for key in exp_keys)
    op=D(typed["exact_yuan_result"])
    if sum((D(amount) for _,_,amount,_ in costs),D(0))+op!=total:
        raise ValueError("BANK_COST_OPERATING_PROFIT_TOTAL_MISMATCH " + code)
    return FlowPlan(
        issuer=code,kind=kind,
        title="银行净收入如何承担信用成本并留下营业利润？",
        source_label="净收入来源",outcome_label="营业费用与利润",
        sources=original_sources,
        outcomes=costs+(("operating_profit","营业利润",str(op),"profit"),),
        footnote="净利息收入已经扣除利息支出；信用减值和运营费用分别列示，不能重复扣息",
    )


def render_typed_finance(code,typed,get,names,*,mobile=False):
    plan=plan_for(code,typed,get,names)
    return render_income_sankey(plan,mobile=mobile,readable_source_rows=True)
