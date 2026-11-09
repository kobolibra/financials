"""Reader-visible original-PDF optical decision evidence, not editorial certification.

The V7 article already has real Sankey and separate financial statements. This
module turns the most consequential accounting/operating conflict into a typed
falsifiable front-page analysis with exact original facts and source pages.

2025H1/2026H1 are comparable half-year *flows*. The previous 2025-12-31
inventory is a balance-sheet *stock*, never a same-quarter cash adjustment.
Reported mixed product revenue / rounded disclosed unit count is NOT ASP.
"""
from __future__ import annotations

from decimal import Decimal as D, InvalidOperation
from html import escape as E
import re

YI = D("100000000")
CONFIG = {
    "300394": (
        ("revenue", "2026H1", "flow", "元"),
        ("cogs", "2026H1", "flow", "元"),
        ("revenue_prior", "2025H1", "flow", "元"),
        ("cogs_prior", "2025H1", "flow", "元"),
        ("cfo", "2026H1", "flow", "元"),
        ("cfo_prior", "2025H1", "flow", "元"),
        ("inventory", "2026-06-30", "stock", "元"),
        ("inventory_prior", "2025-12-31", "stock", "元"),
    ),
    "300502": (
        ("revenue_optics", "2026H1", "flow", "元"),
        ("product_revenue_prior", "2025H1", "flow", "元"),
        ("product_volume_wan", "2026H1", "flow", "万只"),
        ("product_volume_wan_prior", "2025H1", "flow", "万只"),
        ("net_profit", "2026H1", "flow", "元"),
        ("cfo", "2026H1", "flow", "元"),
        ("inventory", "2026-06-30", "stock", "元"),
        ("inventory_prior", "2025-12-31", "stock", "元"),
    ),
}


def exact_source(l: dict, key: str, period: str, kind: str, unit: str) -> D:
    doc = l["document"]
    item = l["facts"].get(key, {})
    if (item.get("period") != period or item.get("kind") != kind
            or item.get("scope") != "consolidated"
            or item.get("status") != "reported"
            or not isinstance(item.get("page"), int)
            or not (1 <= item["page"] <= doc["pages"])
            or item.get("source_confidence") not in
            ("pdf_page_checked", "checked_against_uploaded_pdf")):
        raise ValueError("DECISION_ORIGINAL_FACT_PROVENANCE_INVALID " + key)
    if doc.get("currency") != "CNY" or doc.get("scope") != "consolidated":
        raise ValueError("DECISION_CONSOLIDATION_OR_CURRENCY_INVALID")
    if unit == "万只" and key not in ("product_volume_wan", "product_volume_wan_prior"):
        raise ValueError("DECISION_OPERATING_UNIT_MISMATCH " + key)
    if unit == "元" and key in ("product_volume_wan", "product_volume_wan_prior"):
        raise ValueError("DECISION_PHYSICAL_VOLUME_MISLABELED_MONEY " + key)
    try:
        value = D(str(item["amount"]))
    except (InvalidOperation, TypeError, KeyError) as exc:
        raise ValueError("DECISION_ORIGINAL_AMOUNT_NOT_DECIMAL " + key) from exc
    if not value.is_finite() or value < 0:
        raise ValueError("DECISION_ORIGINAL_AMOUNT_NONFINITE_OR_NEGATIVE " + key)
    return value


def pct(numerator: D, denominator: D, key: str) -> D:
    if denominator <= 0:
        raise ValueError("DECISION_INVALID_COMPARISON_BASE " + key)
    return numerator / denominator * D(100)


def display_pct(x: D) -> str:
    if not x.is_finite():
        raise ValueError("DECISION_NONFINITE_RESULT")
    return f"{x:+,.2f}%"


def money_yi(x: D) -> str:
    return f"{x / YI:,.2f} 亿元"


