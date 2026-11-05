"""Typed financial-flow editorial compiler: conservation is necessary, not enough.

Provides explicit A (source own cost/gross profit), B (group-only gross
allocation with mandatory limitation), C (omission with source-based reason).
No SVG is emitted from invalid/mixed-period or incorrectly grouped facts.
All amounts are original Decimal CNY yuan, never rounded display values.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal as D, InvalidOperation
from typing import Mapping, Sequence

class FlowSemanticError(ValueError):
    pass

@dataclass(frozen=True)
class FinanceFact:
    id: str
    yuan: str
    issuer: str
    period: str
    statement: str
    scope: str
    currency: str
    source_page: int
    group_axis: str = "disclosed"
    hierarchy_level: str = "top"
    parent_id: str | None = None

    @property
    def amount(self) -> D:
        try:
            d = D(str(self.yuan))
        except InvalidOperation as exc:
            raise FlowSemanticError(f"INVALID_ORIGINAL_DECIMAL_YUAN {self.id}") from exc
        if not d.is_finite():
            raise FlowSemanticError(f"NONFINITE_ORIGINAL_DECIMAL_YUAN {self.id}")
        return d

    @property
    def basis(self):
        return (self.issuer, self.period, self.statement, self.scope, self.currency)


@dataclass(frozen=True)
class FlowDecision:
    kind: str
    exact_yuan_total: str
    exact_yuan_group_cost: str
    exact_yuan_group_gp: str
    source_own_cost_gp: tuple[tuple[str, str, str, str], ...]
    reason: str
    source_to_total: tuple[tuple[str, str], ...]
    zero_width_is_zero: bool = True

    def width(self, yuan: str, total_width: str = "400") -> D:
        value = D(str(yuan))
        total = D(self.exact_yuan_total)
        if value < 0 or total <= 0:
            raise FlowSemanticError("NEGATIVE_OR_ZERO_SANKEY_WIDTH_NOT_ALLOWED")
        # Exact Decimal geometry before SVG serialization. NEVER max(1, x).
        return value * D(total_width) / total


def _check_fact(f: FinanceFact):
    if not f.id or not f.period or not f.issuer or not f.statement:
        raise FlowSemanticError("MISSING_TYPED_SOURCE_DIMENSIONS")
    if not isinstance(f.source_page, int) or f.source_page < 1:
        raise FlowSemanticError(f"ORIGINAL_PHYSICAL_PAGE_REQUIRED {f.id}")
    if f.currency != "CNY":
        raise FlowSemanticError(f"NON_CNY_SOURCE_MUST_RENORMALIZE_WITH_PROOF {f.id}")
    if not f.scope:
        raise FlowSemanticError("CONSOLIDATION_SCOPE_REQUIRED")
    _ = f.amount


def assess_financial_income_flow(
    sources: Sequence[FinanceFact],
    group_total: FinanceFact,
    group_cogs: FinanceFact,
    *,
    costs_by_source: Mapping[str, FinanceFact] | None = None,
    individual_costs_disclosed: bool = False,
    target_label: str = "operating_gross_profit",
    negative_cost_is_signed: bool = False,
) -> FlowDecision:
    allfacts = [*sources, group_total, group_cogs, *(costs_by_source or {}).values()]
    for f in allfacts:
        _check_fact(f)
    if not sources:
        raise FlowSemanticError("NO_EXCLUSIVE_SOURCE_INPUTS")
    basis = group_total.basis
    if any(f.basis != basis for f in allfacts):
        raise FlowSemanticError("PERIOD_CONSOLIDATION_OR_STATEMENT_SCOPE_MISMATCH")
    if group_total.statement != "operating_revenue" and group_total.statement != "bank_operating_income":
        raise FlowSemanticError("FLOW_STATEMENT_FAMILY_NOT_REVENUE_OR_BANK_OPERATING_INCOME")
    if group_total.currency != "CNY":
        raise FlowSemanticError("MIXED_CURRENCY_FLOW_CANNOT_BE_SOURCED")
    ids = [x.id for x in sources]
    if len(ids) != len(set(ids)):
        raise FlowSemanticError("DUPLICATED_SOURCE_GROUPS")
    if any(f.parent_id for f in sources):
        raise FlowSemanticError("PARENT_AND_CHILD_REVENUE_DOUBLE_COUNT")
    axes = {f.group_axis for f in sources}
    levels = {f.hierarchy_level for f in sources}
    if len(axes) != 1 or len(levels) != 1:
        raise FlowSemanticError("CROSS_AXIS_OR_LEVEL_SOURCES_CANNOT_ADD")
    if group_total.statement == "bank_operating_income" and group_cogs.id in {"interest_expense","interest_out"} and any(
            "net_interest" in f.id or f.id=="nii" for f in sources):
        raise FlowSemanticError("BANK_NET_INTEREST_DOUBLE_DEDUCTION")
    total = group_total.amount
    if total <= 0:
        raise FlowSemanticError("NONPOSITIVE_ACCOUNTING_TOTAL")
    src_total = sum((f.amount for f in sources), D(0))
    if src_total != total:
        raise FlowSemanticError(f"SOURCE_SUM_NOT_ACTUAL_REVENUE {src_total-total}")
    cogs = group_cogs.amount
    group_gp = total - cogs
    input_rows = tuple((f.id, str(f.amount)) for f in sources)
    if len(sources) == 1:
        return FlowDecision("TYPE_C_SANKEY_OMITTED",str(total),str(cogs),str(group_gp),(),
                           "SINGLE_SOURCE_GROUP_ONLY_NOT_MEANINGFUL",input_rows)
    if any(f.amount < 0 for f in sources) or cogs < 0 or group_gp < 0:
        return FlowDecision("TYPE_C_SANKEY_OMITTED",str(total),str(cogs),str(group_gp),(),
                           "NEGATIVE_SIGNED_FLOW_USE_WATERFALL",input_rows)
    if group_total.statement == "bank_operating_income" and costs_by_source is not None:
        raise FlowSemanticError("BANK_OPERATING_EXPENSES_CANNOT_AUTOMATICALLY_ALLOCATE_TO_NET_INCOME_COMPONENTS")
    if costs_by_source is None:
        if individual_costs_disclosed:
            raise FlowSemanticError("OWN_COGS_DISCLOSED_BUT_GROUP_ONLY_FLOW_WOULD_HIDE_PRODUCT_ECONOMICS")
        return FlowDecision(
            "TYPE_B_GROUP_ONLY_GROSS_ALLOCATION",str(total),str(cogs),str(group_gp),(),
            "PRODUCT_LEVEL_GP_NOT_ESTABLISHED",input_rows)
    if not individual_costs_disclosed:
        raise FlowSemanticError("UNREVIEWED_COST_ALLOCATION_CANNOT_BE_ASSUMED")
    if set(costs_by_source) != set(ids):
        raise FlowSemanticError("MISSING_OR_EXTRA_SOURCE_COST_FACTS")
    per = []
    for item in sources:
        cost = costs_by_source[item.id]
        own_cost = cost.amount
        own_gp = item.amount-own_cost
        if own_cost < 0 or own_gp < 0:
            return FlowDecision("TYPE_C_SANKEY_OMITTED",str(total),str(cogs),str(group_gp),(),
                               "AT_LEAST_ONE_PRODUCT_HAS_NEGATIVE_GROSS_PROFIT_OR_COST",input_rows)
        per.append((item.id,str(item.amount),str(own_cost),str(own_gp)))
    if sum((D(row[2]) for row in per),D(0)) != cogs:
        raise FlowSemanticError("SOURCE_COST_SUM_NOT_GROUP_COST")
    if sum((D(row[3]) for row in per),D(0)) != group_gp:
        raise FlowSemanticError("SOURCE_GP_SUM_NOT_GROUP_GP")
    return FlowDecision("TYPE_A_SOURCE_OWN_COST_GP",str(total),str(cogs),str(group_gp),tuple(per),
                        "EXACT_SOURCE_TO_OWN_COST_AND_GP",input_rows)
