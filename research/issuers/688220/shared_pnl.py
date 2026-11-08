"""Source-typed ASR 688220 adaptation to canonical signed-statement grammar.

This is the FULL signed 2026H1 group P&L, not the source→gross-profit
Sankey and not a net profit attribution to individual chip products.
"""
from __future__ import annotations
from decimal import Decimal as D
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"shared"))
from signed_statement_waterfall import SignedStage,SignedStatement,render_signed_statement

def original_plan(ledger:dict)->SignedStatement:
    source=ledger["source"]
    facts=ledger["facts"]
    def v(k):return D(str(facts[k]["yuan"]))
    def step(ident,label,keys,sign=1,*,role="ordinary",provenance="DISCLOSED_OR_EXACT_ARITHMETIC"):
        return SignedStage(ident,label,sum((v(k) for k in keys),D(0))*sign,tuple(keys),role,provenance)
    stages=(
        SignedStage("gross","合并毛利润",v("rev")-v("cogs"),
                    ("rev","cogs"),"base"),
        step("rnd","扣减：研发费用",("rnd_expense",),-1),
        step("sales_admin","扣减：销售、管理费用",("sell","admin"),-1),
        step("tax_finance","扣减：税金及财务费用",("tax_surcharge","finance_expense"),-1),
        step("other_income","其他收益",("other_income",)),
        step("investment_income","投资收益",("investment_income",)),
        step("fair_value","公允价值变动收益",("fair_value_income",)),
        step("impair_disposal","信用、资产减值及处置损益",
             ("credit_impairment","asset_impairment","asset_disposal_gain"),
             provenance="SIGNED_DISCLOSED_LOSS_ROWS"),
        step("nonoperating","营业外收入扣减营业外支出",
             ("nonoperating_income","nonoperating_expense"),
             provenance="DISCLOSED_INCOME_MINUS_SOURCE_BLANK_DERIVED_ZERO"),
        step("income_tax","减：所得税费用（本期负数为收益）",
             ("income_tax_expense",),-1,
             provenance="NEGATIVE_REPORTED_TAX_EXPENSE_IS_TAX_BENEFIT"),
    )
    # The non-operating expense is blank in the original report; it is
    # explicitly source-led as derived zero and never passed off as print literal.
    stages=list(stages)
    stages[8]=SignedStage("nonoperating","营业外收入扣减营业外支出",
        v("nonoperating_income")-v("nonoperating_expense"),
        ("nonoperating_income","nonoperating_expense"),"ordinary",
        "DISCLOSED_INCOME_MINUS_SOURCE_BLANK_DERIVED_ZERO")
    p=SignedStatement(
        issuer="688220",statement="consolidated_income_2026H1",
        source_sha256=source["original_bytes_sha256"],
        source_status=source["original_bytes_gate"],
        start_label="合并营业毛利",start_yuan=v("rev")-v("cogs"),
        start_fact_ids=("rev","cogs"),stages=tuple(stages),
        checkpoints=(("impair_disposal","operating_profit"),
                     ("nonoperating","pretax_profit")),
        end_fact_id="consolidated_net_profit",
        end_yuan=v("consolidated_net_profit"))
    p.check(facts)
    return p


def render_asr_pnl(ledger:dict,*,mobile:bool)->str:
    return render_signed_statement(original_plan(ledger),ledger["facts"],mobile=mobile)
