"""Original 184-page 300308 exact-CNY P&L into the shared signed visual grammar.

Do not retrofit the 300394/300502 renderers on this change: their existing
published HTML remains byte-reproducible. This adapter requires 300308's
separately verified ORIGINAL 184-page PDF SHA/archive and refuses guessed
finance, cross-period, scope or monetary amounts. Unallocated operating
income remains an expressly derived DIFFERENCE, not product margin or cash.
"""
from __future__ import annotations
from decimal import Decimal as D
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[4]/"research/shared"))
from signed_statement_waterfall import SignedStage,SignedStatement,render_signed_statement,money


def original_plan(ledger:dict):
    doc=ledger.get("document",{})
    if (doc.get("ticker")!="300308.SZ" or doc.get("period_key")!="2026H1"
        or doc.get("currency")!="CNY" or doc.get("scope")!="consolidated"
        or doc.get("pages")!=184
        or not str(doc.get("source_archive_gate","")).startswith("PASS_EXACT_BYTES_2984970_SHA_E0ECD7C3")):
        raise ValueError("ZJ_ORIGINAL_184P_SOURCE_SCOPE_NOT_VERIFIED")
    original=ledger.get("facts",{})
    fields=("revenue","cogs","total_operating_costs","research_expenses",
            "financial_expenses","operating_profit","nonop_income",
            "nonop_expense","income_tax","net_profit")
    normalized={}
    for key in fields:
        v=original.get(key)
        if not isinstance(v,dict) or v.get("status")!="reported" or v.get("period")!="2026H1":
            raise ValueError("ZJ_REPORTED_CONSOLIDATED_FINANCE_FIELD_MISSING "+key)
        if v.get("kind")!="flow" or v.get("scope")!="consolidated" or v.get("table")!="income_statement":
            raise ValueError("ZJ_INCOMPATIBLE_FINANCIAL_FACT "+key)
        if not isinstance(v.get("page"),int) or not 1<=v["page"]<=184:
            raise ValueError("ZJ_UNVERIFIED_ORIGINAL_PAGE "+key)
        normalized[key]={"yuan":v["amount"],"page":v["page"],
                         "period":"2026H1","scope":"consolidated","unit":"元"}
    def v(key):return money(normalized[key]["yuan"])
    rev,cogs,other_total=v("revenue"),v("cogs"),v("total_operating_costs")
    if not (rev>0 and D(0)<=cogs<=other_total and other_total>0):
        raise ValueError("ZJ_REVENUE_COST_UNIT_MISMATCH")
    rd=v("research_expenses")
    fin=v("financial_expenses")
    rest=other_total-cogs-rd-fin
    if rest<0:raise ValueError("ZJ_UNEXPLAINED_NEGATIVE_OTHER_REPORTED_COST")
    op=v("operating_profit")
    residual=op-(rev-other_total)
    gross=rev-cogs
    stages=(
        SignedStage("gross","合并营业毛利",gross,("revenue","cogs"),"base"),
        SignedStage("research","减：研发费用",-rd,("research_expenses",)),
        SignedStage("finance","减：财务费用",-fin,("financial_expenses",)),
        SignedStage("other_period_cost","其余期间费用及税金（合并）",-rest,
            ("total_operating_costs","cogs","research_expenses","financial_expenses"),
            provenance="DERIVED_GROUP_COST_RESIDUAL_NOT_INVENTED_DETAIL"),
        SignedStage("other_operating","其余经营净收益（未归因）",residual,
            ("operating_profit","revenue","total_operating_costs"),
            provenance="DERIVED_UNATTRIBUTED_GROUP_OPERATING_NET_DIFFERENCE"),
        SignedStage("nonoperating","营业外净额",
            v("nonop_income")-v("nonop_expense"),
            ("nonop_income","nonop_expense")),
        SignedStage("income_tax","减：所得税费用",-v("income_tax"),("income_tax",)),
    )
    plan=SignedStatement(
        issuer="300308",statement="consolidated_income_2026H1",
        source_sha256=doc["source_sha256"],
        source_status="ORIGINAL_PDF_SHA256_VERIFIED",
        start_label="营业毛利",start_yuan=gross,
        start_fact_ids=("revenue","cogs"),
        stages=stages,checkpoints=(("other_operating","operating_profit"),),
        end_fact_id="net_profit",end_yuan=v("net_profit"))
    plan.check(normalized)
    return plan,normalized


def render_original_signed_pnl(ledger:dict,*,mobile:bool):
    plan,facts=original_plan(ledger)
    return render_signed_statement(plan,facts,mobile=mobile)
