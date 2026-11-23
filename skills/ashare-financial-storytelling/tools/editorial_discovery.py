"""Find physical pages worth reading before selecting a research thesis."""
from pathlib import Path
import re

INDEX_FILE = "editorial-opportunities.json"

# Cross-cutting disclosure patterns. Each match is a reading lead, including
# mentions in management text, tables of contents and unconsolidated notes.
PAGE_SIGNALS = {
    "comparison_basis": ("同一控制下企业合并", "追溯调整", "会计估计变更", "调整后"),
    "business_economics": ("分产品", "分部报告", "销售量", "单位成本", "产能利用率"),
    "earnings_quality": ("非经常性损益", "资产减值", "公允价值变动", "政府补助", "许可收入"),
    "cash_conversion": ("将净利润调节为经营活动现金流量", "合同负债", "经营性应收", "存货跌价"),
    "capital_constraints": ("受限资产", "未折现合同现金流量", "债务到期", "资本承诺", "受限货币资金"),
    "bank_economics": ("平均生息资产", "净利息收益率", "净息差", "不良贷款迁徙率", "贷款减值准备"),
    "insurance_economics": ("合同服务边际", "保险服务业绩", "新业务价值", "偿付能力充足率"),
    "business_events": ("前五名客户", "重大资产重组", "商誉减值测试", "资产负债表日后事项"),
}


def index_pages(page_texts):
    """Return all literal matches, grouping competing lines of enquiry by page."""
    hits = []
    for number, raw in enumerate(page_texts, 1):
        text = re.sub(r"\s+", "", raw)
        signals = {}
        for topic, needles in PAGE_SIGNALS.items():
            matched = [word for word in needles if word in text]
            if matched:
                signals[topic] = matched
        if signals:
            hits.append({"physical_page": number, "signals": signals})
    return hits


def build_index(dossier: Path, plan: dict, page_count: int) -> dict:
    extracted = dossier / "extracted"
    pages = ((extracted / f"p{number:03d}.txt").read_text(encoding="utf-8")
             for number in range(1, page_count + 1))
    return {
        "schema": "financials.editorial_opportunities.v1",
        "issuer": plan["issuer"],
        "fiscal_period": plan["fiscal_period"],
        "source_pdf_sha256": plan["source_pdf_sha256"],
        "status": "READING_LEADS_ONLY",
        "physical_page_count": page_count,
        "page_signals": index_pages(pages),
        "questions_from_ledger": plan["research_questions"],
    }
