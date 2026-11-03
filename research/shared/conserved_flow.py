"""Reusable typed, exact-money source→cost/gross-profit flow contract.

No issuer code, account format or arbitrary visual minimum appears here.
For profitable, mutually exclusive non-negative segment revenue:
    each source_i = cost_i + gross_profit_i
    total_revenue = Σsource_i = total_cost + total_gp
Loss-making segments are NOT representable as this conserved nonnegative graph
and must use a signed bridge instead.
"""
from __future__ import annotations
from decimal import Decimal
from collections import Counter


def _amount(facts: dict, key: str) -> Decimal:
    try:
        value = Decimal(str(facts[key]["yuan"]))
    except (KeyError, ValueError, TypeError) as e:
        raise ValueError(f"MISSING_OR_INVALID_REPORTED_AMOUNT {key}: {e}") from e
    if not value.is_finite() or value.as_tuple().exponent < -2:
        raise ValueError(f"INVALID_YUAN_PRECISION {key}: {value}")
    return value


def _validate_same_basis(facts: dict, keys: list[str], source_period: str) -> None:
    for key in keys:
        x=facts[key]
        if x.get("currency") != "CNY" or x.get("unit") != "元":
            raise ValueError(f"SANKEY_CURRENCY_UNIT_MISMATCH {key}")
        if x.get("scope") != "consolidated" or x.get("period") != source_period:
            raise ValueError(f"SANKEY_SCOPE_PERIOD_MISMATCH {key}")
        if x.get("type") != "flow":
            raise ValueError(f"SANKEY_STOCK_CANNOT_FLOW {key}")
        if x.get("classification") not in ("DISCLOSED", "DISCLOSED_RESTATED"):
            raise ValueError(f"SANKEY_SOURCE_DISCLOSURE_REQUIRED {key}")
        if not isinstance(x.get("page"), int) or x["page"] < 1:
            raise ValueError(f"SANKEY_SOURCE_PAGE_MISSING {key}")


def build_conserved_income_flow(
    ledger: dict,
    *,
    group_field: str = "segments",
    revenue_total: str = "rev",
    cost_total: str = "cogs",
    required_dimension: str = "contract_goods_type",
) -> dict:
    """Build a canonical graph with source nodes, signed-gated edges and sinks.

    This function enforces *one* explicit product-class partition and rejects:
    mixed axes, duplicates, unknown residuals, loss-as-positive ribbon and
    non-reconciling partial disclosure. Never auto-add an "other" source.
    """
    facts=ledger["facts"]
    period=ledger["issuer"]["fiscal_period"]
    groups=ledger.get(group_field)
    if not isinstance(groups,list) or len(groups)<2:
        raise ValueError("SANKEY_EXCLUSIVE_SOURCES_NOT_DECLARED")
    for seg in groups:
        # Backward-compatible old ledgers may omit dimension; require the
        # common explicit dimension at graph invocation and encode it in output.
        dim=seg.get("dimension",required_dimension)
        if dim != required_dimension:
            raise ValueError("SANKEY_CROSS_DIMENSION_NOT_ADDITIVE")
    keys=[revenue_total,cost_total]
    keys += [k for item in groups for k in (item["rev"],item["cost"])]
    if len(keys)!=len(set(keys)):
        raise ValueError("SANKEY_DUPLICATE_FACT_OR_PARENT_CHILD")
    _validate_same_basis(facts,keys,period)
    seen=set();sum_rev=Decimal("0");sum_cost=Decimal("0")
    nodes=[];edges=[]
    for item in groups:
        name=item.get("label")
        if not name or name in seen or any(t in name for t in ("未知差额","未列示差额","虚构平衡")):
            raise ValueError(f"SANKEY_NON_EXCLUSIVE_OR_FABRICATED_SOURCE {name}")
        seen.add(name)
        rev=_amount(facts,item["rev"]);cost=_amount(facts,item["cost"])
        gp=rev-cost
        if rev < 0 or cost < 0 or gp < 0:
            raise ValueError(f"SANKEY_NEGATIVE_FLOW_USE_SIGNED_WATERFALL {name}")
        if rev == 0:
            raise ValueError(f"SANKEY_ZERO_DENOMINATOR {name}")
        sum_rev+=rev;sum_cost+=cost
        source_node={"key":item["rev"],"label":name,"yuan":f"{rev:.2f}",
                     "physical_page":facts[item["rev"]]["page"],"dimension":required_dimension}
        nodes.append(source_node)
        for kind,amount,dst in (("cost",cost,cost_total),("gp",gp,"gross_profit")):
            edges.append({"from":item["rev"],"to":dst,"kind":kind,"yuan":f"{amount:.2f}",
                          "source_business":name,
                          "physical_pdf_page":facts[item["cost"]]["page"] if kind=="cost" else facts[item["rev"]]["page"],
                          "scope":"consolidated","period":period,
                          "interpretation":"DISCLOSED_COGS" if kind=="cost" else "DERIVED_GP"})
    trev=_amount(facts,revenue_total);tcost=_amount(facts,cost_total)
    if sum_rev!=trev or sum_cost!=tcost:
        raise ValueError(f"SANKEY_NONCONSERVATION revenue_diff={sum_rev-trev} cost_diff={sum_cost-tcost}")
    if sum(x["yuan"] is None for x in edges):
        raise ValueError("SANKEY_UNKNOWN_VALUE")
    tgross=trev-tcost
    if sum((Decimal(e["yuan"]) for e in edges if e["kind"]=="gp"),Decimal("0")) != tgross:
        raise ValueError("SANKEY_GROSS_PROFIT_MISMATCH")
    return {"family":"source_conserved_revenue_to_cost_and_gp","source_dimensions":required_dimension,
            "issuer":ledger["issuer"]["code"],"period":period,"scope":"consolidated","unit":"CNY yuan",
            "source_pdf_sha256":ledger["source"].get("original_bytes_sha256","NOT_CHECKED"),
            "physical_page":facts[revenue_total]["page"],"nodes":nodes,"edges":edges,
            "sinks":[{"key":cost_total,"yuan":f"{tcost:.2f}"},{"key":"gross_profit","yuan":f"{tgross:.2f}"}],
            "revenue_yuan":f"{trev:.2f}","edge_count":len(edges),
            "accounting":"EXACT_DECIMAL_PASS","visual_minimum_thickness":0,
            "negative_flows":"MUST_USE_SIGNED_WATERFALL","cross_axis_merging":"FORBIDDEN"}