def decision_values(l: dict) -> dict:
    doc = l["document"]
    code = doc.get("ticker", "").split(".")[0]
    if code not in CONFIG or doc.get("period_key") != "2026H1" or doc.get("comparative_period_key") != "2025H1":
        raise ValueError("DECISION_UNSUPPORTED_ISSUER_OR_PERIOD")
    if (not re.fullmatch(r"[0-9a-f]{64}", doc.get("source_sha256", ""))
            or doc.get("audited") is not False):
        raise ValueError("DECISION_PDF_IDENTITY_OR_AUDIT_SCOPE_NOT_PROVEN")
    values = {k: exact_source(l, k, period, kind, unit)
              for k, period, kind, unit in CONFIG[code]}
    stock_change = pct(values["inventory"] - values["inventory_prior"],
                       values["inventory_prior"], "inventory_since_year_end")
    if code == "300394":
        gross = values["revenue"] - values["cogs"]
        prior_gross = values["revenue_prior"] - values["cogs_prior"]
        if gross <= 0 or prior_gross <= 0 or values["cfo_prior"] <= 0:
            raise ValueError("DECISION_GROSS_OR_CASH_SIGNED_EXCEPTION_REQUIRED")
        g = pct(gross - prior_gross, prior_gross, "gross_2025H1")
        c = pct(values["cfo"] - values["cfo_prior"],
                values["cfo_prior"], "cfo_2025H1")
        metrics = (
            ("gross_profit_yoy", "毛利同比 · 两个半年同期", g),
            ("cfo_yoy", "经营现金同比 · 两个半年同期", c),
            ("inventory_since_year_end", "存货余额较年末 · 两个时点", stock_change),
        )
        title = "毛利扩大、现金改善，却为何仍要追问库存兑现？"
        narrative = (f"营业毛利从 {money_yi(prior_gross)} 变为 {money_yi(gross)}；"
                     f"同口径经营现金变化 {display_pct(c)}。存货余额较2025年末变化"
                     f" {display_pct(stock_change)}，不能把期末存货差额当作经营现金流的间接调整。")
        contrary = "若后续存货周转和回款转弱，单期较高毛利率便不能独立证明增长质量。"
        provenance = "GROSS_CFO_HALF_YEAR_FLOW_VS_YEAR_END_INVENTORY_STOCK"
    else:
        if min(values["product_volume_wan"], values["product_volume_wan_prior"],
               values["net_profit"], values["product_revenue_prior"]) <= 0:
            raise ValueError("DECISION_PRODUCT_VOLUME_OR_NET_PROFIT_NONPOSITIVE")
        # The reported volume unit is 万只, an integer rounded disclosure.
        # These are *mixed recognized revenue per disclosed unit*, not realized
        # same-SKU pricing and not a causal price/mix/volume attribution.
        avg = values["revenue_optics"] / (values["product_volume_wan"] * D(10000))
        avg_prior = values["product_revenue_prior"] / (values["product_volume_wan_prior"] * D(10000))
        mixed = pct(avg - avg_prior, avg_prior, "mixed_unit_revenue")
        conversion = pct(values["cfo"], values["net_profit"], "cfo_to_profit")
        metrics = (
            ("mixed_product_revenue_per_disclosed_unit", "混合收入／只变化 · 非同型号价格", mixed),
            ("cfo_to_net_profit", "经营现金／合并净利润 · 同期", conversion),
            ("inventory_since_year_end", "存货余额较年末 · 两个时点", stock_change),
        )
        title = "产品混合收入／只提高，现金是否同步兑现？"
        narrative = (f"按已披露且取整的万只销量，产品混合收入／只由约"
                     f" {avg_prior:,.2f} 元变为 {avg:,.2f} 元；"
                     f"现金／净利润为 {display_pct(conversion)}。"
                     f"库存较2025年末变化 {display_pct(stock_change)}。")
        contrary = "缺型号级售价、订单、收款和期后库存证据，不能把混合收入／只的变化归因于实际提价。"
        provenance = "MIXED_REVENUE_PER_ROUNDED_UNIT_VS_CFO_AND_STOCK"
    if len({z[0] for z in metrics}) != 3:
        raise ValueError("DECISION_DUPLICATE_METRIC")
    return {"issuer": code, "values": values, "metrics": metrics,
            "title": title, "narrative": narrative, "contrary": contrary,
            "method": provenance}


