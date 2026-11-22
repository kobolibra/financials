"""Adapt verified industrial dossier facts to the shared complete-profit flow."""
from full_profit_chain import compile_chain
from income_flow_v3 import plan
from source_income_adapter import compile_disclosed_income


OPERATING_ADJUSTMENTS = (
    ("税金及附加", "tax_surcharge", -1),
    ("销售费用", "selling", -1),
    ("管理费用", "admin", -1),
    ("研发费用", "rd_expense", -1),
    ("财务费用", "finance", -1),
    ("其他收益", "other_income", 1),
    ("投资净损益", "investment_income", 1),
    ("公允价值变动", "fair_value", 1),
    ("信用减值", "credit_impairment", 1),
    ("资产减值", "asset_impairment", 1),
    ("资产处置", "asset_disposal", 1),
)


def build(ledger):
    issuer = ledger["issuer"]
    if issuer.get("statement_format") != "general":
        raise ValueError("DOSSIER_PROFIT_CHAIN_REQUIRES_INDUSTRIAL_STATEMENT")
    facts, source = ledger["facts"], ledger["source"]
    current, prior = issuer["fiscal_period"], issuer["comparative_period"]

    def stages_row(key, label, terms, adjustments=()):
        return {
            "id": key, "label": label, "terms": terms,
            "adjustments": [{"label": name, "terms": [[fact, sign]]}
                            for name, fact, sign in adjustments if fact in facts],
        }

    stages = [
        stages_row("revenue", "营业收入", [["rev", 1]]),
        stages_row("gross", "营业毛利", [["rev", 1], ["cogs", -1]], [("营业成本", "cogs", -1)]),
        stages_row("operating", "营业利润", [["operating_profit", 1]], OPERATING_ADJUSTMENTS),
        stages_row("pretax", "税前利润", [["pretax", 1]],
                   [("营业外收入", "nonop_income", 1), ("营业外支出", "nonop_expense", -1)]),
        stages_row("net", "合并净利润", [["net_profit", 1]], [("所得税费用", "income_tax", -1)]),
        stages_row("parent", "归母净利润", [["parent_net", 1]], [("少数股东损益", "nci", -1)]),
    ]
    stage_keys = {key for stage in stages for group in (stage, *stage["adjustments"])
                  for key, _ in group["terms"]}
    if ledger.get("segments"):
        compile_disclosed_income(ledger)
    sources = [{"label": row["label"], "terms": [[row["rev"], 1]]}
               for row in ledger.get("segments", [])]
    if not sources:
        sources = [{"label": "合并营业收入", "terms": [["rev", 1]]}]
    source_keys = {key for group in sources for key, _ in group["terms"]}

    def flow(key, period):
        fact = facts[key]
        if (fact["period"] != period or fact["type"] != "flow" or fact["scope"] != "consolidated"
                or fact.get("unit") != "元" or fact.get("currency") != "CNY"):
            raise ValueError("DOSSIER_PROFIT_CHAIN_INCOMPATIBLE_FACT " + key)
        return fact

    for key in sorted(stage_keys):
        flow(key, current)
    comparatives = {key + "_prior": flow(key + "_prior", prior) for key in sorted(stage_keys)}
    for key in sorted(source_keys - stage_keys):
        other = key + "_prior"
        if other in facts:
            comparatives[other] = flow(other, prior)
    bundle = {
        "issuer": issuer["code"], "period": current,
        "scope": "consolidated", "currency": "CNY", "unit": "元",
        "source_pdf": {"source_sha256": source["original_bytes_sha256"]},
        "facts": {key: flow(key, current) for key in sorted(stage_keys | source_keys)},
        "comparatives": {"period": prior, "facts": comparatives},
        "sources": sources,
        "stages": stages,
        "editorial": {"layout": "INCOME_FLOW_V3", "show_disclosed_checkpoints": True},
    }
    compile_chain(bundle)
    # The same exact six-step closure must hold in the comparison column.
    prior_stages = [
        {**stage, "terms": [[key + "_prior", c] for key, c in stage["terms"]],
         "adjustments": [{**group, "terms": [[key + "_prior", c] for key, c in group["terms"]]}
                         for group in stage["adjustments"]]}
        for stage in stages
    ]
    from full_profit_chain import amount
    comparison = {"facts": comparatives}
    for previous, following in zip(prior_stages, prior_stages[1:]):
        if (amount(comparison, previous["terms"])
                + sum(amount(comparison, group["terms"]) for group in following["adjustments"])
                != amount(comparison, following["terms"])):
            raise ValueError("DOSSIER_PROFIT_CHAIN_PRIOR_STAGE_NOT_CLOSED " + following["id"])
    plan(bundle)
    return bundle
