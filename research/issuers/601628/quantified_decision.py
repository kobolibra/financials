"""Original-CAS insurance research decision, not a premium-to-service Sankey.

All fact references keep period, CNY, consolidated source, physical PDF page.
The fair-value and insurance-finance changes are two signed accounting lines,
not evidence of an independently identified matching/causal response.
"""
from __future__ import annotations
from decimal import Decimal as D
from html import escape as E
import re

FACT_SPEC = {
    "premium_total":("2026H1","flow"), "premium_prior":("2025H1","flow"),
    "service_revenue":("2026H1","flow"), "service_revenue_prior":("2025H1","flow"),
    "parent_net":("2026H1","flow"), "parent_net_prior":("2025H1","flow"),
    "fairvalue_income":("2026H1","flow"), "fairvalue_income_prior":("2025H1","flow"),
    "insurance_finance":("2026H1","flow"), "insurance_finance_prior":("2025H1","flow"),
    "cfo":("2026H1","flow"), "cfo_prior":("2025H1","flow"),
    "csm":("2026-06-30","stock"),
}

def decisions(ledger):
    source=ledger["source"]
    if (ledger["issuer"]["code"]!="601628" or
        ledger["issuer"]["fiscal_period"]!="2026H1" or
        source.get("original_bytes_gate")!="COMPLETE_ARCHIVED_PDF_SHA_PASS" or
        not re.fullmatch("[0-9a-f]{64}",source.get("original_bytes_sha256",""))):
        raise AssertionError("INSURER_DECISION_SOURCE_IDENTITY_INVALID")
    values={}
    for key,(period,kind) in FACT_SPEC.items():
        fact=ledger["facts"].get(key,{})
        if (fact.get("period")!=period or fact.get("type")!=kind
            or fact.get("scope")!="consolidated"
            or fact.get("classification")!="DISCLOSED"
            or fact.get("unit")!="元" or fact.get("currency")!="CNY"
            or fact.get("page_semantic_review")!="ORIGINAL_REPORT_TABLE_COLUMN_REVIEWED"
            or type(fact.get("page")) is not int or not 1<=fact["page"]<=source["physical_pages_observed"]):
            raise AssertionError("INSURER_DECISION_SOURCE_SEMANTIC_INVALID_"+key)
        v=D(str(fact["yuan"]))
        if not v.is_finite() or (v<0 and key not in ("insurance_finance","insurance_finance_prior")):
            raise AssertionError("INSURER_DECISION_AMOUNT_OR_SIGN_INVALID_"+key)
        values[key]=v
    for key in ("parent_net_prior","premium_prior","cfo_prior","service_revenue_prior"):
        if values[key]<=0:raise AssertionError("INSURER_DECISION_YOY_BASE_INVALID_"+key)
    ratios={
        "premium_yoy":(values["premium_total"]/values["premium_prior"]-1)*100,
        "service_yoy":(values["service_revenue"]/values["service_revenue_prior"]-1)*100,
        "parent_net_yoy":(values["parent_net"]/values["parent_net_prior"]-1)*100,
        "cfo_yoy":(values["cfo"]/values["cfo_prior"]-1)*100,
        "fair_value_delta_yuan":values["fairvalue_income"]-values["fairvalue_income_prior"],
        "insurance_finance_delta_yuan":values["insurance_finance"]-values["insurance_finance_prior"],
    }
    if ratios["fair_value_delta_yuan"]<=0 or ratios["insurance_finance_delta_yuan"]>=0:
        raise AssertionError("INSURER_DECISION_SIGNED_COMPARISON_CHANGED")
    return values,ratios

def render(ledger):
    values,ratios=decisions(ledger)
    source=ledger["source"]
    source_pdf=source["official_announcement"]
    def percent(key):return f'{ratios[key]:+,.2f}%'
    def yi(v):return f'{v/D(100000000):+,.2f}亿元'
    card_info=(
        ("parent_net_yoy","归母净利润同比 · 两个半年同期",percent("parent_net_yoy")),
        ("cfo_yoy","经营现金同比 · 两个半年同期",percent("cfo_yoy")),
        ("fair_value_delta_yuan","公允价值损益的法定同比变化",yi(ratios["fair_value_delta_yuan"])),
        ("insurance_finance_delta_yuan","承保财务损益的法定同比变化",yi(ratios["insurance_finance_delta_yuan"])),
    )
    cards="".join(
        f'<div class="insurance-decision-card" data-decision-key="{E(k)}" '
        f'data-derived-decimal="{E(format(ratios[k],"f"))}">'
        f'<small>{E(label)}</small><strong>{E(shown)}</strong></div>'
        for k,label,shown in card_info)
    lines=[]
    for key,(period,kind) in FACT_SPEC.items():
        fact=ledger["facts"][key]
        lines.append(
            f'<tr data-source-key="{E(key)}" data-period="{E(period)}" '
            f'data-financial-kind="{E(kind)}" data-exact-yuan="{E(format(values[key],"f"))}" '
            f'data-physical-page="{fact["page"]}">'
            f'<th scope="row">{E(fact["label"])}</th>'
            f'<td>{values[key]:,.2f}</td><td>{E(period)}</td>'
            f'<td><a href="{E(source_pdf,quote=True)}#page={fact["page"]}" '
            f'target="_blank" rel="noopener noreferrer">p.{fact["page"]}</a></td></tr>')
    return (
        f'<section class="insurance-decision" id="quantified-decision" '
        f'data-issuer="601628" data-pdf-sha256="{E(source["original_bytes_sha256"])}" '
        f'data-accounting-not-causal="true">'
        '<p class="insurance-decision-tag">THE DECISION / 可复算的寿险利润矛盾</p>'
        '<h2>保费增长不是利润增长：先拆保险服务，再看估值与负债计量。</h2>'
        f'<p class="insurance-decision-lead">管理层保费同比 {E(percent("premium_yoy"))}，'
        f'法定保险服务收入同比 {E(percent("service_yoy"))}；'
        f'归母净利润同比 {E(percent("parent_net_yoy"))}，'
        f'经营现金同比 {E(percent("cfo_yoy"))}。'
        '这是不同会计定义下的事实对照，不是把保费现金流进当期净利润。</p>'
        f'<div class="insurance-decision-grid">{cards}</div>'
        '<p class="insurance-decision-counter"><b>最强反证：</b>投资市场上涨带来的公允价值增量'
        '与保险财务负担的同比变化不能相加成已识别的投资阿尔法。'
        '若未来市场回落而服务利润与赔付现金没有同步改善，当期利润弹性可能不可持续。'
        'CSM 813,253 百万元是期末保险合同存量，不是本期保险服务收入或现金。</p>'
        '<details class="insurance-decision-evidence"><summary>查验 13 条原始元金额、时点／期间和财报物理页</summary>'
        '<div class="insurance-decision-table"><table><thead><tr><th>披露行项</th>'
        '<th>人民币元</th><th>期间</th><th>原件</th></tr></thead>'
        f'<tbody>{"".join(lines)}</tbody></table></div></details>'
        '<p class="insurance-decision-limit">以上仅证明可逐元复算的会计关系，不能识别市值、利率、'
        '保单流入与负债估值的因果或完全匹配比例。原始财报 p42 为有限保证审阅，不是审计意见。'
        '独立人类财务／视觉复核、同业估值与 8–12 个季度因果分析：NOT_CHECKED。</p>'
        '</section>'
    )