def render_optical_decision(l: dict, memo: dict) -> str:
    d = decision_values(l)
    code = d["issuer"]
    doc = l["document"]
    if memo.get("review_status") not in (
            "ANALYST_REVIEWED",
            "AI_INTERNAL_ORIGINAL_SOURCE_CRITICAL_REVIEW__HUMAN_NOT_CHECKED"):
        raise ValueError("DECISION_MEMO_SOURCE_STATUS_NOT_ACCEPTED")
    if not memo.get("growth_counter") or not memo.get("watchlist"):
        raise ValueError("DECISION_NO_COUNTERCASE_OR_NEXT_DISCOUNTED_TEST")
    if not doc.get("source_url", "").startswith("https://"):
        raise ValueError("DECISION_ORIGINAL_PDF_URL_MISSING")
    if not doc.get("source_public_url_bytes_sha_verification", "").startswith("NOT_CHECKED"):
        # Separately revalidate a future proven public PDF before changing the
        # archival provenance. The URL is a locator, not a source SHA claim.
        raise ValueError("DECISION_PUBLIC_PDF_EQUIVALENCE_STATUS_DRIFT")
    research_falsifier = memo["watchlist"][0]["test"]
    if not research_falsifier:
        raise ValueError("DECISION_NEXT_DISCLOSURE_FALSIFIER_MISSING")
    metrics = "".join(
        f'<div class="optical-decision-metric" data-derived-key="{E(key, quote=True)}" '
        f'data-derived-ratio="{E(format(value, "f"), quote=True)}">'
        f'<small>{E(label)}</small><strong>{E(display_pct(value))}</strong></div>'
        for key, label, value in d["metrics"]
    )
    source_rows = []
    for key, period, kind, unit in CONFIG[code]:
        fact = l["facts"][key]
        original = d["values"][key]
        display = f"{original:,.0f} 万只" if unit == "万只" else f"{original:,.2f} 元"
        source_rows.append(
            f'<tr data-fact-id="{E(key)}" data-period="{E(period)}" '
            f'data-statement-kind="{E(kind)}" data-source-unit="{E(unit)}" '
            f'data-original-value="{E(format(original, "f"))}" '
            f'data-physical-page="{fact["page"]}">'
            f'<th scope="row">{E(fact.get("source_label", key))}</th>'
            f'<td>{E(display)}</td><td>{E(period)}</td>'
            f'<td><a target="_blank" rel="noopener noreferrer" '
            f'href="{E(doc["source_url"], quote=True)}#page={fact["page"]}">'
            f'p.{fact["page"]}</a></td></tr>'
        )
    return (
        f'<section class="optical-decision wrap" id="quantified-decision" '
        f'data-research-schema="financials.optical_decision.v1" '
        f'data-issuer="{E(code)}" data-original-pdf-sha256="{doc["source_sha256"]}" '
        f'data-derived-method="{d["method"]}" data-accounting-not-causal="true">'
        '<p class="optical-decision-eyebrow">SOURCE-BOUND DECISION / 关键经营矛盾</p>'
        f'<h2>{E(d["title"])}</h2>'
        f'<p class="optical-decision-lead">{E(d["narrative"])}</p>'
        f'<div class="optical-decision-metrics">{metrics}</div>'
        f'<p class="optical-decision-alternative"><b>竞争性解释：</b>{E(d["contrary"])} '
        f'{E(memo["growth_counter"])}</p>'
        f'<p class="optical-decision-falsifier"><b>下一期可推翻本判断的证据：</b>{E(research_falsifier)}</p>'
        '<details class="optical-decision-sources"><summary>展开 8 条可复算原始财报事实、期间及页码</summary>'
        '<div class="optical-decision-source-scroller"><table>'
        '<thead><tr><th>原报表指标</th><th>披露原值</th><th>期间 / 时点</th><th>PDF 物理页</th></tr></thead>'
        f'<tbody>{"".join(source_rows)}</tbody></table></div></details>'
        '<p class="optical-decision-integrity">算术和数据类型已校验；前后期流量、时点存量不可混为因果。'
        '原 PDF SHA 对应仓库存档；公开下载 URL 的字节等价未独立验证。'
        '跨公司、8–12 季度及独立人类财务／视觉审稿 NOT_CHECKED。</p>'
        '</section>'
    )
